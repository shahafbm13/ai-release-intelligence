import os
import subprocess
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from api.main import app
from shared.config import get_settings
from shared.database import get_engine, reset_database_singletons

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def database_url() -> str:
    return os.getenv(
        "TEST_DATABASE_URL",
        "postgresql+psycopg2://release_intel:release_intel@localhost:5432/release_intel",
    )


@pytest.fixture(scope="module")
def test_env(database_url: str):
    reset_database_singletons()
    get_settings.cache_clear()
    os.environ["DATABASE_URL"] = database_url
    os.environ["JWT_SECRET"] = "test-secret-key-for-integration-tests"
    os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
    os.environ.setdefault("GITHUB_WEBHOOK_SECRET", "test-webhook-secret")
    os.environ["GROQ_API_KEY"] = ""
    os.environ["GEMINI_API_KEY"] = ""
    yield
    reset_database_singletons()
    get_settings.cache_clear()


def _run_alembic(*args: str) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "-c", "migrations/alembic.ini", *args],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout)


def _reset_database_schema() -> None:
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
        conn.execute(text("GRANT ALL ON SCHEMA public TO public"))


@pytest.fixture(scope="module")
def prepare_database(test_env, database_url):
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except OperationalError as exc:
        pytest.skip(f"PostgreSQL not available: {exc}")

    reset_database_singletons()
    get_settings.cache_clear()
    _reset_database_schema()
    _run_alembic("stamp", "base")
    _run_alembic("upgrade", "head")
    yield


@pytest.fixture
def client(prepare_database):
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def seeded_client(client):
    from api.seed import seed

    seed()
    return client
