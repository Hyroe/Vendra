# ADR-029: Privacy and data retention baseline

**Status:** accepted (development baseline; legal review required for production)

## Context

OPEN-010 requires a privacy and retention policy for personal data. LocalHub
stores customer emails, addresses, order address snapshots, seller/business data
and audit/security events.

## Decision

- Account data is retained while the account is active.
- Order and payment records are retained for 5 years as development baseline.
- Address records are retained until deleted by the user or 2 years of inactivity.
- Audit and security events are retained for 2 years.
- Idempotency responses follow ADR-027 retention.
- Deletion is user-initiated for accounts and addresses; order/payment history is
  retained to preserve financial integrity.
- PII is excluded from logs, Sentry and outbox payloads.
- Production retention must be reviewed by legal/privacy stakeholders.

## Consequences

- Soft deletion and export flows are not implemented in this milestone.
- Retention jobs are not automated yet; cleanup commands can be extended.
- The policy is explicit and non-production.

## Tests and observable evidence

- Existing tests confirm PII is not logged in error responses.
- This ADR is the policy artifact; operational deletion/export flows remain open.