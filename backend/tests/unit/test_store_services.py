import pytest

from apps.accounts.models import User
from apps.stores.services import create_store


@pytest.mark.django_db
def test_store_slug_is_unique_for_duplicate_names(db):
    owner = User.objects.create_user(email="owner@example.com", password="StrongPass123!")

    first = create_store(owner=owner, name="Corner Shop")
    second = create_store(owner=owner, name="Corner Shop")

    assert first.slug == "corner-shop"
    assert second.slug == "corner-shop-2"
