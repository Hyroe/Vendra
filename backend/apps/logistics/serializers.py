from rest_framework import serializers

from .models import Delivery, DeliveryEvent


class DeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        fields = [
            "id",
            "order",
            "courier",
            "status",
            "assigned_at",
            "picked_up_at",
            "in_transit_at",
            "delivered_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class DeliveryEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryEvent
        fields = ["id", "from_status", "to_status", "actor", "created_at"]


class DeliveryAssignSerializer(serializers.Serializer):
    courier_id = serializers.UUIDField()
