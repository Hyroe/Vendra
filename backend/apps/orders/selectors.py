from apps.stores.selectors import store_for_user

from .models import Order


def orders_for_customer(*, customer):
    return Order.objects.filter(customer=customer).order_by("-created_at")


def order_for_customer(*, customer, order_id):
    return Order.objects.filter(customer=customer, pk=order_id).first()


def orders_for_store(*, user, store_id, status=None):
    store = store_for_user(user=user, store_id=store_id)
    if store is None:
        return None
    queryset = Order.objects.filter(store=store).order_by("-created_at")
    if status is not None:
        queryset = queryset.filter(status=status)
    return queryset


def order_for_store_user(*, user, order_id):
    return (
        Order.objects.filter(
            pk=order_id,
            store__memberships__user=user,
            store__memberships__active=True,
        )
        .select_related("store")
        .first()
    )
