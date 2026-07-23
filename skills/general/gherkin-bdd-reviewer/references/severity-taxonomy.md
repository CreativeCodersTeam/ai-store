# Severity Taxonomy and Category Tags

Every finding is tagged `[Severity][Category]` followed by `file:line`.

Assign severity by **impact**, not by which rule was broken — the same rule can be
Minor in one spot and Major when pervasive.

## Severity Levels

| Severity | When to use | Examples |
|---|---|---|
| **Critical** | The test is broken or misleading. | Undefined or ambiguous step that fails / mis-binds at runtime; scenario asserting the wrong outcome; scenarios coupled by shared state so results are order-dependent / non-deterministic. |
| **Major** | A core rule is violated in a way that undermines the spec's value. | Multiple behaviors or multiple `When` in one scenario; pervasive imperative / UI-detail steps; dead or duplicated step definitions across the suite. |
| **Minor** | A localized rule violation, low blast radius. | A single chained step; one imperative step; a misused `Background` step used by only some scenarios. |
| **Suggestion** | A maintainability improvement, not a violation. | Parameterize near-duplicate steps; clearer scenario / step naming; extract a shared `Background`. |
| **Nitpick** | Cosmetic. | Wording, step ordering, optional tags, trailing whitespace. |

## Category Tags

Pick the **dominant** concern. If two apply, pick the higher-severity one.

| Tag | Scope |
|---|---|
| `Gherkin-Style` | Declarative vs imperative phrasing, one-behavior/one-`When`, `Background` discipline, tag hygiene, business language. |
| `Step-Defs` | Step-definition bindings: undefined, ambiguous/duplicate, dead/unused, incorrect regex/expression, leaked implementation detail. |
| `Coverage` | Missing scenarios for stated behavior, scenario independence, untested edge cases implied by the feature. |
| `Maintainability` | Reuse, parameterization, naming, structure, file/feature organization. |

## Heuristic → Severity Mapping

These are **starting points**; adjust by impact and by repo conventions (see
`review-checklist.md` — `gherkin-bdd` is the rule authority and repo conventions override it).

| Observation | Severity | Category |
|---|---|---|
| Undefined / ambiguous step (fails or mis-binds) | Critical | Step-Defs |
| Scenarios coupled by shared state / execution order | Critical | Coverage |
| Multiple `When` or multiple behaviors in one scenario | Major | Gherkin-Style |
| Pervasive imperative / UI-detail steps | Major | Gherkin-Style |
| Dead (unused) or duplicated step definition | Major | Step-Defs |
| One chained/extra step; one imperative step | Minor | Gherkin-Style |
| `Background` step used by only some scenarios | Minor | Gherkin-Style |
| Near-duplicate steps that should be parameterized | Suggestion | Maintainability |
| Wording / ordering / optional tag | Nitpick | Gherkin-Style |

## Example finding

```
[Major][Gherkin-Style] features/checkout.feature:14
Scenario "Manage cart" has two `When` steps (add, then remove) — two behaviors in one scenario.

Split into two scenarios, each with a single `When` and one behavior:

```gherkin
Scenario: Adding an item fills the cart
  Given an empty cart
  When the user adds an item
  Then the cart shows 1 item

Scenario: Removing the last item empties the cart
  Given a cart with one item
  When the user removes the item
  Then the cart is empty
```
```
