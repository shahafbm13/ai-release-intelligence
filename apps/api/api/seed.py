"""Seed demo organization, users, and repositories."""

from domain.enums import UserRole
from shared.config import get_settings
from shared.database import get_session_factory
from shared.logging import configure_logging, get_logger
from shared.repositories import OrganizationRepository, RepositoryRepository, UserRepository
from shared.security import hash_password

logger = get_logger(__name__)

DEMO_ORG_NAME = "Acme Engineering"
DEMO_ORG_SLUG = "acme-eng"
DEMO_USERS = [
    {"email": "analyst@demo.example.com", "password": "demo-pass-1", "role": UserRole.ANALYST},
    {"email": "viewer@demo.example.com", "password": "demo-pass-2", "role": UserRole.VIEWER},
    {"email": "admin@demo.example.com", "password": "demo-pass-3", "role": UserRole.ADMIN},
]
DEMO_REPOS = [
    {"full_name": "acme/checkout-service", "default_branch": "main"},
    {"full_name": "acme/payment-gateway", "default_branch": "main"},
    {"full_name": "acme/e2e-automation", "default_branch": "develop"},
]


def seed() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    session = get_session_factory()()
    try:
        org_repo = OrganizationRepository(session)
        user_repo = UserRepository(session)
        repo_repo = RepositoryRepository(session)

        org = org_repo.get_by_slug(DEMO_ORG_SLUG)
        if org is None:
            org = org_repo.create(DEMO_ORG_NAME, DEMO_ORG_SLUG)
            logger.info("seed_created_org", slug=DEMO_ORG_SLUG)
        else:
            logger.info("seed_org_exists", slug=DEMO_ORG_SLUG)

        for spec in DEMO_USERS:
            if user_repo.get_by_email(spec["email"]) is None:
                user_repo.create(
                    organization_id=org.id,
                    email=spec["email"],
                    password_hash=hash_password(spec["password"]),
                    role=spec["role"],
                )
                logger.info("seed_created_user", email=spec["email"])

        existing = {r.full_name for r in repo_repo.list_by_organization(org.id)}
        for spec in DEMO_REPOS:
            if spec["full_name"] not in existing:
                repo_repo.create(
                    organization_id=org.id,
                    full_name=spec["full_name"],
                    default_branch=spec["default_branch"],
                )
                logger.info("seed_created_repo", full_name=spec["full_name"])

        session.commit()
        logger.info("seed_complete")

        from api.seed_demo_runs import seed_demo_runs

        seed_demo_runs(session)
        session.commit()

        from api.backfill_assessments import backfill_release_assessments

        backfill_release_assessments()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def main() -> None:
    seed()


if __name__ == "__main__":
    main()
