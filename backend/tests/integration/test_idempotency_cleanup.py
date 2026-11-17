from io import StringIO

import pytest
from django.core.management import call_command
from django.utils import timezone

from apps.accounts.models import User
from apps.orders.models import ApiIdempotencyKey


@pytest.mark.django_db
def test_cleanup_deletes_expired_idempotency_keys():
    user = User.objects.create_user(email="buyer@example.com", password="StrongPass123!")
    expired = ApiIdempotencyKey.objects.create(
        user=user,
        scope="checkout",
        key="expired",
        request_hash="a" * 64,
        status="COMPLETED",
        expires_at=timezone.now() - timezone.timedelta(hours=1),
    )
    active = ApiIdempotencyKey.objects.create(
        user=user,
        scope="checkout",
        key="active",
        request_hash="b" * 64,
        status="COMPLETED",
        expires_at=timezone.now() + timezone.timedelta(hours=1),
    )

    output = StringIO()
    call_command("cleanup_idempotency_keys", "--hours", "1", stdout=output)

    assert "Deleted 1" in output.getvalue()
    assert not ApiIdempotencyKey.objects.filter(pk=expired.pk).exists()
    assert ApiIdempotencyKey.objects.filter(pk=active.pk).exists()
