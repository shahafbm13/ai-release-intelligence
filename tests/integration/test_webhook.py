import json
import uuid

import pytest
from worker.tasks.process_ci_run import process_ci_run

from tests.conftest import WEBHOOK_SECRET, sign_webhook_body


@pytest.fixture(autouse=True)
def webhook_secret(test_env):
    import os

    os.environ["GITHUB_WEBHOOK_SECRET"] = WEBHOOK_SECRET


def _run_worker(ci_run_id: str, correlation_id: str) -> None:
    process_ci_run.apply(kwargs={"ci_run_id": ci_run_id, "correlation_id": correlation_id})


@pytest.mark.integration
def test_webhook_ingest_success(seeded_client, failed_run_payload, webhook_headers):
    delivery_id = f"delivery-{uuid.uuid4()}"
    body = json.dumps(failed_run_payload).encode("utf-8")
    headers = webhook_headers(delivery_id)

    response = seeded_client.post(
        "/api/v1/webhooks/github",
        content=body,
        headers=headers,
    )
    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "accepted"
    assert data["ci_run_id"] is not None

    _run_worker(data["ci_run_id"], data["correlation_id"])

    login = seeded_client.post(
        "/api/v1/auth/login",
        json={"email": "analyst@demo.example.com", "password": "demo-pass-1"},
    )
    token = login.json()["access_token"]
    run = seeded_client.get(
        f"/api/v1/ci-runs/{data['ci_run_id']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert run.status_code == 200
    body = run.json()
    assert body["conclusion"] == "failure"
    assert body["processing_status"] == "completed"
    assert body["failure_count"] == 2


@pytest.mark.integration
def test_webhook_duplicate_delivery(seeded_client, failed_run_payload, webhook_headers):
    delivery_id = f"delivery-dup-{uuid.uuid4()}"
    body = json.dumps(failed_run_payload).encode("utf-8")
    headers = webhook_headers(delivery_id)

    first = seeded_client.post("/api/v1/webhooks/github", content=body, headers=headers)
    assert first.status_code == 202
    first_id = first.json()["ci_run_id"]

    second = seeded_client.post("/api/v1/webhooks/github", content=body, headers=headers)
    assert second.status_code == 200
    assert second.json()["status"] == "duplicate"
    assert second.json()["ci_run_id"] == first_id


@pytest.mark.integration
def test_webhook_invalid_signature(seeded_client, failed_run_payload):
    body = json.dumps(failed_run_payload).encode("utf-8")
    response = seeded_client.post(
        "/api/v1/webhooks/github",
        content=body,
        headers={
            "X-GitHub-Delivery": "bad-sig-delivery",
            "X-Hub-Signature-256": "sha256=invalid",
            "Content-Type": "application/json",
        },
    )
    assert response.status_code == 401


@pytest.mark.integration
def test_webhook_unknown_repository(seeded_client, failed_run_payload, webhook_headers):
    payload = dict(failed_run_payload)
    payload["repository"] = {"full_name": "unknown/repo"}
    payload["workflow_run"] = dict(payload["workflow_run"])
    payload["workflow_run"]["repository"] = {"full_name": "unknown/repo"}
    delivery_id = f"delivery-unknown-{uuid.uuid4()}"
    body = json.dumps(payload).encode("utf-8")
    headers = {
        "X-GitHub-Delivery": delivery_id,
        "X-Hub-Signature-256": sign_webhook_body(body),
        "Content-Type": "application/json",
    }
    response = seeded_client.post("/api/v1/webhooks/github", content=body, headers=headers)
    assert response.status_code == 422


@pytest.mark.integration
def test_list_ci_runs(seeded_client, failed_run_payload, webhook_headers):
    delivery_id = f"delivery-list-{uuid.uuid4()}"
    body = json.dumps(failed_run_payload).encode("utf-8")
    seeded_client.post(
        "/api/v1/webhooks/github",
        content=body,
        headers=webhook_headers(delivery_id),
    )

    login = seeded_client.post(
        "/api/v1/auth/login",
        json={"email": "analyst@demo.example.com", "password": "demo-pass-1"},
    )
    token = login.json()["access_token"]
    response = seeded_client.get(
        "/api/v1/ci-runs?conclusion=failure",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1
