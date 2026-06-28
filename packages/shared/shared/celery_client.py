from uuid import UUID

from celery import Celery

from shared.config import get_settings


def _client() -> Celery:
    settings = get_settings()
    return Celery(broker=settings.celery_broker_url, backend=settings.celery_result_backend)


def enqueue_process_ci_run(ci_run_id: UUID, correlation_id: str) -> None:
    _client().send_task(
        "worker.process_ci_run",
        kwargs={"ci_run_id": str(ci_run_id), "correlation_id": correlation_id},
    )
