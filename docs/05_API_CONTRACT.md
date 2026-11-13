# REST API contract — draft v0.1

**Base:** `/api/v1` • `application/json` • UUID IDs • ISO-8601 UTC times. OpenAPI schema generated from DRF and committed/checked in CI when the implementation exists.

## Response conventions
Success returns explicit serializers, never accidental Django internals. Paginated collection: `{"results":[],"next":null,"count":0}` (count can be omitted for cursor pagination if documented). Error:
```json
{"error":{"code":"ORDER_CONFLICT","message":"Order cannot transition from its current state.","request_id":"uuid"}}
```
Error codes stable; messages informational. Validation returns `400`; unauthenticated `401`; forbidden `403` or masked `404` for sensitive cross-tenant objects (choose consistently); missing `404`; conflict `409`; throttle `429`. Do not include tracebacks.

## Authentication baseline (development choice)
DRF session authentication with CSRF for browser/admin and an explicitly reviewed mobile authentication transport (token scheme **TBD before Flutter login**). Use Django's secure password hashing and throttling. Never deliver a production mobile access/refresh implementation by guessing. Endpoints below assume an authenticated user principal regardless of transport.

## Public catalog
| Method | Route | Purpose |
|---|---|---|
| GET | `/stores` | list active stores |
| GET | `/stores/{store_id}` | read public store |
| GET | `/products?store_id=&search=&page=` | list published products |
| GET | `/products/{product_id}` | public product detail |

## Accounts and sellers
| Method | Route | Auth | Purpose |
|---|---|---|---|
| POST | `/auth/register` | public | create customer account |
| POST | `/auth/login` | public | start authenticated session (transport TBD) |
| POST | `/auth/logout` | user | revoke/end session |
| GET | `/me` | user | profile + roles |
| POST | `/seller/stores` | seller | create store |
| PATCH | `/seller/stores/{id}` | store member | edit own store |
| POST | `/seller/stores/{id}/products` | store member | create product |
| PATCH | `/seller/products/{id}` | store member | edit own product |
| PUT | `/seller/products/{id}/inventory` | store member | adjust stock via auditable operation |

## Cart and orders
| Method | Route | Auth | Notes |
|---|---|---|---|
| GET | `/cart` | customer | active cart |
| PUT | `/cart/items/{product_id}` | customer | `{ "quantity": 2 }`, zero may remove if documented |
| DELETE | `/cart/items/{product_id}` | customer | remove line |
| POST | `/orders` | customer | checkout, requires `Idempotency-Key` |
| GET | `/orders` | customer | own orders |
| GET | `/orders/{id}` | customer or authorized seller | scoped detail |
| POST | `/orders/{id}/cancel` | customer/system | permitted pending cancellation |
| POST | `/seller/orders/{id}/accept` | store member | PAID → ACCEPTED |
| POST | `/seller/orders/{id}/prepare` | store member | ACCEPTED → PREPARING |
| POST | `/seller/orders/{id}/ready` | store member | PREPARING → READY_FOR_PICKUP |
| GET | `/seller/stores/{id}/orders` | store member | own store orders |

### Checkout request
`POST /api/v1/orders` header `Idempotency-Key: <random-unique-value>`
```json
{"cart_id":"uuid","delivery_address_id":"uuid","shipping_option_id":"standard"}
```
**Note:** persistent address and shipping-option models are not yet frozen. Initial implementation may use validated `delivery_address` snapshot with a fixed mock shipping option, after an ADR. Never accept prices/totals from client as authoritative.

Response `201`:
```json
{"id":"uuid","status":"PAYMENT_PENDING","currency":"USD","totals":{"subtotal":"39.98","shipping":"4.00","tax":"0.00","discount":"0.00","grand_total":"43.98"},"payment":{"attempt_id":"uuid","status":"PENDING"}}
```
Same idempotency key + same normalized payload returns original result; same key + changed payload returns `409 IDEMPOTENCY_CONFLICT`. Concurrent duplicates must be serialized at DB level.

## Fake payment API (dev/test only)
`POST /api/v1/dev/payments/{attempt_id}/simulate` with `{ "outcome": "succeeded" | "failed" }`; accessible **only** when fake provider enabled and caller authorized as test/admin, not publicly exposed in production. Provider event handler is internal and deduplicates by event ID. A real provider webhook route will be designed later with signature verification, replay window and scope.

## Future logistics
`GET /courier/deliveries`, `POST /courier/deliveries/{id}/pickup`, `POST /courier/deliveries/{id}/in-transit`, `POST /courier/deliveries/{id}/complete`. No anonymous dispatch or arbitrary courier assignment.

## API contract tests
Cover valid flows, malformed quantity, forged price, unauthorized seller/customer lookup, duplicate `Idempotency-Key`, conflicting checkout, invalid order transitions, missing and duplicate webhook events, throttling, and 5xx scrubbing.
