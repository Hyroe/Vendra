import uuid

import pytest

from apps.catalog.models import Inventory
from apps.orders.models import OutboxEvent


def _login(client, email, password="StrongPass123!"):
    client.post(
        "/api/v1/auth/login",
        {"email": email, "password": password},
        content_type="application/json",
    )


@pytest.mark.django_db
def test_fake_payment_success_moves_order_to_paid_once(client):
    # Staff seller creates store/product.
    from apps.accounts.models import User

    User.objects.create_superuser(email="staff@example.com", password="StrongPass123!")
    _login(client, "staff@example.com")

    store = client.post(
        "/api/v1/seller/stores", {"name": "Pay Shop"}, content_type="application/json"
    ).json()
    product = client.post(
        f"/api/v1/seller/stores/{store['id']}/products",
        {
            "sku": "PAY-1",
            "name": "Pay Widget",
            "unit_price": "9.99",
            "is_published": True,
            "initial_stock": 5,
        },
        content_type="application/json",
    ).json()

    # Buyer uses same staff account for simplicity.
    cart = client.put(
        f"/api/v1/cart/items/{product['id']}",
        {"quantity": 2},
        content_type="application/json",
    ).json()
    order = client.post(
        "/api/v1/orders",
        {"cart_id": cart["id"]},
        content_type="application/json",
        HTTP_IDEMPOTENCY_KEY="pay-success",
    ).json()

    attempt_id = order["payment"]["attempt_id"]
    inventory_before = Inventory.objects.get(product_id=product["id"])

    response = client.post(
        f"/api/v1/dev/payments/{attempt_id}/simulate",
        {"outcome": "succeeded", "event_id": "evt-success-1"},
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.json()["status"] == "succeeded"
    assert response.json()["order_status"] == "PAID"

    order_detail = client.get(f"/api/v1/orders/{order['id']}").json()
    assert order_detail["status"] == "PAID"

    inventory_after = Inventory.objects.get(product_id=product["id"])
    assert inventory_after.on_hand == inventory_before.on_hand - 2
    assert inventory_after.reserved == inventory_before.reserved - 2

    assert OutboxEvent.objects.filter(event_type="payment.succeeded.v1").count() == 1


@pytest.mark.django_db
def test_duplicate_payment_event_is_idempotent(client):
    from apps.accounts.models import User

    User.objects.create_superuser(email="staff@example.com", password="StrongPass123!")
    _login(client, "staff@example.com")

    store = client.post(
        "/api/v1/seller/stores", {"name": "Pay Shop"}, content_type="application/json"
    ).json()
    product = client.post(
        f"/api/v1/seller/stores/{store['id']}/products",
        {
            "sku": "PAY-1",
            "name": "Pay Widget",
            "unit_price": "9.99",
            "is_published": True,
            "initial_stock": 5,
        },
        content_type="application/json",
    ).json()

    cart = client.put(
        f"/api/v1/cart/items/{product['id']}",
        {"quantity": 2},
        content_type="application/json",
    ).json()
    order = client.post(
        "/api/v1/orders",
        {"cart_id": cart["id"]},
        content_type="application/json",
        HTTP_IDEMPOTENCY_KEY="pay-dup",
    ).json()

    attempt_id = order["payment"]["attempt_id"]

    first = client.post(
        f"/api/v1/dev/payments/{attempt_id}/simulate",
        {"outcome": "succeeded", "event_id": "evt-dup"},
        content_type="application/json",
    )
    second = client.post(
        f"/api/v1/dev/payments/{attempt_id}/simulate",
        {"outcome": "succeeded", "event_id": "evt-dup"},
        content_type="application/json",
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["status"] == "duplicate"

    assert OutboxEvent.objects.filter(event_type="payment.succeeded.v1").count() == 1


@pytest.mark.django_db
def test_fake_payment_failure_releases_reservation(client):
    from apps.accounts.models import User

    User.objects.create_superuser(email="staff@example.com", password="StrongPass123!")
    _login(client, "staff@example.com")

    store = client.post(
        "/api/v1/seller/stores", {"name": "Pay Shop"}, content_type="application/json"
    ).json()
    product = client.post(
        f"/api/v1/seller/stores/{store['id']}/products",
        {
            "sku": "PAY-1",
            "name": "Pay Widget",
            "unit_price": "9.99",
            "is_published": True,
            "initial_stock": 5,
        },
        content_type="application/json",
    ).json()

    cart = client.put(
        f"/api/v1/cart/items/{product['id']}",
        {"quantity": 2},
        content_type="application/json",
    ).json()
    order = client.post(
        "/api/v1/orders",
        {"cart_id": cart["id"]},
        content_type="application/json",
        HTTP_IDEMPOTENCY_KEY="pay-fail",
    ).json()

    attempt_id = order["payment"]["attempt_id"]
    inventory_before = Inventory.objects.get(product_id=product["id"])

    response = client.post(
        f"/api/v1/dev/payments/{attempt_id}/simulate",
        {"outcome": "failed", "event_id": "evt-fail-1"},
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.json()["status"] == "failed"
    assert response.json()["order_status"] == "PAYMENT_FAILED"

    inventory_after = Inventory.objects.get(product_id=product["id"])
    assert inventory_after.on_hand == inventory_before.on_hand
    assert inventory_after.reserved == inventory_before.reserved - 2

    assert OutboxEvent.objects.filter(event_type="payment.failed.v1").count() == 1


@pytest.mark.django_db
def test_dev_payment_simulation_requires_staff(client):
    from apps.accounts.models import User

    User.objects.create_user(email="buyer@example.com", password="StrongPass123!")
    _login(client, "buyer@example.com")

    response = client.post(
        f"/api/v1/dev/payments/{uuid.uuid4()}/simulate",
        {"outcome": "succeeded"},
        content_type="application/json",
    )

    assert response.status_code == 404
