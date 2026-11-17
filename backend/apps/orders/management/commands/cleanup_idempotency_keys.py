from django.core.management.base import BaseCommand
from django.db import models
from django.utils import timezone

from apps.orders.models import ApiIdempotencyKey


class Command(BaseCommand):
    help = "Delete expired API idempotency keys."

    def add_arguments(self, parser):
        parser.add_argument(
            "--hours",
            type=int,
            default=None,
            help="Override retention age in hours.",
        )

    def handle(self, *args, **options):
        from django.conf import settings

        hours = options["hours"]
        if hours is None:
            hours = settings.IDEMPOTENCY_KEY_RETENTION_HOURS

        cutoff = timezone.now() - timezone.timedelta(hours=hours)
        queryset = ApiIdempotencyKey.objects.filter(
            models.Q(expires_at__isnull=False, expires_at__lt=cutoff)
            | models.Q(expires_at__isnull=True, created_at__lt=cutoff)
        )
        count = queryset.count()
        queryset.delete()
        self.stdout.write(f"Deleted {count} expired idempotency keys.")
