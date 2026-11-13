from rest_framework import serializers

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "sku_snapshot",
            "title_snapshot",
            "unit_price",
            "quantity",
            "line_total",
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    totals = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "customer",
            "store",
            "currency",
            "status",
            "totals",
            "address_snapshot",
            "items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "customer",
            "store",
            "currency",
            "status",
            "totals",
            "created_at",
            "updated_at",
        ]

    def get_totals(self, obj):
        return {
            "subtotal": str(obj.subtotal),
            "shipping": str(obj.shipping_total),
            "tax": str(obj.tax_total),
            "discount": str(obj.discount_total),
            "grand_total": str(obj.grand_total),
        }
