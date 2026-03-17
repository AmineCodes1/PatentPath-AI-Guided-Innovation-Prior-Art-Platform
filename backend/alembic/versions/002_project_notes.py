"""Add project notes table.

Revision ID: 002_project_notes
Revises: 001_initial_schema
Create Date: 2026-03-17
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "002_project_notes"
down_revision = "001_initial_schema"
branch_labels = None
depends_on = None

NOW_EXPR = sa.text("now()")


def upgrade() -> None:
    """Create project_notes table for project-level note management."""
    op.create_table(
        "project_notes",
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("linked_session_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=NOW_EXPR, nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["linked_session_id"], ["search_sessions.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["project_id"], ["innovation_projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_project_notes_linked_session_id"), "project_notes", ["linked_session_id"], unique=False)
    op.create_index(op.f("ix_project_notes_project_id"), "project_notes", ["project_id"], unique=False)


def downgrade() -> None:
    """Drop project_notes table and indexes."""
    op.drop_index(op.f("ix_project_notes_project_id"), table_name="project_notes")
    op.drop_index(op.f("ix_project_notes_linked_session_id"), table_name="project_notes")
    op.drop_table("project_notes")
