import pytest


@pytest.mark.django_db
def test_store_currency_is_validated(client):
    client.post(
        "/api/v1/auth/register",
        {"email": "seller@example.com", "password": "StrongPass123!"},
        content_type="application/json",
    )
    client.post(
        "/api/v1/auth/login",
        {"email": "seller@example.com", "password": "StrongPass123!"},
        content_type="application/json",
    )

    created = client.post(
        "/api/v1/seller/stores",
        {"name": "USD Shop", "currency": "usd"},
        content_type="application/json",
    )
    assert created.status_code == 201
    assert created.json()["currency"] == "USD"

    rejected = client.post(
        "/api/v1/seller/stores",
        {"name": "JPY Shop", "currency": "JPY"},
        content_type="application/json",
    )
    assert rejected.status_code == 400
    assert rejected.json()["error"]["code"] == "VALIDATION_ERROR"
