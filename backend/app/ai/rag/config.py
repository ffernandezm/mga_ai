"""Configuración del subsistema RAG."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# El .env del backend se carga aquí para que la configuración RAG sea
# determinista y no dependa de que otro módulo (p. ej. llm_manager) se haya
# importado antes. `load_dotenv` no sobrescribe variables ya presentes.
_BACKEND_DIR = Path(__file__).resolve().parents[3]
_ENV_PATH = _BACKEND_DIR / ".env"

# Única fuente documental del RAG. El corpus es intencionalmente un solo
# documento; no combinar PDFs.
DEFAULT_SOURCE_DOCUMENT = _BACKEND_DIR / "app" / "data" / "Documento_conceptual_2023.pdf"


def _resolve_path(raw: str, default: Path) -> Path:
    """Resuelve rutas relativas contra la raíz del backend (portable entre entornos)."""
    candidate = Path(raw).expanduser() if raw else default
    if not candidate.is_absolute():
        candidate = _BACKEND_DIR / candidate
    return candidate


@dataclass
class RAGConfig:
    """Configuración principal para indexación y recuperación."""

    enabled: bool
    source_document_path: Path
    index_dir: Path
    chunk_size: int
    chunk_overlap: int
    top_k: int
    min_similarity: float
    embedding_provider: str
    auto_reindex: bool
    max_context_chars: int

    @classmethod
    def from_env(cls) -> "RAGConfig":
        load_dotenv(dotenv_path=_ENV_PATH)

        default_index_dir = Path(__file__).resolve().parent / "index"

        return cls(
            enabled=os.getenv("RAG_ENABLED", "true").strip().lower() in {"1", "true", "yes", "on"},
            source_document_path=_resolve_path(os.getenv("RAG_SOURCE_DOCUMENT", ""), DEFAULT_SOURCE_DOCUMENT),
            index_dir=_resolve_path(os.getenv("RAG_INDEX_DIR", ""), default_index_dir),
            chunk_size=max(int(os.getenv("RAG_CHUNK_SIZE", "1400")), 300),
            chunk_overlap=max(int(os.getenv("RAG_CHUNK_OVERLAP", "250")), 0),
            top_k=max(int(os.getenv("RAG_TOP_K", "4")), 1),
            min_similarity=float(os.getenv("RAG_MIN_SIMILARITY", "0.10")),
            embedding_provider=os.getenv("RAG_EMBEDDING_PROVIDER", "tfidf").strip().lower(),
            auto_reindex=os.getenv("RAG_AUTO_REINDEX", "false").strip().lower() in {"1", "true", "yes", "on"},
            max_context_chars=max(int(os.getenv("RAG_MAX_CONTEXT_CHARS", "7000")), 500),
        )
