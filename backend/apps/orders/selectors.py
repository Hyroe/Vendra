from apps.stores.selectors import store_for_user

from .models import Order


def orders_for_customer(*, customer):
    return Order.objects.filter(customer=customer).order_by("-created_at")


def order_for_customer(*, customer, order_id):
    return Order.objects.filter(customer=customer, pk=order_id).first()


def orders_for_store(*, user, store_id):
    store = store_for_user(user=user, store_id=store_id)
    if store is None:
        return None
    return Order.objects.filter(store=store).order_by("-created_at")
