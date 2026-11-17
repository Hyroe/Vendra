import pytest


def _setup(client):
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
        "/api/v1/seller/stores", {"name": "Checkout Shop"}, content_type="application/json"
    ).json()
    product = client.post(
        f"/api/v1/seller/stores/{store['id']}/products",
        {
            "sku": "CHK-1",
            "name": "Checkout Widget",
            "unit_price": "9.99",
            "is_published": True,
            "initial_stock": 5,
        },
        content_type="application/json",
    ).json()
    option = client.post(
        f"/api/v1/seller/stores/{store['id']}/shipping-options",
        {"code": "express", "name": "Express", "price": "9.50", "active": True},
        content_type="application/json",
    ).json()
    client.post("/api/v1/auth/logout", content_type="application/json")

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
    address = client.post(
        "/api/v1/addresses",
        {"line1": "123 Main St", "city": "Springfield", "country": "US"},
        content_type="application/json",
    ).json()
    cart = client.put(
        f"/api/v1/cart/items/{product['id']}",
        {"quantity": 2},
        content_type="application/json",
    ).json()
    return store, product, option, address, cart


@pytest.mark.django_db
def test_checkout_supports_address_and_shipping_option_ids(client):
    store, product, option, address, cart = _setup(client)

    response = client.post(
        "/api/v1/orders",
        {
            "cart_id": cart["id"],
            "delivery_address_id": address["id"],
            "shipping_option_id": "express",
        },
        content_type="application/json",
        HTTP_IDEMPOTENCY_KEY="address-shipping-key",
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["totals"]["shipping"] == "9.50"
    assert payload["totals"]["grand_total"] == "29.48"

    detail = client.get(f"/api/v1/orders/{payload['id']}")
    assert detail.json()["address_snapshot"]["city"] == "Springfield"
    assert detail.json()["shipping_option_snapshot"]["code"] == "express"
