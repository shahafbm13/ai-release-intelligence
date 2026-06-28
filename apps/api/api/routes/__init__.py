import uuid

from fastapi import APIRouter, Header, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse
from api.schemas import (
    CIRunResponse,
    FailureResponse,
    FeedbackCreateRequest,
    FeedbackResponse,
    LoginRequest,
    OrganizationResponse,
    MetricsSummaryResponse,
    PaginatedCIRunsResponse,
    PaginatedFailuresResponse,
    RepositoryCreateRequest,
    RepositoryResponse,
    ReleaseAssessmentResponse,
    SimilarFailuresResponse,
    TokenResponse,
    UserResponse,
    WebhookAcceptedResponse,
)
from api.services.assessment_service import AssessmentService
from api.services.auth_service import AuthService
from api.services.ci_run_service import CIRunService
from api.services.failure_service import FailureService
from api.services.ingest_service import IngestService
from api.services.metrics_service import MetricsService
from domain.enums import UserRole

from api.dependencies import AuthServiceDep, CurrentUser, DbSession, OrgServiceDep

router = APIRouter(prefix="/api/v1")


@router.post("/auth/login", response_model=TokenResponse)
def login(body: LoginRequest, session: DbSession) -> TokenResponse:
    return AuthService(session).login(body)


@router.get("/auth/me", response_model=UserResponse)
def me(current_user: CurrentUser, auth: AuthServiceDep) -> UserResponse:
    return auth.get_me(current_user)


@router.get("/organizations/me", response_model=OrganizationResponse)
def get_organization(current_user: CurrentUser, orgs: OrgServiceDep) -> OrganizationResponse:
    return orgs.get_my_organization(current_user)


@router.get("/repositories", response_model=list[RepositoryResponse])
def list_repositories(current_user: CurrentUser, orgs: OrgServiceDep) -> list[RepositoryResponse]:
    return orgs.list_repositories(current_user)


@router.post("/repositories", response_model=RepositoryResponse, status_code=201)
def create_repository(
    body: RepositoryCreateRequest,
    current_user: CurrentUser,
    auth: AuthServiceDep,
    orgs: OrgServiceDep,
) -> RepositoryResponse:
    auth.require_role(current_user, UserRole.ANALYST, UserRole.ADMIN)
    return orgs.create_repository(current_user, body)


@router.get("/repositories/{repository_id}", response_model=RepositoryResponse)
def get_repository(
    repository_id: uuid.UUID,
    current_user: CurrentUser,
    orgs: OrgServiceDep,
) -> RepositoryResponse:
    return orgs.get_repository(current_user, repository_id)


@router.post("/webhooks/github", response_model=WebhookAcceptedResponse)
async def github_webhook(
    request: Request,
    session: DbSession,
    x_github_delivery: str | None = Header(default=None, alias="X-GitHub-Delivery"),
    x_hub_signature_256: str | None = Header(default=None, alias="X-Hub-Signature-256"),
) -> WebhookAcceptedResponse:
    raw_body = await request.body()
    correlation_id = getattr(request.state, "correlation_id", str(uuid.uuid4()))
    result = IngestService(session).ingest_github_webhook(
        raw_body=raw_body,
        signature_header=x_hub_signature_256,
        delivery_id=x_github_delivery,
        correlation_id=correlation_id,
    )
    return JSONResponse(status_code=result.http_status, content=result.response.model_dump(mode="json"))


@router.get("/ci-runs", response_model=PaginatedCIRunsResponse)
def list_ci_runs(
    current_user: CurrentUser,
    session: DbSession,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    conclusion: str | None = Query(default=None),
) -> PaginatedCIRunsResponse:
    return CIRunService(session).list_runs(
        current_user,
        page=page,
        page_size=page_size,
        conclusion=conclusion,
    )


@router.get("/ci-runs/{ci_run_id}", response_model=CIRunResponse)
def get_ci_run(
    ci_run_id: uuid.UUID,
    current_user: CurrentUser,
    session: DbSession,
) -> CIRunResponse:
    return CIRunService(session).get_run(current_user, ci_run_id)


@router.get("/failures", response_model=PaginatedFailuresResponse)
def list_failures(
    current_user: CurrentUser,
    session: DbSession,
    ci_run_id: uuid.UUID = Query(...),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> PaginatedFailuresResponse:
    return FailureService(session).list_failures(
        current_user,
        ci_run_id=ci_run_id,
        page=page,
        page_size=page_size,
    )


@router.get("/failures/{failure_id}", response_model=FailureResponse)
def get_failure(
    failure_id: uuid.UUID,
    current_user: CurrentUser,
    session: DbSession,
) -> FailureResponse:
    return FailureService(session).get_failure(current_user, failure_id)


@router.get("/failures/{failure_id}/similar", response_model=SimilarFailuresResponse)
def list_similar_failures(
    failure_id: uuid.UUID,
    current_user: CurrentUser,
    session: DbSession,
) -> SimilarFailuresResponse:
    return FailureService(session).list_similar_failures(current_user, failure_id)


@router.post("/failures/{failure_id}/feedback", response_model=FeedbackResponse, status_code=201)
def submit_feedback(
    failure_id: uuid.UUID,
    body: FeedbackCreateRequest,
    current_user: CurrentUser,
    auth: AuthServiceDep,
    session: DbSession,
    request: Request,
) -> FeedbackResponse:
    auth.require_role(current_user, UserRole.ANALYST, UserRole.ADMIN)
    correlation_id = getattr(request.state, "correlation_id", str(uuid.uuid4()))
    return FailureService(session).submit_feedback(
        current_user,
        failure_id,
        body,
        correlation_id=correlation_id,
    )


@router.get("/ci-runs/{ci_run_id}/assessment", response_model=ReleaseAssessmentResponse)
def get_release_assessment(
    ci_run_id: uuid.UUID,
    current_user: CurrentUser,
    session: DbSession,
) -> ReleaseAssessmentResponse:
    return AssessmentService(session).get_assessment(current_user, ci_run_id)


@router.get("/metrics/summary", response_model=MetricsSummaryResponse)
def metrics_summary(current_user: CurrentUser, session: DbSession) -> MetricsSummaryResponse:
    return MetricsService(session).get_summary(current_user)


@router.post("/admin/seed/replay", response_model=WebhookAcceptedResponse)
def replay_seed_fixture(
    current_user: CurrentUser,
    auth: AuthServiceDep,
    session: DbSession,
    request: Request,
    fixture_name: str = Query(default="failed_run.json"),
) -> WebhookAcceptedResponse:
    auth.require_role(current_user, UserRole.ADMIN)
    import json
    from pathlib import Path

    fixture_path = (
        Path(__file__).resolve().parents[4]
        / "tests"
        / "contract"
        / "fixtures"
        / "github"
        / fixture_name
    )
    if not fixture_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": f"Fixture not found: {fixture_name}"},
        )
    payload_dict = json.loads(fixture_path.read_text(encoding="utf-8"))
    delivery_id = f"seed-replay-{uuid.uuid4()}"
    correlation_id = getattr(request.state, "correlation_id", str(uuid.uuid4()))
    result = IngestService(session).replay_fixture_payload(
        payload_dict=payload_dict,
        delivery_id=delivery_id,
        correlation_id=correlation_id,
    )
    if result.response.ci_run_id is not None:
        from shared.processing.ci_run_processor import CIRunProcessor

        CIRunProcessor(session).process(result.response.ci_run_id, correlation_id)
    return JSONResponse(status_code=result.http_status, content=result.response.model_dump(mode="json"))
