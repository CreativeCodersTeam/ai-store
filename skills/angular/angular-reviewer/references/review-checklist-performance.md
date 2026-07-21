# Review Checklist — Performance

## Change Detection

- New components use `ChangeDetectionStrategy.OnPush`. Flag default strategy on new components.
- Prefer **signals** so views update only when read values change.
- No function calls or object/array literals in template bindings that run every change-detection cycle (`[x]="compute()"`, `[style]="{...}"`). Flag — memoize via `computed()` or a field.
- Avoid heavy work in lifecycle hooks that run often (`ngDoCheck`, getters bound in templates).

## Rendering Lists

- Every `@for` declares `track` (legacy `*ngFor` declares `trackBy`). Flag missing tracking — it destroys and recreates DOM nodes.
- Virtualize large lists (`cdk-virtual-scroll-viewport`) instead of rendering thousands of rows.

## Subscriptions & Memory

- No subscription without a teardown path — use `async` pipe, `toSignal()`, or `takeUntilDestroyed()`. Flag manual `.subscribe()` in components without unsubscription (memory leak).
- Avoid nested subscribes; use higher-order operators (`switchMap`/`mergeMap`/`concatMap`/`exhaustMap`).
- `shareReplay({ bufferSize: 1, refCount: true })` to dedupe shared streams; flag duplicate identical HTTP requests.

## Network & Data

- Avoid over-fetching: request only needed fields/pages; paginate large collections.
- Debounce high-frequency inputs (`debounceTime` on search) and ignore double-submits (`exhaustMap`).
- Cache idempotent GETs (cache interceptor) where appropriate; invalidate on mutation.

## Bundle Size

- Lazy-load feature routes (`loadComponent`/`loadChildren`). Flag large eagerly-loaded features.
- No heavy library imported for a trivial need; import submodules/functions, not whole namespaces, to keep tree-shaking effective.
- Watch for new dependencies that materially grow the bundle; flag and suggest alternatives.

## Hot-Path Heuristics

A path is "hot" if any of:
- It runs on every change-detection cycle (template-bound function/getter).
- It's inside a `@for` / loop over a user-sized collection.
- It's in a frequently-emitting observable (scroll, resize, input, websocket).

## RxJS Operator Choice

- `switchMap` to cancel superseded requests (typeahead); `exhaustMap` to ignore while busy (submit); `concatMap` to preserve order; `mergeMap` only when concurrency is intended and bounded.
- Flag `mergeMap` over a user-sized source with no concurrency bound.
