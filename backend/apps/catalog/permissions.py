from rest_framework.permissions import BasePermission

from apps.stores.models import StoreMembership


class IsProductStoreMember(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return StoreMembership.objects.filter(
            user=request.user,
            store=obj.store,
            active=True,
        ).exists()
