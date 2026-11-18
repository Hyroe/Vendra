import pytest


@pytest.mark.django_db
def test_seller_can_confirm_manual_payment(client):
    from apps.accounts.models import User

    User.objects.create_superuser(email="seller@example.com", password="StrongPass123!")
    client.post(
        "/api/v1/auth/login",
        {"email": "seller@example.com", "password": "StrongPass123!"},
        content_type="application/json",
    )

    store = client.post(
        "/api/v1/seller/stores", {"name": "Manual Shop"}, content_type="application/json"
    ).json()
    product = client.post(
        f"/api/v1/seller/stores/{store['id']}/products",
        {
            "sku": "MAN-1",
            "name": "Manual Widget",
            "unit_price": "9.99",
            "is_published": True,
            "initial_stock": 5,
        },
        content_type="application/json",
    ).json()

    client.post("/api/v1/auth/logout", content_type="application/json")
    User.objects.create_user(email="buyer@example.com", password="StrongPass123!")
    client.post(
        "/api/v1/auth/login",
        {"email": "buyer@example.com", "password": "StrongPass123!"},
        content_type="application/json",
    )

    cart = client.put(
        f"/api/v1/cart/items/{product['id']}",
        {"quantity": 1},
        content_type="application/json",
    ).json()
    order = client.post(
        "/api/v1/orders",
        {"cart_id": cart["id"]},
        content_type="application/json",
        HTTP_IDEMPOTENCY_KEY="manual-key",
    ).json()

    client.post("/api/v1/auth/logout", content_type="application/json")
    client.post(
        "/api/v1/auth/login",
        {"email": "seller@example.com", "password": "StrongPass123!"},
        content_type="application/json",
    )

    response = client.post(
        f"/api/v1/seller/orders/{order['id']}/confirm-payment",
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.json()["status"] == "succeeded"
    assert response.json()["order_status"] == "PAID"

    duplicate = client.post(
        f"/api/v1/seller/orders/{order['id']}/confirm-payment",
        content_type="application/json",
    )
    assert duplicate.status_code == 200
    assert duplicate.json()["status"] == "duplicate"
