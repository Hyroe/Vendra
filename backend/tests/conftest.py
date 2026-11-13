import pytest

from apps.accounts.models import User


@pytest.fixture
def user(db):
    return User.objects.create_user(email="owner@example.com", password="StrongPass123!")
