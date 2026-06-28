from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from domain.entities import Classification, FailureOccurrence
from shared.models import CIRunModel, ClassificationModel, FailureOccurrenceModel
from shared.similarity.matcher import HistoricalFailure, SIMILARITY_WINDOW_DAYS


def _to_failure(model: FailureOccurrenceModel) -> FailureOccurrence:
    return FailureOccurrence(
        id=model.id,
        ci_run_id=model.ci_run_id,
        test_name=model.test_name,
        suite_name=model.suite_name,
        error_type=model.error_type,
        error_message=model.error_message,
        stack_trace=model.stack_trace,
        log_excerpt=model.log_excerpt,
        retry_number=model.retry_number,
        fingerprint=model.fingerprint,
        created_at=model.created_at,
    )


def _to_classification(model: ClassificationModel) -> Classification:
    evidence_refs = model.evidence_refs if isinstance(model.evidence_refs, list) else []
    return Classification(
        id=model.id,
        failure_occurrence_id=model.failure_occurrence_id,
        category=model.category,
        subcategory=model.subcategory,
        suspected_component=model.suspected_component,
        summary=model.summary,
        likely_cause=model.likely_cause,
        suggested_action=model.suggested_action,
        confidence=float(model.confidence),
        evidence_refs=[str(ref) for ref in evidence_refs],
        insufficient_information=model.insufficient_information,
        provider=model.provider,
        model=model.model,
        prompt_version=model.prompt_version,
        input_hash=model.input_hash,
        input_tokens=model.input_tokens,
        output_tokens=model.output_tokens,
        duration_ms=model.duration_ms,
        trace_id=model.trace_id,
        created_at=model.created_at,
    )


class FailureOccurrenceRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(
        self,
        *,
        ci_run_id: UUID,
        test_name: str,
        suite_name: str,
        error_type: str,
        error_message: str,
        stack_trace: str,
        log_excerpt: str,
        retry_number: int,
        fingerprint: str,
    ) -> FailureOccurrence:
        model = FailureOccurrenceModel(
            ci_run_id=ci_run_id,
            test_name=test_name,
            suite_name=suite_name,
            error_type=error_type,
            error_message=error_message,
            stack_trace=stack_trace,
            log_excerpt=log_excerpt,
            retry_number=retry_number,
            fingerprint=fingerprint,
        )
        self._session.add(model)
        self._session.flush()
        return _to_failure(model)

    def list_by_ci_run(self, ci_run_id: UUID) -> list[FailureOccurrence]:
        models = self._session.scalars(
            select(FailureOccurrenceModel)
            .where(FailureOccurrenceModel.ci_run_id == ci_run_id)
            .order_by(FailureOccurrenceModel.created_at)
        ).all()
        return [_to_failure(m) for m in models]

    def get_by_id(self, failure_id: UUID) -> FailureOccurrence | None:
        model = self._session.get(FailureOccurrenceModel, failure_id)
        return _to_failure(model) if model else None

    def get_model_by_id(self, failure_id: UUID) -> FailureOccurrenceModel | None:
        return self._session.get(FailureOccurrenceModel, failure_id)

    def list_historical_by_repository(
        self,
        repository_id: UUID,
        *,
        exclude_ci_run_id: UUID,
        exclude_failure_id: UUID | None = None,
        window_days: int = SIMILARITY_WINDOW_DAYS,
    ) -> list[HistoricalFailure]:
        from datetime import UTC, datetime, timedelta

        cutoff = datetime.now(UTC) - timedelta(days=window_days)
        stmt = (
            select(
                FailureOccurrenceModel,
                ClassificationModel.category,
            )
            .join(CIRunModel, FailureOccurrenceModel.ci_run_id == CIRunModel.id)
            .outerjoin(
                ClassificationModel,
                ClassificationModel.failure_occurrence_id == FailureOccurrenceModel.id,
            )
            .where(
                CIRunModel.repository_id == repository_id,
                CIRunModel.id != exclude_ci_run_id,
                FailureOccurrenceModel.created_at >= cutoff,
            )
            .order_by(FailureOccurrenceModel.created_at.desc())
        )
        if exclude_failure_id is not None:
            stmt = stmt.where(FailureOccurrenceModel.id != exclude_failure_id)

        rows = self._session.execute(stmt).all()
        return [
            HistoricalFailure(
                id=failure.id,
                ci_run_id=failure.ci_run_id,
                test_name=failure.test_name,
                error_type=failure.error_type,
                error_message=failure.error_message,
                fingerprint=failure.fingerprint,
                created_at=failure.created_at,
                category=category,
            )
            for failure, category in rows
        ]


class ClassificationRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(
        self,
        *,
        failure_occurrence_id: UUID,
        category: str,
        subcategory: str,
        suspected_component: str,
        summary: str,
        likely_cause: str,
        suggested_action: str,
        confidence: float,
        evidence_refs: list[str],
        insufficient_information: bool,
        provider: str,
        model: str,
        prompt_version: str,
        input_hash: str,
        input_tokens: int,
        output_tokens: int,
        duration_ms: int,
        trace_id: str,
    ) -> Classification:
        record = ClassificationModel(
            failure_occurrence_id=failure_occurrence_id,
            category=category,
            subcategory=subcategory,
            suspected_component=suspected_component,
            summary=summary,
            likely_cause=likely_cause,
            suggested_action=suggested_action,
            confidence=confidence,
            evidence_refs=evidence_refs,
            insufficient_information=insufficient_information,
            provider=provider,
            model=model,
            prompt_version=prompt_version,
            input_hash=input_hash,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            duration_ms=duration_ms,
            trace_id=trace_id,
        )
        self._session.add(record)
        self._session.flush()
        return _to_classification(record)

    def get_by_failure_id(self, failure_occurrence_id: UUID) -> Classification | None:
        model = self._session.scalar(
            select(ClassificationModel).where(
                ClassificationModel.failure_occurrence_id == failure_occurrence_id
            )
        )
        return _to_classification(model) if model else None

    def list_by_ci_run(self, ci_run_id: UUID) -> list[Classification]:
        models = self._session.scalars(
            select(ClassificationModel)
            .join(
                FailureOccurrenceModel,
                ClassificationModel.failure_occurrence_id == FailureOccurrenceModel.id,
            )
            .where(FailureOccurrenceModel.ci_run_id == ci_run_id)
            .order_by(ClassificationModel.created_at)
        ).all()
        return [_to_classification(m) for m in models]
