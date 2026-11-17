from django.urls import path

from .token_views import (
    MobileSessionListView,
    MobileSessionRevokeView,
    MobileTokenLoginView,
    MobileTokenRefreshView,
    MobileTokenRevokeView,
)
from .views import (
    AddressDetailView,
    AddressListCreateView,
    LoginView,
    LogoutView,
    MeView,
    RegisterView,
)

urlpatterns = [
    path("auth/register", RegisterView.as_view(), name="auth-register"),
    path("auth/login", LoginView.as_view(), name="auth-login"),
    path("auth/logout", LogoutView.as_view(), name="auth-logout"),
    path("auth/token", MobileTokenLoginView.as_view(), name="auth-token-login"),
    path("auth/token/refresh", MobileTokenRefreshView.as_view(), name="auth-token-refresh"),
    path("auth/token/revoke", MobileTokenRevokeView.as_view(), name="auth-token-revoke"),
    path("auth/sessions", MobileSessionListView.as_view(), name="auth-sessions"),
    path(
        "auth/sessions/<uuid:session_id>",
        MobileSessionRevokeView.as_view(),
        name="auth-session-revoke",
    ),
    path("addresses", AddressListCreateView.as_view(), name="address-list-create"),
    path("addresses/<uuid:address_id>", AddressDetailView.as_view(), name="address-detail"),
    path("me", MeView.as_view(), name="me"),
]
