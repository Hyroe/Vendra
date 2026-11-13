import logging

from celery import shared_task
from django.db import IntegrityError

from .models import OutboxEvent, ProcessedEvent

logger = logging.getLogger(__name__)


@shared_task
def process_outbox_event(event_id):
    try:
        event = OutboxEvent.objects.get(pk=event_id)
    except OutboxEvent.DoesNotExist:
        return

    try:
        ProcessedEvent.objects.create(event=event, handler="default")
    except IntegrityError:
        return

    logger.info("Processed outbox event %s (%s)", event.id, event.event_type)


@shared_task
def dispatch_outbox():
    from .services import dispatch_outbox_events

    dispatch_outbox_events()
