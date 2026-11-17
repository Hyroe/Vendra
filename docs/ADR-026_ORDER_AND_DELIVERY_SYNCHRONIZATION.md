# ADR-026: Order and delivery synchronization

**Status:** accepted

## Context

OPEN-008 requires that order and delivery states do not diverge after
`READY_FOR_PICKUP`. The order state machine previously stopped at
`READY_FOR_PICKUP`, while the delivery lifecycle can complete independently.

## Decision

- Add `DELIVERED` to `OrderStatus`.
- Allow `READY_FOR_PICKUP -> DELIVERED` only through `sync_order_with_delivery`.
- When a courier completes a delivery, the synchronization service updates the
  order to `DELIVERED` and records an `OrderTransition` and outbox event.
- If the order is already `DELIVERED`, synchronization is idempotent.
- If the order is not `READY_FOR_PICKUP`, synchronization does not mutate it.
- Delivery failures or cancellations do not automatically change the order state
  in this milestone.

## Consequences

- Order and delivery remain separate aggregates, but completion is synchronized.
- Late or inconsistent states are visible through reconciliation.
- Future cancellation/refund policies must account for delivered orders.

## Tests and observable evidence

- Logistics API test verifies the order becomes `DELIVERED` after completion.
- Verified with `pytest`: 89 passed after Open-008.