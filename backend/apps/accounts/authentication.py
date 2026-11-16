import jwt
from django.conf import settings
from django.utils import timezone
from rest_framework import authentication, exceptions

from .models import MobileSession


class JWTAuthentication(authentication.BaseAuthentication):
    keyword = "Bearer"

    def authenticate(self, request):
        header = authentication.get_authorization_header(request).decode("utf-8")
        if not header:
            return None

        parts = header.split()
        if len(parts) != 2 or parts[0] != self.keyword:
            return None

        token = parts[1]
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=["HS256"],
                options={"verify_exp": True},
            )
        except jwt.PyJWTError as exc:
            raise exceptions.AuthenticationFailed("Invalid access token.") from exc

        user_id = payload.get("sub")
        session_id = payload.get("sid")
        if not user_id or not session_id:
            raise exceptions.AuthenticationFailed("Invalid access token.")

        try:
            session = MobileSession.objects.select_related("user").get(pk=session_id)
        except MobileSession.DoesNotExist as exc:
            raise exceptions.AuthenticationFailed("Session not found.") from exc

        if not session.is_active():
            raise exceptions.AuthenticationFailed("Session is revoked or expired.")

        user = session.user
        if not user.is_active:
            raise exceptions.AuthenticationFailed("User is inactive.")

        session.last_used_at = timezone.now()
        session.save(update_fields=["last_used_at", "updated_at"])

        return (user, token)

    def authenticate_header(self, request):
        return self.keyword
