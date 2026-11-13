from rest_framework.permissions import BasePermission

from .models import StoreMembership


class IsStoreMember(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return StoreMembership.objects.filter(
            user=request.user,
            store=obj,
            active=True,
        ).exists()
