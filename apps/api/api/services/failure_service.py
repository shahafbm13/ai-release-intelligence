from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from api.deps import AuthenticatedUser
from api.schemas import (
    ClassificationResponse,
    FailureResponse,
    FeedbackCreateRequest,
    FeedbackResponse,
    PaginatedFailuresResponse,
    SimilarFailureItemResponse,
    SimilarFailuresResponse,
)
from domain.enums import FeedbackAction
from shared.repositories.ci_runs import CIRunRepository
from shared.repositories.failures import ClassificationRepository, FailureOccurrenceRepository
from shared.repositories import RepositoryRepository
from shared.repositories.intelligence import AuditEventRepository, HumanFeedbackRepository, SimilarFailureLinkRepository
from shared.models import ClassificationModel, FailureOccurrenceModel


class FailureService:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._runs = CIRunRepository(session)
        self._failures = FailureOccurrenceRepository(session)
        self._classifications = ClassificationRepository(session)
        self._repos = RepositoryRepository(session)
        self._similar_links = SimilarFailureLinkRepository(session)
        self._feedback = HumanFeedbackRepository(session)
        self._audit = AuditEventRepository(session)

    def list_failures(
        self,
        current_user: AuthenticatedUser,
        *,
        ci_run_id: UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedFailuresResponse:
        run = self._runs.get_by_id(ci_run_id)
        if run is None or not self._user_can_access_run(current_user, run.repository_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "NOT_FOUND", "message": "CI run not found"},
            )
        failures = self._failures.list_by_ci_run(ci_run_id)
        total = len(failures)
        offset = (page - 1) * page_size
        page_items = failures[offset : offset + page_size]
        return PaginatedFailuresResponse(
            items=[self._to_response(f) for f in page_items],
            page=page,
            page_size=page_size,
            total=total,
        )

    def get_failure(self, current_user: AuthenticatedUser, failure_id: UUID) -> FailureResponse:
        failure = self._get_accessible_failure(current_user, failure_id)
        return self._to_response(failure)

    def list_similar_failures(
        self,
        current_user: AuthenticatedUser,
        failure_id: UUID,
    ) -> SimilarFailuresResponse:
        failure = self._get_accessible_failure(current_user, failure_id)
        links = self._similar_links.list_for_failure(failure.id)
        if not links:
            return SimilarFailuresResponse(items=[], message="no_similar_failures_found")

        items: list[SimilarFailureItemResponse] = []
        for link in links:
            matched = self._failures.get_by_id(link.matched_failure_occurrence_id)
            if matched is None:
                continue
            classification = self._classifications.get_by_failure_id(matched.id)
            items.append(
                SimilarFailureItemResponse(
                    failure_id=matched.id,
                    test_name=matched.test_name,
                    match_method=link.method,
                    score=float(link.score),
                    matched_at=matched.created_at,
                    classification_summary=classification.summary if classification else None,
                )
            )
        if not items:
            return SimilarFailuresResponse(items=[], message="no_similar_failures_found")
        return SimilarFailuresResponse(items=items)

    def submit_feedback(
        self,
        current_user: AuthenticatedUser,
        failure_id: UUID,
        body: FeedbackCreateRequest,
        *,
        correlation_id: str = "",
    ) -> FeedbackResponse:
        failure = self._get_accessible_failure(current_user, failure_id)
        classification = self._classifications.get_by_failure_id(failure.id)
        if classification is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"code": "CONFLICT", "message": "Failure has no classification to review"},
            )

        if body.action == FeedbackAction.CORRECT.value and not body.corrected_category:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"code": "VALIDATION_ERROR", "message": "corrected_category required for correct action"},
            )

        ai_snapshot = {
            "classification_id": str(classification.id),
            "category": classification.category,
            "subcategory": classification.subcategory,
            "suspected_component": classification.suspected_component,
            "summary": classification.summary,
            "likely_cause": classification.likely_cause,
            "suggested_action": classification.suggested_action,
            "confidence": classification.confidence,
            "provider": classification.provider,
        }
        record = self._feedback.create(
            failure_occurrence_id=failure.id,
            classification_id=classification.id,
            actor_id=current_user.user_id,
            action=body.action,
            corrected_category=body.corrected_category,
            corrected_component=body.corrected_component,
            note=body.note,
            resolved=body.resolved,
            cluster_id=body.cluster_id,
            ai_snapshot_json=ai_snapshot,
        )
        run = self._runs.get_by_id(failure.ci_run_id)
        if run is not None:
            org_id = self._repos.get_by_id(run.repository_id)
            if org_id is not None:
                self._audit.create(
                    organization_id=org_id.organization_id,
                    actor_id=current_user.user_id,
                    action="feedback_submitted",
                    resource_type="failure_occurrence",
                    resource_id=failure.id,
                    correlation_id=correlation_id,
                    metadata_json={
                        "feedback_id": str(record.id),
                        "action": body.action,
                        "classification_id": str(classification.id),
                    },
                )
        self._session.commit()
        return FeedbackResponse(
            id=record.id,
            failure_occurrence_id=record.failure_occurrence_id,
            classification_id=record.classification_id,
            action=record.action,
            corrected_category=record.corrected_category,
            corrected_component=record.corrected_component,
            note=record.note,
            resolved=record.resolved,
            cluster_id=record.cluster_id,
            created_at=record.created_at,
        )

    def _get_accessible_failure(self, current_user: AuthenticatedUser, failure_id: UUID):
        failure = self._failures.get_by_id(failure_id)
        if failure is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "NOT_FOUND", "message": "Failure not found"},
            )
        run = self._runs.get_by_id(failure.ci_run_id)
        if run is None or not self._user_can_access_run(current_user, run.repository_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "NOT_FOUND", "message": "Failure not found"},
            )
        return failure

    def _user_can_access_run(self, current_user: AuthenticatedUser, repository_id: UUID) -> bool:
        repo = self._repos.get_by_id(repository_id)
        return repo is not None and repo.organization_id == current_user.organization_id

    def _to_response(self, failure) -> FailureResponse:
        classification = self._classifications.get_by_failure_id(failure.id)
        return FailureResponse(
            id=failure.id,
            ci_run_id=failure.ci_run_id,
            test_name=failure.test_name,
            suite_name=failure.suite_name,
            error_type=failure.error_type,
            error_message=failure.error_message,
            stack_trace=failure.stack_trace,
            log_excerpt=failure.log_excerpt,
            retry_number=failure.retry_number,
            fingerprint=failure.fingerprint,
            created_at=failure.created_at,
            classification=self._to_classification_response(classification) if classification else None,
        )

    @staticmethod
    def _to_classification_response(classification) -> ClassificationResponse:
        return ClassificationResponse(
            id=classification.id,
            category=classification.category,
            subcategory=classification.subcategory,
            suspected_component=classification.suspected_component,
            summary=classification.summary,
            likely_cause=classification.likely_cause,
            suggested_action=classification.suggested_action,
            confidence=classification.confidence,
            evidence_refs=classification.evidence_refs,
            insufficient_information=classification.insufficient_information,
            provider=classification.provider,
            model=classification.model,
            prompt_version=classification.prompt_version,
            trace_id=classification.trace_id,
            created_at=classification.created_at,
        )
