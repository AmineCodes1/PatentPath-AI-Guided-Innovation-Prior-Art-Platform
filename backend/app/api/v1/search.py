"""Patent search API endpoints for query preview, execution, and results retrieval."""

from __future__ import annotations

import csv
import io
from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.middleware.rate_limiter import enforce_search_rate_limit
from app.models.innovation_project import InnovationProject
from app.models.scored_result import ScoredResult
from app.models.scored_result import RiskLabel
from app.models.search_session import SearchSession, SearchSessionStatus
from app.schemas.filters import SearchFilters
from app.schemas.scored_result import SearchResultsResponse
from app.schemas.search_session import SearchSessionRead
from app.services.query_builder import (
	LAST_BUILD_METADATA,
	build_cql_query,
	extract_keywords,
	suggest_ipc_classes,
	validate_cql,
)
from app.services.search_service import get_search_stats, get_session_results as get_session_results_service
from app.worker.celery_app import celery_app

router = APIRouter(prefix="/search", tags=["search"])
SESSION_NOT_FOUND_DETAIL = "Search session not found"

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


class SavePatentRequest(BaseModel):
	"""Request payload for bookmarking a patent within a search session context."""

	model_config = ConfigDict(from_attributes=True)

	publication_number: str = Field(min_length=3)
	notes: str | None = Field(default=None, max_length=2000)


def _resolve_user_id_from_token(token: str) -> UUID:
	"""Temporary user resolution until full JWT auth dependency is wired."""
	try:
		return UUID(token.strip())
	except Exception as exc:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid authentication token format",
			headers={"WWW-Authenticate": "Bearer"},
		) from exc


@router.post("/preview-query")
async def preview_query(
	payload: PreviewQueryRequest,
	_: Annotated[str, Depends(require_auth_token)],
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


@router.post("/execute", status_code=status.HTTP_202_ACCEPTED)
async def execute_search(
	payload: ExecuteSearchRequest,
	db: Annotated[AsyncSession, Depends(get_db)],
	_: Annotated[str, Depends(enforce_search_rate_limit)],
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


@router.get("/session/{session_id}")
async def get_session(
	session_id: UUID,
	db: Annotated[AsyncSession, Depends(get_db)],
	_: Annotated[str, Depends(require_auth_token)],
) -> SearchSessionRead:
	"""Return a search session by ID."""
	session = await db.scalar(select(SearchSession).where(SearchSession.id == session_id))
	if session is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=SESSION_NOT_FOUND_DETAIL)
	return SearchSessionRead.model_validate(session)


@router.get("/session/{session_id}/results")
async def get_session_results(
	session_id: UUID,
	page: Annotated[int, Query(default=1, ge=1)],
	per_page: Annotated[int, Query(default=20, ge=1, le=50)],
	risk_filter: Annotated[list[RiskLabel] | None, Query(default=None)],
	db: Annotated[AsyncSession, Depends(get_db)],
	token: Annotated[str, Depends(require_auth_token)],
) -> SearchResultsResponse:
	"""Return paginated scored results for a completed or in-progress search session."""
	user_id = _resolve_user_id_from_token(token)
	return await get_session_results_service(
		db=db,
		session_id=session_id,
		user_id=user_id,
		page=page,
		per_page=per_page,
		risk_filter=risk_filter,
	)


@router.post("/session/{session_id}/save-patent")
async def save_patent_to_project(
	session_id: UUID,
	payload: SavePatentRequest,
	db: Annotated[AsyncSession, Depends(get_db)],
	token: Annotated[str, Depends(require_auth_token)],
) -> dict[str, object]:
	"""Persist a user-selected patent reference for later project-level review."""
	user_id = _resolve_user_id_from_token(token)
	session = await db.scalar(
		select(SearchSession)
		.join(InnovationProject, InnovationProject.id == SearchSession.project_id)
		.where(SearchSession.id == session_id, InnovationProject.user_id == user_id)
	)
	if session is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=SESSION_NOT_FOUND_DETAIL)

	saved_patents = list((session.filters_json or {}).get("saved_patents", []))
	publication_number = payload.publication_number.strip().upper()

	if not any(item.get("publication_number") == publication_number for item in saved_patents if isinstance(item, dict)):
		saved_patents.append(
			{
				"publication_number": publication_number,
				"notes": payload.notes,
				"saved_at": datetime.now(timezone.utc).isoformat(),
			}
		)

	updated_filters = dict(session.filters_json or {})
	updated_filters["saved_patents"] = saved_patents
	session.filters_json = updated_filters
	await db.commit()

	return {
		"session_id": session_id,
		"project_id": session.project_id,
		"saved_patent": publication_number,
		"saved_count": len(saved_patents),
	}


@router.get("/session/{session_id}/stats")
async def get_session_stats(
	session_id: UUID,
	db: Annotated[AsyncSession, Depends(get_db)],
	token: Annotated[str, Depends(require_auth_token)],
) -> dict[str, object]:
	"""Return aggregated metrics for the search results dashboard widget."""
	user_id = _resolve_user_id_from_token(token)
	return await get_search_stats(db=db, session_id=session_id, user_id=user_id)


@router.get("/session/{session_id}/results/export")
async def export_session_results_csv(
	session_id: UUID,
	db: Annotated[AsyncSession, Depends(get_db)],
	token: Annotated[str, Depends(require_auth_token)],
) -> StreamingResponse:
	"""Export all scored results for a session as a downloadable CSV file."""
	user_id = _resolve_user_id_from_token(token)
	session = await db.scalar(
		select(SearchSession)
		.join(InnovationProject, InnovationProject.id == SearchSession.project_id)
		.where(SearchSession.id == session_id, InnovationProject.user_id == user_id)
	)
	if session is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=SESSION_NOT_FOUND_DETAIL)

	rows = list(
		(
			await db.execute(
				select(ScoredResult)
				.where(ScoredResult.session_id == session_id)
				.options(selectinload(ScoredResult.patent))
				.order_by(ScoredResult.rank.asc())
			)
		).scalars()
	)

	buffer = io.StringIO()
	writer = csv.writer(buffer)
	writer.writerow([
		"Rank",
		"Publication Number",
		"Title",
		"Composite Score",
		"Risk Label",
		"Espacenet URL",
	])
	for result in rows:
		if result.patent is None:
			continue
		writer.writerow([
			result.rank,
			result.patent.publication_number,
			result.patent.title,
			f"{result.composite_score:.4f}",
			result.risk_label.value,
			result.patent.espacenet_url,
		])

	buffer.seek(0)
	headers = {
		"Content-Disposition": f'attachment; filename="patentpath_results_{session_id}.csv"',
	}
	return StreamingResponse(iter([buffer.getvalue()]), media_type="text/csv", headers=headers)
