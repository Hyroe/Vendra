import pytest


@pytest.mark.django_db
def test_mobile_token_login_and_refresh(client):
    from apps.accounts.models import User

    User.objects.create_user(email="mobile@example.com", password="StrongPass123!")

    login = client.post(
        "/api/v1/auth/token",
        {"email": "mobile@example.com", "password": "StrongPass123!", "device_name": "Pixel"},
        content_type="application/json",
    )
    assert login.status_code == 200
    access = login.json()["access"]
    refresh = login.json()["refresh"]

    me = client.get("/api/v1/me", HTTP_AUTHORIZATION=f"Bearer {access}")
    assert me.status_code == 200
    assert me.json()["email"] == "mobile@example.com"

    refreshed = client.post(
        "/api/v1/auth/token/refresh",
        {"refresh_token": refresh},
        content_type="application/json",
    )
    assert refreshed.status_code == 200
    assert refreshed.json()["access"] != access
    assert refreshed.json()["refresh"] != refresh

    # Old refresh token is revoked after rotation.
    replay = client.post(
        "/api/v1/auth/token/refresh",
        {"refresh_token": refresh},
        content_type="application/json",
    )
    assert replay.status_code == 401


@pytest.mark.django_db
def test_mobile_token_revoke(client):
    from apps.accounts.models import User

    User.objects.create_user(email="mobile@example.com", password="StrongPass123!")

    login = client.post(
        "/api/v1/auth/token",
        {"email": "mobile@example.com", "password": "StrongPass123!"},
        content_type="application/json",
    )
    access = login.json()["access"]
    refresh = login.json()["refresh"]

    revoke = client.post(
        "/api/v1/auth/token/revoke",
        {"refresh_token": refresh},
        content_type="application/json",
    )
    assert revoke.status_code == 204

    me = client.get("/api/v1/me", HTTP_AUTHORIZATION=f"Bearer {access}")
    assert me.status_code == 401


@pytest.mark.django_db
def test_mobile_sessions_are_user_scoped(client):
    from apps.accounts.models import User

    User.objects.create_user(email="mobile@example.com", password="StrongPass123!")
    User.objects.create_user(email="other@example.com", password="StrongPass123!")

    login = client.post(
        "/api/v1/auth/token",
        {"email": "mobile@example.com", "password": "StrongPass123!"},
        content_type="application/json",
    )
    access = login.json()["access"]
    session_id = login.json()["session_id"]

    sessions = client.get("/api/v1/auth/sessions", HTTP_AUTHORIZATION=f"Bearer {access}")
    assert sessions.status_code == 200
    assert len(sessions.json()) == 1

    # Another user cannot revoke the first user's session.
    other_login = client.post(
        "/api/v1/auth/token",
        {"email": "other@example.com", "password": "StrongPass123!"},
        content_type="application/json",
    )
    other_access = other_login.json()["access"]

    response = client.delete(
        f"/api/v1/auth/sessions/{session_id}",
        HTTP_AUTHORIZATION=f"Bearer {other_access}",
    )
    assert response.status_code == 404
