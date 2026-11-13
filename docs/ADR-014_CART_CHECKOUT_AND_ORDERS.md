# ADR-014: Cart, checkout and order baseline

**Status:** accepted

## Context

M3 implements one-store carts, server-side checkout pricing, atomic inventory
reservation, order state transitions and idempotent checkout. The API contract
specifies checkout shape and idempotency behavior, while cart storage, shipping
calculation and concurrency details are implementation decisions.

## Decision

- A cart belongs to one customer and one store. Adding an item from a different
  store is rejected with `409 CART_STORE_MISMATCH`.
- Cart totals are computed server-side from current product prices.
- Checkout requires an `Idempotency-Key` header and records request hashes in
  `ApiIdempotencyKey`.
- Repeating the same key and payload returns the original result; changing the
  payload returns `409 IDEMPOTENCY_CONFLICT`.
- Inventory rows are locked in stable product-id order before availability checks
  and reservation.
- Checkout creates an order in `PAYMENT_PENDING`, reserves stock, creates order
  items, reservation records, a payment attempt and a transition record.
- Shipping uses a fixed development default of `4.00`; tax and discounts are zero
  in M3.
- Pending orders can be cancelled by the customer, releasing reserved stock.
- Concurrency is verified with a threaded PostgreSQL integration test.

## Consequences

- Cart and checkout remain synchronous in M3; asynchronous payment work arrives
  in M4.
- The fixed shipping fee is a development default and must be revisited before
  real sales (OPEN-003).
- `PaymentAttempt` exists but fake payment confirmation is implemented in M4.

## Tests and observable evidence

- API tests: cart, checkout, idempotency, insufficient stock, cancellation,
  order listing/detail.
- Concurrency test: two buyers racing for one unit produce exactly one success.
- Verified with `pytest`: 69 passed after M3.