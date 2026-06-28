from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from domain.entities import CIRun, IngestedEvent
from domain.enums import ProcessingStatus
from shared.models import CIRunModel, IngestedEventModel


def _to_ingested_event(model: IngestedEventModel) -> IngestedEvent:
    return IngestedEvent(
        id=model.id,
        delivery_id=model.delivery_id,
        event_type=model.event_type,
        correlation_id=model.correlation_id,
        status=model.status,
        created_at=model.created_at,
    )


def _to_ci_run(model: CIRunModel) -> CIRun:
    return CIRun(
        id=model.id,
        repository_id=model.repository_id,
        workflow_name=model.workflow_name,
        branch=model.branch,
        commit_sha=model.commit_sha,
        conclusion=model.conclusion,
        status_url=model.status_url,
        processing_status=model.processing_status,
        idempotency_key=model.idempotency_key,
        ingested_at=model.ingested_at,
        enqueued_at=model.enqueued_at,
        completed_at=model.completed_at,
        failure_count=model.failure_count,
    )


class IngestedEventRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_delivery_id(self, delivery_id: str) -> IngestedEvent | None:
        model = self._session.scalar(
            select(IngestedEventModel).where(IngestedEventModel.delivery_id == delivery_id)
        )
        return _to_ingested_event(model) if model else None

    def get_model_by_delivery_id(self, delivery_id: str) -> IngestedEventModel | None:
        return self._session.scalar(
            select(IngestedEventModel).where(IngestedEventModel.delivery_id == delivery_id)
        )

    def create(
        self,
        *,
        delivery_id: str,
        event_type: str,
        payload_json: dict,
        correlation_id: str,
        status: str = "accepted",
    ) -> IngestedEvent:
        model = IngestedEventModel(
            delivery_id=delivery_id,
            event_type=event_type,
            payload_json=payload_json,
            correlation_id=correlation_id,
            status=status,
        )
        self._session.add(model)
        self._session.flush()
        return _to_ingested_event(model)


class CIRunRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, ci_run_id: UUID) -> CIRun | None:
        model = self._session.get(CIRunModel, ci_run_id)
        return _to_ci_run(model) if model else None

    def get_model_by_id(self, ci_run_id: UUID) -> CIRunModel | None:
        return self._session.get(CIRunModel, ci_run_id)

    def get_by_idempotency_key(self, idempotency_key: str) -> CIRun | None:
        model = self._session.scalar(
            select(CIRunModel).where(CIRunModel.idempotency_key == idempotency_key)
        )
        return _to_ci_run(model) if model else None

    def get_by_ingested_event_id(self, ingested_event_id: UUID) -> CIRun | None:
        model = self._session.scalar(
            select(CIRunModel).where(CIRunModel.ingested_event_id == ingested_event_id)
        )
        return _to_ci_run(model) if model else None

    def list_by_organization(
        self,
        organization_id: UUID,
        *,
        conclusion: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[CIRun]:
        from shared.models import RepositoryModel

        stmt = (
            select(CIRunModel)
            .join(RepositoryModel, CIRunModel.repository_id == RepositoryModel.id)
            .where(RepositoryModel.organization_id == organization_id)
            .order_by(CIRunModel.ingested_at.desc())
            .limit(limit)
            .offset(offset)
        )
        if conclusion:
            stmt = stmt.where(CIRunModel.conclusion == conclusion)
        models = self._session.scalars(stmt).all()
        return [_to_ci_run(m) for m in models]

    def count_by_organization(self, organization_id: UUID, *, conclusion: str | None = None) -> int:
        from sqlalchemy import func

        from shared.models import RepositoryModel

        stmt = (
            select(func.count())
            .select_from(CIRunModel)
            .join(RepositoryModel, CIRunModel.repository_id == RepositoryModel.id)
            .where(RepositoryModel.organization_id == organization_id)
        )
        if conclusion:
            stmt = stmt.where(CIRunModel.conclusion == conclusion)
        return self._session.scalar(stmt) or 0

    def create(
        self,
        *,
        repository_id: UUID,
        ingested_event_id: UUID,
        workflow_name: str,
        branch: str,
        commit_sha: str,
        conclusion: str,
        status_url: str | None,
        idempotency_key: str,
        failure_count: int = 0,
    ) -> CIRun:
        model = CIRunModel(
            repository_id=repository_id,
            ingested_event_id=ingested_event_id,
            workflow_name=workflow_name,
            branch=branch,
            commit_sha=commit_sha,
            conclusion=conclusion,
            status_url=status_url,
            processing_status=ProcessingStatus.PENDING.value,
            idempotency_key=idempotency_key,
            failure_count=failure_count,
        )
        self._session.add(model)
        self._session.flush()
        return _to_ci_run(model)

    def mark_enqueued(self, ci_run_id: UUID) -> None:
        model = self.get_model_by_id(ci_run_id)
        if model is None:
            return
        model.enqueued_at = datetime.now(UTC)

    def update_processing_status(self, ci_run_id: UUID, status: ProcessingStatus) -> None:
        model = self.get_model_by_id(ci_run_id)
        if model is None:
            return
        model.processing_status = status.value
        if status == ProcessingStatus.COMPLETED:
            model.completed_at = datetime.now(UTC)
