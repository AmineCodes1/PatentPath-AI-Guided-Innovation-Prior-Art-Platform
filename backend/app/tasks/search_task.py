"""Celery task executing end-to-end patent search and scoring pipeline."""

from __future__ import annotations

import asyncio
import logging
from uuid import UUID

from sqlalchemy import delete, select

from app.core.database import SessionLocal
from app.models.scored_result import ScoredResult
from app.models.search_session import SearchSession, SearchSessionStatus
from app.schemas.filters import SearchFilters
from app.services.nlp.scoring_pipeline import ScoringPipeline
from app.services.ops_connector import ops_connector
from app.services.patent_cache_service import bulk_fetch_and_cache
from app.services.query_builder import build_cql_query
from app.worker.celery_app import celery_app

logger = logging.getLogger(__name__)


async def _mark_session_failed(session_id: str, error_message: str) -> None:
    """Persist failed status and failure details for a search session."""
    session_uuid = UUID(session_id)
    async with SessionLocal() as db:
        session = await db.scalar(select(SearchSession).where(SearchSession.id == session_uuid))
        if session is None:
            return

        current_filters = dict(session.filters_json or {})
        current_filters["error_message"] = error_message
        session.filters_json = current_filters
        session.status = SearchSessionStatus.FAILED
        await db.commit()


async def _run_patent_search_async(session_id: str) -> dict[str, object]:
    """Run the async search flow for one search session."""
    session_uuid = UUID(session_id)

    async with SessionLocal() as db:
        session = await db.scalar(select(SearchSession).where(SearchSession.id == session_uuid))
        if session is None:
            raise ValueError(f"Search session not found: {session_id}")

        session.status = SearchSessionStatus.PROCESSING
        await db.commit()

        filters = SearchFilters.model_validate(session.filters_json or {})
        cql = build_cql_query(session.query_text, filters)
        session.cql_generated = cql
        await db.commit()

        raw_refs = await ops_connector.search_patents(cql=cql, rows=50)
        pub_refs = [item.publication_ref for item in raw_refs if item.publication_ref]
        patents = await bulk_fetch_and_cache(db=db, pub_refs=pub_refs)

        scored_payloads = ScoringPipeline().score_patents(query_text=session.query_text, patents=patents)

        await db.execute(delete(ScoredResult).where(ScoredResult.session_id == session.id))
        db.add_all(
            [
                ScoredResult(
                    session_id=session.id,
                    patent_id=payload.patent_id,
                    bm25_score=payload.bm25_score,
                    tfidf_cosine=payload.tfidf_cosine,
                    semantic_cosine=payload.semantic_cosine,
                    composite_score=payload.composite_score,
                    risk_label=payload.risk_label,
                    rank=payload.rank,
                )
                for payload in scored_payloads
            ]
        )

        session.result_count = len(scored_payloads)
        session.status = SearchSessionStatus.COMPLETE
        await db.commit()

        return {
            "session_id": session_id,
            "status": SearchSessionStatus.COMPLETE.value,
            "result_count": len(scored_payloads),
        }


@celery_app.task(bind=True, max_retries=3, name="run_patent_search")
def run_patent_search(self, session_id: str) -> dict[str, object]:
    """Celery entrypoint for search execution with retry support."""
    try:
        return asyncio.run(_run_patent_search_async(session_id=session_id))
    except Exception as exc:
        logger.exception("Search task failed for session %s", session_id)
        asyncio.run(_mark_session_failed(session_id=session_id, error_message=str(exc)))

        if self.request.retries < self.max_retries:
            countdown = 2 ** (self.request.retries + 1)
            raise self.retry(exc=exc, countdown=countdown)

        raise
