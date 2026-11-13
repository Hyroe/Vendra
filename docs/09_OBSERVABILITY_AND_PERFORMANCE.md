# Observability and performance

## Signals
- **Errors:** Sentry for Django/DRF, Celery, Flutter; environment and release tags; scrub PII/secrets.
- **Structured logs:** JSON with `timestamp`, `level`, `event`, `request_id`, `actor_id` when allowed, `duration_ms`, `status_code`; avoid raw bodies.
- **Metrics:** request count/latency/error rate by route (low-cardinality), DB query latency, order checkout success/failure, outbox age/backlog, queue depth, worker retry/failures, payment reconciliation issues and inventory conflicts.
- **Tracing:** propagate request/correlation IDs into outbox event, task and error reports. Do not place user data in span names or metric labels.

## Early SLO proposals, not achieved claims
| Operation | Target under documented controlled workload |
|---|---|
| GET `/products` | p95 < 300 ms |
| POST `/orders` | p95 < 800 ms |
| API unexpected 5xx | < 1% requests |
| Outbox publishing | 99% dispatched < 30 s when broker healthy |
These are initial hypotheses. Benchmark hardware, fixture volumes, concurrency and geography must be recorded before interpreting results.

## k6 scripts
Store versioned scripts in `performance/`. Scenarios: catalog browse/search (read-heavy), cart updates, checkout with fresh test identities/inventory, seller order listing. Ramp through e.g. 10/50/100 virtual users; 500 only after safe fixture capacity and environment review. Use synthetic data, isolate against staging, never load-test real payment APIs without authorization.

## Reports
Each load run records Git SHA, environment, dataset size, VUs, duration, thresholds, p50/p95/p99, RPS, error classification, PostgreSQL CPU/queries, queue depth, regressions and next hypotheses. Do not compare unlike environments as proof of optimization.

## Sample k6 threshold policy
Use `http_req_failed` plus endpoint-specific expected 4xx handling and `http_req_duration` percentile thresholds. Track business correctness (e.g. valid orders per checkout request), not latency alone.
