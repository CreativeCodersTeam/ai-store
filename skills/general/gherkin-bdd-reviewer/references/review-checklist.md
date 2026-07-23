# Review Checklist

This checklist **operationalizes** the Gherkin/BDD rules into review questions. It
owns **no rules of its own**.

> **Rule authority:** the `gherkin-bdd` skill is the source of truth for the rule set
> (`SKILL.md` "Best Practices & Anti-Patterns" + `references/gherkin-style.md`).
> **Repo conventions override built-in rules** (Rule Precedence). A scenario that
> breaks a built-in rule but matches an explicit repo convention is **not** a finding;
> breaking an established repo convention **is** a finding. Note overrides in the
> report's "Conventions Applied" section.

Default severities below are starting points — assign by impact per
`severity-taxonomy.md`.

## Feature-file rules

| Rule (gherkin-bdd) | What to look for | Default severity / category |
|---|---|---|
| One behavior per scenario | A scenario asserting multiple unrelated outcomes. | Major · Gherkin-Style |
| Exactly one `When` per scenario | Two+ `When` (or chained `When … Then … When`) hiding what's tested. | Major · Gherkin-Style (Minor if a single stray step) |
| Declarative, business-language steps | UI/implementation detail: clicks, selectors (`#id`), URLs, SQL, HTTP verbs. | Major if pervasive, Minor if isolated · Gherkin-Style |
| Reusable, parameterized steps | Near-duplicate steps differing only by a literal value. | Suggestion · Maintainability |
| `Background` only for shared setup | `Background` steps used by only some scenarios in the file. | Minor · Gherkin-Style |
| Meaningful tags, no dead tags | Tag sprawl; tags no runner/filter uses; inconsistent taxonomy. | Nitpick–Minor · Gherkin-Style |
| Independent scenarios | Scenarios depending on execution order or shared mutable state. | Critical · Coverage |
| Coverage of stated behavior | `Feature` description / acceptance criteria with no scenario exercising them. | Major–Minor · Coverage |

## Step-definition rules

Detect statically — match feature steps against step-definition patterns; do **not**
build or run the suite.

| Rule | What to look for | Default severity / category |
|---|---|---|
| No undefined steps | A feature step with no matching binding pattern. | Critical · Step-Defs |
| No ambiguous/duplicate steps | Two+ bindings whose patterns match the same step text. | Critical · Step-Defs |
| No dead step definitions | A binding pattern no feature step exercises. | Major · Step-Defs |
| Correct bindings | Regex/expression that over- or under-matches (greedy `(.*)`, wrong type). | Major–Minor · Step-Defs |
| No leaked implementation detail | Step text that encodes solution-domain mechanics (selectors, SQL, wait/sleep). | Major–Minor · Step-Defs |

## Framework step syntax

Use the framework reported by `detect-framework.sh` to read step patterns correctly
(load the matching `gherkin-bdd/references/` file):

| Framework | Binding markers | Reference |
|---|---|---|
| reqnroll | `[Binding]`, `[Given]/[When]/[Then]` attributes | `gherkin-bdd/references/reqnroll-dotnet.md` |
| cucumber-jvm | `@Given/@When/@Then` annotations | `gherkin-bdd/references/cucumber-jvm.md` |
| cucumber-js | `Given('…', fn)` from `@cucumber/cucumber` | `gherkin-bdd/references/cucumber-js.md` |
| unknown | infer from existing step files; note the gap in the report | — |
