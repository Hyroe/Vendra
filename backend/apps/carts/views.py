from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.models import Product

from .selectors import get_active_cart
from .serializers import CartSerializer
from .services import CartStoreMismatch, add_item, remove_item


class CartDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart = get_active_cart(customer=request.user)
        if cart is None:
            return Response({"id": None, "store_id": None, "items": [], "subtotal": "0.00"})
        return Response(CartSerializer(cart).data)


class CartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        product = get_object_or_404(Product, pk=self.kwargs["product_id"])
        quantity = request.data.get("quantity", 1)
        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            return Response(
                {
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "Quantity must be an integer.",
                        "request_id": getattr(request, "request_id", None),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            cart = add_item(customer=request.user, product=product, quantity=quantity)
        except CartStoreMismatch as exc:
            return Response(
                {
                    "error": {
                        "code": "CART_STORE_MISMATCH",
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
        if cart is None:
            return Response({"id": None, "store_id": None, "items": [], "subtotal": "0.00"})
        return Response(CartSerializer(cart).data)

    def delete(self, request, *args, **kwargs):
        product = get_object_or_404(Product, pk=self.kwargs["product_id"])
        remove_item(customer=request.user, product=product)
        cart = get_active_cart(customer=request.user)
        if cart is None:
            return Response({"id": None, "store_id": None, "items": [], "subtotal": "0.00"})
        return Response(CartSerializer(cart).data)
