import uuid

from django.test import override_settings


def test_unknown_api_route_returns_json_error(client):
    response = client.get("/api/v1/does-not-exist")

    assert response.status_code == 404
    assert response["Content-Type"].startswith("application/json")

    payload = response.json()
    error = payload["error"]
    assert error["code"] == "NOT_FOUND"
    assert error["message"] == "Resource not found."
    assert uuid.UUID(error["request_id"])
    assert response["X-Request-ID"] == error["request_id"]


def test_unknown_api_route_returns_json_error_when_debug(client):
    with override_settings(DEBUG=True):
        response = client.get("/api/v1/does-not-exist")

    assert response.status_code == 404
    assert response["Content-Type"].startswith("application/json")
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_request_id_is_echoed_in_health_response(client):
    request_id = "123e4567-e89b-42d3-a456-426614174000"
    response = client.get("/healthz", headers={"X-Request-ID": request_id})

    assert response["X-Request-ID"] == request_id


def test_invalid_request_id_is_replaced_in_health_response(client):
    response = client.get("/healthz", headers={"X-Request-ID": "not-a-uuid"})

    assert response["X-Request-ID"] != "not-a-uuid"
    assert uuid.UUID(response["X-Request-ID"])


def test_error_response_does_not_contain_traceback(client):
    response = client.get("/api/v1/does-not-exist")

    body = response.content.decode()
    assert "Traceback" not in body
    assert "SECRET" not in body
