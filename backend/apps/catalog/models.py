import uuid

from django.db import models
from django.db.models import F, Q


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    store = models.ForeignKey(
        "stores.Store",
        on_delete=models.PROTECT,
        related_name="products",
    )
    sku = models.CharField(max_length=64)
    name = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "catalog_product"
        constraints = [
            models.UniqueConstraint(
                fields=["store", "sku"],
                name="catalog_product_store_sku_unique",
            ),
            models.CheckConstraint(
                condition=Q(unit_price__gte=0),
                name="catalog_product_price_nonnegative",
            ),
        ]
        indexes = [
            models.Index(fields=["store", "is_published"]),
        ]

    def __str__(self) -> str:
        return self.name


class Inventory(models.Model):
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="inventory",
    )
    on_hand = models.PositiveIntegerField(default=0)
    reserved = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "catalog_inventory"
        constraints = [
            models.CheckConstraint(
                condition=Q(reserved__lte=F("on_hand")),
                name="catalog_inventory_reserved_le_on_hand",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.product_id}: {self.on_hand}/{self.reserved}"
