from unittest.mock import patch

import pytest
from django.db import OperationalError


def test_liveness_is_public_and_returns_ok(client):
    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.django_db
def test_readiness_returns_database_ok(client):
    response = client.get("/readyz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "checks": {"database": "ok"}}


def test_readiness_returns_503_when_database_is_unavailable(client):
    with patch(
        "common.views.connection.ensure_connection",
        side_effect=OperationalError("database unavailable"),
    ):
        response = client.get("/readyz")

    assert response.status_code == 503
    assert response.json()["status"] == "unavailable"
    assert response.json()["checks"] == {"database": "unavailable"}


def test_health_response_includes_request_id(client):
    response = client.get("/healthz")

    assert response["X-Request-ID"]
    assert len(response["X-Request-ID"]) == 36
