import pytest

from apps.catalog.models import Product
from apps.catalog.services import create_product
from apps.stores.services import create_store


@pytest.mark.django_db
def test_product_and_inventory_are_persisted(user):
    store = create_store(owner=user, name="Persisted Catalog")
    product = create_product(
        store=store, sku="SKU-1", name="Widget", unit_price="9.99", initial_stock=7
    )

    assert Product.objects.filter(pk=product.pk).exists()
    assert product.inventory.on_hand == 7
