"""Patent search API endpoints for query preview, execution, and results retrieval."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.gap_analysis import GapAnalysis
from app.models.innovation_project import InnovationProject
from app.models.scored_result import RiskLabel, ScoredResult
from app.models.search_session import SearchSession, SearchSessionStatus
from app.schemas.filters import SearchFilters
from app.schemas.gap_analysis import GapAnalysisSummary
from app.schemas.scored_result import ScoredResultRead, SearchResultsResponse
from app.schemas.search_session import SearchSessionRead
from app.services.query_builder import (
	LAST_BUILD_METADATA,
	build_cql_query,
	extract_keywords,
	suggest_ipc_classes,
	validate_cql,
)
from app.worker.celery_app import celery_app

router = APIRouter(prefix="/search", tags=["search"])

auth_scheme = HTTPBearer(auto_error=False)


def require_auth_token(
	credentials: HTTPAuthorizationCredentials | None = Depends(auth_scheme),
) -> str:
	"""Temporary auth guard requiring a Bearer token on protected search endpoints."""
	if credentials is None or not credentials.credentials:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Authentication required",
			headers={"WWW-Authenticate": "Bearer"},
		)
	return credentials.credentials


class PreviewQueryRequest(BaseModel):
	"""Request payload for previewing a generated CQL query."""

	model_config = ConfigDict(from_attributes=True)

	query_text: str = Field(min_length=10)
	filters: SearchFilters | None = None


class PreviewQueryResponse(BaseModel):
	"""Response payload for query preview endpoint."""

	model_config = ConfigDict(from_attributes=True)

	cql_generated: str
	keywords_extracted: list[str]
	ipc_suggestions: list[str]
	is_valid: bool
	validation_error: str | None = None
	metadata: dict[str, str] = Field(default_factory=dict)


class ExecuteSearchRequest(BaseModel):
	"""Request payload used to create and dispatch a search session."""

	model_config = ConfigDict(from_attributes=True)

	project_id: UUID
	query_text: str = Field(min_length=10)
	cql_override: str | None = None
	filters: SearchFilters | None = None


class ExecuteSearchResponse(BaseModel):
	"""Response payload returned after scheduling a background search task."""

	model_config = ConfigDict(from_attributes=True)

	session_id: UUID
	status: SearchSessionStatus
	estimated_seconds: int


def _to_scored_result_read(result: ScoredResult) -> ScoredResultRead:
	return ScoredResultRead.model_validate(
		{
			"patent": result.patent,
			"bm25_score": result.bm25_score,
			"tfidf_cosine": result.tfidf_cosine,
			"semantic_cosine": result.semantic_cosine,
			"composite_score": result.composite_score,
			"risk_label": result.risk_label,
			"rank": result.rank,
		}
	)


def _to_gap_summary(gap: GapAnalysis | None) -> GapAnalysisSummary | None:
	if gap is None:
		return None
	return GapAnalysisSummary.model_validate(gap)


@router.post("/preview-query", response_model=PreviewQueryResponse)
async def preview_query(
	payload: PreviewQueryRequest,
	_: str = Depends(require_auth_token),
) -> PreviewQueryResponse:
	"""Generate and validate a CQL preview before executing a full OPS search."""
	filters = payload.filters or SearchFilters()
	keywords = extract_keywords(payload.query_text)
	suggested_ipc = suggest_ipc_classes(keywords)
	cql = build_cql_query(payload.query_text, filters)
	is_valid, error_message = validate_cql(cql)

	return PreviewQueryResponse(
		cql_generated=cql,
		keywords_extracted=keywords,
		ipc_suggestions=suggested_ipc,
		is_valid=is_valid,
		validation_error=error_message or None,
		metadata=dict(LAST_BUILD_METADATA),
	)


@router.post("/execute", response_model=ExecuteSearchResponse, status_code=status.HTTP_202_ACCEPTED)
async def execute_search(
	payload: ExecuteSearchRequest,
	db: AsyncSession = Depends(get_db),
	_: str = Depends(require_auth_token),
) -> ExecuteSearchResponse:
	"""Create a pending search session and dispatch async processing through Celery."""
	project = await db.scalar(
		select(InnovationProject).where(InnovationProject.id == payload.project_id)
	)
	if project is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

	filters = payload.filters or SearchFilters()
	generated_cql = payload.cql_override or build_cql_query(payload.query_text, filters)
	is_valid, error_message = validate_cql(generated_cql)
	if not is_valid:
		raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=error_message)

	session = SearchSession(
		project_id=payload.project_id,
		query_text=payload.query_text,
		cql_generated=generated_cql,
		filters_json=filters.model_dump(mode="json"),
		status=SearchSessionStatus.PENDING,
		result_count=0,
	)
	db.add(session)
	await db.commit()
	await db.refresh(session)

	task = celery_app.send_task("run_patent_search", args=[str(session.id)])
	if task is None:
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to dispatch search task")

	return ExecuteSearchResponse(
		session_id=session.id,
		status=SearchSessionStatus.PENDING,
		estimated_seconds=15,
	)


@router.get("/session/{session_id}", response_model=SearchSessionRead)
async def get_session(
	session_id: UUID,
	db: AsyncSession = Depends(get_db),
	_: str = Depends(require_auth_token),
) -> SearchSessionRead:
	"""Return a search session by ID."""
	session = await db.scalar(select(SearchSession).where(SearchSession.id == session_id))
	if session is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Search session not found")
	return SearchSessionRead.model_validate(session)


@router.get("/session/{session_id}/results", response_model=SearchResultsResponse)
async def get_session_results(
	session_id: UUID,
	page: int = Query(default=1, ge=1),
	per_page: int = Query(default=20, ge=1, le=50),
	risk_filter: list[RiskLabel] | None = Query(default=None),
	db: AsyncSession = Depends(get_db),
	_: str = Depends(require_auth_token),
) -> SearchResultsResponse:
	"""Return paginated scored results for a completed or in-progress search session."""
	session = await db.scalar(select(SearchSession).where(SearchSession.id == session_id))
	if session is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Search session not found")

	filters = [ScoredResult.session_id == session_id]
	if risk_filter:
		filters.append(ScoredResult.risk_label.in_(risk_filter))

	total_count = await db.scalar(select(func.count()).select_from(ScoredResult).where(*filters))
	total_count = int(total_count or 0)

	query = (
		select(ScoredResult)
		.where(*filters)
		.options(selectinload(ScoredResult.patent))
		.order_by(ScoredResult.rank.asc())
		.offset((page - 1) * per_page)
		.limit(per_page)
	)
	results = list((await db.scalars(query)).all())

	gap_analysis = await db.scalar(
		select(GapAnalysis).where(GapAnalysis.session_id == session_id)
	)

	return SearchResultsResponse(
		session_id=session_id,
		total_count=total_count,
		results=[_to_scored_result_read(result) for result in results],
		gap_analysis=_to_gap_summary(gap_analysis),
	)
