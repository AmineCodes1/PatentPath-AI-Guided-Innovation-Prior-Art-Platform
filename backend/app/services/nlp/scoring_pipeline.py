"""Composite scoring pipeline orchestrating BM25, TF-IDF, and semantic similarity."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import logging
from time import perf_counter
from uuid import UUID

import numpy as np

from app.core.exceptions import NLPProcessingError
from app.models.patent_record import PatentRecord
from app.models.scored_result import RiskLabel
from app.services.nlp.bm25_scorer import BM25Scorer
from app.services.nlp.semantic_scorer import SemanticScorer
from app.services.nlp.tfidf_scorer import TFIDFScorer

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ScoredResultCreate:
    """Internal scored result payload used before DB persistence."""

    patent_id: UUID
    bm25_score: float
    tfidf_cosine: float
    semantic_cosine: float
    composite_score: float
    risk_label: RiskLabel
    rank: int


class ScoringPipeline:
    """Main NLP scoring orchestrator for prior-art ranking."""

    def __init__(self) -> None:
        self.semantic_scorer = get_semantic_scorer()

    @staticmethod
    def _risk_label(score: float) -> RiskLabel:
        if score >= 0.80:
            return RiskLabel.HIGH
        if score >= 0.55:
            return RiskLabel.MEDIUM
        if score >= 0.30:
            return RiskLabel.LOW
        return RiskLabel.MINIMAL

    def score_patents(self, query_text: str, patents: list[PatentRecord]) -> list[ScoredResultCreate]:
        """Score and rank patents using weighted lexical and semantic components."""
        if not patents:
            return []

        try:
            prepare_start = perf_counter()
            bm25_texts: list[str] = [f"{(p.title or '').strip()} {(p.abstract or '').strip()}".strip() for p in patents]
            tfidf_texts: list[str] = [
                (p.claims.strip() if p.claims and p.claims.strip() else (p.abstract or "").strip())
                for p in patents
            ]
            semantic_texts: list[str] = [f"{(p.title or '').strip()} {(p.abstract or '').strip()}".strip() for p in patents]
            logger.info("scoring.prepare_seconds=%0.4f", perf_counter() - prepare_start)

            score_start = perf_counter()
            bm25_scores = BM25Scorer(bm25_texts).normalized_scores(query_text)
            tfidf_scores = TFIDFScorer(tfidf_texts).score(query_text)
            semantic_scores = self.semantic_scorer.score(query_text, semantic_texts)
            logger.info("scoring.score_seconds=%0.4f", perf_counter() - score_start)

            rank_start = perf_counter()
            composite_scores = 0.30 * bm25_scores + 0.50 * tfidf_scores + 0.20 * semantic_scores
            ordering = np.argsort(-composite_scores)

            results: list[ScoredResultCreate] = []
            for rank, corpus_idx in enumerate(ordering, start=1):
                score_value = float(composite_scores[corpus_idx])
                results.append(
                    ScoredResultCreate(
                        patent_id=patents[int(corpus_idx)].id,
                        bm25_score=float(bm25_scores[corpus_idx]),
                        tfidf_cosine=float(tfidf_scores[corpus_idx]),
                        semantic_cosine=float(semantic_scores[corpus_idx]),
                        composite_score=score_value,
                        risk_label=self._risk_label(score_value),
                        rank=rank,
                    )
                )
            logger.info("scoring.rank_seconds=%0.4f", perf_counter() - rank_start)

            return results
        except Exception as exc:
            raise NLPProcessingError(f"Scoring pipeline failed: {exc}") from exc


@lru_cache(maxsize=128)
def get_semantic_scorer() -> SemanticScorer:
    """Return cached semantic scorer instances for repeated scoring tasks."""
    return SemanticScorer()
