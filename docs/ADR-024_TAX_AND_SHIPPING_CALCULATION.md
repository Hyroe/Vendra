# ADR-024: Tax and shipping calculation

**Status:** accepted

## Context

OPEN-003 requires explicit tax and shipping calculation. The current checkout
calculates a fixed shipping fee inline and hard-codes zero tax. Address and
ShippingOption now exist, so totals should be calculated by a dedicated service.

## Decision

- Introduce `apps.orders.pricing` as the single owner of checkout totals.
- Shipping is resolved from an active `ShippingOption` belonging to the order's
  store. If none is available or the request uses the development `standard`
  fallback, the development default shipping fee of `4.00` is used.
- Tax is explicitly `0.00` in development. The tax function is isolated so a
  jurisdiction-aware implementation can replace it without changing checkout.
- Discounts remain `0.00` until promotions are introduced.
- Totals are calculated server-side from immutable product snapshots and the
  selected shipping option.
- Historical orders retain their stored totals and snapshots.

## Consequences

- Checkout no longer embeds pricing rules.
- Tax is not production-ready and must be revisited before real sales.
- Shipping options are store-scoped and auditable through their price field.
- Future tax engines can replace `calculate_tax_total` without changing the
  checkout transaction.

## Tests and observable evidence

- Unit tests for shipping resolution, fallback, tax default and total calculation.
- Existing checkout tests continue to pass.