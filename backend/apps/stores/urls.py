from django.urls import path

from .views import (
    PublicStoreDetailView,
    PublicStoreListView,
    SellerShippingOptionDetailView,
    SellerShippingOptionListCreateView,
    SellerStoreDetailView,
    SellerStoreListCreateView,
)

urlpatterns = [
    path("stores", PublicStoreListView.as_view(), name="public-store-list"),
    path("stores/<uuid:store_id>", PublicStoreDetailView.as_view(), name="public-store-detail"),
    path("seller/stores", SellerStoreListCreateView.as_view(), name="seller-store-list-create"),
    path(
        "seller/stores/<uuid:store_id>", SellerStoreDetailView.as_view(), name="seller-store-detail"
    ),
    path(
        "seller/stores/<uuid:store_id>/shipping-options",
        SellerShippingOptionListCreateView.as_view(),
        name="seller-shipping-option-list-create",
    ),
    path(
        "seller/shipping-options/<uuid:option_id>",
        SellerShippingOptionDetailView.as_view(),
        name="seller-shipping-option-detail",
    ),
]
