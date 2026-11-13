import logging

from rest_framework import status
from rest_framework.exceptions import (
    AuthenticationFailed,
    MethodNotAllowed,
    NotAcceptable,
    NotAuthenticated,
    NotFound,
    ParseError,
    PermissionDenied,
    Throttled,
    UnsupportedMediaType,
    ValidationError,
)
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)

_STATUS_CODES = {
    400: "VALIDATION_ERROR",
    401: "UNAUTHENTICATED",
    403: "PERMISSION_DENIED",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    406: "NOT_ACCEPTABLE",
    409: "CONFLICT",
    415: "UNSUPPORTED_MEDIA_TYPE",
    429: "THROTTLED",
    500: "INTERNAL_ERROR",
}


def _error_code(exc: Exception, status_code: int) -> str:
    if isinstance(exc, ValidationError):
        return "VALIDATION_ERROR"
    if isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
        return "UNAUTHENTICATED"
    if isinstance(exc, PermissionDenied):
        return "PERMISSION_DENIED"
    if isinstance(exc, NotFound):
        return "NOT_FOUND"
    if isinstance(exc, MethodNotAllowed):
        return "METHOD_NOT_ALLOWED"
    if isinstance(exc, ParseError):
        return "MALFORMED_REQUEST"
    if isinstance(exc, Throttled):
        return "THROTTLED"
    if isinstance(exc, UnsupportedMediaType):
        return "UNSUPPORTED_MEDIA_TYPE"
    if isinstance(exc, NotAcceptable):
        return "NOT_ACCEPTABLE"
    return _STATUS_CODES.get(status_code, "API_ERROR")


def _message_from_detail(detail) -> str:
    if isinstance(detail, str):
        return str(detail)
    if isinstance(detail, dict):
        for value in detail.values():
            return _message_from_detail(value)
    if isinstance(detail, (list, tuple)) and detail:
        return _message_from_detail(detail[0])
    return "Request could not be processed."


def api_exception_handler(exc, context):
    """Return the documented JSON error envelope for API failures."""

    response = drf_exception_handler(exc, context)
    request = context.get("request")
    request_id = getattr(request, "request_id", None)

    if isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
        response.status_code = status.HTTP_401_UNAUTHORIZED

    if response is None:
        logger.exception("Unhandled API exception", extra={"request_id": request_id})
        return Response(
            {
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Internal server error.",
                    "request_id": request_id,
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    code = _error_code(exc, response.status_code)
    message = (
        "Internal server error."
        if response.status_code >= 500
        else "Request could not be processed."
    )
    if response.status_code < 500:
        detail = getattr(exc, "detail", None)
        if detail is not None:
            message = _message_from_detail(detail)

    payload = {
        "error": {
            "code": code,
            "message": message,
            "request_id": request_id,
        }
    }

    if response.status_code < 500 and isinstance(exc, ValidationError):
        payload["error"]["details"] = exc.detail

    response.data = payload
    return response
