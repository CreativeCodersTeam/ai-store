---
name: gherkin-bdd
description: Authoring Gherkin feature files and implementing BDD tests. Use when asked to write .feature files, Given/When/Then scenarios, scenario outlines, BDD specs, or to implement step definitions/bindings and wire up a BDD runner (Reqnroll, Cucumber-JVM, Cucumber.js). Covers Gherkin syntax, best practices, anti-patterns, and framework-specific step implementation. For reviewing existing BDD tests, use gherkin-bdd-reviewer instead.
license: MIT
---

# Gherkin & BDD Skill

Author well-structured Gherkin `.feature` files and turn them into runnable BDD
tests (step definitions + runner) for Reqnroll (.NET), Cucumber-JVM (Java), or
Cucumber.js (TypeScript).

## When to Use This Skill

- Writing or refining `.feature` files, scenarios, or scenario outlines.
- Translating acceptance criteria / requirements into Given-When-Then specs.
- Implementing step definitions / bindings and wiring up a BDD test runner.
- Running and verifying a BDD suite.

Do **not** use this skill for reviewing/auditing existing BDD tests — use
`gherkin-bdd-reviewer` for that.

## Rule Precedence (read first)

Repo-local Gherkin/BDD conventions **always override** this skill's built-in rules
when they conflict. The built-in rules are the fallback for anything the repo does
not specify. Before authoring or implementing, scan the repo and adopt existing
conventions. Check these sources (first match wins, in order):

1. Project instruction files: `CLAUDE.md`, `AGENTS.md`,
   `.github/copilot-instructions.md`, and any `*.md` style/contribution guide that
   mentions Gherkin or BDD.
2. Linter/formatter config: `.gherkin-lintrc` / `gherkin-lint` config, `.editorconfig`
   rules for `*.feature`.
3. Existing `.feature` files and step-definition folders — infer the established
   style (spoken language tag, file/scenario naming, step phrasing, tag taxonomy)
   and follow it.
4. Framework config that constrains conventions: `reqnroll.json`,
   `cucumber.js`/`cucumber.json`, `@CucumberOptions`.

When a repo convention is silent on a point, fall back to the rules below. When the
repo conflicts with a rule below, follow the repo and note the override to the user.

**Defaults when the repo is silent:** write scenarios in English. The `# language:`
header is optional for English (Gherkin assumes English without it); add it explicitly
only when existing `.feature` files do, or when the spoken language is not English.

## Gherkin Core

A feature file uses these keywords:

- `Feature:` — the capability under test (one per file). Optional free-text
  description lines follow.
- `Scenario:` — one concrete example of behavior.
- `Scenario Outline:` + `Examples:` — a parameterized scenario run once per data row,
  using `<placeholder>` tokens.
- `Background:` — steps run before every scenario in the file (shared setup only).
- `Given` (context/preconditions), `When` (the single action under test),
  `Then` (observable outcome). `And` / `But` continue the previous keyword.
- Tags (`@smoke`, `@wip`) attach metadata to features/scenarios for filtering.

These keywords combine into one file (each keyword annotated):

```gherkin
@checkout                                   # tag: metadata for filtering
Feature: Checkout                           # the capability under test (one per file)
  As a shopper                              # optional free-text description
  I want to pay for items in my cart
  So that I receive my order

  Background:                               # runs before every scenario (shared setup)
    Given the store sells "book" for 10

  Scenario: Pay for a single item           # one concrete behavior
    Given the cart contains a "book"        # context / precondition
    When the user checks out                # the single action under test
    Then the order total is 10              # observable outcome

  Scenario Outline: Bulk discount applies   # parameterized — runs once per row
    Given the cart contains <count> copies of "book"
    When the user checks out
    Then the order total is <total>

    Examples:                               # data rows for the outline
      | count | total |
      | 5     | 45    |
      | 10    | 80    |
```

Write **declarative** business-language steps, not **imperative** UI steps. Keep the
solution domain out of the spec:

```gherkin
# ❌ Imperative — couples the spec to the UI
Scenario: Login
  Given I open "/login"
  When I type "alice" into "#username"
  And I click "#submit"
  Then I see "Welcome"

# ✅ Declarative — survives UI changes, reads as business behavior
Scenario: Returning user signs in
  Given Alice has a registered account
  When she signs in with valid credentials
  Then she sees her dashboard
```

## Best Practices & Anti-Patterns

This table is the **canonical fallback rule set** (subordinate to repo conventions
per *Rule Precedence*). See `references/gherkin-style.md` for depth and examples.

| Rule | Anti-pattern it prevents |
|---|---|
| One behavior per scenario | Multiple unrelated assertions in one scenario |
| Exactly one `When` per scenario | Chained actions hiding what's actually tested |
| Declarative, business-language steps | UI/implementation detail (clicks, selectors, SQL) |
| Reusable, parameterized steps | Near-duplicate steps differing only by a literal |
| `Background` only for shared setup | Background steps used by some scenarios only |
| Meaningful tags, no dead tags | Tag sprawl / tags no runner uses |
| Independent scenarios | Scenarios depending on execution order/shared state |

Example — "one behavior, one `When`" in practice:

```gherkin
# ❌ Two behaviors and two When steps crammed into one scenario
Scenario: Manage cart
  When the user adds an item
  Then the cart shows 1 item
  When the user removes the item
  Then the cart is empty

# ✅ Split: each scenario has exactly one When and one behavior
Scenario: Adding an item fills the cart
  Given an empty cart
  When the user adds an item
  Then the cart shows 1 item

Scenario: Removing the last item empties the cart
  Given a cart with one item
  When the user removes the item
  Then the cart is empty
```

## Workflow

1. **Scan repo conventions** — apply *Rule Precedence* above.
2. **Write/refine the `.feature`** — apply Gherkin Core + Best Practices (or repo
   conventions where they differ). Use `assets/example.feature` as a template.
3. **Detect the stack** — see *Framework Detection* below.
4. **Load the matching framework reference** — read the relevant file under
   `references/` for setup, step-definition syntax, hooks, and the run command.
5. **Generate step definitions** — implement bindings for each step; reuse existing
   steps before adding new ones.
6. **Run the suite** — use the run command from the framework reference.
7. **Verify** — confirm scenarios pass; fix undefined/ambiguous steps.

## Framework Detection

| Signal | Framework | Reference |
|---|---|---|
| `.csproj` referencing `Reqnroll` | Reqnroll (.NET) | `references/reqnroll-dotnet.md` |
| `pom.xml` / `build.gradle` with `io.cucumber` | Cucumber-JVM | `references/cucumber-jvm.md` |
| `package.json` with `@cucumber/cucumber` | Cucumber.js | `references/cucumber-js.md` |

If no BDD framework is present, recommend the conventional choice for the project's
language and follow the matching reference's setup section.
