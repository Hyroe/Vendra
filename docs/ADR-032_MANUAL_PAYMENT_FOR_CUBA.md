# ADR-032: Manual payment confirmation for Cuba

**Status:** accepted (development default; not production payment compliance)

## Context

OPEN-007 remains open for a real payment gateway. Global card providers are not
available for Cuban merchants. LocalHub needs a practical payment flow for the
Cuban market without handling card data.

## Decision

- Support manual payment confirmation for bank transfer or cash on pickup.
- The seller or an authorized store operator confirms that funds were received.
- Confirmation reuses the existing payment transition, reservation commit,
  audit and outbox flow.
- The provider value is `manual` and the event is deduplicated by provider event
  ID.
- Cryptocurrency is not implemented in MVP due to volatility, refund complexity,
  compliance uncertainty and low consumer adoption.
- Real gateway integration remains a separate future decision.

## Consequences

- Orders can be paid without a card gateway.
- Payment confirmation depends on seller action and is not instant.
- Manual payments still require clear operational policy and reconciliation.
- No card numbers or CVV are handled.