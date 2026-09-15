---
name: angular
description: Entry point and router for Angular and TypeScript front-end work — directs you to the right specialized Angular skill. Use when a request mentions Angular in general but the specific tool is not obvious, or to get an overview of the available Angular skills. Routes to knowledge skills (angular-fundamentals, angular-components, angular-state, angular-rxjs, angular-tsdoc) and workflow skills (angular-library-builder, angular-tester, angular-reviewer, angular-package-manager). When the matching skill is already clear, invoke that skill directly instead.
---

# Angular Skill Router

Signpost to the specialized Angular skills. This skill holds no best-practice
knowledge of its own — it maps a request to the appropriate specialized skill.

## When to Use

- A task concerns Angular, but it is unclear which specialized skill applies.
- You need an overview of the available Angular skills and their responsibilities.

When the matching skill is already clear, load it directly — the router is only
orientation, not an intermediate step.

## Routing

### Knowledge skills (best practices, `references/` only)

| Concern | Skill |
|---------|-------|
| Dependency Injection, providers, injection tokens, `inject()`, standalone bootstrap, environments/configuration, modern TypeScript idioms (for any Angular app) | `angular-fundamentals` |
| Components, templates, control flow, routing, forms, model binding, validation, guards, interceptors, `HttpClient` consumption, project structure | `angular-components` |
| Reactive data & state: services, signals, NgRx/component store, change detection, `OnPush`, optimistic updates and concurrency | `angular-state` |
| RxJS stream code: Observable consumption in components, operator choice (`switchMap` & co.), error handling in streams, `toSignal`/`toObservable` interop, resource APIs, testing RxJS in zoneless/Vitest projects | `angular-rxjs` |
| TSDoc / JSDoc documentation comments (`@param`, `@returns`, `@remarks`, Compodoc) | `angular-tsdoc` |

### Workflow skills (active tools, scripts, agents)

| Concern | Skill |
|---------|-------|
| Generate an Angular library / client SDK / typed `HttpClient` wrapper | `angular-library-builder` |
| Write/run unit tests (Vitest, Jasmine + Karma, or Jest; `TestBed`, spies) | `angular-tester` |
| Structured code review for Angular (explicit invocation only, see below) | `angular-reviewer` |
| Manage npm packages, `ng add`, `ng update`, version verification | `angular-package-manager` |

## Notes

- **`angular-reviewer` activates only on explicit name** — the phrases
  `angular-reviewer`, `angular code review`, or `angular review`. It does **not**
  trigger on generic "review my code", and the router does not trigger it
  automatically.
- **`angular-dev` activates only when the user names it** — `/angular-dev`,
  `/cc-ai-angular:angular-dev`, `angular-dev`, or `angular dev` in the prompt.
  It is the gated end-to-end implementation workflow (requirement review →
  clarification → task breakdown → implementation → `angular-reviewer` →
  summary). A plain "implement this feature" / "fix this bug" request is served
  by the knowledge skills above; neither the router nor any other skill or
  agent starts `angular-dev` on the user's behalf.
- **Composition:** `angular-library-builder` invokes `angular-tsdoc` and
  `angular-tester`; `angular-components`, `angular-state`, and `angular-rxjs`
  build on `angular-fundamentals`.
- **`angular-state` vs. `angular-rxjs`:** choosing the state approach and
  designing stores is `angular-state`; writing or fixing the streams themselves
  (operators, error handling, interop, stream tests) is `angular-rxjs`.
- **Version baseline:** the target version resolves explicit user directive → repo
  directive (installed `@angular/core`, then `package.json`) → latest stable,
  resolved at runtime with `npm view @angular/core dist-tags.latest`. The rule is
  canonical in
  [`angular-fundamentals/references/angular-version.md`](../angular-fundamentals/references/angular-version.md);
  no skill hardcodes a version of its own. These skills' examples are written
  against **Angular 21**, which is also the offline fallback; version-specific
  statements name the major where the feature changed and never select a target.