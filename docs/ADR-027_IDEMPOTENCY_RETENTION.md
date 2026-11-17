# ADR-027: Idempotency key retention and cleanup

**Status:** accepted

## Context

OPEN-012 requires a bounded retention policy for `ApiIdempotencyKey` records and
their stored responses. Indefinite retention would grow the database and could
retain unnecessary response data.

## Decision

- `ApiIdempotencyKey` records receive an `expires_at` timestamp at creation.
- The default retention is 24 hours, configurable with
  `IDEMPOTENCY_KEY_RETENTION_HOURS`.
- `cleanup_idempotency_keys` deletes expired keys and keys older than the
  retention window.
- Cleanup is operational and does not mutate orders, payments or inventory.
- Stored responses remain minimal and are not logged.

## Consequences

- Replaying an idempotency key after expiry may create a new order.
- Retention can be adjusted per environment.
- Cleanup should be scheduled by cron or Celery beat in production.

## Tests and observable evidence

- Integration test verifies expired keys are deleted and active keys remain.
- Verified with `pytest`: 90 passed after Open-012.