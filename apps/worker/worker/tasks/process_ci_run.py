from uuid import UUID

from celery import shared_task

from shared.database import get_session_factory
from shared.logging import configure_logging, get_logger
from shared.processing.ci_run_processor import CIRunProcessor

logger = get_logger(__name__)


@shared_task(name="worker.process_ci_run", bind=True, max_retries=3, default_retry_delay=2)
def process_ci_run(self, ci_run_id: str, correlation_id: str) -> dict:
    configure_logging()
    session = get_session_factory()()
    try:
        return CIRunProcessor(session).process(UUID(ci_run_id), correlation_id)
    except Exception as exc:
        session.rollback()
        logger.error(
            "process_ci_run_task_failed",
            ci_run_id=ci_run_id,
            correlation_id=correlation_id,
            error=str(exc),
        )
        raise self.retry(exc=exc) from exc
    finally:
        session.close()
