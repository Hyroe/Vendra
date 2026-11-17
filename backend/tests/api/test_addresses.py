import pytest


@pytest.mark.django_db
def test_customer_can_manage_addresses(client):
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

    created = client.post(
        "/api/v1/addresses",
        {
            "label": "Home",
            "recipient_name": "Buyer",
            "line1": "123 Main St",
            "city": "Springfield",
            "postal_code": "12345",
            "country": "us",
            "is_default": True,
        },
        content_type="application/json",
    )
    assert created.status_code == 201
    address_id = created.json()["id"]
    assert created.json()["country"] == "US"

    listing = client.get("/api/v1/addresses")
    assert listing.status_code == 200
    assert len(listing.json()) == 1

    updated = client.patch(
        f"/api/v1/addresses/{address_id}",
        {"city": "Shelbyville"},
        content_type="application/json",
    )
    assert updated.status_code == 200
    assert updated.json()["city"] == "Shelbyville"

    deleted = client.delete(f"/api/v1/addresses/{address_id}", content_type="application/json")
    assert deleted.status_code == 204


@pytest.mark.django_db
def test_seller_can_manage_shipping_options(client):
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
    store = client.post(
        "/api/v1/seller/stores",
        {"name": "Shipping Shop"},
        content_type="application/json",
    ).json()

    created = client.post(
        f"/api/v1/seller/stores/{store['id']}/shipping-options",
        {"code": "express", "name": "Express", "price": "9.50", "active": True},
        content_type="application/json",
    )
    assert created.status_code == 201
    option_id = created.json()["id"]
    assert created.json()["code"] == "express"

    updated = client.patch(
        f"/api/v1/seller/shipping-options/{option_id}",
        {"price": "10.00"},
        content_type="application/json",
    )
    assert updated.status_code == 200
    assert updated.json()["price"] == "10.00"

    deleted = client.delete(
        f"/api/v1/seller/shipping-options/{option_id}", content_type="application/json"
    )
    assert deleted.status_code == 204
