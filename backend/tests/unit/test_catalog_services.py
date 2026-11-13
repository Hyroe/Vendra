import pytest

from apps.accounts.models import User
from apps.catalog.models import Inventory, Product
from apps.catalog.services import adjust_inventory, create_product
from apps.stores.services import create_store


@pytest.mark.django_db
def test_create_product_creates_inventory(db):
    owner = User.objects.create_user(email="owner@example.com", password="StrongPass123!")
    store = create_store(owner=owner, name="Catalog Shop")

    product = create_product(
        store=store,
        sku="SKU-1",
        name="Widget",
        unit_price="9.99",
        initial_stock=5,
    )

    assert Product.objects.filter(pk=product.pk).exists()
    assert Inventory.objects.get(product=product).on_hand == 5
    assert Inventory.objects.get(product=product).reserved == 0


@pytest.mark.django_db
def test_adjust_inventory_rejects_values_below_reserved(db):
    owner = User.objects.create_user(email="owner@example.com", password="StrongPass123!")
    store = create_store(owner=owner, name="Catalog Shop")
    product = create_product(
        store=store, sku="SKU-1", name="Widget", unit_price="9.99", initial_stock=5
    )
    inventory = product.inventory
    inventory.reserved = 3
    inventory.save(update_fields=["reserved"])

    with pytest.raises(ValueError):
        adjust_inventory(product=product, on_hand=2)


@pytest.mark.django_db
def test_inventory_constraint_rejects_reserved_above_on_hand(db):
    from django.db import IntegrityError, transaction

    owner = User.objects.create_user(email="owner@example.com", password="StrongPass123!")
    store = create_store(owner=owner, name="Catalog Shop")
    product = create_product(
        store=store, sku="SKU-1", name="Widget", unit_price="9.99", initial_stock=5
    )
    inventory = product.inventory

    with pytest.raises(IntegrityError), transaction.atomic():
        inventory.on_hand = 1
        inventory.reserved = 3
        inventory.save()
