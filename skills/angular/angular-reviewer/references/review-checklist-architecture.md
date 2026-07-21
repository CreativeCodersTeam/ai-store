# Review Checklist — Architecture

## Layering

- Presentational (dumb) components have no service injection and no side effects — `@Input`/`input()` in, `@Output`/`output()` out. Flag dumb components reaching into services or the router.
- Container (smart) components orchestrate — they inject services/state and handle navigation; they delegate rendering to presentational children.
- Data/HTTP access lives in services, not components/templates. Flag `HttpClient` injected directly into a presentational component.
- Cross-cutting behavior (auth, errors, caching) lives in interceptors/guards, not duplicated per component.

## Dependency Direction

- Feature code depends on shared/core, not the reverse. Flag a shared/core file importing from a feature folder.
- Libraries (`projects/*`) do not depend on the host application. Flag app imports leaking into a library.

## SOLID

- **SRP:** components/services that change for multiple reasons (a component that fetches, transforms, and renders complex logic). Suggest extracting a service/store.
- **OCP:** repeated `if (type === X) … else if (type === Y)` across files — suggest a strategy map / polymorphism.
- **LSP:** a subtype/derived directive that breaks the base contract.
- **ISP:** "fat" services with unrelated responsibilities; split by concern.
- **DIP:** `new`-ing dependencies inside a class instead of injecting (except plain value objects). Flag direct construction of services.

## Dependency Injection

See the `angular-fundamentals` skill (DI + typed-config sections) for scope rules and the `provide` pattern. Reviewer-specific hook: flag providing a stateful service in `root` when it must be per-route/per-component, injecting `Injector` to resolve manually (service locator), or depending on a TypeScript `interface` as a DI token (use an `abstract class`/`InjectionToken`).

## State-Approach Consistency

- New code matches the project's existing state approach (signals vs RxJS service vs NgRx). Flag a new pattern introduced silently (e.g., adding NgRx to a signals-based app without rationale).
- Single source of truth — flag duplicated state copied into multiple components instead of read from a store/service.
- Naming consistency within a bounded context: `XxxService` vs `XxxStore` vs `XxxFacade` — pick one and stay consistent.

## Module / Project Boundaries

- Each library/project has a clear purpose and a deliberate public API (`public-api.ts`). Flag internal helpers leaking through the barrel.
- Feature folders are self-contained (components, services, routes together). Flag generic `components/`, `services/`, `models/` buckets in new feature work.
