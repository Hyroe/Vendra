# ADR-030: Seller onboarding and verification baseline

**Status:** accepted (development baseline)

## Context

OPEN-011 requires seller onboarding and verification. MVP currently allows any
authenticated user to create a store. Production marketplace compliance requires
a more rigorous process.

## Decision

- Add `verification_status`, `verified_at` and `verified_by` to `Store`.
- Default status is `UNVERIFIED`.
- Staff-only endpoint `POST /seller/stores/{store_id}/verify` marks a store
  `VERIFIED`.
- Verification metadata is auditable through the store record.
- Real seller onboarding, document collection and abuse prevention remain out of
  scope for MVP.

## Consequences

- Existing stores default to `UNVERIFIED`.
- No store behavior changes based on verification status in MVP.
- Production seller onboarding requires legal/compliance review before enforcement.