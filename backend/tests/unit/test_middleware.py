import uuid

from django.http import HttpResponse
from django.test import RequestFactory

from common.middleware import RequestIDMiddleware


def _run(request):
    def get_response(_request):
        return HttpResponse("ok")

    return RequestIDMiddleware(get_response)(request)


def test_missing_request_id_is_generated():
    response = _run(RequestFactory().get("/healthz"))

    assert response["X-Request-ID"]
    assert uuid.UUID(response["X-Request-ID"])


def test_valid_request_id_is_preserved():
    request_id = "123e4567-e89b-42d3-a456-426614174000"
    request = RequestFactory().get("/healthz", headers={"X-Request-ID": request_id})

    response = _run(request)

    assert response["X-Request-ID"] == request_id
    assert request.request_id == request_id


def test_malformed_request_id_is_replaced():
    request = RequestFactory().get("/healthz", headers={"X-Request-ID": "not-a-uuid"})

    response = _run(request)

    assert response["X-Request-ID"] != "not-a-uuid"
    assert uuid.UUID(response["X-Request-ID"])
    assert request.request_id != "not-a-uuid"
