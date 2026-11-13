from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Store
from .permissions import IsStoreMember
from .selectors import public_store_detail, public_stores, store_for_user, stores_for_user
from .serializers import (
    StoreCreateSerializer,
    StoreSerializer,
    StoreUpdateSerializer,
)
from .services import create_store, update_store


class PublicStoreListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = StoreSerializer

    def get_queryset(self):
        return public_stores()


class PublicStoreDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = StoreSerializer
    lookup_field = "pk"
    queryset = Store.objects.none()

    def get_object(self):
        return public_store_detail(store_id=self.kwargs["store_id"])


class SellerStoreListCreateView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = StoreSerializer(stores_for_user(user=request.user), many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = StoreCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        store = create_store(owner=request.user, **serializer.validated_data)
        return Response(StoreSerializer(store).data, status=status.HTTP_201_CREATED)


class SellerStoreDetailView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsStoreMember]

    def get_object(self):
        store = store_for_user(user=self.request.user, store_id=self.kwargs["store_id"])
        if store is None:
            from django.http import Http404

            raise Http404
        self.check_object_permissions(self.request, store)
        return store

    def get(self, request, *args, **kwargs):
        store = self.get_object()
        return Response(StoreSerializer(store).data)

    def patch(self, request, *args, **kwargs):
        store = self.get_object()
        serializer = StoreUpdateSerializer(store, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        store = update_store(store=store, **serializer.validated_data)
        return Response(StoreSerializer(store).data)
