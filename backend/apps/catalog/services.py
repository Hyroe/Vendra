from decimal import Decimal

from django.db import transaction

from .models import Inventory, Product


def create_product(
    *,
    store,
    sku: str,
    name: str,
    unit_price: Decimal,
    description: str = "",
    is_published: bool = False,
    initial_stock: int = 0,
) -> Product:
    with transaction.atomic():
        product = Product.objects.create(
            store=store,
            sku=sku,
            name=name,
            unit_price=unit_price,
            description=description,
            is_published=is_published,
        )
        Inventory.objects.create(product=product, on_hand=initial_stock, reserved=0)
    return product


def update_product(*, product: Product, **fields) -> Product:
    for field, value in fields.items():
        setattr(product, field, value)
    product.save()
    return product


def adjust_inventory(*, product: Product, on_hand: int) -> Inventory:
    if on_hand < 0:
        raise ValueError("on_hand must be non-negative.")
    inventory = product.inventory
    if on_hand < inventory.reserved:
        raise ValueError("on_hand cannot be less than reserved stock.")
    inventory.on_hand = on_hand
    inventory.save(update_fields=["on_hand", "updated_at"])
    return inventory
