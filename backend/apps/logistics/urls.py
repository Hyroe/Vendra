from django.urls import path

from .views import (
    CourierDeliveryCompleteView,
    CourierDeliveryInTransitView,
    CourierDeliveryListView,
    CourierDeliveryPickupView,
    SellerDeliveryAssignView,
)

urlpatterns = [
    path("courier/deliveries", CourierDeliveryListView.as_view(), name="courier-delivery-list"),
    path(
        "courier/deliveries/<uuid:delivery_id>/pickup",
        CourierDeliveryPickupView.as_view(),
        name="courier-delivery-pickup",
    ),
    path(
        "courier/deliveries/<uuid:delivery_id>/in-transit",
        CourierDeliveryInTransitView.as_view(),
        name="courier-delivery-in-transit",
    ),
    path(
        "courier/deliveries/<uuid:delivery_id>/complete",
        CourierDeliveryCompleteView.as_view(),
        name="courier-delivery-complete",
    ),
    path(
        "seller/orders/<uuid:order_id>/assign-courier",
        SellerDeliveryAssignView.as_view(),
        name="seller-delivery-assign",
    ),
]
