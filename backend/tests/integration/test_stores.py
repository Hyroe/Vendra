import pytest

from apps.stores.models import Store, StoreMembership
from apps.stores.services import create_store


@pytest.mark.django_db
def test_store_and_membership_are_persisted(user):
    store = create_store(owner=user, name="Persisted Shop")

    assert Store.objects.filter(pk=store.pk).exists()
    assert StoreMembership.objects.filter(
        user=user, store=store, role="OWNER", active=True
    ).exists()
