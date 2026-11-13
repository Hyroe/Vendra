# ADR-013: Catalog and inventory baseline

**Status:** accepted

## Context

M2 introduces products, inventory, publication and public catalog search/filtering.
The API contract defines routes and pagination expectations but leaves payload
details, publication semantics and inventory adjustment shape as development
decisions.

## Decision

- `Product` belongs to exactly one `Store` and has a store-scoped unique SKU.
- `Inventory` is a one-to-one companion of `Product`, with `on_hand` and
  `reserved` counters and a database check that `reserved <= on_hand`.
- A product is publicly visible only when `is_published=True` and its store is
  `ACTIVE`.
- Sellers manage products only for stores where they have an active membership.
- `POST /seller/stores/{store_id}/products` creates the product and its inventory
  transactionally.
- `PUT /seller/products/{product_id}/inventory` sets `on_hand` absolutely and
  rejects values below `reserved`.
- Public catalog supports `store_id`, `search` (name/SKU) and page pagination.
- Cross-tenant product access returns `404 NOT_FOUND`.

## Consequences

- Inventory adjustments are auditable at service level; the formal `AuditEvent`
  table is introduced in a later milestone.
- Stock reservation logic is not part of M2; it arrives with M3 checkout.
- Public catalog remains cache-free in M2; Redis caching is introduced in M6.

## Tests and observable evidence

- API tests: creation, ownership, update, inventory adjustment, validation,
  publication visibility, filtering and search.
- Unit tests: inventory creation, reserved constraint, adjustment validation.
- Integration test: product and inventory persistence.
- Verified with `pytest`: 60 passed after M2.