"""Initial PatentPath schema.

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-03-17
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


project_status_enum = sa.Enum("ACTIVE", "ARCHIVED", "REPORT_READY", name="project_status")
search_session_status_enum = sa.Enum("PENDING", "PROCESSING", "COMPLETE", "FAILED", name="search_session_status")
risk_label_enum = sa.Enum("HIGH", "MEDIUM", "LOW", "MINIMAL", name="risk_label")
overall_risk_enum = sa.Enum("HIGH", "MEDIUM", "LOW", name="overall_risk")
NOW_EXPR = sa.text("now()")
JSONB_EMPTY_OBJECT_EXPR = sa.text("'{}'::jsonb")
JSONB_EMPTY_ARRAY_EXPR = sa.text("'[]'::jsonb")


def upgrade() -> None:
    """Apply initial schema with all core PatentPath tables."""
    bind = op.get_bind()
    project_status_enum.create(bind, checkfirst=True)
    search_session_status_enum.create(bind, checkfirst=True)
    risk_label_enum.create(bind, checkfirst=True)
    overall_risk_enum.create(bind, checkfirst=True)

    op.create_table(
        "users",
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column("epo_consumer_key", sa.String(length=255), nullable=True, comment="Store encrypted at the application layer."),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=NOW_EXPR, nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=NOW_EXPR, nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=False)

    op.create_table(
        "innovation_projects",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("problem_statement", sa.Text(), nullable=False),
        sa.Column("domain_ipc_class", sa.String(length=32), nullable=True),
        sa.Column("status", project_status_enum, server_default="ACTIVE", nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=NOW_EXPR, nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=NOW_EXPR, nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_innovation_projects_user_id"), "innovation_projects", ["user_id"], unique=False)

    op.create_table(
        "search_sessions",
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("query_text", sa.Text(), nullable=False),
        sa.Column("cql_generated", sa.Text(), nullable=False),
        sa.Column("filters_json", postgresql.JSONB(astext_type=sa.Text()), server_default=JSONB_EMPTY_OBJECT_EXPR, nullable=False),
        sa.Column("result_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("status", search_session_status_enum, server_default="PENDING", nullable=False),
        sa.Column("executed_at", sa.DateTime(timezone=True), server_default=NOW_EXPR, nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["innovation_projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_search_sessions_project_id"), "search_sessions", ["project_id"], unique=False)

    op.create_table(
        "patent_records",
        sa.Column("publication_number", sa.String(length=64), nullable=False),
        sa.Column("country_code", sa.String(length=2), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("abstract", sa.Text(), nullable=False),
        sa.Column("claims", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("applicants", postgresql.JSONB(astext_type=sa.Text()), server_default=JSONB_EMPTY_ARRAY_EXPR, nullable=False),
        sa.Column("inventors", postgresql.JSONB(astext_type=sa.Text()), server_default=JSONB_EMPTY_ARRAY_EXPR, nullable=False),
        sa.Column("ipc_classes", postgresql.JSONB(astext_type=sa.Text()), server_default=JSONB_EMPTY_ARRAY_EXPR, nullable=False),
        sa.Column("cpc_classes", postgresql.JSONB(astext_type=sa.Text()), server_default=JSONB_EMPTY_ARRAY_EXPR, nullable=False),
        sa.Column("publication_date", sa.Date(), nullable=False),
        sa.Column("priority_date", sa.Date(), nullable=True),
        sa.Column("family_id", sa.String(length=128), nullable=True),
        sa.Column("legal_status", sa.String(length=64), nullable=True),
        sa.Column("espacenet_url", sa.Text(), nullable=False),
        sa.Column("cached_at", sa.DateTime(timezone=True), server_default=NOW_EXPR, nullable=False),
        sa.Column("cache_expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("publication_number"),
    )
    op.create_index(op.f("ix_patent_records_publication_number"), "patent_records", ["publication_number"], unique=False)

    op.create_table(
        "scored_results",
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("patent_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("bm25_score", sa.Float(), nullable=False),
        sa.Column("tfidf_cosine", sa.Float(), nullable=False),
        sa.Column("semantic_cosine", sa.Float(), nullable=False),
        sa.Column("composite_score", sa.Float(), nullable=False),
        sa.Column("risk_label", risk_label_enum, nullable=False),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["patent_id"], ["patent_records.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["session_id"], ["search_sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("session_id", "patent_id", name="uq_scored_result_session_patent"),
    )
    op.create_index(op.f("ix_scored_results_composite_score"), "scored_results", ["composite_score"], unique=False)
    op.create_index(op.f("ix_scored_results_patent_id"), "scored_results", ["patent_id"], unique=False)
    op.create_index(op.f("ix_scored_results_session_id"), "scored_results", ["session_id"], unique=False)

    op.create_table(
        "gap_analyses",
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("overall_risk", overall_risk_enum, nullable=False),
        sa.Column("covered_aspects", sa.ARRAY(sa.Text()), nullable=False),
        sa.Column("gap_aspects", sa.ARRAY(sa.Text()), nullable=False),
        sa.Column("suggestions", sa.ARRAY(sa.Text()), nullable=False),
        sa.Column("narrative_text", sa.Text(), nullable=False),
        sa.Column("model_used", sa.Text(), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), server_default=NOW_EXPR, nullable=False),
        sa.Column("feasibility_technical", sa.Float(), nullable=True),
        sa.Column("feasibility_domain", sa.Float(), nullable=True),
        sa.Column("feasibility_claim", sa.Float(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["search_sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("session_id"),
    )
    op.create_index(op.f("ix_gap_analyses_session_id"), "gap_analyses", ["session_id"], unique=True)


def downgrade() -> None:
    """Revert initial schema tables and enum types."""
    op.drop_index(op.f("ix_gap_analyses_session_id"), table_name="gap_analyses")
    op.drop_table("gap_analyses")

    op.drop_index(op.f("ix_scored_results_session_id"), table_name="scored_results")
    op.drop_index(op.f("ix_scored_results_patent_id"), table_name="scored_results")
    op.drop_index(op.f("ix_scored_results_composite_score"), table_name="scored_results")
    op.drop_table("scored_results")

    op.drop_index(op.f("ix_patent_records_publication_number"), table_name="patent_records")
    op.drop_table("patent_records")

    op.drop_index(op.f("ix_search_sessions_project_id"), table_name="search_sessions")
    op.drop_table("search_sessions")

    op.drop_index(op.f("ix_innovation_projects_user_id"), table_name="innovation_projects")
    op.drop_table("innovation_projects")

    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")

    bind = op.get_bind()
    overall_risk_enum.drop(bind, checkfirst=True)
    risk_label_enum.drop(bind, checkfirst=True)
    search_session_status_enum.drop(bind, checkfirst=True)
    project_status_enum.drop(bind, checkfirst=True)
