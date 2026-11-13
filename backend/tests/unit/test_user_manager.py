import uuid

import pytest
from django.db import IntegrityError, transaction

from apps.accounts.models import User


@pytest.mark.django_db
def test_create_user_normalizes_email_and_uses_uuid():
    user = User.objects.create_user(
        email="  Customer@Example.COM  ",
        password="correct-password",
    )

    assert user.email == "customer@example.com"
    assert isinstance(user.pk, uuid.UUID)
    assert user.check_password("correct-password")
    assert user.is_active is True
    assert user.is_staff is False
    assert user.is_superuser is False


@pytest.mark.django_db
def test_email_uniqueness_is_enforced():
    User.objects.create_user(email="buyer@example.com", password="correct-password")

    with pytest.raises(IntegrityError), transaction.atomic():
        User.objects.create_user(
            email="buyer@example.com",
            password="another-password",
        )


@pytest.mark.django_db
def test_create_superuser_has_admin_flags():
    user = User.objects.create_superuser(
        email="admin@example.com",
        password="correct-password",
    )

    assert user.is_staff is True
    assert user.is_superuser is True


def test_create_user_rejects_invalid_email():
    with pytest.raises(ValueError):
        User.objects.create_user(email="not-an-email", password="correct-password")


def test_create_user_requires_email():
    with pytest.raises(ValueError):
        User.objects.create_user(email="", password="correct-password")
