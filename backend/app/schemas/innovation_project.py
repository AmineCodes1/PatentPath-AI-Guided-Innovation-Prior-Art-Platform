"""Innovation project request and response schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.innovation_project import ProjectStatus


class ProjectCreate(BaseModel):
    """Payload for creating an innovation project."""

    model_config = ConfigDict(from_attributes=True)

    title: str = Field(min_length=3, max_length=255)
    problem_statement: str = Field(min_length=20)
    domain_ipc_class: str | None = Field(default=None, max_length=32)


class ProjectUpdate(BaseModel):
    """Payload for partial updates to an innovation project."""

    model_config = ConfigDict(from_attributes=True)

    title: str | None = Field(default=None, min_length=3, max_length=255)
    problem_statement: str | None = Field(default=None, min_length=20)
    status: ProjectStatus | None = None
    domain_ipc_class: str | None = Field(default=None, max_length=32)


class ProjectRead(BaseModel):
    """Project representation returned by project API endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    title: str
    problem_statement: str
    domain_ipc_class: str | None
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime
    sessions_count: int = 0
