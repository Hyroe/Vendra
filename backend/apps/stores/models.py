import uuid

from django.conf import settings
from django.db import models


class StoreStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    INACTIVE = "INACTIVE", "Inactive"


class StoreCurrency(models.TextChoices):
    USD = "USD", "USD"
    EUR = "EUR", "EUR"
    GBP = "GBP", "GBP"


class StoreVerificationStatus(models.TextChoices):
    UNVERIFIED = "UNVERIFIED", "Unverified"
    PENDING = "PENDING", "Pending"
    VERIFIED = "VERIFIED", "Verified"
    REJECTED = "REJECTED", "Rejected"


class StoreMembershipRole(models.TextChoices):
    OWNER = "OWNER", "Owner"
    MANAGER = "MANAGER", "Manager"
    STAFF = "STAFF", "Staff"


class Store(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True)
    currency = models.CharField(
        max_length=3,
        choices=StoreCurrency.choices,
        default=StoreCurrency.USD,
    )
    status = models.CharField(
        max_length=16,
        choices=StoreStatus.choices,
        default=StoreStatus.ACTIVE,
    )
    verification_status = models.CharField(
        max_length=16,
        choices=StoreVerificationStatus.choices,
        default=StoreVerificationStatus.UNVERIFIED,
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_stores",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="owned_stores",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "stores_store"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class StoreMembership(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="store_memberships",
    )
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    role = models.CharField(
        max_length=16,
        choices=StoreMembershipRole.choices,
        default=StoreMembershipRole.OWNER,
    )
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "stores_membership"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "store"],
                name="stores_membership_user_store_unique",
            ),
        ]
        indexes = [
            models.Index(fields=["store", "role"]),
        ]

    def __str__(self) -> str:
        return f"{self.user_id}:{self.store_id}:{self.role}"


class ShippingOption(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name="shipping_options",
    )
    code = models.CharField(max_length=64)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    active = models.BooleanField(default=True)
    estimated_days = models.PositiveSmallIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "stores_shipping_option"
        constraints = [
            models.UniqueConstraint(
                fields=["store", "code"],
                name="stores_shipping_option_store_code_unique",
            ),
            models.CheckConstraint(
                condition=models.Q(price__gte=0),
                name="stores_shipping_option_price_nonnegative",
            ),
        ]
        ordering = ["price", "name"]

    def __str__(self) -> str:
        return f"{self.store_id}:{self.code}"
