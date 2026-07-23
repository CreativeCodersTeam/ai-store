---
name: angular
description: Entry point and router for Angular and TypeScript front-end work — directs you to the right specialized Angular skill. Use when a request mentions Angular in general but the specific tool is not obvious, or to get an overview of the available Angular skills. Routes to knowledge skills (angular-fundamentals, angular-components, angular-state, angular-tsdoc) and workflow skills (angular-library-builder, angular-tester, angular-reviewer, angular-package-manager). When the matching skill is already clear, invoke that skill directly instead.
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
| Write/run unit tests (Jasmine + Karma or Jest, `TestBed`, spies) | `angular-tester` |
| Structured code review for Angular (explicit invocation only, see below) | `angular-reviewer` |
| Manage npm packages, `ng add`, `ng update`, version verification | `angular-package-manager` |

## Notes

- **`angular-reviewer` activates only on explicit name** — the phrases
  `angular-reviewer`, `angular code review`, or `angular review`. It does **not**
  trigger on generic "review my code", and the router does not trigger it
  automatically.
- **Composition:** `angular-library-builder` invokes `angular-tsdoc` and
  `angular-tester`; `angular-components` and `angular-state` build on
  `angular-fundamentals`.
- **No package-API inspector:** the npm/Angular ecosystem has no CLI for
  querying compiled library APIs, so there is no `angular-inspect`. Use
  `angular-package-manager` for package version/metadata questions instead.
