import pytest


@pytest.mark.integration
def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.integration
def test_ready(client):
    response = client.get("/ready")
    assert response.status_code in (200, 503)
    body = response.json()
    assert "checks" in body
    assert "database" in body["checks"]
