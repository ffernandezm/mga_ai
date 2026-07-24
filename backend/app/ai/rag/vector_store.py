"""Vector store local para recuperación semántica simple."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from scipy import sparse

from .document_processor import DocumentChunk
from .embeddings import TfidfEmbeddingModel


class LocalVectorStore:
    """Persistencia local de chunks y matriz TF-IDF."""

    def __init__(self, index_dir: Path):
        self.index_dir = index_dir
        self.index_dir.mkdir(parents=True, exist_ok=True)

        self.chunks_file = self.index_dir / "chunks.json"
        self.matrix_file = self.index_dir / "embeddings.npz"
        self.vectorizer_file = self.index_dir / "vectorizer.joblib"

        self._embedding_model = TfidfEmbeddingModel()
        self._chunks: List[DocumentChunk] = []
        self._matrix: sparse.csr_matrix | None = None

    def exists(self) -> bool:
        return self.chunks_file.exists() and self.matrix_file.exists() and self.vectorizer_file.exists()

    def build(self, chunks: List[DocumentChunk]) -> None:
        if not chunks:
            raise ValueError("No hay chunks para indexar")

        self._chunks = chunks
        texts = [chunk.text for chunk in chunks]
        self._matrix = self._embedding_model.fit_transform(texts).tocsr()

        self._embedding_model.save(self.vectorizer_file)
        sparse.save_npz(self.matrix_file, self._matrix)

        serialized_chunks = [
            {
                "chunk_id": chunk.chunk_id,
                "text": chunk.text,
                "metadata": chunk.metadata,
            }
            for chunk in chunks
        ]
        self.chunks_file.write_text(json.dumps(serialized_chunks, ensure_ascii=False), encoding="utf-8")

    def load(self) -> None:
        raw_chunks = json.loads(self.chunks_file.read_text(encoding="utf-8"))
        self._chunks = [
            DocumentChunk(
                chunk_id=item["chunk_id"],
                text=item["text"],
                metadata=item.get("metadata", {}),
            )
            for item in raw_chunks
        ]
        self._embedding_model.load(self.vectorizer_file)
        self._matrix = sparse.load_npz(self.matrix_file).tocsr()

    def similarity_search(self, query: str, top_k: int, min_similarity: float) -> List[Dict]:
        if not query or self._matrix is None or not self._chunks:
            return []

        query_vector = self._embedding_model.transform([query]).tocsr()
        scores = (self._matrix @ query_vector.T).toarray().ravel().tolist()
        ranked = sorted(enumerate(scores), key=lambda item: item[1], reverse=True)

        results: List[Dict] = []
        for chunk_index, score in ranked[:top_k * 3]:
            if score < min_similarity:
                continue
            chunk = self._chunks[chunk_index]
            results.append(
                {
                    "chunk_id": chunk.chunk_id,
                    "text": chunk.text,
                    "metadata": chunk.metadata,
                    "score": float(score),
                }
            )
            if len(results) >= top_k:
                break

        return results
