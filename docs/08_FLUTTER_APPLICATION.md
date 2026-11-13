# Flutter client specification

## Target
One Flutter codebase with role-aware navigation: customer MVP first; seller screens second; courier screens later. Prefer repository/service abstractions, not direct HTTP from widgets. State management choice is **open** (Riverpod or Bloc are candidates), decide once in an ADR.

## Main flows
**Customer:** onboarding/login → browse stores/products → product detail → cart → checkout → payment result → own orders/details.  
**Seller:** select authorized store → products/inventory → paid order queue → accept/prepare/ready.  
**Courier (later):** assigned deliveries → pickup → in transit → confirm delivered.

## Suggested structure
```
mobile/lib/
  app/ (router, dependency injection, theme)
  core/ (api client, auth, errors, config)
  features/
    auth/
    catalog/
    cart/
    checkout/
    orders/
    seller/
    courier/
  shared/widgets/
```
Each feature contains presentation/domain/data layers when needed, without boilerplate for trivial views.

## Client responsibilities
- Use backend price totals as authoritative; display checkout quote and detect changed cart price before confirmation.
- Parse stable `error.code`, implement retry UX (network timeout ≠ failure), and reuse checkout idempotency key across retries for same intent.
- Store credentials only in reviewed secure platform storage, never plain preferences or logs. Authentication mechanism must be finalized first.
- Display only data allowed by current role and server response; UI hiding never replaces API authorization.
- Sentry captures crashes with redaction, consent/privacy choices as required; no full request-body breadcrumbs for checkout.
- Accessibility, loading/empty/error states, consistent currency formatting and offline-safe messaging.

## Flutter acceptance tests
Widget tests for catalog/cart/status; API integration tests against isolated backend/fake provider; end-to-end happy path; failure/retry path; role switching; unauthorized response; checkout duplicate tap disabled or same idempotency key; session expiry.
