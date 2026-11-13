from rest_framework.exceptions import (
    APIException,
    MethodNotAllowed,
    NotAuthenticated,
    NotFound,
    ParseError,
    PermissionDenied,
    Throttled,
    ValidationError,
)
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from common.exceptions import api_exception_handler

REQUEST_ID = "123e4567-e89b-42d3-a456-426614174000"


def _handle(exc):
    django_request = APIRequestFactory().get("/api/v1/test")
    django_request.request_id = REQUEST_ID
    drf_request = Request(django_request)

    return api_exception_handler(exc, {"request": drf_request, "view": None})


def _payload(response):
    return response.data["error"]


def test_validation_error_uses_documented_shape():
    response = _handle(ValidationError({"price": ["Enter a valid amount."]}))

    assert response.status_code == 400
    payload = _payload(response)
    assert payload["code"] == "VALIDATION_ERROR"
    assert payload["request_id"] == REQUEST_ID
    assert payload["details"] == {"price": ["Enter a valid amount."]}


def test_not_authenticated_maps_to_401():
    response = _handle(NotAuthenticated())

    assert response.status_code == 401
    assert _payload(response)["code"] == "UNAUTHENTICATED"


def test_permission_denied_maps_to_403():
    response = _handle(PermissionDenied())

    assert response.status_code == 403
    assert _payload(response)["code"] == "PERMISSION_DENIED"


def test_not_found_maps_to_404():
    response = _handle(NotFound())

    assert response.status_code == 404
    assert _payload(response)["code"] == "NOT_FOUND"


def test_method_not_allowed_maps_to_405():
    response = _handle(MethodNotAllowed("POST"))

    assert response.status_code == 405
    assert _payload(response)["code"] == "METHOD_NOT_ALLOWED"


def test_parse_error_maps_to_400():
    response = _handle(ParseError("Invalid JSON."))

    assert response.status_code == 400
    assert _payload(response)["code"] == "MALFORMED_REQUEST"


def test_throttled_maps_to_429():
    response = _handle(Throttled(wait=5))

    assert response.status_code == 429
    assert _payload(response)["code"] == "THROTTLED"


def test_api_exception_500_is_sanitized():
    response = _handle(APIException("SECRET_PROVIDER_TOKEN_123"))

    assert response.status_code == 500
    payload = _payload(response)
    assert payload["code"] == "INTERNAL_ERROR"
    assert payload["message"] == "Internal server error."
    assert "SECRET_PROVIDER_TOKEN_123" not in str(response.data)


def test_unhandled_exception_returns_json_500():
    response = _handle(ValueError("SECRET_STACK_VALUE"))

    assert response.status_code == 500
    payload = _payload(response)
    assert payload["code"] == "INTERNAL_ERROR"
    assert payload["message"] == "Internal server error."
    assert "SECRET_STACK_VALUE" not in str(response.data)
