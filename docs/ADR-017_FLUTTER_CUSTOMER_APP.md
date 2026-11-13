# ADR-017: Flutter customer app baseline

**Status:** accepted

## Context

M5 delivers the customer-facing Flutter app. The client must use the backend's
stable API, handle session/CSRF, display backend-authoritative totals, and provide
retry-safe checkout. OPEN-001 remains unresolved for production mobile auth.

## Decision

- Flutter 3.50 project lives in `mobile/`.
- Dependencies are limited to `http` for API access and `shared_preferences` for
  future secure-session work; no state-management package is introduced in M5.
- `ApiClient` centralizes base URL, JSON encoding, CSRF token handling and stable
  `ApiException` parsing from the backend error envelope.
- Customer flows implemented: login, catalog list/search, product detail, cart,
  checkout with server-side idempotency key, and orders.
- Checkout uses a fresh `Idempotency-Key` per user action; retries for the same
  action should reuse the key (future hardening).
- The app targets the backend at `http://10.0.2.2:8000/api/v1` for Android
  emulator by default, overridable with `--dart-define=API_BASE_URL=...`.

## Consequences

- No Riverpod/Bloc in M5; simple `StatefulWidget` state is intentional.
- Secure storage of session credentials is not implemented; development only.
- E2E synthetic purchase against PostgreSQL requires running the backend and
  Flutter integration harness, which is documented as the M5 exit criterion.

## Tests and observable evidence

- `flutter analyze`: no errors (only deprecation/info lints).
- `flutter test`: 2 tests passed (app boot and API exception contract).
- Manual/API smoke verification is required before claiming the E2E exit.