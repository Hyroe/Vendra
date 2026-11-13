# Instructions for implementation agents

You are implementing **LocalHub**, a modular-monolith e-commerce marketplace with a Flutter client. Treat the documents in this folder as the specification; do not reinterpret the project as a generic CRUD application.

## Before changing code
1. Read `README.md`, `01_PRODUCT_REQUIREMENTS.md`, `03_DOMAIN_MODEL.md`, `05_API_CONTRACT.md`, `07_SECURITY.md`, and the current milestone in `11_IMPLEMENTATION_PLAN.md`.
2. Inspect the actual repository state. Existing code and migrations may be incomplete; compare reality with these documents.
3. Work on the **smallest uncompleted milestone**. Do not add features from later milestones without a dependency-based justification.
4. If a material decision is unspecified (real payment provider, precise authentication transport, deployment cloud), use the documented development default only or create a proposal in `13_DECISIONS_AND_OPEN_QUESTIONS.md`; do not pretend it is approved for production.

## Architecture constraints
- **Modular monolith**, not microservices. Django apps map to bounded business areas.
- DRF views handle HTTP; serializers validate and represent payloads; service functions perform multi-model workflows; selectors centralize nontrivial reads; models enforce local data constraints.
- PostgreSQL is the authority for orders, payments, and stock; Redis is never authoritative for these.
- Cross-app operations are explicit, transactionally safe, and tested; avoid circular imports.
- Queue jobs are at-least-once, retryable, and idempotent. Use a transactional outbox for business-critical messages.
- Do not use Django signals as the main way of coordinating orders/payments/stock.
- No payment card numbers or CVV handled/stored locally. Fake provider in early milestones.

## Security rules
- Default deny on access to another user/store/order, with server-side ownership/role checks in *every* applicable query.
- Never trust client-submitted price, seller ID, user ID, order totals, payment status, or role.
- Do not expose credentials, session tokens, full request bodies, payment provider secrets, or unnecessary PII to Sentry/logs.
- Use parameterized ORM access, explicit permissions, throttling, server-verified webhook signatures for future real providers.
- Prefer `Decimal`, integer minor units at external payment boundaries, and UTC timestamps. Never use floats for currency.
- Do not claim endpoint is secure without authorization and negative tests.

## Work cycle for each slice
1. Summarize scope, dependencies, impacted documents and tests.
2. Implement models/migrations, services, selectors, serializers, views, then tests (or test-first).
3. Run relevant formatting, linting, unit and database tests; explain failures honestly.
4. Provide a completion report: files changed, migrations, tests run/results, known risks, and next incremental task.
5. Update docs/ADR when a contract or invariant changes.

## Required scenarios to preserve
- Multiple customers racing for one inventory unit must not oversell.
- Repeated `Idempotency-Key` must not create duplicate orders.
- Duplicate/out-of-order payment notifications must not double-confirm or duplicate side effects.
- Cross-tenant access must not leak another seller's or customer's data.
- Failed asynchronous workers must not lose committed orders or notifications.

## No speculative overengineering
No Kubernetes, event sourcing, service mesh, multi-region replication, live courier GPS, or real payment integration for MVP unless explicitly requested. Simplicity is preferred where correctness and observability remain intact.
