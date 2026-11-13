# PostgreSQL data model — implementation blueprint

**Status:** Proposed logical schema, not a generated Django migration. Field names/indices may be adjusted through reviewed migrations; preserve invariants and document changes.

## Entities
| Table/model | Essential fields | Constraints/indexes |
|---|---|---|
| `User` | UUID id, email, password hash, is_active, created_at | unique normalized email; use custom Django user from first migration |
| `Store` | UUID id, owner_id, name, slug, currency, status | unique slug; indexed owner/status |
| `StoreMembership` | user_id, store_id, role, active | unique (user,store), index (store,role) |
| `Product` | id, store_id, sku, name, description, unit_price, is_published, created_at | unique (store,sku), price >= 0; index (store,is_published) |
| `Inventory` | product_id PK, on_hand, reserved, updated_at | check on_hand >= 0, reserved >= 0, reserved <= on_hand |
| `Cart` | id, customer_id, store_id, updated_at | one active cart per customer/store or explicit single active cart policy |
| `CartItem` | cart_id, product_id, quantity | unique (cart,product), quantity > 0 |
| `Order` | id, customer_id, store_id, currency, status, subtotal, shipping_total, tax_total, discount_total, grand_total, address_snapshot, created_at | totals >= 0; indexed (customer,created_at), (store,status,created_at) |
| `OrderItem` | order_id, product_id nullable, sku_snapshot, title_snapshot, unit_price, quantity, line_total | quantity > 0, unit_price >= 0; immutable price/title snapshots |
| `InventoryReservation` | id, order_item_id, product_id, quantity, status | unique order_item; status RESERVED/COMMITTED/RELEASED |
| `PaymentAttempt` | id, order_id, provider, provider_ref, status, amount, currency, idempotency_key, created_at | unique scoped (provider,provider_ref) when provided; indexed order/status |
| `PaymentEvent` | provider, provider_event_id, payment_attempt_id, event_type, received_at, processed_at | unique (provider,provider_event_id) |
| `OrderTransition` | order_id, from_status, to_status, actor_id nullable, reason, created_at | index (order,created_at), append-only |
| `OutboxEvent` | id, aggregate_type, aggregate_id, event_type, schema_version, payload, created_at, published_at, attempt_count | index (published_at,created_at); append-only business payload |
| `ApiIdempotencyKey` | user_id, scope, key, request_hash, status, response_status, response_body, expires_at | unique (user,scope,key) |
| `AuditEvent` | id, actor_id nullable, action, target_type, target_id, request_id, safe_metadata, created_at | append-only; index (target_type,target_id), (created_at) |
| `Delivery` (later) | order_id unique, courier_id nullable, status, assigned_at, delivered_at | index (courier,status) |
| `DeliveryEvent` (later) | delivery_id, from_status, to_status, actor_id, created_at | append-only |

## Integrity
- Foreign keys use explicit on-delete strategies: protect orders and financial history from cascade deletion; soft-delete public-facing store/products where needed.
- Use database CHECK constraints for quantity and monetary nonnegativity; app validation complements, never replaces, constraints.
- Unique keys and transaction locks protect concurrency. Never infer payment uniqueness only from a callback timestamp.
- Normalize email and currency consistently; use timezone-aware UTC timestamps.
- JSONB snapshots and outbox payloads have schema versions; avoid placing full personal addresses in generic logs/outbox messages.
- Store secret-bearing application settings in environment/secret manager, not database fixtures.

## Recommended migration sequence
Custom User → Store + Membership → Product + Inventory → Cart + CartItem → Order + OrderItem + Reservation + Transitions → PaymentAttempt/Event + Idempotency → Outbox + Audit → Delivery models.

## Query and race review checklist
- Checkout locks inventory records in a stable sorted product-id order.
- Reserve once per order item; rollback entire operation if any line lacks stock.
- Payment callbacks lock payment attempt and order before transition/release/commit.
- Expiry and callbacks racing must resolve to one terminal outcome, with late successes handled by reconciliation.
- All seller queryset access is scoped to store membership; no bare `get(pk=...)` before ownership checks in sensitive handlers.
