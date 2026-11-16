import uuid

from django.conf import settings
from django.db import models


class DeliveryStatus(models.TextChoices):
    UNASSIGNED = "UNASSIGNED", "Unassigned"
    ASSIGNED = "ASSIGNED", "Assigned"
    PICKED_UP = "PICKED_UP", "Picked up"
    IN_TRANSIT = "IN_TRANSIT", "In transit"
    DELIVERED = "DELIVERED", "Delivered"
    FAILED = "FAILED", "Failed"
    CANCELLED = "CANCELLED", "Cancelled"


class Delivery(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField(
        "orders.Order",
        on_delete=models.PROTECT,
        related_name="delivery",
    )
    courier = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deliveries",
    )
    status = models.CharField(
        max_length=16,
        choices=DeliveryStatus.choices,
        default=DeliveryStatus.UNASSIGNED,
    )
    assigned_at = models.DateTimeField(null=True, blank=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)
    in_transit_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "logistics_delivery"
        indexes = [
            models.Index(fields=["courier", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.id}:{self.status}"


class DeliveryEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    delivery = models.ForeignKey(
        Delivery,
        on_delete=models.CASCADE,
        related_name="events",
    )
    from_status = models.CharField(max_length=16, choices=DeliveryStatus.choices)
    to_status = models.CharField(max_length=16, choices=DeliveryStatus.choices)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="delivery_events",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "logistics_delivery_event"
        indexes = [
            models.Index(fields=["delivery", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.delivery_id}:{self.from_status}->{self.to_status}"
