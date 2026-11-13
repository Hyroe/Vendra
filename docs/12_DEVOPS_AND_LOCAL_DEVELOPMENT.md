# Local development, environments and CI/CD

## Runtime services (planned)
Docker Compose: `postgres`, `rabbitmq`, `redis`, `api`, `worker`, optional `beat` and `outbox-dispatcher`. Introduce optional services in milestones where actually used. Use health checks and startup retries; `depends_on` alone is not readiness.

## Configuration
Example non-secret names: `DJANGO_SETTINGS_MODULE`, `DATABASE_URL`, `RABBITMQ_URL`, `REDIS_URL`, `SENTRY_DSN`, `APP_ENV`, `FAKE_PAYMENT_ENABLED`, `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`. Never commit real tokens, private keys or DSNs. `.env.example` contains placeholders only. Different databases/users for development, test and staging.

## Common future commands (illustrative; do not claim implemented)
```
docker compose up -d postgres rabbitmq redis
cd backend && python manage.py migrate
cd backend && pytest
cd backend && python manage.py check --deploy
cd mobile && flutter analyze && flutter test
```
Commands become authoritative only after corresponding repository scripts exist.

## CI pipelines
Pull request: lint, Python security/dependency checks, DB migrations, unit/integration suite, OpenAPI drift if applicable. Mobile analysis/test when changed. Branch protection + reviews. Deployment pipeline and cloud environment are intentionally unselected.

## Operational readiness
Document backup/restore and retention, TLS termination, health checks, DB connection budget, worker queues/limits, alerting on outbox age and payment reconciliation, shutdown behavior, migrations/rollback strategy, access controls and minimum-privilege credentials.
