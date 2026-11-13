import uuid

from django.conf import settings
from django.db import models


class OrderStatus(models.TextChoices):
    CREATED = "CREATED", "Created"
    PAYMENT_PENDING = "PAYMENT_PENDING", "Payment pending"
    PAID = "PAID", "Paid"
    ACCEPTED = "ACCEPTED", "Accepted"
    PREPARING = "PREPARING", "Preparing"
    READY_FOR_PICKUP = "READY_FOR_PICKUP", "Ready for pickup"
    PAYMENT_FAILED = "PAYMENT_FAILED", "Payment failed"
    CANCELLED = "CANCELLED", "Cancelled"


class ReservationStatus(models.TextChoices):
    RESERVED = "RESERVED", "Reserved"
    COMMITTED = "COMMITTED", "Committed"
    RELEASED = "RELEASED", "Released"


class PaymentStatus(models.TextChoices):
    INITIATED = "INITIATED", "Initiated"
    PENDING = "PENDING", "Pending"
    SUCCEEDED = "SUCCEEDED", "Succeeded"
    FAILED = "FAILED", "Failed"
    CANCELLED = "CANCELLED", "Cancelled"


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders",
    )
    store = models.ForeignKey(
        "stores.Store",
        on_delete=models.PROTECT,
        related_name="orders",
    )
    currency = models.CharField(max_length=3)
    status = models.CharField(
        max_length=32,
        choices=OrderStatus.choices,
        default=OrderStatus.CREATED,
    )
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    shipping_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2)
    address_snapshot = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "orders_order"
        indexes = [
            models.Index(fields=["customer", "created_at"]),
            models.Index(fields=["store", "status", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.id}:{self.status}"


class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.PROTECT,
        related_name="order_items",
        null=True,
        blank=True,
    )
    sku_snapshot = models.CharField(max_length=64)
    title_snapshot = models.CharField(max_length=160)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField()
    line_total = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = "orders_order_item"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(quantity__gt=0),
                name="orders_order_item_quantity_positive",
            ),
            models.CheckConstraint(
                condition=models.Q(unit_price__gte=0),
                name="orders_order_item_price_nonnegative",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.order_id}:{self.sku_snapshot}"


class InventoryReservation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_item = models.OneToOneField(
        OrderItem,
        on_delete=models.CASCADE,
        related_name="reservation",
    )
    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.PROTECT,
        related_name="inventory_reservations",
    )
    quantity = models.PositiveIntegerField()
    status = models.CharField(
        max_length=16,
        choices=ReservationStatus.choices,
        default=ReservationStatus.RESERVED,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "orders_inventory_reservation"

    def __str__(self) -> str:
        return f"{self.order_item_id}:{self.status}"


class PaymentAttempt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name="payment_attempts",
    )
    provider = models.CharField(max_length=64)
    provider_ref = models.CharField(max_length=128, unique=True)
    status = models.CharField(
        max_length=16,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3)
    idempotency_key = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "orders_payment_attempt"
        indexes = [
            models.Index(fields=["order", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.id}:{self.status}"


class OrderTransition(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="transitions",
    )
    from_status = models.CharField(max_length=32, choices=OrderStatus.choices)
    to_status = models.CharField(max_length=32, choices=OrderStatus.choices)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_transitions",
    )
    reason = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "orders_order_transition"
        indexes = [
            models.Index(fields=["order", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.order_id}:{self.from_status}->{self.to_status}"


class ApiIdempotencyKey(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="idempotency_keys",
    )
    scope = models.CharField(max_length=64)
    key = models.CharField(max_length=255)
    request_hash = models.CharField(max_length=64)
    status = models.CharField(max_length=16, default="PROCESSING")
    response_status = models.PositiveSmallIntegerField(null=True, blank=True)
    response_body = models.JSONField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "orders_api_idempotency_key"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "scope", "key"],
                name="orders_api_idempotency_user_scope_key_unique",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user_id}:{self.scope}:{self.key}"
