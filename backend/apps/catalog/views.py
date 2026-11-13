from django.http import Http404
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.stores.selectors import store_for_user

from .models import Product
from .permissions import IsProductStoreMember
from .selectors import public_product_detail, search_products
from .serializers import (
    InventoryAdjustSerializer,
    InventorySerializer,
    ProductCreateSerializer,
    ProductSerializer,
    ProductUpdateSerializer,
)
from .services import adjust_inventory, create_product, update_product


class ProductPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class PublicProductListView(GenericAPIView):
    permission_classes = [AllowAny]
    pagination_class = ProductPagination

    def get(self, request):
        store_id = request.query_params.get("store_id")
        search = request.query_params.get("search")
        queryset = search_products(store_id=store_id, search=search)
        page = self.paginate_queryset(queryset)
        serializer = ProductSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class PublicProductDetailView(GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        product = public_product_detail(product_id=self.kwargs["product_id"])
        if product is None:
            raise Http404
        return Response(ProductSerializer(product).data)


class SellerProductCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        store = store_for_user(user=request.user, store_id=self.kwargs["store_id"])
        if store is None:
            raise Http404

        serializer = ProductCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = dict(serializer.validated_data)
        initial_stock = validated.pop("initial_stock", 0)
        product = create_product(
            store=store,
            initial_stock=initial_stock,
            **validated,
        )
        return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)


class SellerProductDetailView(APIView):
    permission_classes = [IsAuthenticated, IsProductStoreMember]

    def get_object(self):
        product = (
            Product.objects.filter(
                pk=self.kwargs["product_id"],
                store__memberships__user=self.request.user,
                store__memberships__active=True,
            )
            .select_related("store", "inventory")
            .first()
        )
        if product is None:
            raise Http404
        self.check_object_permissions(self.request, product)
        return product

    def get(self, request, *args, **kwargs):
        product = self.get_object()
        return Response(ProductSerializer(product).data)

    def patch(self, request, *args, **kwargs):
        product = self.get_object()
        serializer = ProductUpdateSerializer(product, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        product = update_product(product=product, **serializer.validated_data)
        return Response(ProductSerializer(product).data)


class SellerProductInventoryView(APIView):
    permission_classes = [IsAuthenticated, IsProductStoreMember]

    def get_object(self):
        product = (
            Product.objects.filter(
                pk=self.kwargs["product_id"],
                store__memberships__user=self.request.user,
                store__memberships__active=True,
            )
            .select_related("store", "inventory")
            .first()
        )
        if product is None:
            raise Http404
        self.check_object_permissions(self.request, product)
        return product

    def put(self, request, *args, **kwargs):
        product = self.get_object()
        serializer = InventoryAdjustSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            inventory = adjust_inventory(
                product=product,
                on_hand=serializer.validated_data["on_hand"],
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
        return Response(InventorySerializer(inventory).data)
