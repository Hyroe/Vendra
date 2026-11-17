from rest_framework import serializers

from .models import ShippingOption, Store, StoreCurrency, StoreStatus


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = [
            "id",
            "name",
            "slug",
            "currency",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "slug", "created_at", "updated_at"]


class StoreCreateSerializer(serializers.ModelSerializer):
    currency = serializers.CharField(required=False)

    class Meta:
        model = Store
        fields = ["name", "currency", "status"]

    def validate_currency(self, value):
        value = value.upper()
        if value not in {c.value for c in StoreCurrency}:
            raise serializers.ValidationError(
                f"Currency must be one of {[c.value for c in StoreCurrency]}."
            )
        return value

    def validate_status(self, value):
        if value not in {StoreStatus.ACTIVE, StoreStatus.INACTIVE}:
            raise serializers.ValidationError("Invalid store status.")
        return value


class StoreUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ["name", "currency", "status"]

    def validate_currency(self, value):
        value = value.upper()
        if value not in {c.value for c in StoreCurrency}:
            raise serializers.ValidationError(
                f"Currency must be one of {[c.value for c in StoreCurrency]}."
            )
        return value

    def validate_status(self, value):
        if value not in {StoreStatus.ACTIVE, StoreStatus.INACTIVE}:
            raise serializers.ValidationError("Invalid store status.")
        return value


class ShippingOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingOption
        fields = [
            "id",
            "store",
            "code",
            "name",
            "description",
            "price",
            "active",
            "estimated_days",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "store", "created_at", "updated_at"]

    def validate_code(self, value):
        return value.strip().lower()

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price must be non-negative.")
        return value
