import json
import uuid

import pytest
from worker.tasks.process_ci_run import process_ci_run

from tests.conftest import sign_webhook_body


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
    process_ci_run.apply(kwargs={"ci_run_id": data["ci_run_id"], "correlation_id": data["correlation_id"]})
    return data["ci_run_id"]


@pytest.mark.integration
def test_similar_failures_assessment_and_feedback(seeded_client, failed_run_payload):
    first_run_id = _ingest_and_process(
        seeded_client,
        failed_run_payload,
        f"delivery-m4-first-{uuid.uuid4()}",
    )
    second_run_id = _ingest_and_process(
        seeded_client,
        failed_run_payload,
        f"delivery-m4-second-{uuid.uuid4()}",
    )

    login = seeded_client.post(
        "/api/v1/auth/login",
        json={"email": "analyst@demo.example.com", "password": "demo-pass-1"},
    )
    token = login.json()["access_token"]
    auth = {"Authorization": f"Bearer {token}"}

    failures = seeded_client.get(
        f"/api/v1/failures?ci_run_id={second_run_id}",
        headers=auth,
    ).json()["items"]
    assert len(failures) == 2

    similar = seeded_client.get(
        f"/api/v1/failures/{failures[0]['id']}/similar",
        headers=auth,
    )
    assert similar.status_code == 200
    similar_body = similar.json()
    assert len(similar_body["items"]) >= 1
    assert similar_body["items"][0]["classification_summary"]

    assessment = seeded_client.get(
        f"/api/v1/ci-runs/{second_run_id}/assessment",
        headers=auth,
    )
    assert assessment.status_code == 200
    assessment_body = assessment.json()
    assert assessment_body["risk_level"] in {"medium", "high", "critical"}
    assert assessment_body["recommendation"] in {"caution", "hold"}
    assert len(assessment_body["factors"]) == 6

    feedback = seeded_client.post(
        f"/api/v1/failures/{failures[0]['id']}/feedback",
        headers=auth,
        json={
            "action": "correct",
            "corrected_category": "test_defect",
            "corrected_component": "checkout-ui",
            "note": "Selector drift in checkout page",
            "resolved": False,
        },
    )
    assert feedback.status_code == 201
    assert feedback.json()["action"] == "correct"


@pytest.mark.integration
def test_similar_failures_empty_message(seeded_client):
    isolated_payload = {
        "action": "completed",
        "workflow_run": {
            "id": 999001,
            "name": "CI",
            "head_branch": "main",
            "head_sha": "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
            "conclusion": "failure",
            "html_url": "https://github.com/acme/checkout-service/actions/runs/999001",
            "repository": {"full_name": "acme/checkout-service"},
        },
        "repository": {"full_name": "acme/checkout-service"},
        "test_failures": [
            {
                "test_name": "test_m4_isolated_unique_failure_only",
                "suite_name": "tests.m4.isolated",
                "error_type": "M4IsolatedError",
                "error_message": "unique message that should not match history",
                "stack_trace": "M4IsolatedError: unique",
                "log_excerpt": "isolated run",
                "retry_number": 0,
            }
        ],
    }
    run_id = _ingest_and_process(
        seeded_client,
        isolated_payload,
        f"delivery-m4-single-{uuid.uuid4()}",
    )
    login = seeded_client.post(
        "/api/v1/auth/login",
        json={"email": "analyst@demo.example.com", "password": "demo-pass-1"},
    )
    token = login.json()["access_token"]
    failure_id = seeded_client.get(
        f"/api/v1/failures?ci_run_id={run_id}",
        headers={"Authorization": f"Bearer {token}"},
    ).json()["items"][0]["id"]

    similar = seeded_client.get(
        f"/api/v1/failures/{failure_id}/similar",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert similar.status_code == 200
    assert similar.json()["message"] == "no_similar_failures_found"
