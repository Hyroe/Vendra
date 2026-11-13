from django.shortcuts import get_object_or_404

from .models import Store, StoreStatus


def public_stores():
    return Store.objects.filter(status=StoreStatus.ACTIVE).order_by("name")


def public_store_detail(*, store_id):
    return get_object_or_404(Store, pk=store_id, status=StoreStatus.ACTIVE)


def stores_for_user(*, user):
    return Store.objects.filter(memberships__user=user, memberships__active=True).distinct()


def store_for_user(*, user, store_id):
    return stores_for_user(user=user).filter(pk=store_id).first()
