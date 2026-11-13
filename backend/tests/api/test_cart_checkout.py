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


def _setup_store_and_product(client, stock=5):
    _register_and_login(client, "seller@example.com")
    store = client.post(
        "/api/v1/seller/stores",
        {"name": "Order Shop"},
        content_type="application/json",
    ).json()
    product = client.post(
        f"/api/v1/seller/stores/{store['id']}/products",
        {
            "sku": "SKU-1",
            "name": "Widget",
            "unit_price": "9.99",
            "is_published": True,
            "initial_stock": stock,
        },
        content_type="application/json",
    ).json()
    client.post("/api/v1/auth/logout", content_type="application/json")
    return store, product


@pytest.mark.django_db
def test_cart_add_and_checkout_creates_pending_order(client):
    store, product = _setup_store_and_product(client, stock=5)
    _register_and_login(client, "buyer@example.com")

    add = client.put(
        f"/api/v1/cart/items/{product['id']}",
        {"quantity": 2},
        content_type="application/json",
    )
    assert add.status_code == 200

    response = client.post(
        "/api/v1/orders",
        {"cart_id": add.json()["id"]},
        content_type="application/json",
        HTTP_IDEMPOTENCY_KEY="checkout-key-1",
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["status"] == "PAYMENT_PENDING"
    assert payload["totals"]["subtotal"] == "19.98"
    assert payload["totals"]["shipping"] == "4.00"
    assert payload["totals"]["grand_total"] == "23.98"
    assert payload["payment"]["status"] == "PENDING"

    # Cart is cleared after checkout.
    cart = client.get("/api/v1/cart")
    assert cart.json()["items"] == []


@pytest.mark.django_db
def test_checkout_is_idempotent_for_same_key_and_payload(client):
    store, product = _setup_store_and_product(client, stock=5)
    _register_and_login(client, "buyer@example.com")

    cart = client.put(
        f"/api/v1/cart/items/{product['id']}",
        {"quantity": 2},
        content_type="application/json",
    ).json()

    first = client.post(
        "/api/v1/orders",
        {"cart_id": cart["id"]},
        content_type="application/json",
        HTTP_IDEMPOTENCY_KEY="same-key",
    )
    second = client.post(
        "/api/v1/orders",
        {"cart_id": cart["id"]},
        content_type="application/json",
        HTTP_IDEMPOTENCY_KEY="same-key",
    )

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["id"] == second.json()["id"]


@pytest.mark.django_db
def test_checkout_rejects_changed_payload_for_same_key(client):
    store, product = _setup_store_and_product(client, stock=5)
    _register_and_login(client, "buyer@example.com")

    cart = client.put(
        f"/api/v1/cart/items/{product['id']}",
        {"quantity": 2},
        content_type="application/json",
    ).json()

    first = client.post(
        "/api/v1/orders",
        {"cart_id": cart["id"]},
        content_type="application/json",
        HTTP_IDEMPOTENCY_KEY="conflict-key",
    )
    assert first.status_code == 201

    # Re-create a cart for a second attempt with same key but different cart id.
    second_cart = client.put(
        f"/api/v1/cart/items/{product['id']}",
        {"quantity": 1},
        content_type="application/json",
    ).json()

    second = client.post(
        "/api/v1/orders",
        {"cart_id": second_cart["id"]},
        content_type="application/json",
        HTTP_IDEMPOTENCY_KEY="conflict-key",
    )

    assert second.status_code == 409
    assert second.json()["error"]["code"] == "IDEMPOTENCY_CONFLICT"


@pytest.mark.django_db
def test_checkout_requires_idempotency_key(client):
    store, product = _setup_store_and_product(client, stock=5)
    _register_and_login(client, "buyer@example.com")

    cart = client.put(
        f"/api/v1/cart/items/{product['id']}",
        {"quantity": 1},
        content_type="application/json",
    ).json()

    response = client.post(
        "/api/v1/orders",
        {"cart_id": cart["id"]},
        content_type="application/json",
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "IDEMPOTENCY_KEY_REQUIRED"


@pytest.mark.django_db
def test_checkout_rejects_insufficient_stock(client):
    store, product = _setup_store_and_product(client, stock=1)
    _register_and_login(client, "buyer@example.com")

    cart = client.put(
        f"/api/v1/cart/items/{product['id']}",
        {"quantity": 2},
        content_type="application/json",
    ).json()

    response = client.post(
        "/api/v1/orders",
        {"cart_id": cart["id"]},
        content_type="application/json",
        HTTP_IDEMPOTENCY_KEY="stock-key",
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "INSUFFICIENT_STOCK"


@pytest.mark.django_db
def test_two_customers_cannot_oversell_last_unit(client):
    store, product = _setup_store_and_product(client, stock=1)

    # Buyer A
    _register_and_login(client, "buyer-a@example.com")
    cart_a = client.put(
        f"/api/v1/cart/items/{product['id']}",
        {"quantity": 1},
        content_type="application/json",
    ).json()
    client.post("/api/v1/auth/logout", content_type="application/json")

    # Buyer B
    _register_and_login(client, "buyer-b@example.com")
    cart_b = client.put(
        f"/api/v1/cart/items/{product['id']}",
        {"quantity": 1},
        content_type="application/json",
    ).json()

    # Both attempt checkout; exactly one should succeed.
    client.post("/api/v1/auth/logout", content_type="application/json")
    _register_and_login(client, "buyer-a@example.com")
    response_a = client.post(
        "/api/v1/orders",
        {"cart_id": cart_a["id"]},
        content_type="application/json",
        HTTP_IDEMPOTENCY_KEY="race-a",
    )

    client.post("/api/v1/auth/logout", content_type="application/json")
    _register_and_login(client, "buyer-b@example.com")
    response_b = client.post(
        "/api/v1/orders",
        {"cart_id": cart_b["id"]},
        content_type="application/json",
        HTTP_IDEMPOTENCY_KEY="race-b",
    )

    statuses = sorted([response_a.status_code, response_b.status_code])
    assert statuses == [201, 409]


@pytest.mark.django_db
def test_customer_can_cancel_pending_order(client):
    store, product = _setup_store_and_product(client, stock=5)
    _register_and_login(client, "buyer@example.com")

    cart = client.put(
        f"/api/v1/cart/items/{product['id']}",
        {"quantity": 2},
        content_type="application/json",
    ).json()

    order = client.post(
        "/api/v1/orders",
        {"cart_id": cart["id"]},
        content_type="application/json",
        HTTP_IDEMPOTENCY_KEY="cancel-key",
    ).json()

    response = client.post(
        f"/api/v1/orders/{order['id']}/cancel",
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.json()["status"] == "CANCELLED"


@pytest.mark.django_db
def test_customer_can_list_and_read_own_orders(client):
    store, product = _setup_store_and_product(client, stock=5)
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
        HTTP_IDEMPOTENCY_KEY="read-key",
    ).json()

    listing = client.get("/api/v1/orders")
    assert listing.status_code == 200
    assert len(listing.json()) == 1

    detail = client.get(f"/api/v1/orders/{order['id']}")
    assert detail.status_code == 200
    assert detail.json()["id"] == order["id"]
    assert len(detail.json()["items"]) == 1
