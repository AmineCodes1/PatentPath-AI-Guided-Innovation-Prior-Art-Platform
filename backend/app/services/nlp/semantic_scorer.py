"""Semantic embedding scorer built on SentenceTransformer MiniLM."""

from __future__ import annotations

from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer


@lru_cache(maxsize=1)
def _get_embedding_model() -> SentenceTransformer:
    """Load and cache the MiniLM model once for the process lifetime."""
    return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


class SemanticScorer:
    """Compute semantic cosine similarity between query and patent corpus text."""

    def __init__(self) -> None:
        self._model = _get_embedding_model()
        self._embedding_dim = int(self._model.get_sentence_embedding_dimension())

    def encode(self, texts: list[str]) -> np.ndarray:
        """Encode text list into L2-normalized embeddings of shape (n_texts, 384)."""
        if not texts:
            return np.zeros((0, self._embedding_dim), dtype=np.float32)

        normalized_texts = [text.strip() for text in texts]
        embeddings = self._model.encode(
            normalized_texts,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        return np.asarray(embeddings, dtype=np.float32)

    def score(self, query_text: str, corpus_texts: list[str]) -> np.ndarray:
        """Return cosine similarities mapped to [0, 1] for all corpus entries."""
        if not corpus_texts:
            return np.zeros(0, dtype=float)

        query = (query_text or "").strip()
        if not query:
            return np.zeros(len(corpus_texts), dtype=float)

        query_vec = self.encode([query])
        corpus_matrix = self.encode(corpus_texts)
        if query_vec.size == 0 or corpus_matrix.size == 0:
            return np.zeros(len(corpus_texts), dtype=float)

        cosine = query_vec @ corpus_matrix.T
        cosine = np.asarray(cosine, dtype=np.float32).reshape(-1)

        # Normalize cosine from [-1, 1] to [0, 1] to keep scorer output comparable.
        scaled = (cosine + 1.0) / 2.0
        return np.clip(scaled, 0.0, 1.0).astype(float)
