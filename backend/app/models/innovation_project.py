"""Innovation project ORM model for inventor problem statements and lifecycle state."""

from __future__ import annotations

import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.project_note import ProjectNote
    from app.models.search_session import SearchSession
    from app.models.user import User


class ProjectStatus(str, enum.Enum):
    """Lifecycle states of an innovation project."""

    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    REPORT_READY = "REPORT_READY"


class InnovationProject(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """User-owned innovation project containing search sessions."""

    __tablename__ = "innovation_projects"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    problem_statement: Mapped[str] = mapped_column(Text, nullable=False)
    domain_ipc_class: Mapped[str | None] = mapped_column(String(32), nullable=True)
    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus, name="project_status"),
        nullable=False,
        default=ProjectStatus.ACTIVE,
        server_default=ProjectStatus.ACTIVE.value,
    )

    owner: Mapped[User] = relationship("User", back_populates="projects")
    search_sessions: Mapped[list[SearchSession]] = relationship(
        "SearchSession",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    notes: Mapped[list[ProjectNote]] = relationship(
        "ProjectNote",
        back_populates="project",
        cascade="all, delete-orphan",
    )
