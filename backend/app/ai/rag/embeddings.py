"""Embeddings locales para el pipeline RAG."""

from __future__ import annotations

from pathlib import Path
from typing import List

import joblib
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer


class TfidfEmbeddingModel:
    """Modelo de embeddings TF-IDF persistible."""

    def __init__(self, max_features: int = 20000):
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2),
            max_features=max_features,
            strip_accents="unicode",
            token_pattern=r"(?u)\\b\\w\\w+\\b",
        )

    def fit_transform(self, texts: List[str]) -> sparse.csr_matrix:
        return self.vectorizer.fit_transform(texts)

    def transform(self, texts: List[str]) -> sparse.csr_matrix:
        return self.vectorizer.transform(texts)

    def save(self, file_path: Path) -> None:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.vectorizer, file_path)

    def load(self, file_path: Path) -> None:
        self.vectorizer = joblib.load(file_path)
