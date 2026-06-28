"""Seed demo CI runs from contract fixtures for dashboard demos."""

import json
import uuid
from pathlib import Path

from shared.logging import get_logger
from shared.processing.ci_run_processor import CIRunProcessor
from shared.repositories import OrganizationRepository
from shared.repositories.ci_runs import CIRunRepository

logger = get_logger(__name__)

FIXTURES_DIR = Path(__file__).resolve().parents[3] / "tests" / "contract" / "fixtures" / "github"

DEMO_FIXTURES = [
    "failed_run.json",
    "timeout_run.json",
    "auth_failure.json",
    "infra_outage.json",
    "flaky_retry.json",
    "network_failure.json",
]


def seed_demo_runs(session) -> None:
    from api.services.ingest_service import IngestService

    org = OrganizationRepository(session).get_by_slug("acme-eng")
    if org is None:
        return

    existing = CIRunRepository(session).count_by_organization(org.id)
    if existing >= len(DEMO_FIXTURES):
        logger.info("seed_demo_runs_skipped", existing_runs=existing)
        return

    ingest = IngestService(session)
    processor = CIRunProcessor(session)

    for fixture_name in DEMO_FIXTURES:
        fixture_path = FIXTURES_DIR / fixture_name
        if not fixture_path.is_file():
            logger.warning("seed_demo_fixture_missing", fixture=fixture_name)
            continue
        payload_dict = json.loads(fixture_path.read_text(encoding="utf-8"))
        delivery_id = f"seed-demo-{fixture_name}-{uuid.uuid4()}"
        correlation_id = str(uuid.uuid4())
        result = ingest.replay_fixture_payload(
            payload_dict=payload_dict,
            delivery_id=delivery_id,
            correlation_id=correlation_id,
        )
        if result.response.ci_run_id is None:
            continue
        processor.process(result.response.ci_run_id, correlation_id)
        logger.info("seed_demo_run_processed", fixture=fixture_name, ci_run_id=str(result.response.ci_run_id))

    session.commit()
    logger.info("seed_demo_runs_complete")
