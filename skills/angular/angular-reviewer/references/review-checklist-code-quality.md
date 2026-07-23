# Review Checklist — Code Quality

## Naming

- Methods are verbs; properties/signals are nouns. Outputs are events (`saved`, `selectionChange`).
- Booleans read as questions: `isValid`, `hasItems`, `canRetry`.
- Component selectors are prefixed and kebab-case (`app-order-card`); file names follow the project's convention consistently — either legacy `order-card.component.ts` or the v20 suffix-less `order-card.ts`, not a mix.
- Observables conventionally end in `$` (`orders$`); signals do not.
- No abbreviations that obscure meaning; consistent casing for acronyms (`Url`, `Id`, `Api`).

## Null Safety

- `"strict"` (incl. `strictNullChecks`) is on (project-level check).
- No non-null assertion `!` without a comment justifying it.
- Optional chaining (`?.`) and nullish coalescing (`??`) used where values may be absent; flag `||` used where `??` is meant (loses `0`/`''`/`false`).
- Template values that may be `null`/`undefined` are guarded (`@if (x; as v)`).

## Complexity

- Components over ~30 lines of logic, or templates with deep nesting / heavy inline expressions, deserve a closer look — extract child components or a service.
- A `switch`/`@switch` with many arms over the same value often wants a lookup map.
- Boolean parameters often hide two methods — flag and suggest splitting.

## Error Handling

- Observable errors are handled (`catchError`) or surfaced — flag silent swallow (`catchError(() => EMPTY)` with no user feedback or comment).
- A global `ErrorHandler` and/or HTTP error interceptor exists for uncaught errors; raw error text/stack is never rendered to users.
- Don't use exceptions for control flow.

## Teardown & Resources

- Every manual subscription has a teardown path (`async` pipe / `toSignal()` / `takeUntilDestroyed()`).
- Manually created resources (timers, event listeners, `effect()` outside injection context) are cleaned up via `DestroyRef.onDestroy`.

## Dead Code

- Unused imports → lint should catch; flag if lint is off.
- Unreachable code; commented-out blocks.
- Unused private members. Exported/public members may be API for a consumer — leave unless clearly orphaned.

## Comments and Docs

- Exported/public library API and component `@Input`/`@Output` have TSDoc, especially for libraries. See the `angular-tsdoc` skill for tag conventions (`@param`, `@returns`, `@throws`, `{@link}`, etc.).
- Comments explain *why*, not *what*. Flag comments that restate the code.
- TODOs without a ticket reference are a smell; flag.

## Tests (cross-cutting)

See the `angular-tester` skill for AAA layout, `Method_Condition_Expected` (or readable `should …`) naming, `TestBed`/spy conventions, and edge-case coverage. Reviewer-specific hook: flag any new public behavior shipped without at least one meaningful test, a test asserting only `toBeTruthy()` on creation, and any test body containing conditional logic (`if`/`for`).

## Logging

- Use a logging service, not scattered `console.log` (flag `console.log`/`console.error` left in production code).
- Log level matches consequence; no PII (emails, names, full payloads) logged without redaction.
