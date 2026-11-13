import hashlib
import json
import uuid
from decimal import Decimal

from django.db import IntegrityError, transaction
from django.db.models import F
from django.utils import timezone

from apps.carts.models import Cart
from apps.catalog.models import Inventory

from .models import (
    ApiIdempotencyKey,
    InventoryReservation,
    Order,
    OrderItem,
    OrderStatus,
    OrderTransition,
    OutboxEvent,
    PaymentAttempt,
    PaymentEvent,
    PaymentStatus,
    ReservationStatus,
)


class IdempotencyConflict(Exception):
    pass


class InsufficientStock(Exception):
    pass


class InvalidOrderTransition(Exception):
    pass


def _request_hash(payload):
    normalized = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _serialize_order(order, payment):
    return {
        "id": str(order.id),
        "status": order.status,
        "currency": order.currency,
        "totals": {
            "subtotal": str(order.subtotal),
            "shipping": str(order.shipping_total),
            "tax": str(order.tax_total),
            "discount": str(order.discount_total),
            "grand_total": str(order.grand_total),
        },
        "payment": {
            "attempt_id": str(payment.id),
            "status": payment.status,
        },
    }


def checkout(
    *, customer, cart_id, delivery_address=None, shipping_option_id="standard", idempotency_key=None
):
    if not idempotency_key:
        raise ValueError("Idempotency-Key is required.")

    payload = {
        "cart_id": str(cart_id),
        "delivery_address": delivery_address or {},
        "shipping_option_id": shipping_option_id,
    }
    request_hash = _request_hash(payload)

    # Idempotency key handling
    try:
        with transaction.atomic():
            idem = ApiIdempotencyKey.objects.create(
                user=customer,
                scope="checkout",
                key=idempotency_key,
                request_hash=request_hash,
                status="PROCESSING",
            )
            created = True
    except IntegrityError:
        idem = ApiIdempotencyKey.objects.get(user=customer, scope="checkout", key=idempotency_key)
        created = False

    if not created:
        if idem.request_hash != request_hash:
            raise IdempotencyConflict("Idempotency key was used with a different request.")
        if idem.status == "COMPLETED" and idem.response_body is not None:
            return idem.response_body, idem.response_status
        raise IdempotencyConflict("Checkout is already being processed.")

    try:
        with transaction.atomic():
            cart = Cart.objects.select_for_update().get(pk=cart_id, customer=customer)
            items = list(
                cart.items.select_related("product", "product__store", "product__inventory")
            )
            if not items:
                raise ValueError("Cart is empty.")

            store = cart.store
            if store is None or store.status != "ACTIVE":
                raise ValueError("Store is not available.")

            for item in items:
                product = item.product
                if not product.is_published:
                    raise ValueError("Product is not available.")

            # Lock inventories in stable product-id order.
            product_ids = sorted({item.product_id for item in items})
            inventories = {
                inv.product_id: inv
                for inv in Inventory.objects.select_for_update().filter(product_id__in=product_ids)
            }
            for item in items:
                inventory = inventories.get(item.product_id)
                if inventory is None:
                    raise ValueError("Inventory is missing.")
                available = inventory.on_hand - inventory.reserved
                if available < item.quantity:
                    raise InsufficientStock("Insufficient stock for checkout.")

            for item in items:
                inventory = inventories[item.product_id]
                inventory.reserved += item.quantity
                inventory.save(update_fields=["reserved", "updated_at"])

            subtotal = sum(
                (item.product.unit_price * item.quantity for item in items), Decimal("0.00")
            )
            shipping_total = Decimal("4.00")
            tax_total = Decimal("0.00")
            discount_total = Decimal("0.00")
            grand_total = subtotal + shipping_total + tax_total - discount_total

            order = Order.objects.create(
                customer=customer,
                store=store,
                currency=store.currency,
                status=OrderStatus.PAYMENT_PENDING,
                subtotal=subtotal,
                shipping_total=shipping_total,
                tax_total=tax_total,
                discount_total=discount_total,
                grand_total=grand_total,
                address_snapshot=delivery_address or {},
            )

            for item in items:
                order_item = OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    sku_snapshot=item.product.sku,
                    title_snapshot=item.product.name,
                    unit_price=item.product.unit_price,
                    quantity=item.quantity,
                    line_total=item.product.unit_price * item.quantity,
                )
                InventoryReservation.objects.create(
                    order_item=order_item,
                    product=item.product,
                    quantity=item.quantity,
                    status=ReservationStatus.RESERVED,
                )

            OrderTransition.objects.create(
                order=order,
                from_status=OrderStatus.CREATED,
                to_status=OrderStatus.PAYMENT_PENDING,
                actor=customer,
                reason="checkout",
            )

            payment = PaymentAttempt.objects.create(
                order=order,
                provider="fake",
                provider_ref=str(uuid.uuid4()),
                status=PaymentStatus.PENDING,
                amount=grand_total,
                currency=store.currency,
                idempotency_key=idempotency_key,
            )

            response_data = _serialize_order(order, payment)
            idem.status = "COMPLETED"
            idem.response_status = 201
            idem.response_body = response_data
            idem.save(update_fields=["status", "response_status", "response_body"])

            cart.items.all().delete()
            cart.delete()

    except Exception:
        if created:
            ApiIdempotencyKey.objects.filter(pk=idem.pk).update(status="FAILED")
        raise

    return response_data, 201


def cancel_order(*, order, actor=None):
    if order.status != OrderStatus.PAYMENT_PENDING:
        raise InvalidOrderTransition("Order cannot be cancelled in its current state.")

    with transaction.atomic():
        order = Order.objects.select_for_update().get(pk=order.pk)
        if order.status != OrderStatus.PAYMENT_PENDING:
            raise InvalidOrderTransition("Order cannot be cancelled in its current state.")

        product_ids = sorted({item.product_id for item in order.items.select_related("product")})
        inventories = {
            inv.product_id: inv
            for inv in Inventory.objects.select_for_update().filter(product_id__in=product_ids)
        }
        for order_item in order.items.select_related("product"):
            reservation = getattr(order_item, "reservation", None)
            if reservation is None or reservation.status != ReservationStatus.RESERVED:
                continue
            inventory = inventories[reservation.product_id]
            inventory.reserved -= reservation.quantity
            if inventory.reserved < 0:
                inventory.reserved = 0
            inventory.save(update_fields=["reserved", "updated_at"])
            reservation.status = ReservationStatus.RELEASED
            reservation.save(update_fields=["status"])

        OrderTransition.objects.create(
            order=order,
            from_status=order.status,
            to_status=OrderStatus.CANCELLED,
            actor=actor,
            reason="customer_cancel",
        )
        order.status = OrderStatus.CANCELLED
        order.save(update_fields=["status", "updated_at"])

    return order


def release_reservation_for_order(order):
    with transaction.atomic():
        order = Order.objects.select_for_update().get(pk=order.pk)
        product_ids = sorted({item.product_id for item in order.items.select_related("product")})
        inventories = {
            inv.product_id: inv
            for inv in Inventory.objects.select_for_update().filter(product_id__in=product_ids)
        }
        for order_item in order.items.select_related("product"):
            reservation = getattr(order_item, "reservation", None)
            if reservation is None or reservation.status != ReservationStatus.RESERVED:
                continue
            inventory = inventories[reservation.product_id]
            inventory.reserved = max(0, inventory.reserved - reservation.quantity)
            inventory.save(update_fields=["reserved", "updated_at"])
            reservation.status = ReservationStatus.RELEASED
            reservation.save(update_fields=["status"])


def simulate_payment(*, attempt_id, outcome, event_id=None, actor=None):
    if outcome not in {"succeeded", "failed"}:
        raise ValueError("outcome must be 'succeeded' or 'failed'.")

    provider = "fake"
    provider_event_id = event_id or f"fake-{attempt_id}-{outcome}-{uuid.uuid4()}"

    try:
        with transaction.atomic():
            event = PaymentEvent.objects.create(
                provider=provider,
                provider_event_id=provider_event_id,
                payment_attempt_id=attempt_id,
                event_type=f"payment.{outcome}",
            )
        event_created = True
    except IntegrityError:
        event = PaymentEvent.objects.get(provider=provider, provider_event_id=provider_event_id)
        event_created = False

    if not event_created:
        return {"status": "duplicate", "order_status": None}

    with transaction.atomic():
        attempt = PaymentAttempt.objects.select_for_update().get(pk=attempt_id)
        order = Order.objects.select_for_update().get(pk=attempt.order_id)
        event.payment_attempt = attempt
        event.save(update_fields=["payment_attempt"])

        if attempt.status in {
            PaymentStatus.SUCCEEDED,
            PaymentStatus.FAILED,
            PaymentStatus.CANCELLED,
        }:
            event.processed_at = timezone.now()
            event.save(update_fields=["processed_at"])
            return {"status": "already_terminal", "order_status": order.status}

        if outcome == "succeeded":
            if order.status == OrderStatus.PAYMENT_PENDING:
                product_ids = sorted(
                    {item.product_id for item in order.items.select_related("product")}
                )
                inventories = {
                    inv.product_id: inv
                    for inv in Inventory.objects.select_for_update().filter(
                        product_id__in=product_ids
                    )
                }
                for order_item in order.items.select_related("product"):
                    reservation = getattr(order_item, "reservation", None)
                    if reservation is None or reservation.status != ReservationStatus.RESERVED:
                        continue
                    inventory = inventories[reservation.product_id]
                    inventory.on_hand = max(0, inventory.on_hand - reservation.quantity)
                    inventory.reserved = max(0, inventory.reserved - reservation.quantity)
                    inventory.save(update_fields=["on_hand", "reserved", "updated_at"])
                    reservation.status = ReservationStatus.COMMITTED
                    reservation.save(update_fields=["status"])

                OrderTransition.objects.create(
                    order=order,
                    from_status=order.status,
                    to_status=OrderStatus.PAID,
                    actor=actor,
                    reason="fake_payment_succeeded",
                )
                order.status = OrderStatus.PAID
                order.save(update_fields=["status", "updated_at"])
                attempt.status = PaymentStatus.SUCCEEDED
                attempt.save(update_fields=["status"])
                OutboxEvent.objects.create(
                    aggregate_type="order",
                    aggregate_id=order.id,
                    event_type="payment.succeeded.v1",
                    payload={"order_id": str(order.id), "payment_attempt_id": str(attempt.id)},
                )
            else:
                attempt.status = PaymentStatus.SUCCEEDED
                attempt.save(update_fields=["status"])
                OutboxEvent.objects.create(
                    aggregate_type="order",
                    aggregate_id=order.id,
                    event_type="payment.late_success.v1",
                    payload={"order_id": str(order.id), "payment_attempt_id": str(attempt.id)},
                )
        else:
            if order.status == OrderStatus.PAYMENT_PENDING:
                product_ids = sorted(
                    {item.product_id for item in order.items.select_related("product")}
                )
                inventories = {
                    inv.product_id: inv
                    for inv in Inventory.objects.select_for_update().filter(
                        product_id__in=product_ids
                    )
                }
                for order_item in order.items.select_related("product"):
                    reservation = getattr(order_item, "reservation", None)
                    if reservation is None or reservation.status != ReservationStatus.RESERVED:
                        continue
                    inventory = inventories[reservation.product_id]
                    inventory.reserved = max(0, inventory.reserved - reservation.quantity)
                    inventory.save(update_fields=["reserved", "updated_at"])
                    reservation.status = ReservationStatus.RELEASED
                    reservation.save(update_fields=["status"])

                OrderTransition.objects.create(
                    order=order,
                    from_status=order.status,
                    to_status=OrderStatus.PAYMENT_FAILED,
                    actor=actor,
                    reason="fake_payment_failed",
                )
                order.status = OrderStatus.PAYMENT_FAILED
                order.save(update_fields=["status", "updated_at"])

            attempt.status = PaymentStatus.FAILED
            attempt.save(update_fields=["status"])
            OutboxEvent.objects.create(
                aggregate_type="order",
                aggregate_id=order.id,
                event_type="payment.failed.v1",
                payload={"order_id": str(order.id), "payment_attempt_id": str(attempt.id)},
            )

        event.processed_at = timezone.now()
        event.save(update_fields=["processed_at"])

        return {"status": outcome, "order_status": order.status}


def dispatch_outbox_events():
    events = list(
        OutboxEvent.objects.filter(published_at__isnull=True).order_by("created_at")[:100]
    )
    for event in events:
        try:
            with transaction.atomic():
                locked = OutboxEvent.objects.select_for_update(skip_locked=True).get(
                    pk=event.pk, published_at__isnull=True
                )
                from .tasks import process_outbox_event

                process_outbox_event.delay(str(locked.id))
                locked.published_at = timezone.now()
                locked.attempt_count += 1
                locked.save(update_fields=["published_at", "attempt_count"])
        except Exception:
            OutboxEvent.objects.filter(pk=event.pk).update(attempt_count=F("attempt_count") + 1)
