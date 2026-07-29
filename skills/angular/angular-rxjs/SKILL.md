---
name: angular-rxjs
description: Use when writing or reviewing RxJS code in an Angular 21+ app — components or services consuming Observables, typeahead/autocomplete streams, chained or combined HttpClient calls (switchMap, forkJoin, combineLatest), converting Observables to signals with toSignal/toObservable, deciding between httpResource/rxResource and classic HttpClient+RxJS, fixing memory leaks or streams that silently stop after an error, or testing debounced/async RxJS code with Vitest in zoneless projects.
---

# Angular RxJS (Angular 21+)

RxJS patterns for modern zoneless Angular. Assumes Angular 21+: standalone components, zoneless change detection, signals as the template-facing primitive, Vitest as the default test runner.

## When to Use

- Consuming Observables in components (template data, derived state, side effects)
- Typeahead/autocomplete, debounced inputs, dependent or parallel HttpClient calls
- Bridging RxJS ↔ signals (`toSignal`, `toObservable`) or choosing resource APIs vs. classic streams
- A stream "stops working" after the first error, or QA reports leaks/duplicate requests
- Unit-testing time-based or HTTP-driven RxJS code in a zoneless + Vitest project

**When NOT to use:** choosing a state-management approach or store design → `angular-state`. DI, `DestroyRef`, provider fundamentals → `angular-fundamentals`. Framework-agnostic RxJS in non-Angular TypeScript → the `rxjs` skill.

## The Iron Rule: A Stream That Reaches the Template Must Survive Errors

An unhandled error **permanently terminates** an Observable pipeline. In a typeahead, a single failed HTTP call kills the stream: the input keeps firing, nothing ever updates again, no console hint in production. This is the most common omission in otherwise-correct Angular RxJS code.

**Every pipeline consumed via `toSignal`, `async` pipe, or `subscribe` needs error handling — and `catchError` goes on the *inner* observable, inside the mapping operator, so the outer stream survives:**

```typescript
readonly results = toSignal(
  toObservable(this.term).pipe(
    debounceTime(300),
    distinctUntilChanged(),
    switchMap(term => term.trim()
      ? this.search.query(term).pipe(
          catchError(() => of([] as Result[])), // inner: this request fails, stream lives on
        )
      : of([] as Result[])),
  ),
  { initialValue: [] as Result[] },
);
```

`catchError` placed *after* `switchMap` (outer) also completes the outer stream — the fallback emits once, then the typeahead is dead anyway.

Choose the recovery deliberately:

| Situation | Pattern |
|---|---|
| Fallback is acceptable (search, lists) | inner `catchError(() => of(fallback))` |
| UI must show the error | map to a state object: `{ status: 'error', error }` via `map`/`catchError`/`startWith` |
| Transient failures (network) | `retry({ count: 2, delay: 500 })` *before* `catchError` |
| `forkJoin` over several calls | one failing source fails **all** — `catchError` per source, or accept all-or-nothing explicitly |

## Subscription Lifecycle — Quick Reference

| Goal | Do | Not |
|---|---|---|
| Data for the template | `toSignal(obs$, { initialValue })` | `subscribe` + mutable property |
| Imperative side effect (navigation, toast) | `obs$.pipe(takeUntilDestroyed()).subscribe(...)` in an injection context | `destroy$` Subject + `ngOnDestroy` boilerplate |
| Dependent calls | `switchMap`/`concatMap` | nested `subscribe` |
| N parallel calls | `forkJoin` (dedupe inputs first) | loop of `subscribe`s pushing into an array |

`toSignal` subscribes **eagerly and once**; it unsubscribes with the component's `DestroyRef`. Both `toSignal` and `takeUntilDestroyed` require an injection context (field initializer or constructor) — outside one, pass `injector`/`DestroyRef` explicitly.

## Flattening Operator Choice

| Operator | Semantics | Typical use |
|---|---|---|
| `switchMap` | cancel previous | typeahead, param-driven GETs — stale responses can never win |
| `concatMap` | queue in order | ordered writes |
| `mergeMap` | run concurrently | independent fire-and-forget; order not guaranteed |
| `exhaustMap` | ignore while busy | submit buttons, login — swallows double-clicks |

Typeahead recipe: `debounceTime(300)` + `distinctUntilChanged()` + `switchMap` + inner `catchError`.

## Resource APIs — Verified Version Facts

| API | Angular 21 | Angular 22 (May 2026) |
|---|---|---|
| `resource()`, `rxResource()`, `httpResource()` | developer preview (usable; surface may change without deprecation cycle) | **stable** |

- Signal-driven GET with loading/error state in the template → `httpResource(() => url)` (auto-cancels on param change, `isLoading()`/`error()`/`hasValue()`/`reload()`).
- Loader needs RxJS operators (merge, retry/backoff) → `rxResource({ params, stream })`.
- Org policy forbids preview APIs on 21 → classic `toObservable` + `switchMap` + `catchError`/`startWith` state object, migrate to `httpResource` on 22.
- Mutations (POST/PUT/DELETE) stay classic `HttpClient` + RxJS.

## Testing RxJS (Zoneless + Vitest)

- **No `fakeAsync`/`tick`** — they need zone.js, which zoneless projects don't ship. Use `vi.useFakeTimers()` + `vi.advanceTimersByTime(ms)` for `debounceTime` etc., or `TestScheduler` marbles for pure operator logic.
- HTTP: `provideHttpClient()` + `provideHttpClientTesting()`, `HttpTestingController`. Assert `switchMap` cancellation via `req.cancelled`; `httpMock.verify()` in `afterEach`.
- Subject-driven pipelines emit only to active subscribers: **subscribe before triggering**, collect emissions into an array, assert exact sequences.
- Always test that the stream **survives an error**: flush a 500, then trigger again and expect a normal emission.

## Common Mistakes

| Mistake | Consequence |
|---|---|
| No `catchError` in a template-feeding stream | first error silently kills the feature until reload |
| `catchError` after the flattening operator | outer stream completes after first error |
| `forkJoin` without per-source error handling | one failed call discards all results |
| `mergeMap` for typeahead | stale responses overwrite newer ones |
| `fakeAsync` in a zoneless project | fails — zone.js is not installed |
| Treating `httpResource`/`rxResource` as stable on Angular 21 | preview API; pin the risk or wait for 22 |
| Nested `subscribe` calls | leaks, race conditions, untestable code |

## Related Skills

- `angular-state` — choosing signals vs. RxJS vs. NgRx, store design
- `angular-fundamentals` — DI, `DestroyRef`, injection contexts
- `angular-tester` — general unit-testing workflow (TestBed, spies)
