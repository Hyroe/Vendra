# ADR-016: Mobile authentication transport for development

**Status:** proposed (development default, not production-approved)

## Context

OPEN-001 requires a revocable, secure mobile authentication model. The Flutter
client milestone (M5) cannot wait indefinitely, but the backend already uses
Django session authentication as its development default. No refresh-token or
secure-storage design has been threat-modeled yet.

## Decision

- For M5 development only, Flutter uses the existing backend session-cookie
  transport with CSRF protection for unsafe methods.
- Credentials are stored only in platform secure storage after a reviewed
  implementation; until then, development builds may use in-memory session state
  and must not be distributed.
- Production mobile authentication remains blocked until OPEN-001 is resolved with
  short-lived credentials, refresh rotation, revocation and device storage review.
- The backend does not introduce a separate mobile token scheme in M5.

## Consequences

- M5 can exercise catalog, cart, checkout and orders against the running backend.
- The Flutter client must handle 401/403 and session expiry.
- No claim of production mobile security is made.