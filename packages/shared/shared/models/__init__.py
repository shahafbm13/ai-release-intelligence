import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.database import Base


class OrganizationModel(Base):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    users: Mapped[list["UserModel"]] = relationship(back_populates="organization")
    repositories: Mapped[list["RepositoryModel"]] = relationship(back_populates="organization")


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="viewer")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    organization: Mapped["OrganizationModel"] = relationship(back_populates="users")


class RepositoryModel(Base):
    __tablename__ = "repositories"
    __table_args__ = (UniqueConstraint("organization_id", "full_name", name="uq_repo_org_full_name"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    default_branch: Mapped[str] = mapped_column(String(255), nullable=False, default="main")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    organization: Mapped["OrganizationModel"] = relationship(back_populates="repositories")
    ci_runs: Mapped[list["CIRunModel"]] = relationship(back_populates="repository")


class IngestedEventModel(Base):
    __tablename__ = "ingested_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    delivery_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    payload_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    correlation_id: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="accepted")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    ci_run: Mapped["CIRunModel | None"] = relationship(back_populates="ingested_event")


class CIRunModel(Base):
    __tablename__ = "ci_runs"
    __table_args__ = (
        UniqueConstraint("idempotency_key", name="uq_ci_runs_idempotency_key"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("repositories.id"), nullable=False
    )
    ingested_event_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ingested_events.id"), nullable=True
    )
    workflow_name: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    branch: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    commit_sha: Mapped[str] = mapped_column(String(40), nullable=False, default="")
    conclusion: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    status_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    processing_status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    idempotency_key: Mapped[str] = mapped_column(String(255), nullable=False)
    failure_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    enqueued_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    repository: Mapped["RepositoryModel"] = relationship(back_populates="ci_runs")
    ingested_event: Mapped["IngestedEventModel | None"] = relationship(back_populates="ci_run")
    failure_occurrences: Mapped[list["FailureOccurrenceModel"]] = relationship(
        back_populates="ci_run"
    )
    release_assessment: Mapped["ReleaseAssessmentModel | None"] = relationship(
        back_populates="ci_run", uselist=False
    )


class FailureOccurrenceModel(Base):
    __tablename__ = "failure_occurrences"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ci_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ci_runs.id"), nullable=False
    )
    test_name: Mapped[str] = mapped_column(String(512), nullable=False)
    suite_name: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    error_type: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    error_message: Mapped[str] = mapped_column(Text, nullable=False, default="")
    stack_trace: Mapped[str] = mapped_column(Text, nullable=False, default="")
    log_excerpt: Mapped[str] = mapped_column(Text, nullable=False, default="")
    retry_number: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    ci_run: Mapped["CIRunModel"] = relationship(back_populates="failure_occurrences")
    classification: Mapped["ClassificationModel | None"] = relationship(
        back_populates="failure_occurrence", uselist=False
    )
    similar_links: Mapped[list["SimilarFailureLinkModel"]] = relationship(
        back_populates="failure_occurrence",
        foreign_keys="SimilarFailureLinkModel.failure_occurrence_id",
    )
    feedback_entries: Mapped[list["HumanFeedbackModel"]] = relationship(
        back_populates="failure_occurrence"
    )


class ClassificationModel(Base):
    __tablename__ = "classifications"
    __table_args__ = (
        UniqueConstraint("failure_occurrence_id", name="uq_classifications_failure_occurrence_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    failure_occurrence_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("failure_occurrences.id"), nullable=False
    )
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    subcategory: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    suspected_component: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    likely_cause: Mapped[str] = mapped_column(Text, nullable=False, default="")
    suggested_action: Mapped[str] = mapped_column(Text, nullable=False, default="")
    confidence: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False)
    evidence_refs: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    insufficient_information: Mapped[bool] = mapped_column(nullable=False, default=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    prompt_version: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    input_hash: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    input_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    trace_id: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    failure_occurrence: Mapped["FailureOccurrenceModel"] = relationship(
        back_populates="classification"
    )


class SimilarFailureLinkModel(Base):
    __tablename__ = "similar_failure_links"
    __table_args__ = (
        UniqueConstraint(
            "failure_occurrence_id",
            "matched_failure_occurrence_id",
            name="uq_similar_failure_links_pair",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    failure_occurrence_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("failure_occurrences.id"), nullable=False
    )
    matched_failure_occurrence_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("failure_occurrences.id"), nullable=False
    )
    method: Mapped[str] = mapped_column(String(50), nullable=False)
    score: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    failure_occurrence: Mapped["FailureOccurrenceModel"] = relationship(
        back_populates="similar_links",
        foreign_keys=[failure_occurrence_id],
    )


class ReleaseAssessmentModel(Base):
    __tablename__ = "release_assessments"
    __table_args__ = (UniqueConstraint("ci_run_id", name="uq_release_assessments_ci_run_id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ci_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ci_runs.id"), nullable=False
    )
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False)
    score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    factors_json: Mapped[list | dict] = mapped_column(JSONB, nullable=False)
    missing_info_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    recommendation: Mapped[str] = mapped_column(String(20), nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    engine_version: Mapped[str] = mapped_column(String(20), nullable=False, default="v1")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    ci_run: Mapped["CIRunModel"] = relationship(back_populates="release_assessment")


class HumanFeedbackModel(Base):
    __tablename__ = "human_feedback"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    failure_occurrence_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("failure_occurrences.id"), nullable=False
    )
    classification_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("classifications.id"), nullable=False
    )
    actor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    action: Mapped[str] = mapped_column(String(20), nullable=False)
    corrected_category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    corrected_component: Mapped[str | None] = mapped_column(String(255), nullable=True)
    note: Mapped[str] = mapped_column(Text, nullable=False, default="")
    resolved: Mapped[bool] = mapped_column(nullable=False, default=False)
    cluster_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    ai_snapshot_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    failure_occurrence: Mapped["FailureOccurrenceModel"] = relationship(
        back_populates="feedback_entries"
    )


class AuditEventModel(Base):
    __tablename__ = "audit_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    actor_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    correlation_id: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
