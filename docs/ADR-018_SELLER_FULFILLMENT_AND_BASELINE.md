# ADR-018: Seller fulfillment, observability and baseline

**Status:** accepted

## Context

M6 adds seller fulfillment transitions, Sentry, structured JSON logging, Redis
cache/rate limiting, security scanning and k6 baseline scripts. The
implementation must remain compatible with the existing modular monolith and
not claim production readiness.

## Decision

- Seller transitions `PAID -> ACCEPTED -> PREPARING -> READY_FOR_PICKUP` are
  implemented as explicit, audited state transitions with store membership checks.
- Public catalog reads use Redis cache with a version-based invalidation key.
- DRF throttling uses Redis-backed cache and includes anon/user/login/register
  scopes.
- Request logging emits JSON with request ID, actor ID, method, path, duration
  and status code, without request bodies or secrets.
- Sentry is initialized for Django API, Celery worker and Flutter, with redaction
  of sensitive headers and request data.
- Bandit and pip-audit run in CI with agreed severity policy.
- k6 scripts live under `performance/` with a documented report template.

## Consequences

- k6 is not installed in this environment; the scripts and report template are
  the executable artifact until a controlled run is performed.
- Mobile Sentry uses `SENTRY_DSN` only when configured.
- Cache and rate-limit state are ephemeral and never authoritative.

## Tests and observable evidence

- API tests: seller fulfillment happy path, invalid transition, cross-seller denial.
- Backend: 76 passed, ruff clean, bandit clean, pip-audit clean.
- Flutter: analyze (info/warnings only) and 2 tests passed.
- k6 scripts prepared; execution pending environment support.