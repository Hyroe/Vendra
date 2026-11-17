from decimal import Decimal

import pytest

from apps.accounts.models import User
from apps.orders.pricing import (
    DEVELOPMENT_DEFAULT_SHIPPING,
    calculate_order_totals,
    calculate_shipping_total,
    calculate_tax_total,
)
from apps.stores.services import create_store


@pytest.mark.django_db
def test_default_shipping_fallback():
    owner = User.objects.create_user(email="owner@example.com", password="StrongPass123!")
    store = create_store(owner=owner, name="Pricing Shop")

    shipping_total, snapshot = calculate_shipping_total(store=store, shipping_option_id="standard")

    assert shipping_total == DEVELOPMENT_DEFAULT_SHIPPING
    assert snapshot["code"] == "standard"
    assert snapshot["price"] == "4.00"


@pytest.mark.django_db
def test_tax_defaults_to_zero():
    owner = User.objects.create_user(email="owner@example.com", password="StrongPass123!")
    store = create_store(owner=owner, name="Pricing Shop")

    tax = calculate_tax_total(store=store, address_snapshot={}, subtotal=Decimal("10.00"))

    assert tax == Decimal("0.00")


def test_order_totals():
    totals = calculate_order_totals(
        subtotal=Decimal("19.98"),
        shipping_total=Decimal("9.50"),
        tax_total=Decimal("0.00"),
    )

    assert totals["grand_total"] == Decimal("29.48")
