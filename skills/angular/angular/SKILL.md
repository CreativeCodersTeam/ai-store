---
name: angular
description: Entry point and router for Angular and TypeScript front-end work — directs you to the right specialized Angular skill. Use when a request mentions Angular in general but the specific tool is not obvious, or to get an overview of the available Angular skills. Routes to knowledge skills (angular-fundamentals, angular-components, angular-state, angular-tsdoc) and workflow skills (angular-library-builder, angular-tester, angular-reviewer, angular-package-manager), and the angular-dev implementation workflow. When the matching skill is already clear, invoke that skill directly instead.
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
| Reactive data & state: services, RxJS, signals, NgRx/component store, change detection, `OnPush`, optimistic updates and concurrency | `angular-state` |
| TSDoc / JSDoc documentation comments (`@param`, `@returns`, `@remarks`, Compodoc) | `angular-tsdoc` |

### Workflow skills (active tools, scripts, agents)

| Concern | Skill |
|---------|-------|
| Generate an Angular library / client SDK / typed `HttpClient` wrapper | `angular-library-builder` |
| Write/run unit tests (Vitest, Jasmine + Karma, or Jest; `TestBed`, spies) | `angular-tester` |
| Structured code review for Angular (explicit invocation only, see below) | `angular-reviewer` |
| Manage npm packages, `ng add`, `ng update`, version verification | `angular-package-manager` |

### Orchestration skill

| Concern | Skill |
|---------|-------|
| End-to-end implementation of a feature, user story, requirement, or bug fix (gated workflow; invokes the skills above as bindings) | `angular-dev` |

## Notes

- **Arbitration with `angular-dev`:** requirement-shaped requests — implement,
  extend, or change a feature, user story, or bug fix — belong to the
  `angular-dev` workflow, which invokes the skills above as mandatory bindings
  in its phases. The skills in the tables above are used directly only for pure
  knowledge/how-to questions, or for narrowly scoped tasks the user names
  explicitly (write tests for X, document X, bump package Y, generate a
  library/SDK, run an angular review).
- **`angular-reviewer` activates only on explicit name** — the phrases
  `angular-reviewer`, `angular code review`, or `angular review`. It does **not**
  trigger on generic "review my code", and the router does not trigger it
  automatically.
- **Composition:** `angular-library-builder` invokes `angular-tsdoc` and
  `angular-tester`; `angular-components` and `angular-state` build on
  `angular-fundamentals`.
- **Version baseline:** these skills are written against Angular 21;
  version-specific statements name the major where the feature changed.
  `angular-reviewer` supports Angular 17+.