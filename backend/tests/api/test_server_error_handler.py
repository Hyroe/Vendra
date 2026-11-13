import json

from django.test import RequestFactory

from common.views import api_or_default_server_error


def test_server_error_handler_returns_json_for_api_routes():
    request = RequestFactory().get("/api/v1/boom")
    request.request_id = "123e4567-e89b-42d3-a456-426614174000"

    response = api_or_default_server_error(request)

    assert response.status_code == 500
    payload = json.loads(response.content)
    assert payload["error"]["code"] == "INTERNAL_ERROR"
    assert payload["error"]["request_id"] == request.request_id
