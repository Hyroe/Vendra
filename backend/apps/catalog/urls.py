from django.urls import path

from .views import (
    PublicProductDetailView,
    PublicProductListView,
    SellerProductCreateView,
    SellerProductDetailView,
    SellerProductInventoryView,
)

urlpatterns = [
    path("products", PublicProductListView.as_view(), name="public-product-list"),
    path(
        "products/<uuid:product_id>",
        PublicProductDetailView.as_view(),
        name="public-product-detail",
    ),
    path(
        "seller/stores/<uuid:store_id>/products",
        SellerProductCreateView.as_view(),
        name="seller-product-create",
    ),
    path(
        "seller/products/<uuid:product_id>",
        SellerProductDetailView.as_view(),
        name="seller-product-detail",
    ),
    path(
        "seller/products/<uuid:product_id>/inventory",
        SellerProductInventoryView.as_view(),
        name="seller-product-inventory",
    ),
]
