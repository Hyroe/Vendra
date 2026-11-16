from rest_framework.permissions import BasePermission

from .models import Delivery


class IsDeliveryCourier(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return isinstance(obj, Delivery) and obj.courier_id == request.user.pk
