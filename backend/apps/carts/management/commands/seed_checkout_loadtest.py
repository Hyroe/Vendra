import json
from pathlib import Path

from django.core.management.base import BaseCommand

from apps.accounts.models import User
from apps.carts.models import Cart
from apps.carts.services import add_item
from apps.catalog.services import create_product
from apps.orders.models import Order, PaymentAttempt
from apps.stores.services import create_store


class Command(BaseCommand):
    help = "Seed buyers, carts and a product for checkout load testing."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=100)
        parser.add_argument("--output", default="performance/fixtures/carts.json")
        parser.add_argument("--password", default="LoadTest123!")

    def handle(self, *args, **options):
        count = options["count"]
        output = Path(options["output"])
        password = options["password"]

        PaymentAttempt.objects.filter(order__customer__email__startswith="loadtest-").delete()
        Order.objects.filter(customer__email__startswith="loadtest-").delete()
        Cart.objects.filter(customer__email__startswith="loadtest-").delete()
        from apps.catalog.models import Product

        Product.objects.filter(store__owner__email__startswith="loadtest-").delete()
        from apps.stores.models import Store

        Store.objects.filter(owner__email__startswith="loadtest-").delete()
        User.objects.filter(email__startswith="loadtest-").delete()

        seller = User.objects.create_user(email="loadtest-seller@example.com", password=password)
        store = create_store(owner=seller, name="Load Test Shop")
        product = create_product(
            store=store,
            sku="LOAD-1",
            name="Load Test Widget",
            unit_price="9.99",
            is_published=True,
            initial_stock=count,
        )

        fixtures = []
        for index in range(count):
            buyer = User.objects.create_user(
                email=f"loadtest-buyer-{index}@example.com",
                password=password,
            )
            cart = add_item(customer=buyer, product=product, quantity=1)
            fixtures.append(
                {
                    "email": buyer.email,
                    "password": password,
                    "cart_id": str(cart.id),
                }
            )

        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(fixtures, indent=2))
        self.stdout.write(f"Seeded {count} checkout fixtures in {output}")
