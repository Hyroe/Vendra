from rest_framework import serializers

from .models import Inventory, Product


class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = ["on_hand", "reserved", "updated_at"]
        read_only_fields = ["reserved", "updated_at"]


class ProductSerializer(serializers.ModelSerializer):
    inventory = InventorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "store",
            "sku",
            "name",
            "description",
            "unit_price",
            "is_published",
            "inventory",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "store", "created_at", "updated_at"]


class ProductCreateSerializer(serializers.ModelSerializer):
    initial_stock = serializers.IntegerField(min_value=0, required=False, default=0)

    class Meta:
        model = Product
        fields = ["sku", "name", "description", "unit_price", "is_published", "initial_stock"]

    def validate_unit_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Unit price must be non-negative.")
        return value


class ProductUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["sku", "name", "description", "unit_price", "is_published"]

    def validate_unit_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Unit price must be non-negative.")
        return value


class InventoryAdjustSerializer(serializers.Serializer):
    on_hand = serializers.IntegerField(min_value=0)
