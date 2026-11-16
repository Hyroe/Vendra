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

## Report template
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