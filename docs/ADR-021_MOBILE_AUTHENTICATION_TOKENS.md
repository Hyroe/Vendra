# ADR-021: Mobile authentication tokens

**Status:** accepted (development default; production hardening pending)

## Context

OPEN-001 required a revocable mobile credential model. The backend previously used
session cookies only, which is not ideal for native mobile clients.

## Decision

- Mobile clients use short-lived JWT access tokens (15 minutes) and opaque refresh
  tokens (30 days).
- Refresh tokens are stored hashed in `MobileSession` and rotate on every refresh.
- Reuse of a rotated refresh token revokes the session.
- Sessions can be listed and revoked per user.
- Tokens are stored in `flutter_secure_storage` on the device.
- The mobile client retries once after a 401 by refreshing the access token.
- Session/cookie authentication remains available for browser/admin flows.

## Consequences

- Native mobile requests use `Authorization: Bearer <access>`.
- Mobile auth is now functional but still needs production hardening: secure
  storage review, biometrics, certificate pinning and threat modeling.
- `JWT_SECRET_KEY` must be configured separately in production.