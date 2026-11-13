import uuid

from django.db import models


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="carts",
    )
    store = models.ForeignKey(
        "stores.Store",
        on_delete=models.PROTECT,
        related_name="carts",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "carts_cart"
        constraints = [
            models.UniqueConstraint(
                fields=["customer", "store"],
                name="carts_cart_customer_store_unique",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.customer_id}:{self.store_id}"


class CartItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.PROTECT,
        related_name="cart_items",
    )
    quantity = models.PositiveIntegerField()

    class Meta:
        db_table = "carts_cart_item"
        constraints = [
            models.UniqueConstraint(
                fields=["cart", "product"],
                name="carts_cart_item_cart_product_unique",
            ),
            models.CheckConstraint(
                condition=models.Q(quantity__gt=0),
                name="carts_cart_item_quantity_positive",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.cart_id}:{self.product_id}:{self.quantity}"
