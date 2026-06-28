from celery import Celery

from shared.config import get_settings

settings = get_settings()

celery_app = Celery(
    "release_intelligence",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
)

celery_app.autodiscover_tasks(["worker.tasks"])

import worker.tasks.process_ci_run  # noqa: F401, E402


@celery_app.task(name="worker.ping")
def ping() -> str:
    return "pong"
