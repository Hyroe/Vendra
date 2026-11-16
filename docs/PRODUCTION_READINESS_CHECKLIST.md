# Production readiness checklist — LocalHub

This checklist is a review artifact. Passing MVP tests does not imply production
readiness. Every item must be verified with evidence before a production claim.

## Authentication and authorization
- [ ] Mobile authentication transport finalized and threat-modeled (OPEN-001).
- [ ] Session/token revocation and device storage reviewed.
- [ ] Object- and store-scoped authorization tests pass for every resource.
- [ ] Cross-tenant access returns masked 404/403 consistently.

## Payments
- [ ] Real provider selected, reviewed and approved (OPEN-007).
- [ ] Signed webhook verification with replay protection.
- [ ] Reconciliation job run and reviewed.
- [ ] Refund/cancellation policy approved (OPEN-006).
- [ ] No card data handled or stored locally.

## Data and recovery
- [ ] Backup schedule and restore drill documented and tested.
- [ ] Database migration rollback strategy documented.
- [ ] Outbox backlog and dead-letter handling monitored.
- [ ] Retention and deletion policy approved (OPEN-010).

## Security
- [ ] `DEBUG=False`, secure cookies, HSTS and allowed hosts configured.
- [ ] Secrets in secret manager, not repository.
- [ ] Bandit and pip-audit pass at agreed severity.
- [ ] OWASP ZAP baseline run against staging.
- [ ] Sentry scrubbing verified by regression test.

## Operations
- [ ] Health and readiness endpoints monitored.
- [ ] Worker queues, retries and dead-letter queues configured.
- [ ] Outbox age and queue depth alerted.
- [ ] Capacity test with k6 report and thresholds.

## Verification rule
No production-readiness claim is valid without dated evidence for each checked item.