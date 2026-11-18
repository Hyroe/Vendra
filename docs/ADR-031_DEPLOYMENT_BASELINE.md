# ADR-031: Deployment baseline

**Status:** accepted (development baseline; cloud provider undecided)

## Context

OPEN-009 requires a deployment approach. Production cloud selection depends on
non-functional requirements and budget, but the application already has Docker,
Gunicorn, health checks and production settings.

## Decision

- Use Docker Compose as the portable deployment baseline.
- Use Gunicorn for the API and Celery for workers.
- Use PostgreSQL, Redis and RabbitMQ as separate runtime units.
- Use `config.settings.production` with required secret validation.
- Provide `docker-compose.prod.yml` as a production-shaped override.
- Keep cloud provider selection open (OPEN-009 remains partially open for
  provider-specific choices).

## Consequences

- The same compose baseline can run locally or on a VM/container host.
- Kubernetes, service mesh and multi-region work remain out of scope.
- Cloud-specific hardening must be reviewed before production.