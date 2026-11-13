# Product requirements — v0.1

## Vision
LocalHub allows independent local merchants to sell products through one mobile marketplace, with customers placing orders and optional courier fulfillment. This is a technical learning/portfolio product, **not** a certified financial or logistics platform.

## Personas and authorization roles
- **CUSTOMER**: browse catalog, manage own cart, create/pay/view/cancel eligible orders.
- **SELLER**: operate own store(s), manage own catalog/inventory, accept/prepare associated orders.
- **COURIER**: view eligible assignments, report pickup/delivery for assigned deliveries (post-MVP).
- **ADMIN**: oversee moderated resources through audited administrative flows, never via an undocumented bypass.
A user may have multiple roles; store ownership/membership, not global `SELLER`, governs store resource access.

## MVP (milestones M0–M6)
1. Account registration/login, profiles and permissions.
2. Seller store and product CRUD with publish/unpublish and stock.
3. Customer product listing/search, cart and server-side checkout pricing.
4. Atomic stock reservation and order creation with an explicit state machine.
5. Fake payment authorization/confirmation with idempotency and reliable event dispatch.
6. Seller sees paid orders and can accept/prepare/mark ready; basic Flutter customer flows.
7. Core tests, security checks, Sentry, structured logging and a repeatable k6 baseline.

## Later (M7+)
Courier assignment, pickup/delivery tracking; refunds, admin workflows, real payment-provider integration behind an interface, push notifications, improved reporting, production operations.

## Explicit non-goals for MVP
Real money transfer, storage of card data, multi-seller single-order splitting, tax engine, dynamic pricing/promotions, automatic dispatch optimization, live geolocation, real-time chat, returns management, cross-border commerce.

## Product choices for v0.1
- One **order belongs to exactly one store**. A cart is scoped to one store. Cross-store checkout is rejected rather than silently split.
- One currency per store/order; initial development fixture currency is `USD` (configurable). Do not assume a global fixed tax/shipping rule.
- Checkout uses snapshot product details/prices and a shipping-fee quote; amounts are calculated server-side.
- Inventory is reserved atomically when order is created and released on payment failure, explicit cancellation, or expiry.
- Payment is simulated via a controllable fake provider in development/test; no live charges.
- Delivery is optional for early orders; logistics lifecycle is introduced in a later milestone.

## Key functional acceptance criteria
- A non-authenticated visitor can browse public active products.
- A customer can create an order only from their own cart, containing published available products in one active store.
- A seller can modify only products/stock for stores they manage.
- Sellers see only orders for stores to which they have operational access.
- Order totals and individual line prices are immutable snapshots once created.
- Repeated checkout retries do not create another order when idempotency key and normalized payload match.
- A successful fake payment moves a pending order to `PAID` exactly once.
- Stock never drops below zero during concurrent checkout.
- A customer can retrieve only their own nonpublic order details.

## Quality goals (initial targets, not measured results)
- For a controlled test environment and stated workload: catalog `GET` p95 < 300 ms; checkout `POST` p95 < 800 ms; HTTP error rate < 1% (excluding expected 4xx). Revisit after baseline measurements.
- Every critical mutation has an auditable event and a test for unauthorized access.
- A failed worker can retry an event without duplicating the business result.

## User journeys
**Buyer:** register → browse → cart → checkout → pending payment → simulated success → paid order → seller processing.  
**Merchant:** register seller role → create store → publish product → update stock → receive paid order → accept → prepare → mark ready.  
**Courier (later):** claim authorized assignment → pickup → transit → delivered.
