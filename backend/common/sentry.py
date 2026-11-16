import os

SENSITIVE_HEADERS = {
    "authorization",
    "cookie",
    "set-cookie",
    "x-csrftoken",
    "x-api-key",
    "x-auth-token",
}


def _scrub_event(event, hint):
    request = event.get("request")
    if isinstance(request, dict):
        headers = request.get("headers")
        if isinstance(headers, dict):
            for key in list(headers.keys()):
                if key.lower() in SENSITIVE_HEADERS:
                    headers[key] = "[Filtered]"

        if "data" in request:
            request["data"] = "[Filtered]"

        if "cookies" in request:
            request["cookies"] = "[Filtered]"

    if "user" in event and isinstance(event["user"], dict):
        event["user"] = {
            "id": event["user"].get("id"),
            "username": event["user"].get("username"),
        }

    return event


def init_sentry(kind="api"):
    dsn = os.environ.get("SENTRY_DSN")
    if not dsn:
        return

    import sentry_sdk

    integrations = []
    if kind == "api":
        from sentry_sdk.integrations.django import DjangoIntegration

        integrations.append(DjangoIntegration())
    elif kind == "worker":
        from sentry_sdk.integrations.celery import CeleryIntegration

        integrations.append(CeleryIntegration())

    sentry_sdk.init(
        dsn=dsn,
        integrations=integrations,
        environment=os.environ.get("APP_ENV", "development"),
        release=os.environ.get("SENTRY_RELEASE"),
        traces_sample_rate=float(os.environ.get("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
        send_default_pii=False,
        before_send=_scrub_event,
    )
