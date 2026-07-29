# Review Checklist — Reactivity (Leaks, Races, Side Effects)

Hunts subscription/observable leaks, memory leaks, race conditions, and hidden side effects. Findings here use the `Reactivity` area tag.

**Severity defaults:** a confirmed leak or race is **Major** (Critical if the render path throws or data is corrupted/lost). Do not downgrade a reproducible race or leak to Minor/Suggestion just because the fix is a well-known idiom — double-submit and last-write-wins bugs ship real data corruption.

## Detection Sweep — run it actively

Scan the diff for each token below; for every hit, answer the question. A bad answer is a finding — do not skip hits that "look idiomatic".

| Token in diff | Question to answer |
|---|---|
| `.subscribe(` | Is there a teardown path (`takeUntilDestroyed`, `async` pipe, `toSignal`)? A `subscribe` in a click/submit handler additionally means double-submit: while the first request runs, a second click fires again — needs `exhaustMap` on an action stream or a busy guard. Major. |
| `takeUntil(` | Does the destroy subject **provably fire**? `ngOnDestroy` must call `next()` and `complete()`. A declared-but-never-fired `destroy$` leaks every stream it "guards" despite looking like teardown. |
| `addEventListener` / `setInterval` / `setTimeout` / `ResizeObserver` / `IntersectionObserver` | Is the symmetric cleanup registered (`DestroyRef.onDestroy(...)` or `ngOnDestroy`)? No cleanup = the destroyed component stays referenced. |
| `shareReplay(` | Is the source non-completing (websocket, `Subject`, `interval`)? Then it needs `refCount: true`, or the source runs forever after the last unsubscribe. |
| `mergeMap(` / `concatMap(` | Is the source user-driven reads (typeahead, route/query params)? Then a slow stale response can overwrite a newer one — must be `switchMap`. |
| `new Map(` / array cache in a `providedIn: 'root'` service | Is growth bounded (eviction, max size, invalidation)? An unbounded cache in a root service **is a memory leak (Major)**, not a cache-invalidation nicety. |
| `computed(` | Anything besides pure derivation inside? A signal write inside `computed()` throws NG0600 on first read — Critical. |
| `effect(` | Does it acquire a resource (listener, subscription, timer)? It must release it via the effect's `onCleanup` callback — otherwise each re-run adds another one. |
| `map(` / `filter(` | Any state mutation, navigation, or other side effect in the body? Operators must stay pure; side effects go in `tap` (and even then: visible state belongs in signals). |

## Races Beyond Operator Choice

- **Multiple async writers, one target** — two subscriptions (or a subscription plus a cache stream) assigning the same field/signal: last write wins nondeterministically. Demand a single source of truth. Major.
- **Nested `subscribe`s** — nondeterministic completion order (results `push`ed as responses race) plus no teardown of inner subscriptions. Fix: higher-order operator (`switchMap` + `forkJoin`, inputs deduped).

## Cold Observables — Count the Subscriptions

Each `async` pipe binding and each manual `subscribe` on a cold observable **re-executes its producer** — two `async` pipes plus one `subscribe` on the same `HttpClient` stream = three HTTP requests. More than one subscription → `shareReplay({ bufferSize: 1, refCount: true })` or convert once via `toSignal` and read the signal everywhere.

## Do NOT Flag

- `shareReplay(1)` on a **completing** source (plain HTTP GET) — the refCount concern doesn't apply.
- Correct `takeUntilDestroyed()` / `toSignal(..., { initialValue })` usage — including an explicit `initialValue: undefined`.
- Action streams already guarded with `exhaustMap`.

Fix patterns (operator table, stream-survives-errors rule, signal interop): see the `angular-rxjs` skill.
