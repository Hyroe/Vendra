# LocalHub

LocalHub is a portfolio-scale local multi-vendor marketplace built as a Django/DRF
modular monolith with PostgreSQL, Celery/RabbitMQ, Redis and a Flutter client.

## Status

**M0 — Bootstrap and engineering baseline** is implemented. Identity, stores,
catalog, cart, checkout and payments are later milestones. See
[`docs/11_IMPLEMENTATION_PLAN.md`](docs/11_IMPLEMENTATION_PLAN.md).

## Quickstart

Requirements: Docker with Compose v2.

```bash
cp .env.example .env
docker compose up --build -d
curl http://localhost:8000/healthz
curl http://localhost:8000/readyz
```

Run the backend tests:

```bash
docker compose run --rm -e DJANGO_SETTINGS_MODULE=config.settings.test api pytest
```

Lint and check migrations:

```bash
docker compose exec api ruff check .
docker compose exec api ruff format --check .
docker compose exec api python manage.py makemigrations --check --dry-run
```

## Repository layout

```
AGENTS.md                 # Operating rules for coding agents
docs/                     # Product, architecture, domain, API and security specs
backend/                  # Django/DRF project
docker-compose.yml        # PostgreSQL + API for local development
.github/workflows/ci.yml  # Backend CI
```

## Documentation

Start with [`docs/README.md`](docs/README.md), then follow the reading order in
[`docs/AGENTS.md`](docs/AGENTS.md).