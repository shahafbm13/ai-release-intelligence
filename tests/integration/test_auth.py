import pytest


@pytest.mark.integration
def test_login_success(seeded_client):
    response = seeded_client.post(
        "/api/v1/auth/login",
        json={"email": "analyst@demo.example.com", "password": "demo-pass-1"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


@pytest.mark.integration
def test_login_invalid_password(seeded_client):
    response = seeded_client.post(
        "/api/v1/auth/login",
        json={"email": "analyst@demo.example.com", "password": "wrong-password"},
    )
    assert response.status_code == 401


@pytest.mark.integration
def test_protected_route_requires_auth(seeded_client):
    response = seeded_client.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.integration
def test_me_returns_current_user(seeded_client):
    login = seeded_client.post(
        "/api/v1/auth/login",
        json={"email": "analyst@demo.example.com", "password": "demo-pass-1"},
    )
    token = login.json()["access_token"]
    response = seeded_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "analyst@demo.example.com"
    assert body["role"] == "analyst"


@pytest.mark.integration
def test_org_isolation_on_repositories(seeded_client):
    analyst_login = seeded_client.post(
        "/api/v1/auth/login",
        json={"email": "analyst@demo.example.com", "password": "demo-pass-1"},
    )
    token = analyst_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    list_response = seeded_client.get("/api/v1/repositories", headers=headers)
    assert list_response.status_code == 200
    repos = list_response.json()
    assert len(repos) >= 3

    create_response = seeded_client.post(
        "/api/v1/repositories",
        headers=headers,
        json={"full_name": "acme/new-service", "default_branch": "main"},
    )
    assert create_response.status_code == 201
    assert create_response.json()["full_name"] == "acme/new-service"


@pytest.mark.integration
def test_viewer_cannot_create_repository(seeded_client):
    login = seeded_client.post(
        "/api/v1/auth/login",
        json={"email": "viewer@demo.example.com", "password": "demo-pass-2"},
    )
    token = login.json()["access_token"]
    response = seeded_client.post(
        "/api/v1/repositories",
        headers={"Authorization": f"Bearer {token}"},
        json={"full_name": "acme/forbidden", "default_branch": "main"},
    )
    assert response.status_code == 403
