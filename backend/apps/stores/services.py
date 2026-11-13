from django.db import transaction
from django.utils.text import slugify

from .models import Store, StoreMembership, StoreMembershipRole, StoreStatus


def _unique_slug(name: str) -> str:
    base = slugify(name) or "store"
    slug = base
    counter = 2
    while Store.objects.filter(slug=slug).exists():
        slug = f"{base}-{counter}"
        counter += 1
    return slug


def create_store(*, owner, name: str, currency: str = "USD", status: str = StoreStatus.ACTIVE):
    with transaction.atomic():
        store = Store.objects.create(
            name=name,
            slug=_unique_slug(name),
            currency=currency,
            status=status,
            owner=owner,
        )
        StoreMembership.objects.create(
            user=owner,
            store=store,
            role=StoreMembershipRole.OWNER,
            active=True,
        )
    return store


def update_store(*, store: Store, **fields) -> Store:
    for field, value in fields.items():
        setattr(store, field, value)
    store.save()
    return store
