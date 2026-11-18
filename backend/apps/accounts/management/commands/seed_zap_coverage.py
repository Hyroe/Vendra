import json
from pathlib import Path

from django.core.management.base import BaseCommand

from apps.accounts.models import User
from apps.carts.services import add_item
from apps.catalog.services import create_product
from apps.stores.services import create_store


class Command(BaseCommand):
    help = "Seed API coverage fixtures for OWASP ZAP authenticated scanning."

    def add_arguments(self, parser):
        parser.add_argument("--output", default="performance/fixtures/zap.json")

    def handle(self, *args, **options):
        output = Path(options["output"])

        User.objects.filter(email__startswith="zap-").delete()

        seller = User.objects.create_user(email="zap-seller@example.com", password="StrongPass123!")
        store = create_store(owner=seller, name="ZAP Coverage Shop")
        product = create_product(
            store=store,
            sku="ZAP-1",
            name="ZAP Coverage Widget",
            unit_price="9.99",
            is_published=True,
            initial_stock=50,
        )

        customer = User.objects.create_user(
            email="zap-customer@example.com", password="StrongPass123!"
        )
        cart = add_item(customer=customer, product=product, quantity=1)

        courier = User.objects.create_user(
            email="zap-courier@example.com", password="StrongPass123!"
        )

        other_seller = User.objects.create_user(
            email="zap-other-seller@example.com", password="StrongPass123!"
        )

        payload = {
            "seller": {
                "email": seller.email,
                "password": "StrongPass123!",
                "store_id": str(store.id),
            },
            "customer": {
                "email": customer.email,
                "password": "StrongPass123!",
                "cart_id": str(cart.id),
            },
            "courier": {"email": courier.email, "password": "StrongPass123!"},
            "other_seller": {"email": other_seller.email, "password": "StrongPass123!"},
            "product_id": str(product.id),
        }

        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, indent=2))
        self.stdout.write(f"Seeded ZAP coverage fixtures in {output}")
