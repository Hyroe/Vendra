import secrets
from datetime import timedelta

import jwt
from django.conf import settings
from django.utils import timezone

from .models import MobileSession


def _access_token(user, session):
    now = timezone.now()
    expires = now + timedelta(minutes=settings.JWT_ACCESS_TTL_MINUTES)
    payload = {
        "sub": str(user.pk),
        "sid": str(session.pk),
        "iat": int(now.timestamp()),
        "exp": int(expires.timestamp()),
        "jti": secrets.token_urlsafe(16),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")


def _refresh_token():
    return secrets.token_urlsafe(48)


def issue_tokens(*, user, device_id="", device_name=""):
    refresh = _refresh_token()
    session = MobileSession.objects.create(
        user=user,
        device_id=device_id,
        device_name=device_name,
        refresh_token_hash=MobileSession.hash_token(refresh),
        refresh_expires_at=timezone.now() + timedelta(days=settings.JWT_REFRESH_TTL_DAYS),
        last_used_at=timezone.now(),
    )
    access = _access_token(user, session)
    return {
        "access": access,
        "refresh": refresh,
        "session_id": str(session.pk),
        "expires_in": settings.JWT_ACCESS_TTL_MINUTES * 60,
    }


def refresh_tokens(*, refresh_token):
    token_hash = MobileSession.hash_token(refresh_token)
    session = MobileSession.objects.filter(refresh_token_hash=token_hash).first()
    if session is None:
        # Reuse detection: if token matches previous hash, revoke session.
        session = MobileSession.objects.filter(previous_refresh_token_hash=token_hash).first()
        if session is not None:
            session.revoked_at = timezone.now()
            session.save(update_fields=["revoked_at", "updated_at"])
        raise ValueError("Invalid refresh token.")

    if not session.is_active():
        raise ValueError("Refresh token is expired or revoked.")

    # Rotate refresh token.
    new_refresh = _refresh_token()
    session.previous_refresh_token_hash = session.refresh_token_hash
    session.refresh_token_hash = MobileSession.hash_token(new_refresh)
    session.rotated_at = timezone.now()
    session.refresh_expires_at = timezone.now() + timedelta(days=settings.JWT_REFRESH_TTL_DAYS)
    session.last_used_at = timezone.now()
    session.save(
        update_fields=[
            "previous_refresh_token_hash",
            "refresh_token_hash",
            "rotated_at",
            "refresh_expires_at",
            "last_used_at",
            "updated_at",
        ]
    )

    access = _access_token(session.user, session)
    return {
        "access": access,
        "refresh": new_refresh,
        "session_id": str(session.pk),
        "expires_in": settings.JWT_ACCESS_TTL_MINUTES * 60,
    }


def revoke_session(*, session_id, user):
    session = MobileSession.objects.filter(pk=session_id, user=user).first()
    if session is None:
        return False
    if session.revoked_at is None:
        session.revoked_at = timezone.now()
        session.save(update_fields=["revoked_at", "updated_at"])
    return True


def revoke_by_refresh_token(*, refresh_token):
    token_hash = MobileSession.hash_token(refresh_token)
    session = MobileSession.objects.filter(refresh_token_hash=token_hash).first()
    if session is None:
        return False
    if session.revoked_at is None:
        session.revoked_at = timezone.now()
        session.save(update_fields=["revoked_at", "updated_at"])
    return True


def list_sessions(*, user):
    return MobileSession.objects.filter(user=user).order_by("-created_at")
