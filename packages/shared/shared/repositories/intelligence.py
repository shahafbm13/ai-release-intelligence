from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from domain.risk_engine import ReleaseRiskResult
from shared.models import (
    AuditEventModel,
    HumanFeedbackModel,
    ReleaseAssessmentModel,
    RepositoryModel,
    SimilarFailureLinkModel,
)

class SimilarFailureLinkRepository:
    def __init__(self, session: Session) -> None:        self._session = session

    def replace_for_failure(
        self,
        *,
        failure_occurrence_id: UUID,
        links: list[tuple[UUID, str, float]],
    ) -> None:
        existing = self._session.scalars(
            select(SimilarFailureLinkModel).where(
                SimilarFailureLinkModel.failure_occurrence_id == failure_occurrence_id
            )
        ).all()
        for item in existing:
            self._session.delete(item)

        for matched_id, method, score in links:
            self._session.add(
                SimilarFailureLinkModel(
                    failure_occurrence_id=failure_occurrence_id,
                    matched_failure_occurrence_id=matched_id,
                    method=method,
                    score=score,
                )
            )
        self._session.flush()

    def list_for_failure(self, failure_occurrence_id: UUID) -> list[SimilarFailureLinkModel]:
        return self._session.scalars(
            select(SimilarFailureLinkModel)
            .where(SimilarFailureLinkModel.failure_occurrence_id == failure_occurrence_id)
            .order_by(SimilarFailureLinkModel.score.desc())
        ).all()


class ReleaseAssessmentRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def upsert(self, *, ci_run_id: UUID, result: ReleaseRiskResult) -> ReleaseAssessmentModel:
        model = self._session.scalar(
            select(ReleaseAssessmentModel).where(ReleaseAssessmentModel.ci_run_id == ci_run_id)
        )
        factors_json = [
            {
                "name": factor.name,
                "weight": factor.weight,
                "score": factor.score,
                "contribution": factor.contribution,
                "detail": factor.detail,
            }
            for factor in result.factors
        ]
        if model is None:
            model = ReleaseAssessmentModel(
                ci_run_id=ci_run_id,
                risk_level=result.risk_level,
                score=result.score,
                factors_json=factors_json,
                missing_info_json=result.missing_info,
                recommendation=result.recommendation,
                explanation=result.explanation,
                engine_version=result.engine_version,
            )
            self._session.add(model)
        else:
            model.risk_level = result.risk_level
            model.score = result.score
            model.factors_json = factors_json
            model.missing_info_json = result.missing_info
            model.recommendation = result.recommendation
            model.explanation = result.explanation
            model.engine_version = result.engine_version
        self._session.flush()
        return model

    def get_by_ci_run_id(self, ci_run_id: UUID) -> ReleaseAssessmentModel | None:
        return self._session.scalar(
            select(ReleaseAssessmentModel).where(ReleaseAssessmentModel.ci_run_id == ci_run_id)
        )


class HumanFeedbackRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(
        self,
        *,
        failure_occurrence_id: UUID,
        classification_id: UUID,
        actor_id: UUID,
        action: str,
        corrected_category: str | None,
        corrected_component: str | None,
        note: str,
        resolved: bool,
        cluster_id: UUID | None,
        ai_snapshot_json: dict,
    ) -> HumanFeedbackModel:
        model = HumanFeedbackModel(
            failure_occurrence_id=failure_occurrence_id,
            classification_id=classification_id,
            actor_id=actor_id,
            action=action,
            corrected_category=corrected_category,
            corrected_component=corrected_component,
            note=note,
            resolved=resolved,
            cluster_id=cluster_id,
            ai_snapshot_json=ai_snapshot_json,
        )
        self._session.add(model)
        self._session.flush()
        return model


class AuditEventRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(
        self,
        *,
        organization_id: UUID,
        actor_id: UUID | None,
        action: str,
        resource_type: str,
        resource_id: UUID,
        correlation_id: str = "",
        metadata_json: dict | None = None,
    ) -> AuditEventModel:
        model = AuditEventModel(
            organization_id=organization_id,
            actor_id=actor_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            correlation_id=correlation_id,
            metadata_json=metadata_json or {},
        )
        self._session.add(model)
        self._session.flush()
        return model

    @staticmethod
    def get_organization_id_for_repository(session: Session, repository_id: UUID) -> UUID | None:
        repo = session.get(RepositoryModel, repository_id)
        return repo.organization_id if repo else None
