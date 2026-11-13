import pytest


@pytest.mark.django_db
def test_register_creates_customer_account(client):
    response = client.post(
        "/api/v1/auth/register",
        {"email": "Customer@Example.com", "password": "StrongPass123!"},
        content_type="application/json",
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["email"] == "customer@example.com"
    assert payload["roles"] == ["CUSTOMER"]
    assert payload["stores"] == []


@pytest.mark.django_db
def test_register_rejects_duplicate_email(client):
    client.post(
        "/api/v1/auth/register",
        {"email": "buyer@example.com", "password": "StrongPass123!"},
        content_type="application/json",
    )

    response = client.post(
        "/api/v1/auth/register",
        {"email": "buyer@example.com", "password": "StrongPass123!"},
        content_type="application/json",
    )

    assert response.status_code == 400
    assert "email" in response.json()["error"]["details"]


@pytest.mark.django_db
def test_login_returns_profile_and_session(client):
    client.post(
        "/api/v1/auth/register",
        {"email": "buyer@example.com", "password": "StrongPass123!"},
        content_type="application/json",
    )

    response = client.post(
        "/api/v1/auth/login",
        {"email": "buyer@example.com", "password": "StrongPass123!"},
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.json()["email"] == "buyer@example.com"

    me = client.get("/api/v1/me")
    assert me.status_code == 200
    assert me.json()["email"] == "buyer@example.com"


@pytest.mark.django_db
def test_login_rejects_invalid_credentials(client):
    client.post(
        "/api/v1/auth/register",
        {"email": "buyer@example.com", "password": "StrongPass123!"},
        content_type="application/json",
    )

    response = client.post(
        "/api/v1/auth/login",
        {"email": "buyer@example.com", "password": "wrong-password"},
        content_type="application/json",
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHENTICATED"


@pytest.mark.django_db
def test_me_requires_authentication(client):
    response = client.get("/api/v1/me")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHENTICATED"


@pytest.mark.django_db
def test_logout_revokes_session(client):
    client.post(
        "/api/v1/auth/register",
        {"email": "buyer@example.com", "password": "StrongPass123!"},
        content_type="application/json",
    )
    client.post(
        "/api/v1/auth/login",
        {"email": "buyer@example.com", "password": "StrongPass123!"},
        content_type="application/json",
    )

    logout = client.post("/api/v1/auth/logout", content_type="application/json")
    assert logout.status_code == 204

    me = client.get("/api/v1/me")
    assert me.status_code == 401
