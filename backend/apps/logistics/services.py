from django.db import transaction
from django.utils import timezone

from apps.orders.models import Order, OrderStatus, OrderTransition, OutboxEvent
from apps.stores.selectors import store_for_user

from .models import Delivery, DeliveryEvent, DeliveryStatus


class InvalidDeliveryTransition(Exception):
    pass


def assign_delivery(*, order, courier, actor):
    store = store_for_user(user=actor, store_id=order.store_id)
    if store is None:
        raise PermissionError("Actor is not authorized for this store.")

    with transaction.atomic():
        order = order.__class__.objects.select_for_update().get(pk=order.pk)
        if order.status != OrderStatus.READY_FOR_PICKUP:
            raise ValueError("Order is not ready for pickup.")

        delivery, created = Delivery.objects.get_or_create(
            order=order,
            defaults={"status": DeliveryStatus.UNASSIGNED},
        )
        if delivery.courier is not None or delivery.status != DeliveryStatus.UNASSIGNED:
            raise ValueError("Delivery is already assigned.")

        delivery.courier = courier
        delivery.status = DeliveryStatus.ASSIGNED
        delivery.assigned_at = timezone.now()
        delivery.save(update_fields=["courier", "status", "assigned_at", "updated_at"])

        DeliveryEvent.objects.create(
            delivery=delivery,
            from_status=DeliveryStatus.UNASSIGNED,
            to_status=DeliveryStatus.ASSIGNED,
            actor=actor,
        )

    return delivery


ALLOWED_DELIVERY_TRANSITIONS = {
    DeliveryStatus.ASSIGNED: {DeliveryStatus.PICKED_UP},
    DeliveryStatus.PICKED_UP: {DeliveryStatus.IN_TRANSIT},
    DeliveryStatus.IN_TRANSIT: {DeliveryStatus.DELIVERED},
}


def transition_delivery(*, delivery, to_status, actor):
    if delivery.courier_id != getattr(actor, "pk", None):
        raise PermissionError("Only the assigned courier can update this delivery.")
    if to_status not in ALLOWED_DELIVERY_TRANSITIONS.get(delivery.status, set()):
        raise InvalidDeliveryTransition(
            f"Delivery cannot transition from {delivery.status} to {to_status}."
        )

    with transaction.atomic():
        delivery = Delivery.objects.select_for_update().get(pk=delivery.pk)
        if delivery.courier_id != getattr(actor, "pk", None):
            raise PermissionError("Only the assigned courier can update this delivery.")
        if to_status not in ALLOWED_DELIVERY_TRANSITIONS.get(delivery.status, set()):
            raise InvalidDeliveryTransition(
                f"Delivery cannot transition from {delivery.status} to {to_status}."
            )

        DeliveryEvent.objects.create(
            delivery=delivery,
            from_status=delivery.status,
            to_status=to_status,
            actor=actor,
        )

        delivery.status = to_status
        now = timezone.now()
        if to_status == DeliveryStatus.PICKED_UP:
            delivery.picked_up_at = now
        elif to_status == DeliveryStatus.IN_TRANSIT:
            delivery.in_transit_at = now
        elif to_status == DeliveryStatus.DELIVERED:
            delivery.delivered_at = now
        delivery.save()

        if to_status == DeliveryStatus.DELIVERED:
            sync_order_with_delivery(delivery)

    return delivery


def sync_order_with_delivery(delivery):
    if delivery.status != DeliveryStatus.DELIVERED:
        return delivery.order

    with transaction.atomic():
        order = Order.objects.select_for_update().get(pk=delivery.order_id)
        if order.status == OrderStatus.DELIVERED:
            return order
        if order.status != OrderStatus.READY_FOR_PICKUP:
            return order

        OrderTransition.objects.create(
            order=order,
            from_status=order.status,
            to_status=OrderStatus.DELIVERED,
            actor=delivery.courier,
            reason="delivery_completed",
        )
        order.status = OrderStatus.DELIVERED
        order.save(update_fields=["status", "updated_at"])

        OutboxEvent.objects.create(
            aggregate_type="order",
            aggregate_id=order.id,
            event_type="order.delivered.v1",
            payload={"order_id": str(order.id), "delivery_id": str(delivery.id)},
        )
    return order
