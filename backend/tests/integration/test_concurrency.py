from concurrent.futures import ThreadPoolExecutor

from django.db import connection
from django.test import TransactionTestCase

from apps.accounts.models import User
from apps.carts.services import add_item
from apps.catalog.services import create_product
from apps.orders.services import InsufficientStock, checkout
from apps.stores.services import create_store


class CheckoutConcurrencyTests(TransactionTestCase):
    def setUp(self):
        seller = User.objects.create_user(email="seller@example.com", password="StrongPass123!")
        self.store = create_store(owner=seller, name="Race Shop")
        self.product = create_product(
            store=self.store,
            sku="RACE-1",
            name="Race Widget",
            unit_price="9.99",
            is_published=True,
            initial_stock=1,
        )

        self.buyer_a = User.objects.create_user(
            email="buyer-a@example.com", password="StrongPass123!"
        )
        self.buyer_b = User.objects.create_user(
            email="buyer-b@example.com", password="StrongPass123!"
        )

        cart_a = add_item(customer=self.buyer_a, product=self.product, quantity=1)
        cart_b = add_item(customer=self.buyer_b, product=self.product, quantity=1)
        self.cart_a_id = cart_a.id
        self.cart_b_id = cart_b.id
        connection.close()

    def _run(self, buyer, cart_id, key):
        connection.close()
        try:
            checkout(customer=buyer, cart_id=cart_id, idempotency_key=key)
            return "success"
        except InsufficientStock:
            return "insufficient"
        except Exception as exc:  # pragma: no cover - diagnostic
            return f"error:{exc}"
        finally:
            connection.close()

    def test_concurrent_checkout_only_one_succeeds(self):
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_a = executor.submit(self._run, self.buyer_a, self.cart_a_id, "race-a")
            future_b = executor.submit(self._run, self.buyer_b, self.cart_b_id, "race-b")
            results = [future_a.result(), future_b.result()]

        self.assertEqual(sorted(results), ["insufficient", "success"])
