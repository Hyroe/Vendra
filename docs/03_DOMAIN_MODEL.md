# Domain model, invariants and state machines

## Core aggregates
- **Store**: merchant-managed business unit, currency, active state, memberships.
- **Product**: store-owned catalog item with publish status and price; **Inventory** tracks quantity for one product.
- **Cart**: customer-owned, one store; **CartItem** references product and requested quantity.
- **Order**: customer/store/currency/status/totals/address snapshot; **OrderItem** stores product/title/SKU/price/quantity snapshots.
- **PaymentAttempt**: provider, opaque provider reference, amount/currency, state, unique idempotency identifiers and events.
- **Delivery** (later): order assignment, courier, state, timestamps; immutable **DeliveryEvent** history.

## Money
Use `Decimal` in Python with explicit decimal precision and currencies in ISO 4217 format. Persist decimal monetary columns (`NUMERIC(12,2)` for initial USD-focused MVP), never binary float. At provider boundary convert after validation to integer minor units according to currency exponent. Shipping/tax computation is an explicit service; initial tests may configure zero tax and fixed shipping, never silently assume this works in all jurisdictions.

## Order creation invariant
- Customer and cart ownership verified by authenticated principal.
- All cart lines belong to one eligible active store; products are published and currently sellable.
- Snapshot each product title/SKU/unit price at the time of checkout.
- Compute subtotal + shipping + tax − discounts = grand total; initial MVP discounts=0.
- Reserve stock and persist `Order`, `OrderItem`, `PaymentAttempt`/pending intent metadata, audit and outbox atomically; external payment attempt can be initiated after commit.
- No implicit checkout for an empty cart or quantity <= 0.

## Inventory semantics
`on_hand` = physically available gross units, `reserved` = units committed to unpaid orders. `available = on_hand - reserved`. At order creation: increase `reserved` only when sufficient available. On successful payment: decrease `reserved` and `on_hand` (stock becomes sold). On cancellation/expiry/failure before payment: decrease `reserved` only. Each reservation has a unique `(order_item, product)` identity and single terminal application to support retries.

## Order state machine
```
CREATED → PAYMENT_PENDING → PAID → ACCEPTED → PREPARING → READY_FOR_PICKUP
   └───────────────→ CANCELLED       │                      │
                   PAYMENT_FAILED     └──(policy) CANCELLED  └── later logistics
PAID/ACCEPTED/... → refund/cancel paths only through explicit approved policy
```
The conceptual earlier flow includes `PICKED_UP`, `IN_TRANSIT`, `DELIVERED`, but delivery states are tracked on `Delivery` after logistics is introduced; the order may project a fulfillment status. **Do not independently edit order and delivery states without a defined synchronization service.**

### Transition policy v0.1
| From | To | Actor / condition |
|---|---|---|
| CREATED | PAYMENT_PENDING | system after atomic checkout |
| PAYMENT_PENDING | PAID | payment service after verified success |
| PAYMENT_PENDING | PAYMENT_FAILED | payment service after final failure |
| PAYMENT_PENDING | CANCELLED | customer/system before payment, with release |
| PAID | ACCEPTED | authorized store operator |
| ACCEPTED | PREPARING | authorized store operator |
| PREPARING | READY_FOR_PICKUP | authorized store operator |
| PAYMENT_FAILED | — | terminal for MVP; new checkout required |
| CANCELLED | — | terminal for MVP; refund flow later |
| READY_FOR_PICKUP | — | MVP seller terminal; logistics introduced later |

Disallow all other transitions. Never silently use last-write-wins. All transitions emit state-change history and an audit event.

## PaymentAttempt states
`INITIATED → PENDING → SUCCEEDED | FAILED | CANCELLED`; `SUCCEEDED` is terminal for the attempt. Duplicate successful provider events are no-ops and are recorded/deduplicated. A payment attempt may only confirm an order if amount, currency, ownership/reference, provider verification, and current order state are consistent. Late success after expiry/cancellation goes to exception/reconciliation for follow-up—not automatic reopening or silent loss.

## Delivery (later)
`UNASSIGNED → ASSIGNED → PICKED_UP → IN_TRANSIT → DELIVERED`; optional `FAILED`, `CANCELLED` with explicit policies. Only assigned courier may mutate pickup/delivery status. Completed deliveries immutable except audited administrative remediation.

## Multi-tenancy and privacy
Store memberships/roles scope seller resources. Customer owns cart and orders. Courier sees only explicitly assigned deliveries. Order address data is sensitive, accessible only where needed, retention limited. User-supplied IDs are never authorization evidence.
