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
def test_paid_order_cannot_be_cancelled(client):
    from apps.accounts.models import User

    User.objects.create_superuser(email="staff@example.com", password="StrongPass123!")
    _register_and_login(client, "staff@example.com")

    store = client.post(
        "/api/v1/seller/stores", {"name": "Policy Shop"}, content_type="application/json"
    ).json()
    product = client.post(
        f"/api/v1/seller/stores/{store['id']}/products",
        {
            "sku": "POL-1",
            "name": "Policy Widget",
            "unit_price": "9.99",
            "is_published": True,
            "initial_stock": 5,
        },
        content_type="application/json",
    ).json()

    client.post("/api/v1/auth/logout", content_type="application/json")
    User.objects.create_user(email="buyer@example.com", password="StrongPass123!")
    _register_and_login(client, "buyer@example.com")

    cart = client.put(
        f"/api/v1/cart/items/{product['id']}",
        {"quantity": 1},
        content_type="application/json",
    ).json()
    order = client.post(
        "/api/v1/orders",
        {"cart_id": cart["id"]},
        content_type="application/json",
        HTTP_IDEMPOTENCY_KEY="policy-key",
    ).json()

    client.post("/api/v1/auth/logout", content_type="application/json")
    _register_and_login(client, "staff@example.com")
    client.post(
        f"/api/v1/dev/payments/{order['payment']['attempt_id']}/simulate",
        {"outcome": "succeeded"},
        content_type="application/json",
    )

    client.post("/api/v1/auth/logout", content_type="application/json")
    _register_and_login(client, "buyer@example.com")

    response = client.post(f"/api/v1/orders/{order['id']}/cancel", content_type="application/json")

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "ORDER_CONFLICT"
