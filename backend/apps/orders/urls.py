from django.urls import path

from .views import (
    OrderCancelView,
    OrderDetailView,
    OrderListCreateView,
    SellerOrderListView,
)

urlpatterns = [
    path("orders", OrderListCreateView.as_view(), name="order-list-create"),
    path("orders/<uuid:order_id>", OrderDetailView.as_view(), name="order-detail"),
    path("orders/<uuid:order_id>/cancel", OrderCancelView.as_view(), name="order-cancel"),
    path(
        "seller/stores/<uuid:store_id>/orders",
        SellerOrderListView.as_view(),
        name="seller-order-list",
    ),
]
