# ADR-020: Real payment provider and operational hardening (proposed)

**Status:** proposed

## Context

M8 covers real payment-provider integration, signed webhooks, reconciliation,
refund/cancellation policy, recovery, backup/restore and deployment capacity.
The provider, region, legal requirements and refund policy are open decisions.

## Decision

No production payment provider is selected in this milestone. The repository
implements only a fake adapter and reconciliation reporting. A real provider
must be selected through ADR before implementation.

Proposed webhook requirements:
- Verify provider signature and timestamp.
- Deduplicate by provider event ID.
- Validate provider account, amount, currency and attempt mapping.
- Apply mutations only in a database transaction.
- Record every event in `PaymentEvent`.
- Route late or inconsistent events to reconciliation instead of automatic
  state overwrite.

## Consequences

- M8 remains a hardening and review milestone, not a production-readiness claim.
- Refund and post-payment cancellation require an approved policy before code.
- Deployment and capacity work is documented but not claimed as verified.