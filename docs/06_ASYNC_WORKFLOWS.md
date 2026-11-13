# RabbitMQ / Celery / Redis workflows

## Purpose and delivery semantics
Celery executes jobs asynchronously using RabbitMQ. **At least once** delivery is assumed: messages may repeat, delay, arrive out of order, or be lost temporarily during infrastructure disruption. Handlers must be idempotent and state-aware.

## Initial events and tasks
| Business event (outbox) | Worker action | Idempotency key |
|---|---|---|
| `order.created.v1` | initiate fake payment / notify seller when appropriate | event UUID |
| `payment.succeeded.v1` | notify customer and store after DB confirmation | event UUID + notification type |
| `payment.failed.v1` | send failure notification | event UUID |
| `order.ready.v1` | enqueue logistics assignment (later) | order ID + action |
| `order.expired.v1` | release reservation and notify | order ID + terminal state |

## Transactional outbox
Business transaction inserts its domain update, `AuditEvent`, and `OutboxEvent` in **the same PostgreSQL commit**. A dispatcher locks unprocessed outbox rows using `SELECT ... FOR UPDATE SKIP LOCKED` (or equivalent), publishes to RabbitMQ with publisher confirms if supported, and marks sent. Because publish acknowledgement and DB marking are not atomic, duplicates are expected; consumers deduplicate. Recover stale claiming attempts and use bounded retries with alerts.

## Worker responsibilities
- Receive event identifier, version, aggregate identifier and minimal non-sensitive payload.
- Validate schema and verify current database state before side effects.
- Record a durable processing/delivery receipt where exact-once effects are required (unique event+handler key).
- Retry transient failures with exponential backoff and jitter, bounded max retries; permanent errors go to dead-letter/failed task handling for investigation.
- Never embed credentials, full addresses, access tokens or payment data in task arguments, logs or Sentry breadcrumbs.

## Payment flow
1. HTTP checkout creates order `PAYMENT_PENDING`, reservation, pending attempt and outbox.
2. After commit, worker creates/simulates payment with provider idempotency reference; persistence records attempt status.
3. Provider callback (fake internal handler initially) is validated and deduplicated by provider event ID.
4. Transaction locks payment and order; checks amount/currency and state; commits inventory sale and `PAID` once; writes outbox + audit.
5. Duplicate callback is a no-op; late success after expired/cancelled moves to reconciliation path, **never** silent status overwrite.

## Expiry workflow
A scheduled task queries `PAYMENT_PENDING` orders older than configured TTL (e.g. 15 minutes, configurable). It locks order and attempt, applies cancellation and reservation release once, emits event. For real providers, reconcile/cancel outstanding attempt before final release; race policy must be reviewed before production.

## Redis contract
- Public catalog cache (TTL, targeted invalidation).
- Throttle counters for login/checkout.
- Optional ephemeral distributed coordination.
- No order/payment state, no financial ledger, no irreplaceable events in Redis.

## Failure test matrix
Duplicated event; worker crashes before and after DB commit; publish succeeds but mark-sent fails; delayed event after cancellation; RabbitMQ unavailable; Redis flushed; outbox poll concurrent dispatchers; payment success races with expiry. Verify no double stock decrement and no double transition.
