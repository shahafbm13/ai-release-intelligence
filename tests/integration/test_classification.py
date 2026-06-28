import json
import uuid

import pytest
from worker.tasks.process_ci_run import process_ci_run

from tests.conftest import WEBHOOK_SECRET, sign_webhook_body


@pytest.mark.integration
def test_failed_run_produces_classifications(seeded_client, failed_run_payload, webhook_headers):
    delivery_id = f"delivery-classify-{uuid.uuid4()}"
    body = json.dumps(failed_run_payload).encode("utf-8")
    response = seeded_client.post(
        "/api/v1/webhooks/github",
        content=body,
        headers=webhook_headers(delivery_id),
    )
    assert response.status_code == 202
    data = response.json()
    ci_run_id = data["ci_run_id"]

    process_ci_run.apply(kwargs={"ci_run_id": ci_run_id, "correlation_id": data["correlation_id"]})

    login = seeded_client.post(
        "/api/v1/auth/login",
        json={"email": "analyst@demo.example.com", "password": "demo-pass-1"},
    )
    token = login.json()["access_token"]
    failures = seeded_client.get(
        f"/api/v1/failures?ci_run_id={ci_run_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert failures.status_code == 200
    payload = failures.json()
    assert payload["total"] == 2
    assert len(payload["items"]) == 2
    for item in payload["items"]:
        assert item["classification"] is not None
        assert item["classification"]["provider"] == "rules"
        assert item["classification"]["summary"]

    categories = {item["classification"]["category"] for item in payload["items"]}
    assert "product_defect" in categories
    assert "timeout" in categories
