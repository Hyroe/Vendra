from django.urls import path

from .views import CartDetailView, CartItemView

urlpatterns = [
    path("cart", CartDetailView.as_view(), name="cart-detail"),
    path("cart/items/<uuid:product_id>", CartItemView.as_view(), name="cart-item"),
]
