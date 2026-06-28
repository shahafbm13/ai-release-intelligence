"""Revision 003: failure_occurrences and classifications

Revision ID: 003
Revises: 002
Create Date: 2026-06-18
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "failure_occurrences",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("ci_run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("test_name", sa.String(length=512), nullable=False),
        sa.Column("suite_name", sa.String(length=512), nullable=False, server_default=""),
        sa.Column("error_type", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("error_message", sa.Text(), nullable=False, server_default=""),
        sa.Column("stack_trace", sa.Text(), nullable=False, server_default=""),
        sa.Column("log_excerpt", sa.Text(), nullable=False, server_default=""),
        sa.Column("retry_number", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("fingerprint", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["ci_run_id"], ["ci_runs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_failure_occurrences_ci_run_id", "failure_occurrences", ["ci_run_id"])
    op.create_index("ix_failure_occurrences_fingerprint", "failure_occurrences", ["fingerprint"])

    op.create_table(
        "classifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("failure_occurrence_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("subcategory", sa.String(length=100), nullable=False, server_default=""),
        sa.Column("suspected_component", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("likely_cause", sa.Text(), nullable=False, server_default=""),
        sa.Column("suggested_action", sa.Text(), nullable=False, server_default=""),
        sa.Column("confidence", sa.Numeric(precision=4, scale=3), nullable=False),
        sa.Column("evidence_refs", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("insufficient_information", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("model", sa.String(length=100), nullable=False, server_default=""),
        sa.Column("prompt_version", sa.String(length=50), nullable=False, server_default=""),
        sa.Column("input_hash", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("input_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("output_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("duration_ms", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("trace_id", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["failure_occurrence_id"], ["failure_occurrences.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("failure_occurrence_id", name="uq_classifications_failure_occurrence_id"),
    )


def downgrade() -> None:
    op.drop_table("classifications")
    op.drop_index("ix_failure_occurrences_fingerprint", table_name="failure_occurrences")
    op.drop_index("ix_failure_occurrences_ci_run_id", table_name="failure_occurrences")
    op.drop_table("failure_occurrences")
