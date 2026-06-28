from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from domain.enums import UserRole


@dataclass(frozen=True)
class Organization:
    id: UUID
    name: str
    slug: str
    created_at: datetime


@dataclass(frozen=True)
class User:
    id: UUID
    organization_id: UUID
    email: str
    role: UserRole
    created_at: datetime


@dataclass(frozen=True)
class Repository:
    id: UUID
    organization_id: UUID
    full_name: str
    default_branch: str
    created_at: datetime


@dataclass(frozen=True)
class IngestedEvent:
    id: UUID
    delivery_id: str
    event_type: str
    correlation_id: str
    status: str
    created_at: datetime


@dataclass(frozen=True)
class CIRun:
    id: UUID
    repository_id: UUID
    workflow_name: str
    branch: str
    commit_sha: str
    conclusion: str
    status_url: str | None
    processing_status: str
    idempotency_key: str
    ingested_at: datetime
    enqueued_at: datetime | None
    completed_at: datetime | None
    failure_count: int


@dataclass(frozen=True)
class FailureOccurrence:
    id: UUID
    ci_run_id: UUID
    test_name: str
    suite_name: str
    error_type: str
    error_message: str
    stack_trace: str
    log_excerpt: str
    retry_number: int
    fingerprint: str
    created_at: datetime


@dataclass(frozen=True)
class Classification:
    id: UUID
    failure_occurrence_id: UUID
    category: str
    subcategory: str
    suspected_component: str
    summary: str
    likely_cause: str
    suggested_action: str
    confidence: float
    evidence_refs: list[str]
    insufficient_information: bool
    provider: str
    model: str
    prompt_version: str
    input_hash: str
    input_tokens: int
    output_tokens: int
    duration_ms: int
    trace_id: str
    created_at: datetime
