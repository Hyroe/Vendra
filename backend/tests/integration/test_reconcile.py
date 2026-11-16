from io import StringIO

import pytest
from django.core.management import call_command

from apps.accounts.models import User
from apps.catalog.services import create_product
from apps.orders.models import Order, OrderStatus, PaymentAttempt, PaymentStatus
from apps.stores.services import create_store


@pytest.mark.django_db
def test_reconcile_command_reports_late_success_without_mutation():
    seller = User.objects.create_user(email="seller@example.com", password="StrongPass123!")
    store = create_store(owner=seller, name="Recon Shop")
    create_product(
        store=store,
        sku="R-1",
        name="Recon Widget",
        unit_price="5.00",
        is_published=True,
        initial_stock=1,
    )
    buyer = User.objects.create_user(email="buyer@example.com", password="StrongPass123!")

    order = Order.objects.create(
        customer=buyer,
        store=store,
        currency="USD",
        status=OrderStatus.CANCELLED,
        subtotal="5.00",
        shipping_total="4.00",
        tax_total="0.00",
        discount_total="0.00",
        grand_total="9.00",
    )
    PaymentAttempt.objects.create(
        order=order,
        provider="fake",
        provider_ref="late-1",
        status=PaymentStatus.SUCCEEDED,
        amount="9.00",
        currency="USD",
        idempotency_key="late-1",
    )

    output = StringIO()
    call_command("reconcile_payments", stdout=output)
    rendered = output.getvalue()

    assert "Late successes" in rendered
    assert "Total issues: 1" in rendered
    order.refresh_from_db()
    assert order.status == OrderStatus.CANCELLED
