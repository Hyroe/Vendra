import uuid

import pytest
from django.db import IntegrityError, connection, transaction

from apps.accounts.models import User


@pytest.mark.django_db
def test_user_is_persisted_in_postgres():
    user = User.objects.create_user(
        email="integration@example.com",
        password="correct-password",
    )

    assert User.objects.filter(pk=user.pk).exists()
    assert isinstance(user.pk, uuid.UUID)

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT email FROM accounts_user WHERE id = %s",
            [user.pk],
        )
        row = cursor.fetchone()

    assert row == ("integration@example.com",)


@pytest.mark.django_db
def test_email_uniqueness_is_enforced_by_database():
    User.objects.create_user(email="unique@example.com", password="correct-password")

    with pytest.raises(IntegrityError), transaction.atomic():
        User.objects.create_user(
            email="unique@example.com",
            password="other-password",
        )
