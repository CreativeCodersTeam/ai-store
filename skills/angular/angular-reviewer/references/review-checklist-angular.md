# Review Checklist — Angular (17+)

Apply when `detect-angular-version.sh` reports an Angular major `>= 17`.

## Component Idioms

- **Standalone components** — prefer `standalone` components/directives/pipes over NgModules in new code. Flag new NgModule declarations without a reason.
- **New control flow** — `@if` / `@for` / `@switch` over the legacy `*ngIf` / `*ngFor` / `*ngSwitch`. Flag new structural-directive usage in new templates.
- **`@for` track** — every `@for` must declare `track`. Flag missing `track` (or legacy `trackBy` absence) — it forces full re-render.
- **`input()` / `output()` / `model()`** — prefer the signal-based `input()`/`output()` functions over `@Input()`/`@Output()` decorators in new components.
- **Signal queries** — prefer `viewChild()`/`viewChildren()`/`contentChild()`/`contentChildren()` over the `@ViewChild`/`@ContentChild` decorators in new code.
- **`readonly` on framework-assigned members** — `input`, `model`, `output`, and queries should be `readonly`. Flag reassignable ones.
- **`protected` for template-only members** — members read only by the template should be `protected`, not `public`. Flag needlessly-public template helpers.
- **`class` / `style` bindings** — prefer `[class.x]`/`[style.x]` (and object form) over `NgClass`/`NgStyle`. Flag new `ngClass`/`ngStyle` usage.
- **`inject()`** — prefer `inject()` over constructor parameter injection in new code.
- **`OnPush`** — new components use `ChangeDetectionStrategy.OnPush`. Flag default change detection on new components.

## State & Reactivity

- **Signals** for synchronous view state; `computed()` for derived values. Flag manual recomputation in templates or duplicated derived fields.
- **`async` pipe / `toSignal()`** over manual `subscribe` in components. Flag `subscribe` in components without explicit teardown.
- **Teardown** — long-lived subscriptions use `takeUntilDestroyed()` / `DestroyRef`. Flag subscriptions with no unsubscription path.

## API Idioms

- **`provideХxx()` functions** over `forRoot()` NgModule patterns for configuration in new libraries.
- **Functional guards/interceptors/resolvers** (`CanActivateFn`, `HttpInterceptorFn`, `ResolveFn`) over the deprecated class-based forms.
- **`HttpClient`** for all HTTP — flag `fetch`/`XMLHttpRequest` in app code (breaks interceptors, testing, SSR).

## Project Configuration

- `tsconfig.json` has `"strict": true` (incl. `strictNullChecks`). Flag projects without it.
- Angular compiler `strictTemplates` enabled. Flag if disabled in new work.
- `@angular/*` package versions are aligned (core/cli/common same major). Flag mismatched majors.

## Non-version-specific checks

For framework-neutral pitfalls (subscription leaks, allocation hot spots, etc.) see `review-checklist-performance.md` and `review-checklist-code-quality.md`. This file covers only modern-Angular-specific idioms.
