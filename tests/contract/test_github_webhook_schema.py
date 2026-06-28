import hashlib
import hmac
import json
from pathlib import Path

import pytest
from api.schemas import GitHubWebhookPayload

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures" / "github"
WEBHOOK_SECRET = "test-webhook-secret"


def sign_body(body: bytes, secret: str = WEBHOOK_SECRET) -> str:
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


@pytest.mark.parametrize("fixture_name", ["failed_run.json"])
def test_github_fixture_matches_schema(fixture_name: str):
    payload = json.loads((FIXTURES_DIR / fixture_name).read_text(encoding="utf-8"))
    parsed = GitHubWebhookPayload.model_validate(payload)
    assert parsed.action == "completed"
    assert parsed.workflow_run is not None
    assert len(parsed.test_failures) >= 1
