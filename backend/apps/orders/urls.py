from django.urls import path

from .views import (
    DevPaymentSimulateView,
    OrderCancelView,
    OrderDetailView,
    OrderListCreateView,
    SellerOrderAcceptView,
    SellerOrderConfirmPaymentView,
    SellerOrderListView,
    SellerOrderPrepareView,
    SellerOrderReadyView,
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
    path(
        "seller/orders/<uuid:order_id>/accept",
        SellerOrderAcceptView.as_view(),
        name="seller-order-accept",
    ),
    path(
        "seller/orders/<uuid:order_id>/prepare",
        SellerOrderPrepareView.as_view(),
        name="seller-order-prepare",
    ),
    path(
        "seller/orders/<uuid:order_id>/ready",
        SellerOrderReadyView.as_view(),
        name="seller-order-ready",
    ),
    path(
        "seller/orders/<uuid:order_id>/confirm-payment",
        SellerOrderConfirmPaymentView.as_view(),
        name="seller-order-confirm-payment",
    ),
    path(
        "dev/payments/<uuid:attempt_id>/simulate",
        DevPaymentSimulateView.as_view(),
        name="dev-payment-simulate",
    ),
]
