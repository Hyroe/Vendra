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
| ADR-012 | Identity/store authorization baseline: session auth dev default, membership-governed stores, server-side slugs/currency, masked 404 for cross-tenant access | secure M1 baseline while OPEN-001 remains open |
| ADR-013 | Catalog/inventory baseline: store-scoped products, companion inventory, publication gate, server-side filters/search, absolute auditable stock adjustment | M2 catalog behavior without premature caching/reservation |
| ADR-014 | Cart/checkout/orders baseline: one-store carts, server-side totals, row-locked reservation, idempotent checkout, pending cancellation with release | M3 checkout correctness and retry safety |
| ADR-015 | Fake payments/outbox baseline: staff-only simulation, provider-event dedup, atomic paid/failed transitions, same-transaction outbox, Celery/RabbitMQ/Redis and skip-locked dispatch | M4 reliable async payment workflow |
| ADR-016 | Mobile authentication transport development default: session cookies + CSRF, no production token scheme | M5 unblocks Flutter without resolving OPEN-001 |
| ADR-017 | Flutter customer app baseline: http client, session/CSRF, feature pages, API exception parsing, Sentry dev default | M5 mobile baseline while OPEN-001 remains open |
| ADR-018 | Seller fulfillment/observability baseline: explicit transitions, Redis cache/rate limits, JSON logs, Sentry, Bandit/pip-audit, k6 scripts | M6 operational baseline without production-readiness claims |
| ADR-019 | Logistics baseline: delivery assignment by store member, courier-only transitions, event history, separate delivery state | M7 courier lifecycle without automatic dispatch |
| ADR-020 | Real payment provider and operational hardening proposed: no provider selected, webhook/reconciliation requirements, refund policy pending | M8 review and hardening without production claim |
| ADR-021 | Mobile authentication tokens: JWT access + rotating opaque refresh, secure storage, session revocation | closes OPEN-001 as a development default |
| ADR-022 | Flutter state management: Riverpod for dependency injection and feature state | closes OPEN-002 with a scalable but simple baseline |
| ADR-023 | Address and ShippingOption: reusable customer addresses, store shipping methods, additive snapshots, backward-compatible checkout | closes OPEN-004 as an additive evolution |
| ADR-024 | Tax and shipping calculation: dedicated pricing service, shipping from ShippingOption or development fallback, explicit zero-tax development default | closes OPEN-003 as a development default |
| ADR-025 | Cancellation and refund policy: only PAYMENT_PENDING orders can be cancelled; no refunds or post-payment cancellation in MVP | closes OPEN-006 for MVP scope |
| ADR-026 | Order/delivery synchronization: READY_FOR_PICKUP -> DELIVERED only through sync service, idempotent completion | closes OPEN-008 for delivery completion |

## Provisionally resolved for development (not production-approved)
| ID | Issue | Development default / ADR |
|---|---|---|
| OPEN-001 | Flutter auth/session model | JWT access + rotating refresh tokens, secure storage, session revocation (ADR-021). Production security review still required. |
| OPEN-002 | Flutter state management | Riverpod for dependency injection and feature state (ADR-022). |
| OPEN-003 | Tax and shipping | Pricing service with shipping from ShippingOption or development fallback; tax explicitly zero in development (ADR-024). Production tax policy remains open. |
| OPEN-004 | Address storage / checkout request | Address and ShippingOption models with immutable order snapshots (ADR-023). |
| OPEN-006 | Payment refund/cancel after PAID | MVP allows cancellation only for PAYMENT_PENDING orders; no refunds or post-payment cancellation (ADR-025). |
| OPEN-008 | Fulfillment after READY_FOR_PICKUP | Delivery completion synchronizes Order to DELIVERED through sync_order_with_delivery (ADR-026). |

## Open decisions — do not silently invent a production policy
| ID | Issue | Suggested development default / required decision |
|---|---|---|

| OPEN-007 | Real payment gateway | Stripe or alternative, after regional/legal review |
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
