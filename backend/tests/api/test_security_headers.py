import pytest


@pytest.mark.django_db
def test_security_headers_are_not_added_in_debug(client, settings):
    settings.DEBUG = True
    response = client.get("/healthz")
    assert "Content-Security-Policy" not in response
    assert response.headers.get("Server") != "LocalHub"


@pytest.mark.django_db
def test_security_headers_are_added_outside_debug(client, settings):
    settings.DEBUG = False
    response = client.get("/healthz")
    assert (
        response["Content-Security-Policy"]
        == "default-src 'none'; frame-ancestors 'none'; base-uri 'none'"
    )
    assert response["Server"] == "LocalHub"
