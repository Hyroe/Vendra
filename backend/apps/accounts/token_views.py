from django.contrib.auth import authenticate
from django.http import Http404
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .mobile_auth import (
    issue_tokens,
    list_sessions,
    refresh_tokens,
    revoke_by_refresh_token,
    revoke_session,
)
from .serializers import MobileSessionSerializer


class MobileTokenLoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"

    def post(self, request):
        email = (request.data.get("email") or "").strip().lower()
        password = request.data.get("password") or ""
        user = authenticate(request, username=email, password=password)
        if user is None:
            return Response(
                {
                    "error": {
                        "code": "UNAUTHENTICATED",
                        "message": "Invalid credentials.",
                        "request_id": getattr(request, "request_id", None),
                    }
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        device_id = (request.data.get("device_id") or "").strip()
        device_name = (request.data.get("device_name") or "").strip()
        tokens = issue_tokens(user=user, device_id=device_id, device_name=device_name)
        return Response(tokens, status=status.HTTP_200_OK)


class MobileTokenRefreshView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"

    def post(self, request):
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return Response(
                {
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "refresh_token is required.",
                        "request_id": getattr(request, "request_id", None),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            tokens = refresh_tokens(refresh_token=refresh_token)
        except ValueError as exc:
            return Response(
                {
                    "error": {
                        "code": "UNAUTHENTICATED",
                        "message": str(exc),
                        "request_id": getattr(request, "request_id", None),
                    }
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return Response(tokens, status=status.HTTP_200_OK)


class MobileTokenRevokeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get("refresh_token")
        if refresh_token:
            revoke_by_refresh_token(refresh_token=refresh_token)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MobileSessionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sessions = list_sessions(user=request.user)
        return Response(MobileSessionSerializer(sessions, many=True).data)


class MobileSessionRevokeView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        revoked = revoke_session(session_id=self.kwargs["session_id"], user=request.user)
        if not revoked:
            raise Http404
        return Response(status=status.HTTP_204_NO_CONTENT)
