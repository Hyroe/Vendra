# ADR-012: Identity and store authorization baseline

**Status:** accepted

## Context

M1 introduces customer registration, session login/logout, `/me`, and seller store
CRUD. The API contract specifies routes but leaves auth transport, store roles,
slug generation, currency validation and cross-tenant response behavior as
development details.

## Decision

- Use **Django session authentication** as the development default for M1. It is
  already the documented browser/admin baseline and is marked non-production for
  mobile until OPEN-001 is resolved.
- Registration creates a customer account and does not automatically create a
  session. Login establishes the session and logout revokes it.
- `GET /me` returns profile, derived roles (`CUSTOMER`, `SELLER` when the user has
  an active store membership, `ADMIN` when staff) and active store memberships.
- Store access is governed by `StoreMembership`, not a global seller flag.
- Store creation is available to any authenticated user and creates an `OWNER`
  membership in the same transaction.
- Store edits are limited to users with an active membership for that store.
- Slugs are generated server-side from the store name and made unique with a
  numeric suffix.
- Currency is normalized to uppercase and validated as a 3-letter code.
- Cross-tenant store access returns `404 NOT_FOUND` rather than `403` to avoid
  disclosing resource existence.

## Alternatives considered

- **Issue mobile tokens now:** rejected because OPEN-001 is explicitly unresolved.
- **Global seller role on User:** rejected because store membership is the documented
  authorization boundary.
- **Return 403 for cross-tenant stores:** rejected for object reads/edits because
  masked 404 reduces enumeration risk.

## Consequences

- Flutter cannot rely on this transport until OPEN-001 is closed; M5 remains gated.
- Browser/admin clients must handle CSRF for unsafe methods.
- Store ownership cannot be transferred in M1; only the creating user is OWNER.
- All store reads and writes are tenant-scoped in selectors and views.

## Security and data implications

- Passwords use Django's configured password validators and hashing.
- Login has a scoped throttle (`login`, 10/min by default).
- Registration has a scoped throttle (`register`, 5/min by default).
- Store names, slugs and currencies are validated; ownership is never accepted
  from the client.

## Migration plan

M1 adds `stores.0001_initial` (`Store`, `StoreMembership`) after the M0 user
migration.

## Tests and observable evidence

- Auth API tests: register, duplicate email, login success/failure, `/me`,
  logout, unauthenticated access.
- Store API tests: public list/detail, creation, ownership edit, cross-tenant
  denial, inactive store visibility.
- Integration test: store and membership persistence.
- Unit test: unique slug generation.
- Verified with `pytest`: 46 passed after M1.