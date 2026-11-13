# LocalHub — Documentation for AI-assisted implementation

**Status:** Planning baseline v0.1  
**Last updated:** 2026-11-12  
**Language of specification:** English (API identifiers and code are English).  
**Goal:** Build a production-minded, portfolio-scale local multi-vendor marketplace with order fulfillment and delivery.

## Source of truth and precedence
1. `AGENTS.md`: operating rules for coding agents.
2. `01_PRODUCT_REQUIREMENTS.md`: scope and acceptance criteria.
3. `03_DOMAIN_MODEL.md`: business invariants and state transitions.
4. `05_API_CONTRACT.md`: externally visible HTTP behavior.
5. `04_DATA_MODEL.md`, `06_ASYNC_WORKFLOWS.md`, `07_SECURITY.md`: persistence and implementation contracts.
6. Other documents describe implementation approach and verification.

If documents conflict, **do not silently choose**: write a proposed ADR and flag the conflict. `13_DECISIONS_AND_OPEN_QUESTIONS.md` explicitly distinguishes decisions from assumptions and open items.

## Read in this order
`AGENTS.md` → `01_PRODUCT_REQUIREMENTS.md` → `02_SYSTEM_ARCHITECTURE.md` → `03_DOMAIN_MODEL.md` → `04_DATA_MODEL.md` → `05_API_CONTRACT.md` → `06_ASYNC_WORKFLOWS.md` → `07_SECURITY.md` → `10_TEST_STRATEGY.md` → `11_IMPLEMENTATION_PLAN.md`.

## Technical stack
- Backend: Python, Django, Django REST Framework (DRF), PostgreSQL.
- Async: Celery workers + RabbitMQ broker; Redis for cache/rate limits/ephemeral coordination (not durable business state).
- Mobile: Flutter (one role-aware application initially).
- Observability: Sentry for API/workers/mobile; structured logs and request correlation.
- Performance: k6 as code-based load-testing tool.
- Dev tooling: Docker Compose, pytest/pytest-django, GitHub Actions.

## First demonstrable workflow
Register customer → seller creates store/product → customer browses → adds to cart → places order → simulated payment confirmed → seller sees paid order. No live payment credentials or real delivery required for this milestone.

## Repository target
```
localhub/
  AGENTS.md
  docs/                     # these documents
  backend/
    config/
    apps/{accounts,stores,catalog,carts,orders,payments,logistics,notifications,audit}/
    common/
    tests/
  mobile/
  infrastructure/
  performance/
  .github/workflows/
  docker-compose.yml
  .env.example
```

## Implementation definition of done
A change is complete when contracts and constraints are respected, migrations exist, unit/integration/permission tests pass, linters/type checks pass where configured, and documentation or an ADR is updated if behavior changed. Never report unexecuted tests as passing.
