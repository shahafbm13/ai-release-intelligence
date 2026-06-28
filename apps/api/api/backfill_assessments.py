"""Backfill release assessments for runs processed before M4."""

from shared.database import get_session_factory
from shared.logging import configure_logging, get_logger
from shared.processing.ci_run_processor import CIRunProcessor
from shared.repositories import OrganizationRepository
from shared.config import get_settings

logger = get_logger(__name__)


def backfill_release_assessments() -> int:
    settings = get_settings()
    configure_logging(settings.log_level)
    session = get_session_factory()()
    try:
        org = OrganizationRepository(session).get_by_slug(settings.default_organization_slug)
        if org is None:
            logger.warning("backfill_org_not_found")
            return 0
        count = CIRunProcessor(session).backfill_release_assessments(org.id)
        session.commit()
        logger.info("backfill_release_assessments_complete", updated=count)
        return count
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def main() -> None:
    count = backfill_release_assessments()
    print(f"Backfilled {count} release assessment(s).")


if __name__ == "__main__":
    main()
