"""E2E critical path: ingest → process → classify → assess → feedback."""

import json
import uuid

import pytest
from worker.tasks.process_ci_run import process_ci_run

from tests.conftest import sign_webhook_body

pytestmark = [pytest.mark.e2e, pytest.mark.integration]


def _ingest_and_process(client, payload: dict, delivery_id: str) -> str:
    body = json.dumps(payload).encode("utf-8")
    headers = {
        "X-GitHub-Delivery": delivery_id,
        "X-Hub-Signature-256": sign_webhook_body(body),
        "Content-Type": "application/json",
    }
    response = client.post("/api/v1/webhooks/github", content=body, headers=headers)
    assert response.status_code == 202
    data = response.json()
    process_ci_run.apply(
        kwargs={"ci_run_id": data["ci_run_id"], "correlation_id": data["correlation_id"]}
    )
    return data["ci_run_id"]


@pytest.mark.e2e
def test_critical_path_ingest_classify_assess_feedback(seeded_client, failed_run_payload):
    run_id = _ingest_and_process(
        seeded_client,
        failed_run_payload,
        f"delivery-e2e-{uuid.uuid4()}",
    )

    login = seeded_client.post(
        "/api/v1/auth/login",
        json={"email": "analyst@demo.example.com", "password": "demo-pass-1"},
    )
    assert login.status_code == 200
    auth = {"Authorization": f"Bearer {login.json()['access_token']}"}

    run = seeded_client.get(f"/api/v1/ci-runs/{run_id}", headers=auth)
    assert run.status_code == 200
    assert run.json()["processing_status"] == "completed"

    failures = seeded_client.get(
        f"/api/v1/failures?ci_run_id={run_id}",
        headers=auth,
    ).json()["items"]
    assert len(failures) >= 1
    assert failures[0]["classification"] is not None

    assessment = seeded_client.get(f"/api/v1/ci-runs/{run_id}/assessment", headers=auth)
    assert assessment.status_code == 200
    body = assessment.json()
    assert body["risk_level"] in {"low", "medium", "high", "critical"}
    assert body["recommendation"] in {"proceed", "caution", "hold"}
    assert len(body["factors"]) >= 1

    feedback = seeded_client.post(
        f"/api/v1/failures/{failures[0]['id']}/feedback",
        headers=auth,
        json={"action": "accept", "note": "E2E acceptance", "resolved": False},
    )
    assert feedback.status_code == 201

    metrics = seeded_client.get("/api/v1/metrics/summary", headers=auth)
    assert metrics.status_code == 200
    assert metrics.json()["total_ci_runs"] >= 1
