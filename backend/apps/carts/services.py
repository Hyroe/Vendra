from django.db import transaction

from .models import Cart, CartItem


class CartStoreMismatch(Exception):
    pass


class EmptyCart(Exception):
    pass


def get_active_cart(*, customer):
    return Cart.objects.filter(customer=customer).order_by("-updated_at").first()


def get_or_create_cart_for_product(*, customer, product):
    store = product.store
    existing = Cart.objects.filter(customer=customer).exclude(store=store).first()
    if existing is not None and existing.items.exists():
        raise CartStoreMismatch("Cart already contains items from another store.")
    cart, _ = Cart.objects.get_or_create(customer=customer, store=store)
    return cart


def add_item(*, customer, product, quantity):
    if quantity <= 0:
        remove_item(customer=customer, product=product)
        return get_active_cart(customer=customer)
    if not product.is_published or product.store.status != "ACTIVE":
        raise ValueError("Product is not available.")
    cart = get_or_create_cart_for_product(customer=customer, product=product)
    with transaction.atomic():
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={"quantity": quantity},
        )
        if not created:
            item.quantity = quantity
            item.save(update_fields=["quantity"])
    cart.save(update_fields=["updated_at"])
    return cart


def remove_item(*, customer, product):
    CartItem.objects.filter(cart__customer=customer, product=product).delete()
    cart = Cart.objects.filter(customer=customer, items__isnull=True).first()
    if cart is not None:
        cart.delete()


def clear_cart(*, cart):
    cart.items.all().delete()
    cart.delete()
