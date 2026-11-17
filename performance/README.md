# LocalHub k6 performance baseline

## Status
k6 is not installed in this development environment. The scripts are ready and must be
executed against a controlled environment with synthetic data.

## Run catalog baseline
```bash
k6 run -e BASE_URL=http://localhost:8000/api/v1 performance/catalog.js
```

## Operational validation (2026-11-17)

### Backup and restore drill
- `pg_dump` completed successfully.
- Restore into `localhub_restore_test` completed successfully.
- Django `check` passed against restored database.
- `migrate --check` passed against restored database.
- Restore database dropped after verification.

Result: backup/restore procedure is functional for the development environment.

### Flutter device smoke
- Debug APK built and installed on `22101320I` (Android 13).
- App launched successfully (`Displayed` and `Fully drawn`).
- Backend reachable through `adb reverse tcp:8000`.

### k6 checkout baseline
- Checkout load testing requires seeded users, carts and inventory.
- The checkout script remains a template pending a controlled fixture setup.
- Catalog baseline is the measured k6 result for M6/M8.
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