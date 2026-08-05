---
name: angular-fundamentals
description: Use when registering providers in an Angular app or library (providedIn, providers, provideXxx()), choosing a provider scope, defining InjectionToken-based or typed provideXxx(config) configuration, setting up environment.ts files or runtime config loaded at bootstrap, or adopting standalone APIs, signals, inject(), strict null checks, or DestroyRef/takeUntilDestroyed teardown.
---

# Modern Angular Fundamentals

## When to Use

- Registering providers (`providedIn`, `providers: [...]`, `provideXxx()`) in any app, route, or component injector
- Choosing a provider scope (root singleton, route/lazy scope, component instance)
- Defining `InjectionToken`-based configuration and `provideXxx(config)` library APIs
- Setting up `environment.ts` files, build-time file replacement, or runtime config loaded at bootstrap
- Adopting standalone components, `inject()`, signals, strict null checks, or `DestroyRef`/`takeUntilDestroyed` teardown in new code

## Core Principles

- This skill is **agnostic across Angular surfaces** — standalone apps, libraries, and lazy-loaded routes all sit on these fundamentals. `angular-components` and `angular-state` build on top of them.
- **Token-first registration** — depend on an abstraction (an `abstract class` or `InjectionToken<T>`), not a concrete class, when the implementation should be substitutable for testing or decoration. TypeScript `interface`s don't exist at runtime, so they cannot be DI tokens — use an `abstract class` or `InjectionToken`.
- **No service locator** — never inject `Injector` to resolve dependencies manually in business logic. Use `inject()` (or constructor injection) for the dependencies you actually need.
- **Typed config over scattered lookups** — model configuration as a typed object provided via an `InjectionToken` and a `provideXxx(config)` function; do not read loose string keys all over the app.
- **Fail fast** — validate required configuration at bootstrap (via `provideAppInitializer` / `APP_INITIALIZER`) so misconfiguration surfaces at startup, not at first use.
- **Immutable configuration** — config objects use `readonly` members and are not mutated after provisioning.
- **Teardown flows everywhere** — long-lived subscriptions and async work are torn down with `takeUntilDestroyed()` / `DestroyRef`, and HTTP cancellation happens by unsubscribing.
- **Signal-first APIs** — author component surfaces with `input()`/`output()`/`model()` and signal queries (`viewChild()`/`contentChild()`), not decorators. Mark Angular-initialized members (`input`, `model`, `output`, queries) `readonly` so the framework-assigned value cannot be overwritten.

## Reference Index

- **[angular-version.md](references/angular-version.md)** — the version resolution cascade (explicit user directive → repo directive → latest stable, resolved at runtime); canonical for the whole Angular family
- **[dependency-injection.md](references/dependency-injection.md)** — provider scopes, `providedIn`, `InjectionToken`/abstract-class tokens, `inject()`, multi providers, anti-service-locator
- **[typed-configuration.md](references/typed-configuration.md)** — typed configuration objects, `provideXxx(config)` library APIs, validation at bootstrap, environment- vs runtime-loaded config
- **[configuration.md](references/configuration.md)** — `environment.ts` files, build-time `fileReplacements`, runtime config from `assets/config.json`, and why front-end apps have no real secrets
- **[modern-patterns.md](references/modern-patterns.md)** — standalone APIs, signals, `inject()`, strict null checks, discriminated unions, `DestroyRef`/`takeUntilDestroyed`

## Related Skills

- **[angular-components](../angular-components/SKILL.md)** — Builds the UI layer (components, templates, routing, forms, `HttpClient`) on these DI and config fundamentals
- **[angular-library-builder](../angular-library-builder/SKILL.md)** — Generates Angular libraries / client SDKs (`provideXxx()` extensions, typed `HttpClient` services, typed config, typed errors)
- **[angular-state](../angular-state/SKILL.md)** — Reactive data and state (RxJS, signals, NgRx) registered via DI and configured via these patterns
- **[angular-reviewer](../angular-reviewer/SKILL.md)** — Structured Angular code review producing a severity-tagged Markdown report
- **[angular-tester](../angular-tester/SKILL.md)** — Writes and runs Angular/TypeScript unit tests and identifies missing test cases
- **[angular-package-manager](../angular-package-manager/SKILL.md)** — Use whenever npm packages are added, removed, or updated in a project
- **[angular-dev](../angular-dev/SKILL.md)** — Gated end-to-end implementation workflow that invokes this skill as a mandatory binding
