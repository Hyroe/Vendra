# ADR-015: Fake payments, deduplication and transactional outbox

**Status:** accepted

## Context

M4 introduces fake payment simulation, payment event deduplication, paid/failed
transitions, outbox publishing and Celery/RabbitMQ workers. The specifications
require at-least-once delivery, idempotent consumers and no publication of
uncommitted state.

## Decision

- Payment simulation is available only when `FAKE_PAYMENT_ENABLED=True` and the
  caller is staff, at `POST /api/v1/dev/payments/{attempt_id}/simulate`.
- Provider events are deduplicated by `(provider, provider_event_id)`.
- Payment success commits inventory (`on_hand` and `reserved`) and moves the
  order to `PAID` exactly once; failure releases the reservation and moves the
  order to `PAYMENT_FAILED`.
- Late success after a non-pending order is recorded without reopening the order.
- Business transactions write `OutboxEvent` in the same PostgreSQL commit.
- `dispatch_outbox_events()` publishes pending events through Celery with
  `SELECT ... FOR UPDATE SKIP LOCKED`; failures leave the event unpublished.
- Consumers record a `ProcessedEvent` receipt for exactly-once side effects.
- Celery uses RabbitMQ as broker and Redis as result backend. A beat service
  schedules periodic dispatch.

## Consequences

- The fake provider remains development/test only and must be disabled in
  production.
- Outbox dispatch is periodic, so publication latency depends on beat schedule.
- Broker downtime retains outbox rows for later publication.
- Expiry/reconciliation workflows can reuse the same locking and transition
  services.

## Tests and observable evidence

- API tests: successful payment, duplicate event, failed payment, staff-only access.
- Unit/integration tests from previous milestones continue to pass.
- Verified with `pytest`: 73 passed after M4.