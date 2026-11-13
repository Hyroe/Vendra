# Security baseline and threat model — v0.1

## Assets and trust boundaries
Sensitive assets: account credentials, sessions/tokens, order/customer addresses, seller operational data, payment provider credentials, inventory integrity and audit history. Boundaries: Flutter ↔ public HTTPS API ↔ Django permissions/services ↔ PostgreSQL; API/outbox ↔ RabbitMQ/worker; applications ↔ Sentry. Treat every client field and external callback as untrusted.

## Baseline controls
- HTTPS in deployment; production secure headers, restrictive CORS allowlist and CSRF if cookie-backed.
- Django security settings by environment (`DEBUG=False`, allowed hosts, secure cookies, HSTS after TLS rollout, secret management).
- Password hashing via Django supported password hashers (Argon2 if configured) and login throttling.
- Mobile authentication transport is a **blocking open design item**; evaluate short-lived credentials, refresh rotation, revocation and protected device storage before implementation.
- Object- and store-scoped permission checks on every nonpublic resource. Deny by default. Avoid mass assignment of ownership, role, money or state.
- Strict serializer input shape, server-side price calculation, quantity and size caps, ORM-based queries, safe uploads (future).
- Provider callbacks: verify signatures, provider account, event IDs, amount, currency and attempt mapping before mutating financial state.
- Rate limits on auth, checkout, simulation/dev endpoints, webhooks, and high-cost searches.
- Non-production fake payment routes must be unreachable in production.
- Separate service credentials; least-privilege DB roles; rotate compromised secrets; encrypt backups; patch dependencies.
- Sentry/log scrubbing: never log password/token, authorization headers, cookies, raw card data, full address, webhook secret or unredacted payload.
- Audit critical mutations without secrets and keep audit history tamper-resistant for app roles.

## Primary threats and verification
| Threat | Example | Required test/control |
|---|---|---|
| BOLA/IDOR | customer guesses other order UUID | 403/404 after scoped query |
| Broken seller tenancy | seller edits rival store product | membership permission test |
| Payment forgery | client posts `paid=true` | reject client-controlled payment status |
| Duplicate payment | repeated callback | unique provider event, no double fulfillment |
| Inventory race | two users buy final unit | DB lock + concurrent integration test |
| Checkout replay | duplicate HTTP POST | unique idempotency + payload hash |
| Auth brute-force | repeated login attempts | throttling and generic errors |
| Injection | arbitrary search input | serializer validation + ORM use |
| Secret leakage | exceptions contain tokens | scrub Sentry/logs, regression test |
| Async-loss | publish before commit / broker outage | transactional outbox and replay |

## Security verification pipeline
`ruff`/lint, type checks where practical, `bandit`, `pip-audit`, dependency checks, unit/integration permission tests; add OWASP ZAP baseline against an isolated staging environment. Scan only systems you own or have permission to test.

## Production readiness blockers
Threat model review; authentication design finalized; secure secret storage and key rotation; payment-provider compliance review; privacy/data-retention policy; backup/restore drill; server hardening; real-provider webhook validation; load tests with measurable capacity; external security review where warranted. None of these is automatically satisfied by passing MVP tests.
