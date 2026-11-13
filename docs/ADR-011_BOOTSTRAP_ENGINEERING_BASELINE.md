# ADR-011: Bootstrap engineering baseline

**Status:** accepted

## Context

M0 requires a reproducible Django/DRF + PostgreSQL baseline with Docker Compose,
env templates, pytest, linting, GitHub Actions, health/readiness endpoints, a JSON
error format, request IDs and the first migration. The specifications define the
stack and API conventions but leave several bootstrap details unspecified: the
Python/Django versions, API server, health-route names, request-ID header, exact
error codes and whether unused infrastructure services should start in Compose.

The host development environment only has Python 3.15, which is outside the
official support matrix of Django 5.2 LTS.

## Decision

- Pin backend execution to **Python 3.13** through `python:3.13-slim`.
- Use **Django 5.2 LTS**, **DRF 3.16**, **PostgreSQL 17** and **psycopg 3**.
- Use **Gunicorn** as the production WSGI server in the image; Compose overrides
  the command with `runserver` for local development.
- Expose unauthenticated `GET /healthz` (liveness) and `GET /readyz` (readiness)
  outside `/api/v1`. Readiness checks PostgreSQL and returns 503 JSON when down.
- Use `X-Request-ID` for correlation. Preserve a valid inbound RFC 4122 UUID;
  otherwise generate a new one. Never echo malformed inbound values.
- Return API errors as
  `{"error": {"code": "...", "message": "...", "request_id": "..."}}`.
  Validation errors may add a `details` object. 5xx responses use a generic
  message and log the exception without request bodies or secrets.
- Keep M0 Compose limited to `db` + `api`. Redis, RabbitMQ and Celery workers are
  introduced in M4 when there is real asynchronous work and throttling.
- Create the custom `accounts.User` model (UUID primary key, normalized unique
  email) in the first migration, as required by `04_DATA_MODEL.md`, before the
  M1 identity/store work.

## Alternatives considered

- **Use host Python 3.15:** rejected because Django 5.2 does not officially
  support it and local reproducibility would depend on an unsupported runtime.
- **Expose only `/health`:** rejected as less explicit about liveness vs.
  readiness; `/healthz` and `/readyz` are conventional and unambiguous.
- **Start Redis/RabbitMQ now:** rejected for M0 because no code consumes them
  yet; this avoids unused services and keeps the milestone focused.
- **Let Django return HTML for API 404/500:** rejected because the API contract
  requires a stable JSON error envelope.

## Consequences

- All backend commands run in Docker until a supported local Python 3.13
  installation is available. Docker is a hard requirement for the M0 DB test.
- The error envelope is available globally through the DRF exception handler and
  a custom Django 404/500 handler for `/api/` paths.
- Health routes are intentionally unauthenticated and must not expose database
  credentials or query details.
- The first migration creates only the custom user and Django auth/contenttypes/
  sessions tables. Store, catalog, cart, order and payment migrations follow in
  later milestones.

## Security and data implications

- No secrets are committed; `.env.example` contains placeholders only.
- Malformed request IDs are discarded rather than trusted or logged.
- 5xx responses do not include exception messages or tracebacks.
- The custom user stores only normalized email, password hash, active/staff
  flags and creation time in M0.
- The default development secret key is explicitly insecure and must be replaced
  by `DJANGO_SECRET_KEY` in any shared environment.

## Migration plan

M0 introduces `accounts.0001_initial`. Subsequent milestones add migrations in
the sequence documented in `04_DATA_MODEL.md`: store/membership, catalog/inventory,
cart, order/reservation/transition, payment/idempotency, outbox/audit.

## Tests and observable evidence

Verified on 2026-11-12 in Docker (`python:3.13-slim`, PostgreSQL 17):

- `python manage.py check`: no issues.
- `python manage.py makemigrations --check --dry-run`: no changes.
- `python manage.py migrate --check`: no unapplied migrations.
- `ruff check .`: all checks passed.
- `ruff format --check .`: 31 files already formatted.
- `pytest` with `config.settings.test`: 32 passed.
- `docker compose config`: valid.
- `docker compose up -d api`: `/healthz` and `/readyz` returned 200 with
  `X-Request-ID`; `/api/v1/does-not-exist` returned 404 JSON.
- `manage.py check --deploy` (production settings): only the expected
  short-secret warning for the dummy test key.