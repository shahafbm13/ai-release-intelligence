import json
from dataclasses import dataclass
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from api.schemas import GitHubWebhookPayload, WebhookAcceptedResponse
from domain.enums import IngestStatus, ProcessingStatus
from shared.celery_client import enqueue_process_ci_run
from shared.config import get_settings
from shared.logging import get_logger
from shared.repositories import OrganizationRepository, RepositoryRepository
from shared.repositories.ci_runs import CIRunRepository, IngestedEventRepository
from shared.webhook import verify_github_signature

logger = get_logger(__name__)


@dataclass(frozen=True)
class IngestResult:
    response: WebhookAcceptedResponse
    http_status: int


class IngestService:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._settings = get_settings()
        self._events = IngestedEventRepository(session)
        self._runs = CIRunRepository(session)
        self._repos = RepositoryRepository(session)
        self._orgs = OrganizationRepository(session)

    def ingest_github_webhook(
        self,
        *,
        raw_body: bytes,
        signature_header: str | None,
        delivery_id: str | None,
        correlation_id: str,
        skip_signature_verification: bool = False,
    ) -> IngestResult:
        if not skip_signature_verification and not verify_github_signature(
            raw_body, signature_header, self._settings.github_webhook_secret
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "UNAUTHORIZED", "message": "Invalid webhook signature"},
            )

        if not delivery_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"code": "VALIDATION_ERROR", "message": "Missing X-GitHub-Delivery header"},
            )

        existing_event = self._events.get_by_delivery_id(delivery_id)
        if existing_event is not None:
            existing_run = self._runs.get_by_ingested_event_id(existing_event.id)
            return IngestResult(
                response=WebhookAcceptedResponse(
                    ci_run_id=existing_run.id if existing_run else None,
                    correlation_id=existing_event.correlation_id,
                    status=IngestStatus.DUPLICATE.value,
                ),
                http_status=status.HTTP_200_OK,
            )

        try:
            payload_dict = json.loads(raw_body)
            payload = GitHubWebhookPayload.model_validate(payload_dict)
        except (json.JSONDecodeError, ValueError) as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"code": "VALIDATION_ERROR", "message": str(exc)},
            ) from exc

        event_type = self._resolve_event_type(payload)
        if not self._should_process(payload):
            event = self._events.create(
                delivery_id=delivery_id,
                event_type=event_type,
                payload_json=payload_dict,
                correlation_id=correlation_id,
                status=IngestStatus.IGNORED.value,
            )
            self._session.commit()
            logger.info(
                "webhook_ignored",
                delivery_id=delivery_id,
                correlation_id=correlation_id,
                event_type=event_type,
            )
            return IngestResult(
                response=WebhookAcceptedResponse(
                    correlation_id=correlation_id,
                    status=IngestStatus.IGNORED.value,
                ),
                http_status=status.HTTP_202_ACCEPTED,
            )

        repo_full_name = self._resolve_repo_full_name(payload)
        repository = self._repos.get_by_full_name(repo_full_name)
        if repository is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "code": "VALIDATION_ERROR",
                    "message": f"Unknown repository: {repo_full_name}",
                },
            )

        workflow_run = payload.workflow_run
        assert workflow_run is not None
        failure_count = len(payload.test_failures)
        idempotency_key = f"github:delivery:{delivery_id}"

        event = self._events.create(
            delivery_id=delivery_id,
            event_type=event_type,
            payload_json=payload_dict,
            correlation_id=correlation_id,
            status=IngestStatus.ACCEPTED.value,
        )
        ci_run = self._runs.create(
            repository_id=repository.id,
            ingested_event_id=event.id,
            workflow_name=workflow_run.name,
            branch=workflow_run.head_branch,
            commit_sha=workflow_run.head_sha,
            conclusion=workflow_run.conclusion,
            status_url=workflow_run.html_url,
            idempotency_key=idempotency_key,
            failure_count=failure_count,
        )
        self._runs.mark_enqueued(ci_run.id)
        self._session.commit()

        enqueue_process_ci_run(ci_run.id, correlation_id)

        logger.info(
            "webhook_accepted",
            delivery_id=delivery_id,
            correlation_id=correlation_id,
            ci_run_id=str(ci_run.id),
        )
        return IngestResult(
            response=WebhookAcceptedResponse(
                ci_run_id=ci_run.id,
                correlation_id=correlation_id,
                status=IngestStatus.ACCEPTED.value,
            ),
            http_status=status.HTTP_202_ACCEPTED,
        )

    def replay_fixture_payload(
        self,
        *,
        payload_dict: dict,
        delivery_id: str,
        correlation_id: str,
        skip_signature: bool = True,
    ) -> IngestResult:
        raw_body = json.dumps(payload_dict).encode("utf-8")
        if not skip_signature and self._settings.github_webhook_secret:
            import hashlib
            import hmac

            digest = hmac.new(
                self._settings.github_webhook_secret.encode("utf-8"),
                raw_body,
                hashlib.sha256,
            ).hexdigest()
            return self.ingest_github_webhook(
                raw_body=raw_body,
                signature_header=f"sha256={digest}",
                delivery_id=delivery_id,
                correlation_id=correlation_id,
            )
        return self.ingest_github_webhook(
            raw_body=raw_body,
            signature_header=None,
            delivery_id=delivery_id,
            correlation_id=correlation_id,
            skip_signature_verification=True,
        )

    @staticmethod
    def _resolve_event_type(payload: GitHubWebhookPayload) -> str:
        if payload.workflow_run is not None:
            return "workflow_run"
        return "unknown"

    @staticmethod
    def _should_process(payload: GitHubWebhookPayload) -> bool:
        if payload.action != "completed":
            return False
        if payload.workflow_run is None:
            return False
        return True

    @staticmethod
    def _resolve_repo_full_name(payload: GitHubWebhookPayload) -> str:
        if payload.repository and "full_name" in payload.repository:
            return payload.repository["full_name"]
        if payload.workflow_run and payload.workflow_run.repository:
            return payload.workflow_run.repository.get("full_name", "")
        return ""
