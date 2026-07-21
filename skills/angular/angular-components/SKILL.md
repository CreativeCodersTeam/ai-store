---
name: angular-components
description: Applies Angular best practices for building the UI/presentation layer — components, templates, routing, forms, validation, HTTP consumption, interceptors, guards, and error handling. Use when creating components, configuring the router, building reactive or template-driven forms, wiring HttpClient and interceptors, adding route guards, handling client-side errors, or structuring an Angular app. For dependency injection, the provide/config pattern, and modern TypeScript idioms, use angular-fundamentals.
---

# Angular UI / Presentation Layer Best Practices

## When to Use

- Creating new components, feature folders, or routed views in an Angular app
- Configuring the router, lazy-loaded routes, route data/resolvers, or navigation
- Building reactive (typed) or template-driven forms and validation
- Consuming HTTP APIs with `HttpClient`, and wiring functional interceptors
- Adding route guards (`CanActivate`, `CanMatch`) and an auth/bearer-token interceptor
- Implementing client-side error handling (global `ErrorHandler`, HTTP error interceptor)
- Reviewing or restructuring an existing Angular app to align with best practices

This skill covers the **UI / presentation layer** (the client analogue of a web API's HTTP layer). For dependency injection, the typed-config/`provide` pattern, and modern TypeScript idioms that apply to any Angular surface, see [`angular-fundamentals`](../angular-fundamentals/SKILL.md). For reactive data and state management, see [`angular-state`](../angular-state/SKILL.md).

## Core Principles

- Organize by **feature folders**, not technical layers. Keep `main.ts` / `app.config.ts` lean — extract setup into `provideXxx()` functions.
- Default to **standalone components** (the default since v19 — set `standalone: false` only for legacy NgModule interop); split **container (smart)** vs **presentational (dumb)** components; use `ChangeDetectionStrategy.OnPush` everywhere.
- Prefer native **`[class.x]` / `[style.x]` (and object) bindings over `NgClass` / `NgStyle`** — simpler syntax and cheaper at runtime.
- Mark members used **only by the template** as `protected` (keeps the component's public API minimal), and name event handlers for the **action** they perform (`saveOrder()`), not the triggering event (`onClick()`).
- Use **typed reactive forms** for non-trivial input; prefer signals/`computed` for view state.
- **Map errors to user-facing messages** via a global `ErrorHandler` and an HTTP error interceptor — never render raw exception text or stack traces.
- **Interceptor order matters:** auth (attach token) → caching → retry → error mapping → logging. Order interceptors deliberately when registering them.
- Lazy-load feature routes; keep the initial bundle small. Always thread cancellation via `takeUntilDestroyed()` / unsubscribe.

## Reference Index

Detailed patterns and code samples live in `references/`:

- **[project-and-components.md](references/project-and-components.md)** — Project structure, standalone components, container vs presentational, routing, lazy loading, route data/resolvers
- **[forms-and-validation.md](references/forms-and-validation.md)** — Reactive vs template-driven forms, typed `FormGroup`, built-in & custom validators, async validators, displaying errors
- **[interceptors.md](references/interceptors.md)** — `HttpClient`, functional interceptors, interceptor order, caching/retry (the client analogue of middleware)
- **[auth.md](references/auth.md)** — Route guards, bearer-token interceptor, OIDC/PKCE, role/claim-based access
- **[error-handling.md](references/error-handling.md)** — Global `ErrorHandler`, HTTP error interceptor, RxJS `catchError`, surfacing user-friendly messages
- **[cross-cutting.md](references/cross-cutting.md)** — Title/meta & SEO, i18n, accessibility, route preloading, HTTP caching, debouncing user actions

## Related Skills

- **[angular-fundamentals](../angular-fundamentals/SKILL.md)** — Foundation: DI, typed config/`provide` pattern, modern TypeScript idioms used by every component and service here
- **[angular-state](../angular-state/SKILL.md)** — Reactive data and state management (RxJS, signals, NgRx)
- **[angular-tester](../angular-tester/SKILL.md)** — Unit and integration testing for components and forms
- **[angular-tsdoc](../angular-tsdoc/SKILL.md)** — TSDoc comments for component inputs/outputs and public APIs
- **[angular-package-manager](../angular-package-manager/SKILL.md)** — Invoked for adding router, forms, HTTP, and UI packages (often via `ng add`)
- **[angular-library-builder](../angular-library-builder/SKILL.md)** — Generates typed `HttpClient` services for consuming APIs
- **[angular-reviewer](../angular-reviewer/SKILL.md)** — Reviews Angular UI code for accessibility, performance, and architecture issues
