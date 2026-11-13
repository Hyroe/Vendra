# Test strategy and quality gates

## Pyramid
- **Unit:** domain transitions, pricing, permission helpers, serialization, fake provider, idempotency normalizer.
- **DB integration (pytest-django):** atomic checkout and reservation, order snapshots, payment callback, outbox worker processing, scoped querysets.
- **API integration (DRF test client):** auth/permissions/status codes/contracts, request validation, multiple roles.
- **Flutter tests:** widget/client/service tests plus critical end-to-end flows.
- **System:** Docker Compose with real PostgreSQL + RabbitMQ + Redis; execute a synthetic purchase and inspect persisted state.
- **Security/performance:** Bandit/pip-audit/OWASP ZAP baseline and controlled k6 suites.

## Mandatory cross-cutting cases
| ID | Scenario | Expected |
|---|---|---|
| AUTH-01 | customer reads someone else's order | denied, no data leakage |
| TENANT-01 | seller changes other store's product | denied |
| STOCK-01 | two buyers race for last unit | exactly one reservation succeeds |
| STOCK-02 | checkout rollback mid-transaction | inventory unchanged |
| PAY-01 | payment success delivered twice | exactly one paid transition/stock commit |
| PAY-02 | late success after expiry | reconciliation case, no silent reopen |
| ORD-01 | invalid state jump | 409 stable error |
| IDEMP-01 | same key + request repeated | same order/result |
| IDEMP-02 | same key + different request | 409 conflict |
| ASYNC-01 | broker down after order commit | outbox retained and eventually published |
| ASYNC-02 | duplicate worker message | no duplicate downstream side effect |
| SEC-01 | secret included in exception input | absent from logs/Sentry |

## Concurrency realism
Thread-only SQLite tests are not sufficient. Use isolated PostgreSQL test DB and separate transactions/connections for racing checkout/payment/expiry scenarios. Assert both persistence and API outcome. Ensure tests do not share mutable database state across parallel workers.

## CI minimum
1. Backend formatter/linter + import checks.
2. Migration drift check (`makemigrations --check --dry-run`).
3. Unit + DB integration tests with PostgreSQL service.
4. Security/dependency scans, fail at agreed severity policy.
5. Flutter analyze/tests once Flutter exists.
6. Smoke integration with broker/cache once introduced.
7. k6 baseline in separate controlled CI/manual workflow (not required for every tiny commit).

## Reporting
Always list tests actually executed, their results, skipped tests, and environmental limitations. Coverage percentage is not a substitute for critical behavioral tests.
