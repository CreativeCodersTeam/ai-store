# Severity Taxonomy and Area Tags

Every finding is tagged `[Severity][Area]` followed by `path:line`.

## Severity Levels

| Severity | When to use | Examples |
|---|---|---|
| **Critical** | Ship-blocker. Production correctness, security, data loss, or a failing test. | XSS via `bypassSecurityTrust*`, unhandled `null`/`undefined` deref on a render path, failing test, build error. |
| **Major** | Will hurt users or maintainers but not a ship-blocker. | Missing input validation on a public form/API client, memory leak from un-torn-down subscription, broken `@Input`/`@Output` contract. |
| **Minor** | Real issue, low impact, deserves a fix in this PR. | Build warning, swallowed observable error, missing log context, dead code. |
| **Suggestion** | Improvement worth considering. Author can accept or reject. | Refactor opportunity, alternative idiom, better naming, lint violation. |
| **Nitpick** | Cosmetic. Author should ignore unless trivial. | Whitespace, comment phrasing, minor style preference. |

## Area Tags

Pick the **dominant** concern. If two apply, pick the higher-severity area.

| Tag | Scope |
|---|---|
| `Security` | XSS/sanitization, authn/authz (guards), input validation, secrets in bundle, untrusted HTML/URLs, dependency CVEs. |
| `Performance` | Change detection (`OnPush`, signals), `@for` `track`, bundle size, over-fetching, leak-free subscriptions, unnecessary recomputation. |
| `Architecture` | Layer/dependency direction, smart/dumb split, DI scope misuse, state-approach consistency, coupling. |
| `Code-Quality` | Naming, complexity, null safety, teardown, dead code, error strategy. |
| `Tests` | Missing coverage, flaky tests, weak assertions (`toBeTruthy()` only), test maintenance smell. |
| `Angular-Idioms` | Version-specific idioms (standalone, `inject()`, signals, new control flow `@if`/`@for`, `input()`/`output()`). |

## Mapping from Tool Outputs

| Tool finding | Severity | Area |
|---|---|---|
| `ng build` error | Critical | Code-Quality (or context-driven) |
| `ng build` warning | Minor | Code-Quality |
| `ng test` failure | Critical | Tests |
| `ng lint` violation | Suggestion | Code-Quality |

## Examples

```
[Critical][Security] src/app/feature/comment.component.ts:42
Untrusted comment HTML is passed through bypassSecurityTrustHtml.

Bind with the default [innerHTML] (Angular sanitizes it) or sanitize explicitly; never bypass for user content.

```typescript
// before
this.html = this.sanitizer.bypassSecurityTrustHtml(comment.body);

// after — let Angular sanitize
// template: <div [innerHTML]="comment.body"></div>
```
```
