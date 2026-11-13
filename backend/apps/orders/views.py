from django.conf import settings
from django.http import Http404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Order
from .selectors import order_for_customer, orders_for_customer, orders_for_store
from .services import (
    IdempotencyConflict,
    InsufficientStock,
    InvalidOrderTransition,
    cancel_order,
    checkout,
    simulate_payment,
)


class OrderListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = orders_for_customer(customer=request.user)
        return Response([_serialize_order(order) for order in orders])

    def post(self, request):
        idempotency_key = request.headers.get("Idempotency-Key") or request.META.get(
            "HTTP_IDEMPOTENCY_KEY"
        )
        if not idempotency_key:
            return Response(
                {
                    "error": {
                        "code": "IDEMPOTENCY_KEY_REQUIRED",
                        "message": "Idempotency-Key header is required.",
                        "request_id": getattr(request, "request_id", None),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart_id = request.data.get("cart_id")
        if not cart_id:
            return Response(
                {
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "cart_id is required.",
                        "request_id": getattr(request, "request_id", None),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        delivery_address = request.data.get("delivery_address")
        shipping_option_id = request.data.get("shipping_option_id", "standard")

        try:
            response_data, response_status = checkout(
                customer=request.user,
                cart_id=cart_id,
                delivery_address=delivery_address,
                shipping_option_id=shipping_option_id,
                idempotency_key=idempotency_key,
            )
        except IdempotencyConflict as exc:
            return Response(
                {
                    "error": {
                        "code": "IDEMPOTENCY_CONFLICT",
                        "message": str(exc),
                        "request_id": getattr(request, "request_id", None),
                    }
                },
                status=status.HTTP_409_CONFLICT,
            )
        except InsufficientStock as exc:
            return Response(
                {
                    "error": {
                        "code": "INSUFFICIENT_STOCK",
                        "message": str(exc),
                        "request_id": getattr(request, "request_id", None),
                    }
                },
                status=status.HTTP_409_CONFLICT,
            )
        except ValueError as exc:
            return Response(
                {
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": str(exc),
                        "request_id": getattr(request, "request_id", None),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(response_data, status=response_status)


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        order = order_for_customer(customer=request.user, order_id=self.kwargs["order_id"])
        if order is None:
            # Allow authorized sellers to read their store orders.
            from apps.stores.selectors import store_for_user

            order = Order.objects.filter(pk=self.kwargs["order_id"]).first()
            if order is None or store_for_user(user=request.user, store_id=order.store_id) is None:
                raise Http404
        return Response(_serialize_order_detail(order))


class OrderCancelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        order = order_for_customer(customer=request.user, order_id=self.kwargs["order_id"])
        if order is None:
            raise Http404
        try:
            order = cancel_order(order=order, actor=request.user)
        except InvalidOrderTransition as exc:
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
        return Response(_serialize_order_detail(order))


class SellerOrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        orders = orders_for_store(user=request.user, store_id=self.kwargs["store_id"])
        if orders is None:
            raise Http404
        return Response([_serialize_order(order) for order in orders])


class DevPaymentSimulateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if not getattr(settings, "FAKE_PAYMENT_ENABLED", False) or not request.user.is_staff:
            raise Http404

        attempt_id = self.kwargs["attempt_id"]
        outcome = request.data.get("outcome")
        if outcome not in {"succeeded", "failed"}:
            return Response(
                {
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "outcome must be 'succeeded' or 'failed'.",
                        "request_id": getattr(request, "request_id", None),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        event_id = request.data.get("event_id")
        try:
            result = simulate_payment(
                attempt_id=attempt_id,
                outcome=outcome,
                event_id=event_id,
                actor=request.user,
            )
        except Exception as exc:
            return Response(
                {
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": str(exc),
                        "request_id": getattr(request, "request_id", None),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(result, status=status.HTTP_200_OK)


def _serialize_order(order):
    return {
        "id": str(order.id),
        "status": order.status,
        "currency": order.currency,
        "totals": {
            "subtotal": str(order.subtotal),
            "shipping": str(order.shipping_total),
            "tax": str(order.tax_total),
            "discount": str(order.discount_total),
            "grand_total": str(order.grand_total),
        },
        "created_at": order.created_at.isoformat(),
    }


def _serialize_order_detail(order):
    return {
        "id": str(order.id),
        "status": order.status,
        "currency": order.currency,
        "totals": {
            "subtotal": str(order.subtotal),
            "shipping": str(order.shipping_total),
            "tax": str(order.tax_total),
            "discount": str(order.discount_total),
            "grand_total": str(order.grand_total),
        },
        "address_snapshot": order.address_snapshot,
        "items": [
            {
                "id": str(item.id),
                "product_id": str(item.product_id) if item.product_id else None,
                "sku_snapshot": item.sku_snapshot,
                "title_snapshot": item.title_snapshot,
                "unit_price": str(item.unit_price),
                "quantity": item.quantity,
                "line_total": str(item.line_total),
            }
            for item in order.items.all()
        ],
        "created_at": order.created_at.isoformat(),
    }
