---
name: angular-state
description: Applies Angular best practices for reactive data access and client-side state management. Use when designing a store or state service, choosing between signals, RxJS, and NgRx, modeling state shape, writing selectors/derived state, optimizing change detection, handling optimistic updates and concurrency, persisting/hydrating state, or troubleshooting over-fetching and re-render performance.
---

# Angular Reactive Data & State Best Practices

## When to Use

- Designing or restructuring a store, state service, or facade (the client analogue of a data layer)
- Choosing a state approach: signals, RxJS services, NgRx Store, or NgRx Component Store
- Modeling state shape, normalizing collections, or keeping state immutable
- Writing selectors / derived state, or troubleshooting over-fetching, redundant requests, and re-render performance
- Implementing optimistic updates and handling server-side concurrency conflicts
- Persisting and hydrating state (localStorage/sessionStorage) with versioning

## Store / State-Container Design

- Keep stores **focused and cohesive** — one feature's state per store, not a single god-store.
- Treat state as the **single source of truth**; components read from it and dispatch changes, they don't hold duplicate copies.
- Use **constructor/`inject()`** for dependencies (HTTP services, config).
- Expose **read-only** views (`signal.asReadonly()`, `Observable`) and mutate only through explicit methods/actions.
- **Pick the narrowest tool:**
  | State | Use |
  |-------|-----|
  | Local component view state | `signal()` / `computed()` in the component |
  | Feature state shared across a routed area | a `providedIn`-scoped service exposing signals or `BehaviorSubject` |
  | Feature state, signal-first, with less boilerplate than the full Redux flow | **NgRx SignalStore** (`signalStore`, `withState`/`withComputed`/`withMethods`) |
  | Complex, app-wide, multi-source state with strict traceability | **NgRx Store** (actions/reducers/selectors/effects) |
  | Local, self-contained reactive workflows | **NgRx Component Store** |

## Async Data: `resource()` / `httpResource()`

For **reactive reads** (load-on-signal-change), prefer the resource APIs over hand-rolled `subscribe`/`toSignal` plumbing. They expose `value`, `status`, `error`, and `isLoading` as signals and auto-cancel superseded requests when their reactive params change.

- **`resource()`** — wraps any async loader (a `Promise`-returning function); the `request`/`params` signal drives reloads. Use for non-HTTP or custom async sources.
- **`rxResource()`** — same, but the loader returns an `Observable` (integrates an existing RxJS service).
- **`httpResource()`** — declarative, signal-driven `HttpClient` GET; returns `HttpResourceRef` whose `value` is a signal. Use for reactive reads that depend on signals.

```typescript
export class OrderDetail {
  readonly id = input.required<number>();
  // refetches whenever id() changes; exposes value()/isLoading()/error()
  readonly order = httpResource<Order>(() => `/api/orders/${this.id()}`);
}
```

Keep using **`HttpClient`** directly for commands/mutations (POST/PUT/DELETE), streaming, and interceptor-heavy flows — resources are for reactive reads, not write operations.

## State Shape (Model) Design

- Use stable identifiers (`id`) and **normalize** collections (`Record<id, Entity>` + `id[]`) instead of nested arrays when items are referenced in multiple places.
- Keep state **immutable** — replace, don't mutate (`signal.update(s => ({ ...s, ... }))`); enable `readonly` types.
- Model relationships by id reference, not by embedding mutable copies.
- Keep derived data **out** of stored state — compute it (see Selectors).

## Performance

- Use `ChangeDetectionStrategy.OnPush` everywhere; prefer **signals** so views update only when read values change.
- In `@for`, always provide `track` (and `trackBy` in legacy `*ngFor`) to avoid re-rendering unchanged rows.
- Derive with **memoized** `computed()` / NgRx selectors instead of recomputing in templates.
- **Avoid over-fetching:** dedupe in-flight requests (`shareReplay({ bufferSize: 1, refCount: true })`), cache reads, and load only the fields/pages you need (pagination with page/size).
- Use `async` pipe or `toSignal()` rather than manual `subscribe` to prevent leaks and redundant change detection.
- **Zoneless change detection** (`provideZonelessChangeDetection()`, developer preview in v20) removes Zone.js and updates the view only from signal reads, `markForCheck`, and async pipe — the end state of a signal-first app. Adopt it deliberately: ensure state flows through signals/`OnPush`, test in staging, and don't flip a large production app in one step.

## Persistence & Hydration

- The client has no schema migrations, but persisted state **does** have a shape that evolves. Version persisted blobs (`{ version, data }`) and migrate or discard on mismatch when hydrating.
- Persist deliberately (localStorage/sessionStorage/IndexedDB) — only what must survive reloads, never large or sensitive data.
- Hydrate at startup (e.g. in a `provideAppInitializer`) and guard against malformed/stale payloads.

## Selectors & Derived State

- Compute derived values with `computed()` (signals) or memoized selectors (NgRx); don't store what you can derive.
- For **writable** derived state that resets when its source changes, use **`linkedSignal()`** (e.g. a selected-item signal that defaults from a list but can be overridden) instead of syncing with an `effect()`.
- Compose selectors from smaller selectors; keep them pure.
- For RxJS-derived data, choose operators deliberately (`map`, `filter`, `combineLatest`, `switchMap` for cancel-previous, `exhaustMap` to ignore-while-busy, `concatMap` to queue).

## Updates & Concurrency

- Update state **immutably**; batch related changes into one update/action.
- Prefer **optimistic updates** for snappy UX, with rollback on failure.
- Implement concurrency control for multi-user scenarios (see below).
- Use cancellation-aware operators (`switchMap`) so superseded requests don't clobber newer state.

### Optimistic Updates & Concurrency

See [concurrency-control.md](./references/concurrency-control.md) for optimistic-update-with-rollback, ETag/`If-Match` version tokens, and handling `409 Conflict` responses.

## Security

- **Never store secrets or sensitive personal data in client state or localStorage** — it is fully visible to the user and to any XSS payload.
- Treat all server data as untrusted for rendering; rely on Angular's built-in sanitization and avoid `bypassSecurityTrust*` unless unavoidable.
- Scope per-user state and clear it on logout (don't leak one user's cached data to the next).

## Testing

- Test stores/services by asserting emitted state after actions — assert **behavior/output**, not internal fields.
- Use marble testing (`TestScheduler`) for non-trivial RxJS operator chains.
- Mock HTTP with `provideHttpClient()` + `provideHttpClientTesting()` and inject `HttpTestingController` (the `HttpClientTestingModule` is deprecated); mock dependencies with spies.
- For NgRx, test reducers as pure functions, selectors with `projector`, and effects with `provideMockActions`.
- Use the `angular-tester` skill for generating unit tests after state changes.

## Related Skills

- **[angular-fundamentals](../angular-fundamentals/SKILL.md)** — DI scopes for stores, typed config, signals, and `DestroyRef` teardown used in state code
- **[angular-tester](../angular-tester/SKILL.md)** — Generates unit tests for stores, selectors, and effects (marble testing, HttpTestingController)
- **[angular-components](../angular-components/SKILL.md)** — Consumes state via signals/async pipe; wires HTTP and interceptors
- **[angular-reviewer](../angular-reviewer/SKILL.md)** — Reviews state/data code for performance and correctness issues
- **[angular-package-manager](../angular-package-manager/SKILL.md)** — Adds RxJS, NgRx, or component-store packages
