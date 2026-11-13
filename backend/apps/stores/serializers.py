from rest_framework import serializers

from .models import Store, StoreStatus


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
    class Meta:
        model = Store
        fields = ["name", "currency", "status"]

    def validate_currency(self, value):
        value = value.upper()
        if len(value) != 3 or not value.isalpha():
            raise serializers.ValidationError("Currency must be a 3-letter ISO code.")
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
        if len(value) != 3 or not value.isalpha():
            raise serializers.ValidationError("Currency must be a 3-letter ISO code.")
        return value

    def validate_status(self, value):
        if value not in {StoreStatus.ACTIVE, StoreStatus.INACTIVE}:
            raise serializers.ValidationError("Invalid store status.")
        return value
