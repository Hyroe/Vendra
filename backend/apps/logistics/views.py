from django.http import Http404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import User
from apps.orders.models import Order

from .permissions import IsDeliveryCourier
from .selectors import deliveries_for_courier, delivery_for_courier
from .serializers import DeliveryAssignSerializer, DeliverySerializer
from .services import (
    InvalidDeliveryTransition,
    assign_delivery,
    transition_delivery,
)


class CourierDeliveryListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        deliveries = deliveries_for_courier(courier=request.user)
        return Response(DeliverySerializer(deliveries, many=True).data)


class CourierDeliveryTransitionView(APIView):
    permission_classes = [IsAuthenticated, IsDeliveryCourier]
    target_status = None

    def get_object(self):
        delivery = delivery_for_courier(
            courier=self.request.user, delivery_id=self.kwargs["delivery_id"]
        )
        if delivery is None:
            raise Http404
        self.check_object_permissions(self.request, delivery)
        return delivery

    def post(self, request, *args, **kwargs):
        delivery = self.get_object()
        try:
            delivery = transition_delivery(
                delivery=delivery,
                to_status=self.target_status,
                actor=request.user,
            )
        except (InvalidDeliveryTransition, PermissionError) as exc:
            return Response(
                {
                    "error": {
                        "code": "ORDER_CONFLICT",
                        "message": str(exc),
                        "request_id": getattr(request, "request_id", None),
                    }
                },
                status=status.HTTP_409_CONFLICT,
            )
        return Response(DeliverySerializer(delivery).data)


class CourierDeliveryPickupView(CourierDeliveryTransitionView):
    target_status = "PICKED_UP"


class CourierDeliveryInTransitView(CourierDeliveryTransitionView):
    target_status = "IN_TRANSIT"


class CourierDeliveryCompleteView(CourierDeliveryTransitionView):
    target_status = "DELIVERED"


class SellerDeliveryAssignView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        order = Order.objects.filter(pk=self.kwargs["order_id"]).first()
        if order is None:
            raise Http404

        from apps.stores.selectors import store_for_user

        if store_for_user(user=request.user, store_id=order.store_id) is None:
            raise Http404

        serializer = DeliveryAssignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        courier = User.objects.filter(pk=serializer.validated_data["courier_id"]).first()
        if courier is None:
            return Response(
                {
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "Courier not found.",
                        "request_id": getattr(request, "request_id", None),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            delivery = assign_delivery(order=order, courier=courier, actor=request.user)
        except (ValueError, PermissionError) as exc:
            return Response(
                {
                    "error": {
                        "code": "ORDER_CONFLICT",
                        "message": str(exc),
                        "request_id": getattr(request, "request_id", None),
                    }
                },
                status=status.HTTP_409_CONFLICT,
            )
        return Response(DeliverySerializer(delivery).data, status=status.HTTP_201_CREATED)
