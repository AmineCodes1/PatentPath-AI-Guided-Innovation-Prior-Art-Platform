"""BM25 scoring utilities for ranking patent corpus relevance."""

from __future__ import annotations

import numpy as np
from rank_bm25 import BM25Okapi

from app.services.nlp.preprocessor import preprocess_text


class BM25Scorer:
    """Compute raw and normalized BM25 scores for a prepared corpus."""

    def __init__(self, corpus_texts: list[str]):
        self._corpus_tokens: list[list[str]] = [preprocess_text(text) for text in corpus_texts]
        self._size = len(self._corpus_tokens)
        self._bm25 = BM25Okapi(self._corpus_tokens) if self._size > 0 else None

    def score(self, query_text: str) -> np.ndarray:
        """Return raw BM25 relevance scores for each corpus document."""
        if self._size == 0 or self._bm25 is None:
            return np.zeros(0, dtype=float)

        query_tokens = preprocess_text(query_text)
        if not query_tokens:
            return np.zeros(self._size, dtype=float)

        scores = self._bm25.get_scores(query_tokens)
        return np.asarray(scores, dtype=float)

    def normalized_scores(self, query_text: str) -> np.ndarray:
        """Min-max normalize raw BM25 scores into [0, 1] with stable zero fallback."""
        raw_scores = self.score(query_text)
        if raw_scores.size == 0:
            return raw_scores

        minimum = float(np.min(raw_scores))
        maximum = float(np.max(raw_scores))
        if maximum == minimum or np.allclose(raw_scores, 0.0):
            return np.zeros(raw_scores.shape[0], dtype=float)

        return (raw_scores - minimum) / (maximum - minimum)
