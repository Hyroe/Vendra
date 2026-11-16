from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.orders.models import Order, OrderStatus, PaymentAttempt, PaymentStatus


class Command(BaseCommand):
    help = "Report payment/order reconciliation issues without mutating financial state."

    def add_arguments(self, parser):
        parser.add_argument(
            "--older-than",
            type=int,
            default=15,
            help="Age in minutes for expired pending orders.",
        )

    def handle(self, *args, **options):
        older_than = options["older_than"]
        cutoff = timezone.now() - timedelta(minutes=older_than)

        late_successes = PaymentAttempt.objects.filter(
            status=PaymentStatus.SUCCEEDED,
        ).exclude(order__status=OrderStatus.PAID)

        missing_successes = Order.objects.filter(
            status=OrderStatus.PAID,
        ).exclude(payment_attempts__status=PaymentStatus.SUCCEEDED)

        inconsistent_failures = PaymentAttempt.objects.filter(
            status=PaymentStatus.FAILED,
            order__status=OrderStatus.PAID,
        )

        expired_pending = Order.objects.filter(
            status=OrderStatus.PAYMENT_PENDING,
            created_at__lt=cutoff,
        )

        self.stdout.write("Payment reconciliation report")
        self.stdout.write(f"Expired pending threshold: {older_than} minutes")
        self.stdout.write("")

        self._write_section(
            "Late successes (attempt succeeded, order not PAID)",
            late_successes,
            lambda x: f"{x.id} order={x.order_id}",
        )
        self._write_section(
            "Paid orders without succeeded attempt",
            missing_successes,
            lambda x: f"{x.id} store={x.store_id}",
        )
        self._write_section(
            "Failed attempts for PAID orders",
            inconsistent_failures,
            lambda x: f"{x.id} order={x.order_id}",
        )
        self._write_section(
            "Expired pending orders",
            expired_pending,
            lambda x: f"{x.id} created={x.created_at.isoformat()}",
        )

        total = (
            late_successes.count()
            + missing_successes.count()
            + inconsistent_failures.count()
            + expired_pending.count()
        )
        self.stdout.write("")
        self.stdout.write(f"Total issues: {total}")
        if total:
            self.stdout.write(
                self.style.WARNING(
                    "Review these records manually. This command does not mutate state."
                )
            )

    def _write_section(self, title, queryset, formatter):
        count = queryset.count()
        self.stdout.write(f"{title}: {count}")
        for item in queryset[:50]:
            self.stdout.write(f"  - {formatter(item)}")
        if count > 50:
            self.stdout.write(f"  ... {count - 50} more")
