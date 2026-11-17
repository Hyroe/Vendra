# ADR-025: Cancellation and refund policy

**Status:** accepted (MVP scope)

## Context

OPEN-006 asks what happens after payment. The product requirements explicitly
exclude returns management and refunds from MVP. The current state machine allows
cancellation only while an order is `PAYMENT_PENDING`.

## Decision

- For MVP, cancellation is allowed only for `PAYMENT_PENDING` orders.
- `PAID`, `ACCEPTED`, `PREPARING`, `READY_FOR_PICKUP` and later states cannot be
  cancelled through the customer or seller endpoints.
- Cancelling a pending order releases reserved inventory.
- No refunds, partial refunds or post-payment cancellation are implemented in
  MVP.
- Refunds require a separate approved policy, state transitions and provider
  reconciliation before implementation.

## Consequences

- Customers must create a new checkout after payment failure or cancellation.
- Inventory committed by a successful payment is not returned by cancellation.
- Future refund work must add explicit transitions and tests before endpoints.