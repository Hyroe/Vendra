# Deployment baseline — LocalHub

## Status
Development baseline only. No cloud provider is selected and no production
readiness is claimed.

## Runtime units
- `api`: Django/DRF with Gunicorn.
- `worker`: Celery consumer.
- `beat`: Celery scheduler.
- `db`: PostgreSQL.
- `redis`: cache and throttles.
- `rabbitmq`: broker.

## Development
```bash
cp .env.example .env
docker compose up --build -d
```

## Production-shaped local validation
```bash
cp .env.example .env
# Set DJANGO_SECRET_KEY, ALLOWED_HOSTS and SENTRY_DSN in .env
docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d
```

## Required production environment
- `DJANGO_SETTINGS_MODULE=config.settings.production`
- `DJANGO_SECRET_KEY` (long random value)
- `ALLOWED_HOSTS`
- `DATABASE_URL`
- `CACHE_URL` / `REDIS_URL`
- `RABBITMQ_URL`
- `SENTRY_DSN` (optional but recommended)
- `FAKE_PAYMENT_ENABLED=False`

## Health checks
- `GET /healthz` for liveness.
- `GET /readyz` for readiness, including PostgreSQL.

## Migrations
```bash
python manage.py migrate
python manage.py migrate --check
python manage.py check --deploy
```

## Backup and recovery
See `BACKUP_AND_RECOVERY.md`.

## Capacity baseline
See `performance/README.md`. k6 catalog baseline passed the documented 300 ms
p95 target under the controlled 100 VU run. Checkout baseline remains pending
seeded fixtures.