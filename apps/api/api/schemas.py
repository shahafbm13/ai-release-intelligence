from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    role: str
    organization_id: UUID


class OrganizationResponse(BaseModel):
    id: UUID
    name: str
    slug: str


class RepositoryCreateRequest(BaseModel):
    full_name: str = Field(min_length=3, max_length=255)
    default_branch: str = Field(default="main", max_length=255)


class RepositoryResponse(BaseModel):
    id: UUID
    organization_id: UUID
    full_name: str
    default_branch: str


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: list[str] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    error: ErrorDetail
    correlation_id: str


class TestFailurePayload(BaseModel):
    test_name: str
    suite_name: str = ""
    error_type: str = ""
    error_message: str = ""
    stack_trace: str = ""
    log_excerpt: str = ""
    retry_number: int = 0


class WorkflowRunPayload(BaseModel):
    id: int
    name: str = "CI"
    head_branch: str = "main"
    head_sha: str = Field(min_length=7, max_length=40)
    conclusion: str
    html_url: str | None = None
    repository: dict | None = None


class GitHubWebhookPayload(BaseModel):
    action: str
    workflow_run: WorkflowRunPayload | None = None
    repository: dict | None = None
    test_failures: list[TestFailurePayload] = Field(default_factory=list)


class WebhookAcceptedResponse(BaseModel):
    ci_run_id: UUID | None = None
    correlation_id: str
    status: str


class CIRunResponse(BaseModel):
    id: UUID
    repository_id: UUID
    workflow_name: str
    branch: str
    commit_sha: str
    conclusion: str
    status_url: str | None
    processing_status: str
    failure_count: int
    ingested_at: datetime
    enqueued_at: datetime | None
    completed_at: datetime | None


class PaginatedCIRunsResponse(BaseModel):
    items: list[CIRunResponse]
    page: int
    page_size: int
    total: int


class ClassificationResponse(BaseModel):
    id: UUID
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
    trace_id: str
    created_at: datetime


class FailureResponse(BaseModel):
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
    classification: ClassificationResponse | None = None


class PaginatedFailuresResponse(BaseModel):
    items: list[FailureResponse]
    page: int
    page_size: int
    total: int


class SimilarFailureItemResponse(BaseModel):
    failure_id: UUID
    test_name: str
    match_method: str
    score: float
    matched_at: datetime
    classification_summary: str | None = None


class SimilarFailuresResponse(BaseModel):
    items: list[SimilarFailureItemResponse]
    message: str | None = None


class RiskFactorResponse(BaseModel):
    name: str
    weight: float
    score: float
    contribution: float
    detail: str


class ReleaseAssessmentResponse(BaseModel):
    ci_run_id: UUID
    risk_level: str
    score: float
    factors: list[RiskFactorResponse]
    missing_info: list[str]
    recommendation: str
    explanation: str
    engine_version: str
    created_at: datetime


class FeedbackCreateRequest(BaseModel):
    action: str = Field(pattern="^(accept|correct)$")
    corrected_category: str | None = None
    corrected_component: str | None = None
    note: str = ""
    resolved: bool = False
    cluster_id: UUID | None = None


class FeedbackResponse(BaseModel):
    id: UUID
    failure_occurrence_id: UUID
    classification_id: UUID
    action: str
    corrected_category: str | None
    corrected_component: str | None
    note: str
    resolved: bool
    cluster_id: UUID | None
    created_at: datetime


class MetricsSummaryResponse(BaseModel):
    total_ci_runs: int
    failed_ci_runs: int
    completed_runs: int
    total_classifications: int
    classification_fallback_rate_percent: float
    feedback_total: int
    classification_acceptance_rate_percent: float
    similar_match_rate_percent: float
    ingest_success_rate_percent: float
    avg_processing_latency_seconds: float
    release_assessments_total: int
