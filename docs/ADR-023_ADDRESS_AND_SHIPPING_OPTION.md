# ADR-023: Address and ShippingOption

**Status:** accepted

## Context

OPEN-004 requires reusable customer addresses and store shipping methods. The
current checkout accepts an ad-hoc address snapshot and a fixed mock shipping
fee. Historical orders must remain immutable when addresses or shipping prices
change.

## Decision

- Add `Address` owned by a customer, with normalized fields and an optional
  default flag.
- Add `ShippingOption` owned by a store, with a store-scoped code, name, price
  and active flag.
- Checkout accepts `delivery_address_id` and/or `shipping_option_id` while
  preserving the legacy `delivery_address` snapshot for compatibility.
- `Order.address_snapshot` remains an immutable copy of the selected address.
- Add `Order.shipping_option_snapshot` as an immutable copy of the selected
  shipping option.
- `Order.shipping_total` is fixed from the selected option or the development
  fallback at checkout time.
- Updating or deleting an `Address` does not alter historical orders.
- Updating or deactivating a `ShippingOption` does not alter historical orders.

## Consequences

- Address and shipping-option management adds customer and seller endpoints.
- Checkout remains backward compatible with existing clients and tests.
- Tax is still zero in M3/M4; shipping calculation becomes explicit in ADR-024.
- Address deletion is allowed because orders retain snapshots.

## Migration plan

M23 adds `accounts.Address` and `stores.ShippingOption`, plus the additive
`orders.Order.shipping_option_snapshot` field. No existing column is removed.