# Incremental implementation roadmap

**Rule:** complete and verify one vertical slice before moving on. Each milestone creates a meaningful testable deliverable. Later work must not break earlier invariants.

## M0 — Bootstrap and engineering baseline
- Monorepo, Django/DRF, PostgreSQL, Docker Compose, env templates, pytest, linting, GitHub Actions.
- Health/readiness endpoints, basic JSON error format, request IDs, first migrations.
- **Exit:** fresh clone starts services and runs one green DB integration test.

## M1 — Identity and store authorization
- Custom User, seller role/membership, register/login/logout transport design, Store CRUD.
- Secure permissions and negative cross-store tests.
- **Exit:** seller creates store; unauthorized seller cannot edit it.
- **Gate:** finalize mobile authentication approach before Flutter login.

## M2 — Catalog and inventory
- Product and Inventory models, publication, seller ownership, public catalog filters/search.
- **Exit:** store publishes product; customer/public can list only active published items; seller permissions tested.

## M3 — Cart, checkout, orders
- One-store cart, snapshot pricing, inventory reservation with row locks, order transitions, idempotency keys.
- **Exit:** customer creates pending order, retries safely, two customers cannot oversell last item.

## M4 — Fake payments and reliable events
- PaymentAttempt, fake provider adapter, verified internal simulation, event dedup, atomic paid/failure transitions, outbox, Celery/RabbitMQ.
- **Exit:** simulated payment succeeds once; broker downtime/duplicate events do not corrupt state.

## M5 — Flutter customer app
- Auth based on reviewed transport, catalog, cart, checkout, orders; safe retry and error UX.
- **Exit:** automated E2E synthetic purchase from Flutter to PostgreSQL.

## M6 — Seller fulfillment, observability and baseline
- Seller order queue and transitions; Sentry API/worker/mobile, structured logs, Redis cache/rate-limit, security suite, k6 benchmark.
- **Exit:** seller processes paid order to READY_FOR_PICKUP; documented k6 report and permission/security tests.

## M7 — Logistics (post-MVP)
- Delivery assignment, courier authorization, pickup/transit/delivered transitions, event history and notifications.
- **Exit:** assigned courier completes one delivery; unrelated courier denied.

## M8 — Payment provider and operational hardening (post-MVP)
- Real provider after design/security/legal review, signed webhooks and reconciliation, refund/cancellation policy, recovery, backup/restore, deployment and capacity work.
- **Exit:** production readiness checklist reviewed; no claim of production readiness without verification.

## Checklist template per milestone
- [ ] Design/code consistent with docs and ADRs
- [ ] Migration/schema checks
- [ ] Happy path and negative authorization tests
- [ ] Concurrent/failure tests where applicable
- [ ] Error/log redaction
- [ ] Docker/CI checks executed
- [ ] API schema/documentation updated
- [ ] Measured results documented
