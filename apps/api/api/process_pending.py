"""Process CI runs stuck in pending (worker not running)."""

from domain.enums import ProcessingStatus
from shared.config import get_settings
from shared.database import get_session_factory
from shared.logging import configure_logging, get_logger
from shared.models import CIRunModel
from shared.processing.ci_run_processor import CIRunProcessor
from sqlalchemy import select

logger = get_logger(__name__)


def process_pending_runs() -> int:
    settings = get_settings()
    configure_logging(settings.log_level)
    session = get_session_factory()()
    try:
        run_ids = session.scalars(
            select(CIRunModel.id).where(
                CIRunModel.processing_status == ProcessingStatus.PENDING.value
            )
        ).all()
        processor = CIRunProcessor(session)
        processed = 0
        for run_id in run_ids:
            processor.process(run_id, f"process-pending-{run_id}")
            processed += 1
            logger.info("process_pending_run_done", ci_run_id=str(run_id))
        return processed
    finally:
        session.close()


def main() -> None:
    count = process_pending_runs()
    print(f"Processed {count} pending CI run(s).")


if __name__ == "__main__":
    main()
