from decimal import Decimal

from rest_framework import serializers

from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.UUIDField(source="product.id", read_only=True)
    sku = serializers.CharField(source="product.sku", read_only=True)
    name = serializers.CharField(source="product.name", read_only=True)
    unit_price = serializers.DecimalField(
        source="product.unit_price",
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )
    line_total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ["product_id", "sku", "name", "unit_price", "quantity", "line_total"]

    def get_line_total(self, obj):
        return str(obj.product.unit_price * obj.quantity)


class CartSerializer(serializers.ModelSerializer):
    store_id = serializers.UUIDField(source="store.id", read_only=True, allow_null=True)
    items = CartItemSerializer(many=True, read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "store_id", "items", "subtotal", "updated_at"]

    def get_subtotal(self, obj):
        total = Decimal("0.00")
        for item in obj.items.all():
            total += item.product.unit_price * item.quantity
        return str(total)
