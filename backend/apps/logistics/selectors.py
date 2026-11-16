from .models import Delivery


def deliveries_for_courier(*, courier):
    return Delivery.objects.filter(courier=courier).order_by("-created_at")


def delivery_for_courier(*, courier, delivery_id):
    return Delivery.objects.filter(courier=courier, pk=delivery_id).first()
