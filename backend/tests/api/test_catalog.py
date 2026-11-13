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


def _create_store(client, name="Catalog Shop"):
    return client.post(
        "/api/v1/seller/stores",
        {"name": name},
        content_type="application/json",
    ).json()


@pytest.mark.django_db
def test_public_product_list_is_empty_initially(client):
    response = client.get("/api/v1/products")

    assert response.status_code == 200
    assert response.json()["results"] == []


@pytest.mark.django_db
def test_seller_can_create_product(client):
    _register_and_login(client, "seller@example.com")
    store = _create_store(client)

    response = client.post(
        f"/api/v1/seller/stores/{store['id']}/products",
        {
            "sku": "WIDGET-1",
            "name": "Widget",
            "description": "A useful widget",
            "unit_price": "9.99",
            "is_published": True,
            "initial_stock": 5,
        },
        content_type="application/json",
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["sku"] == "WIDGET-1"
    assert payload["is_published"] is True
    assert payload["inventory"]["on_hand"] == 5
    assert payload["inventory"]["reserved"] == 0


@pytest.mark.django_db
def test_product_creation_requires_store_membership(client):
    _register_and_login(client, "seller-a@example.com")
    store = _create_store(client, "Seller A Shop")

    client.post("/api/v1/auth/logout", content_type="application/json")
    _register_and_login(client, "seller-b@example.com")

    response = client.post(
        f"/api/v1/seller/stores/{store['id']}/products",
        {"sku": "WIDGET-1", "name": "Widget", "unit_price": "9.99"},
        content_type="application/json",
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_seller_can_update_own_product(client):
    _register_and_login(client, "seller@example.com")
    store = _create_store(client)
    product = client.post(
        f"/api/v1/seller/stores/{store['id']}/products",
        {"sku": "WIDGET-1", "name": "Widget", "unit_price": "9.99", "is_published": False},
        content_type="application/json",
    ).json()

    response = client.patch(
        f"/api/v1/seller/products/{product['id']}",
        {"name": "Updated Widget", "is_published": True},
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Widget"
    assert response.json()["is_published"] is True


@pytest.mark.django_db
def test_seller_cannot_update_another_sellers_product(client):
    _register_and_login(client, "seller-a@example.com")
    store = _create_store(client, "Seller A Shop")
    product = client.post(
        f"/api/v1/seller/stores/{store['id']}/products",
        {"sku": "WIDGET-1", "name": "Widget", "unit_price": "9.99"},
        content_type="application/json",
    ).json()

    client.post("/api/v1/auth/logout", content_type="application/json")
    _register_and_login(client, "seller-b@example.com")

    response = client.patch(
        f"/api/v1/seller/products/{product['id']}",
        {"name": "Hijacked Widget"},
        content_type="application/json",
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_seller_can_adjust_inventory(client):
    _register_and_login(client, "seller@example.com")
    store = _create_store(client)
    product = client.post(
        f"/api/v1/seller/stores/{store['id']}/products",
        {"sku": "WIDGET-1", "name": "Widget", "unit_price": "9.99", "initial_stock": 5},
        content_type="application/json",
    ).json()

    response = client.put(
        f"/api/v1/seller/products/{product['id']}/inventory",
        {"on_hand": 12},
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.json()["on_hand"] == 12
    assert response.json()["reserved"] == 0


@pytest.mark.django_db
def test_inventory_adjustment_rejects_negative_value(client):
    _register_and_login(client, "seller@example.com")
    store = _create_store(client)
    product = client.post(
        f"/api/v1/seller/stores/{store['id']}/products",
        {"sku": "WIDGET-1", "name": "Widget", "unit_price": "9.99", "initial_stock": 5},
        content_type="application/json",
    ).json()

    response = client.put(
        f"/api/v1/seller/products/{product['id']}/inventory",
        {"on_hand": -1},
        content_type="application/json",
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.django_db
def test_public_list_shows_only_published_products(client):
    _register_and_login(client, "seller@example.com")
    store = _create_store(client)
    client.post(
        f"/api/v1/seller/stores/{store['id']}/products",
        {"sku": "PUB-1", "name": "Published Widget", "unit_price": "9.99", "is_published": True},
        content_type="application/json",
    )
    client.post(
        f"/api/v1/seller/stores/{store['id']}/products",
        {"sku": "DRAFT-1", "name": "Draft Widget", "unit_price": "9.99", "is_published": False},
        content_type="application/json",
    )

    client.post("/api/v1/auth/logout", content_type="application/json")

    response = client.get("/api/v1/products")

    assert response.status_code == 200
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["sku"] == "PUB-1"


@pytest.mark.django_db
def test_public_list_filters_by_store_and_search(client):
    _register_and_login(client, "seller@example.com")
    store = _create_store(client, "Filter Shop")
    client.post(
        f"/api/v1/seller/stores/{store['id']}/products",
        {"sku": "ALPHA-1", "name": "Alpha Widget", "unit_price": "9.99", "is_published": True},
        content_type="application/json",
    )
    client.post(
        f"/api/v1/seller/stores/{store['id']}/products",
        {"sku": "BETA-1", "name": "Beta Gadget", "unit_price": "9.99", "is_published": True},
        content_type="application/json",
    )

    client.post("/api/v1/auth/logout", content_type="application/json")

    by_store = client.get(f"/api/v1/products?store_id={store['id']}")
    assert len(by_store.json()["results"]) == 2

    by_search = client.get("/api/v1/products?search=Alpha")
    assert len(by_search.json()["results"]) == 1
    assert by_search.json()["results"][0]["sku"] == "ALPHA-1"


@pytest.mark.django_db
def test_unpublished_product_is_not_publicly_visible(client):
    _register_and_login(client, "seller@example.com")
    store = _create_store(client)
    product = client.post(
        f"/api/v1/seller/stores/{store['id']}/products",
        {"sku": "DRAFT-1", "name": "Draft Widget", "unit_price": "9.99", "is_published": False},
        content_type="application/json",
    ).json()

    client.post("/api/v1/auth/logout", content_type="application/json")

    response = client.get(f"/api/v1/products/{product['id']}")
    assert response.status_code == 404
