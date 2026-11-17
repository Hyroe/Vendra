import uuid
from decimal import Decimal

from apps.stores.models import ShippingOption

DEVELOPMENT_DEFAULT_SHIPPING = Decimal("4.00")
DEVELOPMENT_DEFAULT_TAX_RATE = Decimal("0.00")


def resolve_shipping_option(*, store, shipping_option_id="standard"):
    if shipping_option_id and shipping_option_id != "standard":
        try:
            parsed = uuid.UUID(str(shipping_option_id))
        except (ValueError, TypeError, AttributeError):
            parsed = None

        if parsed is not None:
            option = ShippingOption.objects.filter(
                pk=shipping_option_id, store=store, active=True
            ).first()
            if option is not None:
                return option

        option = ShippingOption.objects.filter(
            store=store, code=shipping_option_id, active=True
        ).first()
        if option is not None:
            return option

        return None

    return ShippingOption.objects.filter(store=store, active=True).order_by("price", "name").first()


def shipping_snapshot(option):
    if option is None:
        return {
            "code": "standard",
            "name": "Standard",
            "price": str(DEVELOPMENT_DEFAULT_SHIPPING),
        }
    return {
        "id": str(option.id),
        "code": option.code,
        "name": option.name,
        "price": str(option.price),
    }


def calculate_shipping_total(*, store, shipping_option_id="standard"):
    option = resolve_shipping_option(store=store, shipping_option_id=shipping_option_id)
    if option is not None:
        return option.price, shipping_snapshot(option)
    return DEVELOPMENT_DEFAULT_SHIPPING, shipping_snapshot(None)


def calculate_tax_total(*, store, address_snapshot, subtotal):
    # Development default: zero tax. Replace this function for jurisdiction-aware tax.
    return Decimal("0.00")


def calculate_order_totals(
    *, subtotal, shipping_total, tax_total=None, discount_total=Decimal("0.00")
):
    if tax_total is None:
        tax_total = Decimal("0.00")
    grand_total = subtotal + shipping_total + tax_total - discount_total
    return {
        "subtotal": subtotal,
        "shipping_total": shipping_total,
        "tax_total": tax_total,
        "discount_total": discount_total,
        "grand_total": grand_total,
    }
