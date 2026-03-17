"""Innovation project workspace API routes for CRUD, timeline analytics, and notes."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.innovation_project import ProjectCreate, ProjectRead, ProjectUpdate
from app.services.project_service import (
    archive_project,
    create_project,
    create_project_note,
    delete_project_note,
    get_project,
    get_project_risk_trend,
    get_project_sessions,
    get_project_timeline,
    get_user_projects,
    list_project_notes,
    timeline_to_dict,
    update_project,
)

router = APIRouter(prefix="/projects", tags=["projects"])

auth_scheme = HTTPBearer(auto_error=False)


def require_auth_token(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(auth_scheme)],
) -> str:
    """Temporary auth guard requiring a Bearer token."""
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials


def _resolve_user_id_from_token(token: str) -> UUID:
    """Temporary user resolution until full JWT dependency is wired."""
    try:
        return UUID(token.strip())
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token format",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


class ProjectSessionSummary(BaseModel):
    """Compact search session payload for project-level listings."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    query_text: str
    cql_generated: str
    result_count: int
    status: str
    executed_at: datetime


class TimelineEventRead(BaseModel):
    """Timeline event payload for project activity feeds."""

    model_config = ConfigDict(from_attributes=True)

    event_type: str
    timestamp: datetime
    title: str
    summary: str
    session_id: UUID | None


class ProjectNoteCreate(BaseModel):
    """Payload for creating a project note."""

    model_config = ConfigDict(from_attributes=True)

    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)
    linked_session_id: UUID | None = None


class ProjectNoteRead(BaseModel):
    """Project note response payload."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    title: str
    content: str
    linked_session_id: UUID | None
    created_at: datetime


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_project_endpoint(
    payload: ProjectCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[str, Depends(require_auth_token)],
) -> ProjectRead:
    """Create an innovation project for the authenticated user."""
    user_id = _resolve_user_id_from_token(token)
    project = await create_project(db=db, user_id=user_id, data=payload)
    return ProjectRead.model_validate(project).model_copy(update={"sessions_count": 0})


@router.get("")
async def list_projects_endpoint(
    db: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[str, Depends(require_auth_token)],
) -> list[ProjectRead]:
    """List all projects owned by the authenticated user."""
    user_id = _resolve_user_id_from_token(token)
    projects = await get_user_projects(db=db, user_id=user_id)
    return [
        ProjectRead.model_validate(project).model_copy(update={"sessions_count": len(project.search_sessions)})
        for project in projects
    ]


@router.get("/{project_id}")
async def get_project_endpoint(
    project_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[str, Depends(require_auth_token)],
) -> ProjectRead:
    """Return details of one owned project."""
    user_id = _resolve_user_id_from_token(token)
    project = await get_project(db=db, project_id=project_id, user_id=user_id)
    return ProjectRead.model_validate(project).model_copy(update={"sessions_count": len(project.search_sessions)})


@router.put("/{project_id}")
async def update_project_endpoint(
    project_id: UUID,
    payload: ProjectUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[str, Depends(require_auth_token)],
) -> ProjectRead:
    """Update fields of one owned project."""
    user_id = _resolve_user_id_from_token(token)
    updated = await update_project(db=db, project_id=project_id, user_id=user_id, data=payload)
    sessions = await get_project_sessions(db=db, project_id=project_id)
    return ProjectRead.model_validate(updated).model_copy(update={"sessions_count": len(sessions)})


@router.delete("/{project_id}")
async def archive_project_endpoint(
    project_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[str, Depends(require_auth_token)],
) -> ProjectRead:
    """Archive an owned project."""
    user_id = _resolve_user_id_from_token(token)
    archived = await archive_project(db=db, project_id=project_id, user_id=user_id)
    sessions = await get_project_sessions(db=db, project_id=project_id)
    return ProjectRead.model_validate(archived).model_copy(update={"sessions_count": len(sessions)})


@router.get("/{project_id}/sessions")
async def list_project_sessions_endpoint(
    project_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[str, Depends(require_auth_token)],
) -> list[ProjectSessionSummary]:
    """List search sessions for one owned project."""
    user_id = _resolve_user_id_from_token(token)
    await get_project(db=db, project_id=project_id, user_id=user_id)
    sessions = await get_project_sessions(db=db, project_id=project_id)
    return [
        ProjectSessionSummary(
            id=session.id,
            query_text=session.query_text,
            cql_generated=session.cql_generated,
            result_count=session.result_count,
            status=session.status.value,
            executed_at=session.executed_at,
        )
        for session in sessions
    ]


@router.get("/{project_id}/timeline")
async def get_project_timeline_endpoint(
    project_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[str, Depends(require_auth_token)],
) -> list[TimelineEventRead]:
    """Return timeline events for one owned project."""
    user_id = _resolve_user_id_from_token(token)
    await get_project(db=db, project_id=project_id, user_id=user_id)
    timeline = await get_project_timeline(db=db, project_id=project_id)
    return [TimelineEventRead.model_validate(timeline_to_dict(event)) for event in timeline]


@router.get("/{project_id}/risk-trend")
async def get_project_risk_trend_endpoint(
    project_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[str, Depends(require_auth_token)],
) -> list[dict[str, object]]:
    """Return novelty trend series for one owned project."""
    user_id = _resolve_user_id_from_token(token)
    await get_project(db=db, project_id=project_id, user_id=user_id)
    return await get_project_risk_trend(db=db, project_id=project_id)


@router.post("/{project_id}/notes", status_code=status.HTTP_201_CREATED)
async def create_project_note_endpoint(
    project_id: UUID,
    payload: ProjectNoteCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[str, Depends(require_auth_token)],
) -> ProjectNoteRead:
    """Create a note for one owned project."""
    user_id = _resolve_user_id_from_token(token)
    await get_project(db=db, project_id=project_id, user_id=user_id)
    note = await create_project_note(
        db=db,
        project_id=project_id,
        title=payload.title,
        content=payload.content,
        linked_session_id=payload.linked_session_id,
    )
    return ProjectNoteRead.model_validate(note)


@router.get("/{project_id}/notes")
async def list_project_notes_endpoint(
    project_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[str, Depends(require_auth_token)],
) -> list[ProjectNoteRead]:
    """List notes for one owned project."""
    user_id = _resolve_user_id_from_token(token)
    await get_project(db=db, project_id=project_id, user_id=user_id)
    notes = await list_project_notes(db=db, project_id=project_id)
    return [ProjectNoteRead.model_validate(note) for note in notes]


@router.delete("/{project_id}/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_note_endpoint(
    project_id: UUID,
    note_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[str, Depends(require_auth_token)],
) -> None:
    """Delete one note from an owned project."""
    user_id = _resolve_user_id_from_token(token)
    await get_project(db=db, project_id=project_id, user_id=user_id)
    await delete_project_note(db=db, project_id=project_id, note_id=note_id)
