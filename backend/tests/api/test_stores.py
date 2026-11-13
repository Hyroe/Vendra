import pytest


def _register_and_login(client, email):
    client.post(
        "/api/v1/auth/register",
        {"email": email, "password": "StrongPass123!"},
        content_type="application/json",
    )
    client.post(
        "/api/v1/auth/login",
        {"email": email, "password": "StrongPass123!"},
        content_type="application/json",
    )


@pytest.mark.django_db
def test_public_store_list_is_available_without_authentication(client):
    response = client.get("/api/v1/stores")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.django_db
def test_seller_can_create_store(client):
    _register_and_login(client, "seller@example.com")

    response = client.post(
        "/api/v1/seller/stores",
        {"name": "Corner Shop", "currency": "usd", "status": "ACTIVE"},
        content_type="application/json",
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["name"] == "Corner Shop"
    assert payload["currency"] == "USD"
    assert payload["slug"] == "corner-shop"

    me = client.get("/api/v1/me")
    assert "SELLER" in me.json()["roles"]
    assert me.json()["stores"][0]["name"] == "Corner Shop"


@pytest.mark.django_db
def test_store_creation_requires_authentication(client):
    response = client.post(
        "/api/v1/seller/stores",
        {"name": "Corner Shop"},
        content_type="application/json",
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_seller_can_edit_own_store(client):
    _register_and_login(client, "seller@example.com")
    created = client.post(
        "/api/v1/seller/stores",
        {"name": "Corner Shop"},
        content_type="application/json",
    ).json()

    response = client.patch(
        f"/api/v1/seller/stores/{created['id']}",
        {"name": "Updated Shop", "status": "INACTIVE"},
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Shop"
    assert response.json()["status"] == "INACTIVE"


@pytest.mark.django_db
def test_seller_cannot_edit_another_sellers_store(client):
    _register_and_login(client, "seller-a@example.com")
    store_id = client.post(
        "/api/v1/seller/stores",
        {"name": "Seller A Shop"},
        content_type="application/json",
    ).json()["id"]

    client.post("/api/v1/auth/logout", content_type="application/json")
    _register_and_login(client, "seller-b@example.com")

    response = client.patch(
        f"/api/v1/seller/stores/{store_id}",
        {"name": "Hijacked Shop"},
        content_type="application/json",
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


@pytest.mark.django_db
def test_inactive_store_is_not_publicly_visible(client):
    _register_and_login(client, "seller@example.com")
    store_id = client.post(
        "/api/v1/seller/stores",
        {"name": "Hidden Shop", "status": "INACTIVE"},
        content_type="application/json",
    ).json()["id"]

    client.post("/api/v1/auth/logout", content_type="application/json")

    detail = client.get(f"/api/v1/stores/{store_id}")
    assert detail.status_code == 404

    listing = client.get("/api/v1/stores")
    assert listing.json() == []
