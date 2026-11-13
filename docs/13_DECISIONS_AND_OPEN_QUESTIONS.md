# Architecture decisions and unresolved issues

## Accepted for planning baseline v0.1
| ID | Decision | Reason |
|---|---|---|
| ADR-001 | Django/DRF modular monolith | transactional correctness and manageable complexity |
| ADR-002 | PostgreSQL authoritative for business state | concurrency and durable integrity |
| ADR-003 | Celery + RabbitMQ for background execution | explicit async workflow practice |
| ADR-004 | Redis only for cache/throttling/ephemeral state | avoid split-brain financial state |
| ADR-005 | Flutter single role-aware app initially | reduce mobile complexity |
| ADR-006 | Fake payment adapter first | test money workflows without live charges |
| ADR-007 | One store per cart/order for MVP | avoid payment splitting/fulfillment complexity |
| ADR-008 | Transactional outbox for critical events | reliable DB/message boundary |
| ADR-009 | Order snapshots and explicit finite-state machine | preserve accounting correctness |
| ADR-010 | k6 and Sentry | measurable performance/observability |
| ADR-011 | Bootstrap baseline: Python 3.13, Django 5.2 LTS, Gunicorn, `/healthz` + `/readyz`, `X-Request-ID`, JSON error envelope, custom User in first migration, M0 Compose = `db` + `api` | reproducible engineering baseline without unused infrastructure |

## Open decisions — do not silently invent a production policy
| ID | Issue | Suggested development default / required decision |
|---|---|---|
| OPEN-001 | Flutter auth/session model | choose and threat-model revocable mobile credentials; avoid insecure token persistence |
| OPEN-002 | Flutter state management | Riverpod or Bloc after small spike |
| OPEN-003 | Tax and shipping | fixed mock shipping + zero tax in isolated fixtures only; replace with jurisdiction-aware requirements before real sales |
| OPEN-004 | Address storage / checkout request | define Address and ShippingOption or validated address snapshot; update API and privacy policy |
| OPEN-005 | Currency support | USD fixtures; store currency configured, payment capability constrained |
| OPEN-006 | Payment refund/cancel after PAID | business policy and state transitions required before implementing |
| OPEN-007 | Real payment gateway | Stripe or alternative, after regional/legal review |
| OPEN-008 | Fulfillment after READY_FOR_PICKUP | synchronize order projection and Delivery without divergent status |
| OPEN-009 | Production cloud/deployment | select when nonfunctional requirements and budget known |
| OPEN-010 | Privacy/retention and data deletion | needs business/legal decision before production |
| OPEN-011 | Seller onboarding/verification | MVP sandbox registration; real marketplace requires compliance/abuse design |
| OPEN-012 | Idempotency response retention | define bounded retention and response storage/redaction policy |

## ADR proposal template
```
# ADR-XXX: title
Status: proposed | accepted | superseded
Context:
Decision:
Alternatives:
Consequences:
Security and data implications:
Migration plan:
Tests and observable evidence:
```

A coding agent may implement an explicit **development default** when the milestone requires it, but must mark it as non-production and add a recorded ADR; it must not present an open decision as already accepted.
