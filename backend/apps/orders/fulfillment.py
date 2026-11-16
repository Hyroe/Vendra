from django.db import transaction

from .models import Order, OrderStatus, OrderTransition, OutboxEvent
from .services import InvalidOrderTransition

ALLOWED_TRANSITIONS = {
    OrderStatus.PAID: {OrderStatus.ACCEPTED},
    OrderStatus.ACCEPTED: {OrderStatus.PREPARING},
    OrderStatus.PREPARING: {OrderStatus.READY_FOR_PICKUP},
}


def transition_order(*, order, to_status, actor=None):
    if to_status not in ALLOWED_TRANSITIONS.get(order.status, set()):
        raise InvalidOrderTransition(f"Order cannot transition from {order.status} to {to_status}.")

    with transaction.atomic():
        order = Order.objects.select_for_update().get(pk=order.pk)
        if to_status not in ALLOWED_TRANSITIONS.get(order.status, set()):
            raise InvalidOrderTransition(
                f"Order cannot transition from {order.status} to {to_status}."
            )

        OrderTransition.objects.create(
            order=order,
            from_status=order.status,
            to_status=to_status,
            actor=actor,
            reason=f"seller_{to_status.lower()}",
        )
        order.status = to_status
        order.save(update_fields=["status", "updated_at"])

        OutboxEvent.objects.create(
            aggregate_type="order",
            aggregate_id=order.id,
            event_type=f"order.{to_status.lower()}.v1",
            payload={"order_id": str(order.id), "status": to_status},
        )

    return order
