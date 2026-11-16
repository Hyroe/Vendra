# ADR-019: Logistics baseline

**Status:** accepted

## Context

M7 introduces courier delivery assignment and lifecycle transitions after an
order reaches `READY_FOR_PICKUP`. The API contract lists future courier routes
but leaves assignment and authorization details unspecified.

## Decision

- A `Delivery` is created and assigned by a store member when the order is ready.
- Only the assigned courier can perform `PICKED_UP`, `IN_TRANSIT` and `DELIVERED`.
- Unrelated couriers receive `404 NOT_FOUND`.
- Delivery transitions are recorded in `DeliveryEvent`.
- Assignment is restricted to store members for the order's store.
- Courier capability is a development default: any authenticated user can act as
  a courier. Production courier onboarding remains an open decision.
- Delivery creation does not block order payment or fulfillment completion.

## Consequences

- Delivery state is separate from order state; no order mutation occurs in M7.
- Courier authorization relies on assignment, not global roles.
- Notifications and automatic assignment are deferred.

## Tests and observable evidence

- API tests: happy-path delivery completion and unrelated courier denial.
- Verified with `pytest`: 78 passed after M7.