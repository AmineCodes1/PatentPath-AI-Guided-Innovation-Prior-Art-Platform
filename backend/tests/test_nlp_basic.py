"""Unit tests for baseline NLP preprocessing and lexical scorers."""

from __future__ import annotations

import numpy as np

from app.services.nlp.bm25_scorer import BM25Scorer
from app.services.nlp.tfidf_scorer import TFIDFScorer


def test_bm25_highest_score_for_most_similar_document() -> None:
    corpus = [
        "Solar panel mounting bracket for rooftops",
        "Autonomous vehicle navigation with lidar and camera fusion",
        "Industrial fermentation bioreactor temperature controller",
    ]
    scorer = BM25Scorer(corpus)

    scores = scorer.score("autonomous vehicle lidar navigation")
    assert scores.shape == (3,)
    assert int(np.argmax(scores)) == 1


def test_tfidf_identical_text_similarity_is_one() -> None:
    text = "machine learning model for predictive maintenance"
    scorer = TFIDFScorer([text, "biomedical implant coating process"])

    scores = scorer.score(text)
    assert scores.shape == (2,)
    assert np.isclose(scores[0], 1.0, atol=1e-9)


def test_scorers_handle_empty_input_gracefully() -> None:
    bm25_empty = BM25Scorer([])
    tfidf_empty = TFIDFScorer([])

    bm25_scores = bm25_empty.score("any query")
    tfidf_scores = tfidf_empty.score("any query")

    assert bm25_scores.size == 0
    assert tfidf_scores.size == 0

    bm25_nonempty = BM25Scorer(["alpha beta", "gamma delta"])
    tfidf_nonempty = TFIDFScorer(["alpha beta", "gamma delta"])

    assert np.allclose(bm25_nonempty.score(""), np.zeros(2))
    assert np.allclose(bm25_nonempty.normalized_scores(""), np.zeros(2))
    assert np.allclose(tfidf_nonempty.score(""), np.zeros(2))
