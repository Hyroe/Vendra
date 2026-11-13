import re
import uuid

UUID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


class RequestIDMiddleware:
    """Attach a request ID and return it in the response.

    A valid inbound UUID is preserved; missing or malformed values are replaced
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
