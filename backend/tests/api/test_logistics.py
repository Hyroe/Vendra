import pytest


def _login(client, email):
    client.post(
        "/api/v1/auth/login",
        {"email": email, "password": "StrongPass123!"},
        content_type="application/json",
    )


@pytest.mark.django_db
def test_assigned_courier_can_complete_delivery(client):
    from apps.accounts.models import User

    User.objects.create_superuser(email="seller@example.com", password="StrongPass123!")
    _login(client, "seller@example.com")

    store = client.post(
        "/api/v1/seller/stores", {"name": "Logistics Shop"}, content_type="application/json"
    ).json()
    product = client.post(
        f"/api/v1/seller/stores/{store['id']}/products",
        {
            "sku": "LOG-1",
            "name": "Logistics Widget",
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
        HTTP_IDEMPOTENCY_KEY="logistics-key",
    ).json()

    client.post("/api/v1/auth/logout", content_type="application/json")
    _login(client, "seller@example.com")

    client.post(
        f"/api/v1/dev/payments/{order['payment']['attempt_id']}/simulate",
        {"outcome": "succeeded"},
        content_type="application/json",
    )
    client.post(f"/api/v1/seller/orders/{order['id']}/accept", content_type="application/json")
    client.post(f"/api/v1/seller/orders/{order['id']}/prepare", content_type="application/json")
    client.post(f"/api/v1/seller/orders/{order['id']}/ready", content_type="application/json")

    User.objects.create_user(email="courier@example.com", password="StrongPass123!")
    courier_login = client.post(
        "/api/v1/auth/login",
        {"email": "courier@example.com", "password": "StrongPass123!"},
        content_type="application/json",
    )
    courier_id = courier_login.json()["id"]

    client.post("/api/v1/auth/logout", content_type="application/json")
    _login(client, "seller@example.com")

    assign = client.post(
        f"/api/v1/seller/orders/{order['id']}/assign-courier",
        {"courier_id": courier_id},
        content_type="application/json",
    )
    assert assign.status_code == 201
    delivery_id = assign.json()["id"]

    client.post("/api/v1/auth/logout", content_type="application/json")
    _login(client, "courier@example.com")

    pickup = client.post(
        f"/api/v1/courier/deliveries/{delivery_id}/pickup", content_type="application/json"
    )
    assert pickup.status_code == 200
    assert pickup.json()["status"] == "PICKED_UP"

    transit = client.post(
        f"/api/v1/courier/deliveries/{delivery_id}/in-transit", content_type="application/json"
    )
    assert transit.status_code == 200
    assert transit.json()["status"] == "IN_TRANSIT"

    complete = client.post(
        f"/api/v1/courier/deliveries/{delivery_id}/complete", content_type="application/json"
    )
    assert complete.status_code == 200
    assert complete.json()["status"] == "DELIVERED"


@pytest.mark.django_db
def test_unrelated_courier_cannot_update_delivery(client):
    from apps.accounts.models import User

    User.objects.create_superuser(email="seller@example.com", password="StrongPass123!")
    _login(client, "seller@example.com")

    store = client.post(
        "/api/v1/seller/stores", {"name": "Logistics Shop"}, content_type="application/json"
    ).json()
    product = client.post(
        f"/api/v1/seller/stores/{store['id']}/products",
        {
            "sku": "LOG-1",
            "name": "Logistics Widget",
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
        HTTP_IDEMPOTENCY_KEY="logistics-cross",
    ).json()

    client.post("/api/v1/auth/logout", content_type="application/json")
    _login(client, "seller@example.com")

    client.post(
        f"/api/v1/dev/payments/{order['payment']['attempt_id']}/simulate",
        {"outcome": "succeeded"},
        content_type="application/json",
    )
    client.post(f"/api/v1/seller/orders/{order['id']}/accept", content_type="application/json")
    client.post(f"/api/v1/seller/orders/{order['id']}/prepare", content_type="application/json")
    client.post(f"/api/v1/seller/orders/{order['id']}/ready", content_type="application/json")

    User.objects.create_user(email="courier-a@example.com", password="StrongPass123!")
    User.objects.create_user(email="courier-b@example.com", password="StrongPass123!")

    client.post("/api/v1/auth/logout", content_type="application/json")
    _login(client, "courier-a@example.com")
    courier_a_id = client.get("/api/v1/me").json()["id"]
    client.post("/api/v1/auth/logout", content_type="application/json")

    _login(client, "seller@example.com")
    assign = client.post(
        f"/api/v1/seller/orders/{order['id']}/assign-courier",
        {"courier_id": courier_a_id},
        content_type="application/json",
    ).json()
    delivery_id = assign["id"]

    client.post("/api/v1/auth/logout", content_type="application/json")
    _login(client, "courier-b@example.com")

    response = client.post(
        f"/api/v1/courier/deliveries/{delivery_id}/pickup", content_type="application/json"
    )
    assert response.status_code == 404
