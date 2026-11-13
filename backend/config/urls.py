from django.urls import include, path, re_path

from common.views import api_not_found, liveness, readiness

urlpatterns = [
    path("healthz", liveness, name="healthz"),
    path("readyz", readiness, name="readyz"),
    path("api/v1/", include("apps.accounts.urls")),
    path("api/v1/", include("apps.stores.urls")),
    path("api/v1/", include("apps.catalog.urls")),
    re_path(r"^api/v1(?:/.*)?$", api_not_found, name="api_not_found"),
]

handler404 = "common.views.api_or_default_not_found"
handler500 = "common.views.api_or_default_server_error"
