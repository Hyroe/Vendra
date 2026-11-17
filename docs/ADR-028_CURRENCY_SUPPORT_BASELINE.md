# ADR-028: Currency support baseline

**Status:** accepted

## Context

OPEN-005 requires defined currency support. The store currency is currently a
free-form three-letter string and checkout assumes the store currency.

## Decision

- Supported store currencies are limited to `USD`, `EUR` and `GBP` in M5+.
- Store creation and updates normalize currency to uppercase and reject any other
  code with `VALIDATION_ERROR`.
- Orders use the store currency at checkout.
- Payment amount conversion to minor units remains provider-specific and is not
  implemented for real providers.
- Production currency expansion requires ADR and provider capability review.

## Consequences

- Existing stores with non-supported currency values must be migrated before
  deploying this change.
- The system remains USD-first for development fixtures.
- Real multi-currency payments require provider review and exchange handling.

## Tests and observable evidence

- API test: `usd` is normalized and accepted; `JPY` is rejected.
- Serializer unit tests: case normalization and unsupported rejection.
- Verified with `pytest`: 93 passed after Open-005.