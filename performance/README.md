# LocalHub k6 performance baseline

## Status
k6 is not installed in this development environment. The scripts are ready and must be
executed against a controlled environment with synthetic data.

## Run catalog baseline
```bash
k6 run -e BASE_URL=http://localhost:8000/api/v1 performance/catalog.js
```

## Run checkout baseline
```bash
k6 run -e BASE_URL=http://localhost:8000/api/v1 -e PRODUCT_ID=<uuid> performance/checkout.js
```

## Latest controlled run (2026-11-15)

Environment:
- Backend: Django 5.2.19 development settings with test throttle overrides
- Database: PostgreSQL 17 (Docker)
- Cache/rate limit: LocMem (test settings)
- k6: v0.55.0, Windows/amd64
- Git SHA: pending commit

Catalog baseline (`performance/catalog.js`):
- VUs: ramp 10 → 50 → 100, 2m30s
- Requests: 5533 (36.75 req/s)
- `http_req_failed`: 0.00%
- `http_req_duration` p95: 37.78 ms
- `{type:catalog}` p95: 37.78 ms
- Threshold `p(95)<300`: passed

Result: catalog endpoint is comfortably below the 300 ms p95 target under the
documented controlled workload.
Each run must record:
- Git SHA
- Environment and dataset size
- VUs and duration
- p50/p95/p99 latency
- RPS and error classification
- PostgreSQL CPU/query observations
- Queue depth and worker retry counts
- Regressions and next hypotheses

## Exit criterion
M6 requires a documented k6 report. Until k6 is available, this document is the
placeholder and the scripts are the executable artifact.