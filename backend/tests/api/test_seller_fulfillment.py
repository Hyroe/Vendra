import pytest


def _login(client, email):
    client.post(
        "/api/v1/auth/login",
        {"email": email, "password": "StrongPass123!"},
        content_type="application/json",
    )


@pytest.mark.django_db
def test_seller_can_fulfill_paid_order(client):
    from apps.accounts.models import User

    User.objects.create_superuser(email="seller@example.com", password="StrongPass123!")
    _login(client, "seller@example.com")

    store = client.post(
        "/api/v1/seller/stores", {"name": "Fulfillment Shop"}, content_type="application/json"
    ).json()
    product = client.post(
        f"/api/v1/seller/stores/{store['id']}/products",
        {
            "sku": "FUL-1",
            "name": "Fulfillable Widget",
            "unit_price": "9.99",
            "is_published": True,
            "initial_stock": 5,
        },
        content_type="application/json",
    ).json()

    client.post("/api/v1/auth/logout", content_type="application/json")
    User.objects.create_user(email="buyer@example.com", password="StrongPass123!")
    _login(client, "buyer@example.com")

    cart = client.put(
        f"/api/v1/cart/items/{product['id']}",
        {"quantity": 1},
        content_type="application/json",
    ).json()
    order = client.post(
        "/api/v1/orders",
        {"cart_id": cart["id"]},
        content_type="application/json",
        HTTP_IDEMPOTENCY_KEY="fulfill-key",
    ).json()

    # Simulate successful payment as staff.
    client.post("/api/v1/auth/logout", content_type="application/json")
    _login(client, "seller@example.com")
    client.post(
        f"/api/v1/dev/payments/{order['payment']['attempt_id']}/simulate",
        {"outcome": "succeeded"},
        content_type="application/json",
    )

    accept = client.post(
        f"/api/v1/seller/orders/{order['id']}/accept", content_type="application/json"
    )
    assert accept.status_code == 200
    assert accept.json()["status"] == "ACCEPTED"

    prepare = client.post(
        f"/api/v1/seller/orders/{order['id']}/prepare", content_type="application/json"
    )
    assert prepare.status_code == 200
    assert prepare.json()["status"] == "PREPARING"

    ready = client.post(
        f"/api/v1/seller/orders/{order['id']}/ready", content_type="application/json"
    )
    assert ready.status_code == 200
    assert ready.json()["status"] == "READY_FOR_PICKUP"


@pytest.mark.django_db
def test_invalid_order_transition_returns_conflict(client):
    from apps.accounts.models import User

    User.objects.create_superuser(email="seller@example.com", password="StrongPass123!")
    _login(client, "seller@example.com")

    store = client.post(
        "/api/v1/seller/stores", {"name": "Fulfillment Shop"}, content_type="application/json"
    ).json()
    product = client.post(
        f"/api/v1/seller/stores/{store['id']}/products",
        {
            "sku": "FUL-1",
            "name": "Fulfillable Widget",
            "unit_price": "9.99",
            "is_published": True,
            "initial_stock": 5,
        },
        content_type="application/json",
    ).json()

    client.post("/api/v1/auth/logout", content_type="application/json")
    User.objects.create_user(email="buyer@example.com", password="StrongPass123!")
    _login(client, "buyer@example.com")

    cart = client.put(
        f"/api/v1/cart/items/{product['id']}",
        {"quantity": 1},
        content_type="application/json",
    ).json()
    order = client.post(
        "/api/v1/orders",
        {"cart_id": cart["id"]},
        content_type="application/json",
        HTTP_IDEMPOTENCY_KEY="invalid-transition",
    ).json()

    # Order is PAYMENT_PENDING; accepting should fail.
    client.post("/api/v1/auth/logout", content_type="application/json")
    _login(client, "seller@example.com")
    response = client.post(
        f"/api/v1/seller/orders/{order['id']}/accept", content_type="application/json"
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "ORDER_CONFLICT"


@pytest.mark.django_db
def test_seller_cannot_fulfill_another_sellers_order(client):
    from apps.accounts.models import User

    User.objects.create_superuser(email="seller-a@example.com", password="StrongPass123!")
    _login(client, "seller-a@example.com")
    store = client.post(
        "/api/v1/seller/stores", {"name": "Seller A Shop"}, content_type="application/json"
    ).json()
    product = client.post(
        f"/api/v1/seller/stores/{store['id']}/products",
        {
            "sku": "FUL-1",
            "name": "Fulfillable Widget",
            "unit_price": "9.99",
            "is_published": True,
            "initial_stock": 5,
        },
        content_type="application/json",
    ).json()

    client.post("/api/v1/auth/logout", content_type="application/json")
    User.objects.create_user(email="buyer@example.com", password="StrongPass123!")
    _login(client, "buyer@example.com")
    cart = client.put(
        f"/api/v1/cart/items/{product['id']}",
        {"quantity": 1},
        content_type="application/json",
    ).json()
    order = client.post(
        "/api/v1/orders",
        {"cart_id": cart["id"]},
        content_type="application/json",
        HTTP_IDEMPOTENCY_KEY="cross-seller",
    ).json()

    client.post("/api/v1/auth/logout", content_type="application/json")
    User.objects.create_superuser(email="seller-b@example.com", password="StrongPass123!")
    _login(client, "seller-b@example.com")

    response = client.post(
        f"/api/v1/seller/orders/{order['id']}/accept", content_type="application/json"
    )
    assert response.status_code == 404
