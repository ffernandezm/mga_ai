"""Configuración del subsistema RAG."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


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
        base_app_dir = Path(__file__).resolve().parents[2]
        default_document = base_app_dir / "data" / "manual_conceptual_2015.pdf"
        default_index_dir = Path(__file__).resolve().parent / "index"

        return cls(
            enabled=os.getenv("RAG_ENABLED", "true").strip().lower() in {"1", "true", "yes", "on"},
            source_document_path=Path(os.getenv("RAG_SOURCE_DOCUMENT", str(default_document))).expanduser(),
            index_dir=Path(os.getenv("RAG_INDEX_DIR", str(default_index_dir))).expanduser(),
            chunk_size=max(int(os.getenv("RAG_CHUNK_SIZE", "1400")), 300),
            chunk_overlap=max(int(os.getenv("RAG_CHUNK_OVERLAP", "250")), 0),
            top_k=max(int(os.getenv("RAG_TOP_K", "4")), 1),
            min_similarity=float(os.getenv("RAG_MIN_SIMILARITY", "0.10")),
            embedding_provider=os.getenv("RAG_EMBEDDING_PROVIDER", "tfidf").strip().lower(),
            auto_reindex=os.getenv("RAG_AUTO_REINDEX", "false").strip().lower() in {"1", "true", "yes", "on"},
            max_context_chars=max(int(os.getenv("RAG_MAX_CONTEXT_CHARS", "7000")), 500),
        )
