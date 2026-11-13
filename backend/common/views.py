import logging

from django.db import DatabaseError, connection
from django.http import JsonResponse
from django.views.defaults import page_not_found, server_error

logger = logging.getLogger(__name__)


def liveness(request):
    return JsonResponse({"status": "ok"})


def readiness(request):
    try:
        connection.ensure_connection()
    except DatabaseError:
        logger.exception("Database readiness check failed")
        return JsonResponse(
            {"status": "unavailable", "checks": {"database": "unavailable"}},
            status=503,
        )

    return JsonResponse({"status": "ok", "checks": {"database": "ok"}})


def api_not_found(request):
    return JsonResponse(
        {
            "error": {
                "code": "NOT_FOUND",
                "message": "Resource not found.",
                "request_id": getattr(request, "request_id", None),
            }
        },
        status=404,
    )


def api_or_default_not_found(request, exception):
    if request.path.startswith("/api/"):
        return api_not_found(request)
    return page_not_found(request, exception)


def api_or_default_server_error(request):
    if request.path.startswith("/api/"):
        return JsonResponse(
            {
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Internal server error.",
                    "request_id": getattr(request, "request_id", None),
                }
            },
            status=500,
        )
    return server_error(request)
