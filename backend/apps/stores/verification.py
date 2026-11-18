from django.http import Http404
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Store
from .serializers import StoreSerializer


class SellerStoreVerificationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise Http404

        store = Store.objects.filter(pk=self.kwargs["store_id"]).first()
        if store is None:
            raise Http404

        store.verification_status = "VERIFIED"
        store.verified_at = timezone.now()
        store.verified_by = request.user
        store.save(
            update_fields=["verification_status", "verified_at", "verified_by", "updated_at"]
        )
        return Response(StoreSerializer(store).data, status=status.HTTP_200_OK)
