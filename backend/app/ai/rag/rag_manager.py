"""Orquestador RAG: indexación, carga y recuperación de contexto."""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from threading import Lock
from time import perf_counter
from typing import Dict, List, Optional

from .config import RAGConfig
from .document_processor import DocumentProcessor
from .section_terms import build_retrieval_query
from .vector_store import LocalVectorStore

logger = logging.getLogger(__name__)


class RAGManager:
    """Gestiona ciclo de vida del índice y retrieval para prompts."""

    def __init__(self, config: RAGConfig | None = None):
        self.config = config or RAGConfig.from_env()
        self.processor = DocumentProcessor()
        self.vector_store = LocalVectorStore(index_dir=self.config.index_dir)
        self._ready = False
        self._available = False
        self._lock = Lock()

    @property
    def is_ready(self) -> bool:
        return self._ready and (not self.config.enabled or self._available)

    def prepare(self) -> bool:
        """Carga o construye el índice sin ejecutar retrieval ni llamar al LLM."""
        self._index_if_needed()
        return self.is_ready

    def _source_fingerprint(self) -> Dict:
        """Identidad del corpus + configuración que obliga a reindexar si cambia."""
        path = self.config.source_document_path
        digest = hashlib.sha256()
        with open(path, "rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
        return {
            "source_document": path.name,
            "source_size": path.stat().st_size,
            "source_hash": digest.hexdigest(),
            "corpus_scope": self.processor.CORPUS_SCOPE,
            "chunk_size": self.config.chunk_size,
            "chunk_overlap": self.config.chunk_overlap,
            "vectorizer": "tfidf",
            "ngram_range": [1, 2],
        }

    def _index_matches_source(self, fingerprint: Dict) -> bool:
        stored = self.vector_store.read_metadata()
        if not stored:
            logger.info("Índice RAG sin metadata de identidad; se reconstruye para garantizar el corpus correcto.")
            return False
        keys = (
            "source_document",
            "source_hash",
            "corpus_scope",
            "chunk_size",
            "chunk_overlap",
            "vectorizer",
            "ngram_range",
        )
        for key in keys:
            if stored.get(key) != fingerprint[key]:
                logger.warning(
                    "Índice RAG desactualizado: '%s' cambió (índice=%r, actual=%r). Se reconstruye.",
                    key,
                    stored.get(key),
                    fingerprint[key],
                )
                return False
        return True


    def _index_if_needed(self) -> None:
        if not self.config.enabled:
            logger.info("RAG deshabilitado por configuración")
            self._ready = True
            self._available = False
            return

        with self._lock:
            if self._ready:
                return

            if not self.config.source_document_path.exists():
                logger.error(
                    "RAG_SOURCE_MISSING | Documento fuente de RAG no encontrado en %s. "
                    "No se construirá índice; el chatbot continuará sin contexto documental.",
                    self.config.source_document_path,
                )
                self._ready = True
                self._available = False
                return

            logger.info(
                "RAG source: %s | path=%s | size=%s bytes",
                self.config.source_document_path.name,
                self.config.source_document_path,
                self.config.source_document_path.stat().st_size,
            )

            try:
                fingerprint = self._source_fingerprint()
            except OSError:
                logger.exception(
                    "RAG_SOURCE_UNREADABLE | No se pudo leer el documento fuente %s.",
                    self.config.source_document_path,
                )
                self._ready = True
                self._available = False
                return

            should_rebuild = (
                self.config.auto_reindex
                or (not self.vector_store.exists())
                or (not self._index_matches_source(fingerprint))
            )

            if should_rebuild:
                logger.info("Construyendo índice RAG desde %s", self.config.source_document_path)
                try:
                    chunks = self.processor.load_and_chunk_pdf(
                        file_path=self.config.source_document_path,
                        chunk_size=self.config.chunk_size,
                        chunk_overlap=self.config.chunk_overlap,
                    )
                    self.vector_store.build(chunks, metadata=fingerprint)
                except Exception:
                    logger.exception(
                        "RAG_INDEX_BUILD_FAILED | No fue posible construir el índice RAG desde %s "
                        "(chunk_size=%s chunk_overlap=%s). El chatbot continuará sin contexto documental.",
                        self.config.source_document_path,
                        self.config.chunk_size,
                        self.config.chunk_overlap,
                    )
                    self._ready = True
                    self._available = False
                    return
                logger.info("Índice RAG generado con %s chunks", len(chunks))
            else:
                logger.info("Cargando índice RAG existente desde %s", self.config.index_dir)
                try:
                    self.vector_store.load()
                except Exception:
                    logger.exception(
                        "RAG_INDEX_LOAD_FAILED | Índice RAG existente en %s no se pudo cargar (posible índice "
                        "corrupto o incompatible). Usa RAGManager.rebuild_index() para regenerarlo.",
                        self.config.index_dir,
                    )
                    self._ready = True
                    self._available = False
                    return

            self._available = True
            self._ready = True

    def get_relevant_context(self, query: str, section: Optional[str] = None) -> str:
        """Recupera contexto documental.

        `section` (clave canónica MGA) solo enriquece la consulta de retrieval;
        la pregunta original del usuario no se modifica y llega intacta al LLM.
        """
        if not query:
            return ""

        retrieval_query = build_retrieval_query(query, section)

        total_start = perf_counter()
        try:
            index_start = perf_counter()
            self._index_if_needed()
            index_ms = (perf_counter() - index_start) * 1000
            if not self.config.enabled:
                return ""

            search_start = perf_counter()
            results = self.vector_store.similarity_search(
                query=retrieval_query,
                top_k=self.config.top_k,
                min_similarity=self.config.min_similarity,
            )
            search_ms = (perf_counter() - search_start) * 1000

            if not results:
                total_ms = (perf_counter() - total_start) * 1000
                logger.info(
                    "⏱️ RAG timing | enabled=%s index_ms=%.1f search_ms=%.1f total_ms=%.1f hits=0",
                    self.config.enabled,
                    index_ms,
                    search_ms,
                    total_ms,
                )
                return ""

            blocks: List[str] = ["Contexto recuperado (RAG) del documento conceptual:"]
            for item in results:
                metadata = item.get("metadata", {})
                source_document = metadata.get("source_document", self.config.source_document_path.name)
                page = metadata.get("page", "?")
                score = item.get("score", 0.0)
                blocks.append(
                    f"- Fuente: {source_document} | pagina={page} | chunk={item['chunk_id']} | similitud={score:.3f}\n"
                    f"  {item['text']}"
                )

            merged = "\n".join(blocks)
            final_context = merged[: self.config.max_context_chars]
            total_ms = (perf_counter() - total_start) * 1000
            logger.info(
                "⏱️ RAG timing | enabled=%s index_ms=%.1f search_ms=%.1f total_ms=%.1f hits=%s context_chars=%s",
                self.config.enabled,
                index_ms,
                search_ms,
                total_ms,
                len(results),
                len(final_context),
            )
            return final_context
        except Exception:
            total_ms = (perf_counter() - total_start) * 1000
            # Disponibilidad degradada: el chatbot sigue funcionando sin contexto
            # documental, pero el fallo queda registrado con stack trace completo
            # (nunca se expone al usuario final).
            logger.exception(
                "RAG_RETRIEVAL_FAILED | Error recuperando contexto RAG (documento=%s, index_dir=%s, "
                "top_k=%s, min_similarity=%s, total_ms=%.1f). Se devuelve contexto vacío.",
                self.config.source_document_path,
                self.config.index_dir,
                self.config.top_k,
                self.config.min_similarity,
                total_ms,
            )
            return ""

    def get_relevant_sources(self, query: str, section: Optional[str] = None) -> List[Dict]:
        """Return user-safe retrieval metadata without exposing prompts or index internals."""
        if not query or not self.config.enabled:
            return []
        try:
            self._index_if_needed()
            results = self.vector_store.similarity_search(
                query=build_retrieval_query(query, section),
                top_k=self.config.top_k,
                min_similarity=self.config.min_similarity,
            )
            return [
                {
                    "document": item.get("metadata", {}).get("source_document", self.config.source_document_path.name),
                    "page": item.get("metadata", {}).get("page"),
                    "content": item.get("text", "")[:600],
                    "similarity": round(float(item.get("score", 0.0)), 3),
                }
                for item in results
            ]
        except Exception:
            logger.exception("RAG_TRACE_FAILED | No se pudieron recuperar fuentes para trazabilidad")
            return []

    def rebuild_index(self) -> None:
        """Reconstruye índice forzando nueva lectura/chunking/embeddings."""
        with self._lock:
            self._ready = False
            self._available = False
            if self.config.source_document_path.exists():
                chunks = self.processor.load_and_chunk_pdf(
                    file_path=self.config.source_document_path,
                    chunk_size=self.config.chunk_size,
                    chunk_overlap=self.config.chunk_overlap,
                )
                self.vector_store.build(chunks, metadata=self._source_fingerprint())
                self._available = True
                self._ready = True
                logger.info("Índice RAG reconstruido con %s chunks", len(chunks))
