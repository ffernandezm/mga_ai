"""Orquestador RAG: indexación, carga y recuperación de contexto."""

from __future__ import annotations

import logging
from pathlib import Path
from threading import Lock
from typing import List

from .config import RAGConfig
from .document_processor import DocumentProcessor
from .vector_store import LocalVectorStore

logger = logging.getLogger(__name__)


class RAGManager:
    """Gestiona ciclo de vida del índice y retrieval para prompts."""

    def __init__(self, config: RAGConfig | None = None):
        self.config = config or RAGConfig.from_env()
        self.processor = DocumentProcessor()
        self.vector_store = LocalVectorStore(index_dir=self.config.index_dir)
        self._ready = False
        self._lock = Lock()

    def _index_if_needed(self) -> None:
        if not self.config.enabled:
            logger.info("RAG deshabilitado por configuración")
            self._ready = True
            return

        with self._lock:
            if self._ready:
                return

            if not self.config.source_document_path.exists():
                logger.warning(
                    "Documento fuente de RAG no encontrado en %s",
                    self.config.source_document_path,
                )
                self._ready = True
                return

            should_rebuild = self.config.auto_reindex or (not self.vector_store.exists())

            if should_rebuild:
                logger.info("Construyendo índice RAG desde %s", self.config.source_document_path)
                chunks = self.processor.load_and_chunk_pdf(
                    file_path=self.config.source_document_path,
                    chunk_size=self.config.chunk_size,
                    chunk_overlap=self.config.chunk_overlap,
                )
                self.vector_store.build(chunks)
                logger.info("Índice RAG generado con %s chunks", len(chunks))
            else:
                logger.info("Cargando índice RAG existente desde %s", self.config.index_dir)
                self.vector_store.load()

            self._ready = True

    def get_relevant_context(self, query: str) -> str:
        if not query:
            return ""

        try:
            self._index_if_needed()
            if not self.config.enabled:
                return ""

            results = self.vector_store.similarity_search(
                query=query,
                top_k=self.config.top_k,
                min_similarity=self.config.min_similarity,
            )

            if not results:
                return ""

            blocks: List[str] = ["Contexto recuperado (RAG) del documento conceptual:"]
            for item in results:
                start_char = item.get("metadata", {}).get("start_char", "?")
                score = item.get("score", 0.0)
                blocks.append(
                    f"- Fuente: manual_conceptual_2015.pdf | chunk={item['chunk_id']} | start_char={start_char} | similitud={score:.3f}\n"
                    f"  {item['text']}"
                )

            merged = "\n".join(blocks)
            return merged[: self.config.max_context_chars]
        except Exception as exc:
            logger.warning("No fue posible recuperar contexto RAG: %s", exc, exc_info=True)
            return ""

    def rebuild_index(self) -> None:
        """Reconstruye índice forzando nueva lectura/chunking/embeddings."""
        with self._lock:
            self._ready = False
            if self.config.source_document_path.exists():
                chunks = self.processor.load_and_chunk_pdf(
                    file_path=self.config.source_document_path,
                    chunk_size=self.config.chunk_size,
                    chunk_overlap=self.config.chunk_overlap,
                )
                self.vector_store.build(chunks)
                self._ready = True
                logger.info("Índice RAG reconstruido con %s chunks", len(chunks))
