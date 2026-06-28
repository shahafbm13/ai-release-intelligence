from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from domain.enums import ClassificationProvider, FeedbackAction, ProcessingStatus
from shared.models import (
    CIRunModel,
    ClassificationModel,
    FailureOccurrenceModel,
    HumanFeedbackModel,
    IngestedEventModel,
    ReleaseAssessmentModel,
    RepositoryModel,
    SimilarFailureLinkModel,
)


class MetricsRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def summary_for_organization(self, organization_id: UUID) -> dict:
        repo_ids = self._session.scalars(
            select(RepositoryModel.id).where(RepositoryModel.organization_id == organization_id)
        ).all()
        if not repo_ids:
            return self._empty_summary()

        total_runs = self._scalar_count(
            select(func.count())
            .select_from(CIRunModel)
            .where(CIRunModel.repository_id.in_(repo_ids))
        )
        failed_runs = self._scalar_count(
            select(func.count())
            .select_from(CIRunModel)
            .where(
                CIRunModel.repository_id.in_(repo_ids),
                CIRunModel.conclusion == "failure",
            )
        )
        completed_runs = self._scalar_count(
            select(func.count())
            .select_from(CIRunModel)
            .where(
                CIRunModel.repository_id.in_(repo_ids),
                CIRunModel.processing_status == ProcessingStatus.COMPLETED.value,
            )
        )
        total_classifications = self._scalar_count(
            select(func.count())
            .select_from(ClassificationModel)
            .join(
                FailureOccurrenceModel,
                ClassificationModel.failure_occurrence_id == FailureOccurrenceModel.id,
            )
            .join(CIRunModel, FailureOccurrenceModel.ci_run_id == CIRunModel.id)
            .where(CIRunModel.repository_id.in_(repo_ids))
        )
        rule_classifications = self._scalar_count(
            select(func.count())
            .select_from(ClassificationModel)
            .join(
                FailureOccurrenceModel,
                ClassificationModel.failure_occurrence_id == FailureOccurrenceModel.id,
            )
            .join(CIRunModel, FailureOccurrenceModel.ci_run_id == CIRunModel.id)
            .where(
                CIRunModel.repository_id.in_(repo_ids),
                ClassificationModel.provider == ClassificationProvider.RULES.value,
            )
        )
        total_failures = self._scalar_count(
            select(func.count())
            .select_from(FailureOccurrenceModel)
            .join(CIRunModel, FailureOccurrenceModel.ci_run_id == CIRunModel.id)
            .where(CIRunModel.repository_id.in_(repo_ids))
        )
        failures_with_similar = self._scalar_count(
            select(func.count(func.distinct(SimilarFailureLinkModel.failure_occurrence_id)))
            .select_from(SimilarFailureLinkModel)
            .join(
                FailureOccurrenceModel,
                SimilarFailureLinkModel.failure_occurrence_id == FailureOccurrenceModel.id,
            )
            .join(CIRunModel, FailureOccurrenceModel.ci_run_id == CIRunModel.id)
            .where(CIRunModel.repository_id.in_(repo_ids))
        )
        feedback_total = self._scalar_count(
            select(func.count())
            .select_from(HumanFeedbackModel)
            .join(
                FailureOccurrenceModel,
                HumanFeedbackModel.failure_occurrence_id == FailureOccurrenceModel.id,
            )
            .join(CIRunModel, FailureOccurrenceModel.ci_run_id == CIRunModel.id)
            .where(CIRunModel.repository_id.in_(repo_ids))
        )
        feedback_accept = self._scalar_count(
            select(func.count())
            .select_from(HumanFeedbackModel)
            .join(
                FailureOccurrenceModel,
                HumanFeedbackModel.failure_occurrence_id == FailureOccurrenceModel.id,
            )
            .join(CIRunModel, FailureOccurrenceModel.ci_run_id == CIRunModel.id)
            .where(
                CIRunModel.repository_id.in_(repo_ids),
                HumanFeedbackModel.action == FeedbackAction.ACCEPT.value,
            )
        )
        ingested_accepted = self._scalar_count(
            select(func.count()).select_from(IngestedEventModel).where(IngestedEventModel.status == "accepted")
        )
        ingested_total = self._scalar_count(
            select(func.count()).select_from(IngestedEventModel)
        )
        avg_latency = self._session.scalar(
            select(
                func.avg(
                    func.extract("epoch", CIRunModel.completed_at)
                    - func.extract("epoch", CIRunModel.ingested_at)
                )
            ).where(
                CIRunModel.repository_id.in_(repo_ids),
                CIRunModel.completed_at.is_not(None),
            )
        )
        assessments = self._scalar_count(
            select(func.count())
            .select_from(ReleaseAssessmentModel)
            .join(CIRunModel, ReleaseAssessmentModel.ci_run_id == CIRunModel.id)
            .where(CIRunModel.repository_id.in_(repo_ids))
        )

        fallback_rate = (
            (rule_classifications / total_classifications * 100.0) if total_classifications else 0.0
        )
        acceptance_rate = (feedback_accept / feedback_total * 100.0) if feedback_total else 0.0
        similar_match_rate = (
            (failures_with_similar / total_failures * 100.0) if total_failures else 0.0
        )
        ingest_success_rate = (
            (ingested_accepted / ingested_total * 100.0) if ingested_total else 100.0
        )

        return {
            "total_ci_runs": total_runs,
            "failed_ci_runs": failed_runs,
            "completed_runs": completed_runs,
            "total_classifications": total_classifications,
            "classification_fallback_rate_percent": round(fallback_rate, 2),
            "feedback_total": feedback_total,
            "classification_acceptance_rate_percent": round(acceptance_rate, 2),
            "similar_match_rate_percent": round(similar_match_rate, 2),
            "ingest_success_rate_percent": round(ingest_success_rate, 2),
            "avg_processing_latency_seconds": round(float(avg_latency or 0.0), 2),
            "release_assessments_total": assessments,
        }

    def _scalar_count(self, stmt) -> int:
        return int(self._session.scalar(stmt) or 0)

    @staticmethod
    def _empty_summary() -> dict:
        return {
            "total_ci_runs": 0,
            "failed_ci_runs": 0,
            "completed_runs": 0,
            "total_classifications": 0,
            "classification_fallback_rate_percent": 0.0,
            "feedback_total": 0,
            "classification_acceptance_rate_percent": 0.0,
            "similar_match_rate_percent": 0.0,
            "ingest_success_rate_percent": 100.0,
            "avg_processing_latency_seconds": 0.0,
            "release_assessments_total": 0,
        }
