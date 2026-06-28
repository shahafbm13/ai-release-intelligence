import hashlib
import hmac
import json
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).resolve().parent / "contract" / "fixtures" / "github"
WEBHOOK_SECRET = "test-webhook-secret"


def sign_webhook_body(body: bytes, secret: str = WEBHOOK_SECRET) -> str:
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


@pytest.fixture
def failed_run_payload() -> dict:
    return json.loads((FIXTURES_DIR / "failed_run.json").read_text(encoding="utf-8"))


@pytest.fixture
def webhook_headers(failed_run_payload):
    def _headers(delivery_id: str = "test-delivery-001") -> dict[str, str]:
        body = json.dumps(failed_run_payload).encode("utf-8")
        return {
            "X-GitHub-Delivery": delivery_id,
            "X-Hub-Signature-256": sign_webhook_body(body),
            "Content-Type": "application/json",
        }

    return _headers
