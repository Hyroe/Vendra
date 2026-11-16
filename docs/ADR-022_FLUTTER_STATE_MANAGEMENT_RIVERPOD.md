# ADR-022: Flutter state management with Riverpod

**Status:** accepted

## Context

OPEN-002 required choosing a Flutter state-management approach. The app needs
dependency injection for `ApiClient`, session bootstrap and future feature state
without overengineering.

## Decision

- Use `flutter_riverpod` as the app-wide state-management and dependency-injection
  mechanism.
- `apiClientProvider` is overridden at startup with the instance that has loaded
  secure tokens.
- Widgets consume providers via `ConsumerWidget` / `ConsumerStatefulWidget`.
- Complex feature state remains simple in M5; Riverpod is the foundation for later
  feature controllers.

## Consequences

- The app no longer passes `ApiClient` manually through constructors.
- Tests can override `apiClientProvider` with fakes.
- Future features can use `Notifier`/`AsyncNotifier` without changing the app
  bootstrap.