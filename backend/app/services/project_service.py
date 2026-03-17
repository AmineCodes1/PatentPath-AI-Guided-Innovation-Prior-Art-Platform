"""Business logic for innovation project workspace operations and related analytics."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Literal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.gap_analysis import GapAnalysis
from app.models.innovation_project import InnovationProject, ProjectStatus
from app.models.project_note import ProjectNote
from app.models.scored_result import ScoredResult
from app.models.search_session import SearchSession
from app.schemas.innovation_project import ProjectCreate, ProjectUpdate

TimelineEventType = Literal["SEARCH", "ANALYSIS", "REPORT"]


@dataclass(slots=True)
class TimelineEvent:
    """Normalized project timeline event used by timeline endpoints."""

    event_type: TimelineEventType
    timestamp: datetime
    title: str
    summary: str
    session_id: UUID | None


async def create_project(db: AsyncSession, user_id: UUID, data: ProjectCreate) -> InnovationProject:
    """Create a new innovation project for a user."""
    project = InnovationProject(
        user_id=user_id,
        title=data.title.strip(),
        problem_statement=data.problem_statement.strip(),
        domain_ipc_class=data.domain_ipc_class.strip().upper() if data.domain_ipc_class else None,
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


async def get_user_projects(db: AsyncSession, user_id: UUID) -> list[InnovationProject]:
    """Return all projects owned by a user, newest first."""
    query = (
        select(InnovationProject)
        .where(InnovationProject.user_id == user_id)
        .options(selectinload(InnovationProject.search_sessions))
        .order_by(InnovationProject.created_at.desc())
    )
    return list((await db.scalars(query)).all())


async def get_project(db: AsyncSession, project_id: UUID, user_id: UUID) -> InnovationProject:
    """Return a project if owned by user, else raise 404."""
    query = (
        select(InnovationProject)
        .where(InnovationProject.id == project_id, InnovationProject.user_id == user_id)
        .options(selectinload(InnovationProject.search_sessions))
    )
    project = await db.scalar(query)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


async def update_project(
    db: AsyncSession,
    project_id: UUID,
    user_id: UUID,
    data: ProjectUpdate,
) -> InnovationProject:
    """Patch editable project fields for an owned project."""
    project = await get_project(db=db, project_id=project_id, user_id=user_id)
    payload = data.model_dump(exclude_unset=True)

    if "title" in payload and payload["title"] is not None:
        project.title = str(payload["title"]).strip()
    if "problem_statement" in payload and payload["problem_statement"] is not None:
        project.problem_statement = str(payload["problem_statement"]).strip()
    if "domain_ipc_class" in payload:
        value = payload["domain_ipc_class"]
        project.domain_ipc_class = str(value).strip().upper() if value else None
    if "status" in payload and payload["status"] is not None:
        project.status = payload["status"]

    await db.commit()
    await db.refresh(project)
    return project


async def archive_project(db: AsyncSession, project_id: UUID, user_id: UUID) -> InnovationProject:
    """Archive an owned project."""
    project = await get_project(db=db, project_id=project_id, user_id=user_id)
    project.status = ProjectStatus.ARCHIVED
    await db.commit()
    await db.refresh(project)
    return project


async def get_project_sessions(db: AsyncSession, project_id: UUID) -> list[SearchSession]:
    """Return all search sessions for a project, ordered by latest execution."""
    query = (
        select(SearchSession)
        .where(SearchSession.project_id == project_id)
        .order_by(SearchSession.executed_at.desc())
    )
    return list((await db.scalars(query)).all())


async def get_project_timeline(db: AsyncSession, project_id: UUID) -> list[TimelineEvent]:
    """Build a reverse-chronological timeline from searches, analyses, and report readiness state."""
    project = await db.scalar(select(InnovationProject).where(InnovationProject.id == project_id))
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    sessions = list(
        (
            await db.scalars(
                select(SearchSession)
                .where(SearchSession.project_id == project_id)
                .options(selectinload(SearchSession.gap_analysis))
            )
        ).all()
    )

    events: list[TimelineEvent] = []
    for session in sessions:
        events.append(
            TimelineEvent(
                event_type="SEARCH",
                timestamp=session.executed_at,
                title="Search Session Executed",
                summary=f"{session.result_count} results processed with status {session.status.value}.",
                session_id=session.id,
            )
        )

        if session.gap_analysis is not None:
            events.append(
                TimelineEvent(
                    event_type="ANALYSIS",
                    timestamp=session.gap_analysis.generated_at,
                    title="Gap Analysis Generated",
                    summary=f"Overall risk assessed as {session.gap_analysis.overall_risk.value}.",
                    session_id=session.id,
                )
            )

    if project.status == ProjectStatus.REPORT_READY:
        events.append(
            TimelineEvent(
                event_type="REPORT",
                timestamp=project.updated_at,
                title="Project Marked Report Ready",
                summary="Project status indicates report output is ready for review.",
                session_id=None,
            )
        )

    events.sort(key=lambda item: item.timestamp, reverse=True)
    return events


async def get_project_risk_trend(db: AsyncSession, project_id: UUID) -> list[dict[str, object]]:
    """Return trend points for session-level novelty risk and average score."""
    rows = list(
        (
            await db.execute(
                select(
                    func.date(SearchSession.executed_at).label("session_date"),
                    GapAnalysis.overall_risk.label("overall_risk"),
                    func.avg(ScoredResult.composite_score).label("avg_composite_score"),
                )
                .select_from(SearchSession)
                .outerjoin(ScoredResult, ScoredResult.session_id == SearchSession.id)
                .outerjoin(GapAnalysis, GapAnalysis.session_id == SearchSession.id)
                .where(SearchSession.project_id == project_id)
                .group_by(SearchSession.id, func.date(SearchSession.executed_at), GapAnalysis.overall_risk)
                .order_by(func.date(SearchSession.executed_at).asc())
            )
        ).all()
    )

    trend: list[dict[str, object]] = []
    for row in rows:
        risk_value = row.overall_risk.value if row.overall_risk is not None else "UNKNOWN"
        trend.append(
            {
                "session_date": row.session_date.isoformat(),
                "overall_risk": risk_value,
                "avg_composite_score": round(float(row.avg_composite_score or 0.0), 4),
            }
        )
    return trend


async def create_project_note(
    db: AsyncSession,
    project_id: UUID,
    title: str,
    content: str,
    linked_session_id: UUID | None = None,
) -> ProjectNote:
    """Persist a project note after validating optional linked session ownership."""
    if linked_session_id is not None:
        linked = await db.scalar(
            select(SearchSession).where(
                SearchSession.id == linked_session_id,
                SearchSession.project_id == project_id,
            )
        )
        if linked is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Linked search session not found")

    note = ProjectNote(
        project_id=project_id,
        title=title.strip(),
        content=content.strip(),
        linked_session_id=linked_session_id,
    )
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return note


async def list_project_notes(db: AsyncSession, project_id: UUID) -> list[ProjectNote]:
    """Return notes for a project sorted newest-first."""
    return list(
        (
            await db.scalars(
                select(ProjectNote)
                .where(ProjectNote.project_id == project_id)
                .order_by(ProjectNote.created_at.desc())
            )
        ).all()
    )


async def delete_project_note(db: AsyncSession, project_id: UUID, note_id: UUID) -> None:
    """Delete a project note by id within the given project scope."""
    note = await db.scalar(
        select(ProjectNote).where(ProjectNote.id == note_id, ProjectNote.project_id == project_id)
    )
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    await db.delete(note)
    await db.commit()


def timeline_to_dict(event: TimelineEvent) -> dict[str, object]:
    """Convert dataclass timeline event to serializable dictionary."""
    payload = asdict(event)
    payload["timestamp"] = event.timestamp
    return payload
