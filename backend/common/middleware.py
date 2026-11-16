import logging
import re
import time
import uuid

UUID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    re.IGNORECASE,
)

logger = logging.getLogger(__name__)


class RequestIDMiddleware:
    """Attach a request ID and return it in the response.

    A valid inbound RFC 4122 UUID is preserved; missing or malformed values are replaced
    so headers cannot inject arbitrary data into logs.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        inbound = request.META.get("HTTP_X_REQUEST_ID")
        if inbound and UUID_PATTERN.fullmatch(inbound):
            request_id = str(uuid.UUID(inbound))
        else:
            request_id = str(uuid.uuid4())

        request.request_id = request_id
        response = self.get_response(request)
        response["X-Request-ID"] = request_id
        return response


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        started = time.monotonic()
        response = self.get_response(request)
        duration_ms = int((time.monotonic() - started) * 1000)

        user = getattr(request, "user", None)
        actor_id = str(user.pk) if user is not None and user.is_authenticated else None

        logger.info(
            "request",
            extra={
                "request_id": getattr(request, "request_id", None),
                "actor_id": actor_id,
                "duration_ms": duration_ms,
                "status_code": response.status_code,
                "method": request.method,
                "path": request.path,
            },
        )
        return response
