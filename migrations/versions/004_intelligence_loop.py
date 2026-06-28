"""Revision 004: similar links, release assessments, feedback, audit

Revision ID: 004
Revises: 003
Create Date: 2026-06-18
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "similar_failure_links",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("failure_occurrence_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("matched_failure_occurrence_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("method", sa.String(length=50), nullable=False),
        sa.Column("score", sa.Numeric(precision=4, scale=3), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["failure_occurrence_id"], ["failure_occurrences.id"]),
        sa.ForeignKeyConstraint(["matched_failure_occurrence_id"], ["failure_occurrences.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "failure_occurrence_id",
            "matched_failure_occurrence_id",
            name="uq_similar_failure_links_pair",
        ),
    )
    op.create_index(
        "ix_similar_failure_links_failure_occurrence_id",
        "similar_failure_links",
        ["failure_occurrence_id"],
    )

    op.create_table(
        "release_assessments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("ci_run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("risk_level", sa.String(length=20), nullable=False),
        sa.Column("score", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("factors_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("missing_info_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("recommendation", sa.String(length=20), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("engine_version", sa.String(length=20), nullable=False, server_default="v1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["ci_run_id"], ["ci_runs.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ci_run_id", name="uq_release_assessments_ci_run_id"),
    )

    op.create_table(
        "human_feedback",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("failure_occurrence_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("classification_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("action", sa.String(length=20), nullable=False),
        sa.Column("corrected_category", sa.String(length=100), nullable=True),
        sa.Column("corrected_component", sa.String(length=255), nullable=True),
        sa.Column("note", sa.Text(), nullable=False, server_default=""),
        sa.Column("resolved", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("cluster_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("ai_snapshot_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["failure_occurrence_id"], ["failure_occurrences.id"]),
        sa.ForeignKeyConstraint(["classification_id"], ["classifications.id"]),
        sa.ForeignKeyConstraint(["actor_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_human_feedback_failure_occurrence_id",
        "human_feedback",
        ["failure_occurrence_id"],
    )

    op.create_table(
        "audit_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("resource_type", sa.String(length=100), nullable=False),
        sa.Column("resource_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("correlation_id", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["actor_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_events_organization_id", "audit_events", ["organization_id"])


def downgrade() -> None:
    op.drop_index("ix_audit_events_organization_id", table_name="audit_events")
    op.drop_table("audit_events")
    op.drop_index("ix_human_feedback_failure_occurrence_id", table_name="human_feedback")
    op.drop_table("human_feedback")
    op.drop_table("release_assessments")
    op.drop_index("ix_similar_failure_links_failure_occurrence_id", table_name="similar_failure_links")
    op.drop_table("similar_failure_links")
