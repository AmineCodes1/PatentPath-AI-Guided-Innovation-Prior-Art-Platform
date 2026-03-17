"""TF-IDF cosine scoring utilities for patent text similarity."""

from __future__ import annotations

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class TFIDFScorer:
    """Compute cosine similarity between query text and corpus using TF-IDF vectors."""

    def __init__(self, corpus_texts: list[str]):
        self._size = len(corpus_texts)
        self._vectorizer: TfidfVectorizer | None = None
        self._corpus_matrix = None

        if self._size == 0:
            return

        vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=10000,
            sublinear_tf=True,
            min_df=1,
        )

        try:
            matrix = vectorizer.fit_transform(corpus_texts)
        except ValueError:
            self._vectorizer = None
            self._corpus_matrix = None
            return

        self._vectorizer = vectorizer
        self._corpus_matrix = matrix

    def score(self, query_text: str) -> np.ndarray:
        """Return cosine similarities in [0, 1] for each corpus document."""
        if self._size == 0:
            return np.zeros(0, dtype=float)

        if self._vectorizer is None or self._corpus_matrix is None:
            return np.zeros(self._size, dtype=float)

        if not query_text.strip():
            return np.zeros(self._size, dtype=float)

        query_vector = self._vectorizer.transform([query_text])
        similarities = cosine_similarity(query_vector, self._corpus_matrix).flatten()
        return np.asarray(similarities, dtype=float)
