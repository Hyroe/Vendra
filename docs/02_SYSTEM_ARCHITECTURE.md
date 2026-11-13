# System architecture — v0.1

## Architectural style
Django/DRF **modular monolith** with PostgreSQL as transactional database. Celery workers execute asynchronous jobs through RabbitMQ. Redis supplies ephemeral cache/throttling coordination. Flutter calls the versioned REST API. Sentry collects scrubbed exceptions and transactions.

```
Flutter client ─HTTPS─> Django/DRF API ─────> PostgreSQL (source of truth)
                          │                        │
                          ├────> Redis             └── outbox_events
                          │                             │
                          └────> outbox publisher ──────> RabbitMQ
                                                         │
                                                      Celery workers
                                                         │
                                             database + safe notifications
All API, worker, client errors ──────────────────────────> Sentry (redacted)
```

## Deployment units
- `api`: Django WSGI/ASGI application (choose server during bootstrap).
- `worker`: Celery background consumers.
- `beat`: optional Celery scheduler for expiry/reconciliation, introduced when needed.
- `outbox-dispatcher`: may be Celery beat-driven or management command; must not publish uncommitted state.
- `db`: PostgreSQL.
- `rabbitmq`: broker.
- `redis`: cache and throttles.
- `mobile`: separate Flutter project.

## Module responsibilities
| App | Responsibilities | Not responsible for |
|---|---|---|
| accounts | identity, role membership, authentication | order authorization decisions without store context |
| stores | store lifecycle, memberships | payments |
| catalog | products, inventory, price publication | checkout orchestration |
| carts | cart and item ownership | price authority |
| orders | checkout, order lines, state transitions, reservation orchestration | provider-specific payment calls |
| payments | payment attempts, provider adapter, webhook idempotency | arbitrary order state mutation |
| logistics | deliveries, assignments, delivery transitions | order payment confirmation |
| notifications | message templates, dispatch/status | authoritative business state |
| audit | append-only security/business events | raw request/secret storage |

## Layer boundaries
- Views: parse request, authorize HTTP access, call services/selectors, return status and documented error code.
- Serializers: shape/validate input and output; never compute authoritative final price.
- Services: transactional business use cases, state machine, event/outbox writes.
- Selectors: optimized, tenant-scoped queries (`select_related`, `prefetch_related` when warranted).
- Models/managers: local invariants, constraints and query expressions.
- Tasks: invoke idempotent service functions, log failure/retry; no hidden business logic in tasks.

## Consistency
- Use `transaction.atomic()` for checkout, payment confirmation, inventory release, state changes and corresponding outbox/audit entries.
- Concurrency: row-level locks on inventory, deterministic order of lock acquisition, database constraints (`stock >= 0`, `reserved >= 0`, `reserved <= stock`).
- External side effects occur after commit through outbox; **never** call a payment gateway or send external notifications from an open DB transaction.
- RabbitMQ/Celery delivery is **at least once**: consumers must deduplicate and tolerate retries/reordering.

## Interface standards
`/api/v1/`, JSON, UUID identifiers, ISO-8601 UTC timestamps, RFC-friendly documented error payload, cursor/page pagination for collections, no raw Django model serialization exposed.

## Caching
Only public catalog read models initially; explicit TTL/invalidation on product publication/price/inventory updates. Checkout never relies on cache for price or stock. Avoid caching personalized responses unless carefully keyed and authorized.

## Development environments
Docker Compose for PostgreSQL/RabbitMQ/Redis/api/worker; local Flutter emulator. Separate database and fake provider configurations for test. Production deployment provider intentionally undecided.
