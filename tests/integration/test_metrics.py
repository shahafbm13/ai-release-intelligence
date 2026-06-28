import pytest


@pytest.mark.integration
def test_metrics_summary(seeded_client):
    login = seeded_client.post(
        "/api/v1/auth/login",
        json={"email": "analyst@demo.example.com", "password": "demo-pass-1"},
    )
    token = login.json()["access_token"]
    response = seeded_client.get(
        "/api/v1/metrics/summary",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_ci_runs" in data
    assert "classification_fallback_rate_percent" in data
    assert data["total_ci_runs"] >= 0
