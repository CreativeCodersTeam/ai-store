# Gherkin Style Guide

In-depth authoring rules. Subordinate to repo-local conventions (see SKILL.md →
Rule Precedence).

## Declarative vs. Imperative

Imperative (avoid):
```gherkin
Scenario: Login
  Given I open "/login"
  When I type "alice" into "#username"
  And I type "secret" into "#password"
  And I click "#submit"
  Then I see "Welcome"
```

Declarative (prefer):
```gherkin
Scenario: Returning user signs in
  Given Alice has a registered account
  When she signs in with valid credentials
  Then she sees her dashboard
```

Declarative steps survive UI changes and read as business behavior.

## One Behavior, One `When`

Each scenario describes a single behavior with exactly one `When`. If you need a
second `When`, that is a second scenario.

Bad:
```gherkin
Scenario: Manage cart
  When the user adds an item
  Then the cart shows 1 item
  When the user removes the item
  Then the cart is empty
```

Good — split into two scenarios, each with one `When`.

## Scenario Outline

Use outlines to remove duplication across data variations:
```gherkin
Scenario Outline: Password strength
  Given a registration form
  When the user submits the password "<password>"
  Then the strength is shown as "<strength>"

  Examples:
    | password    | strength |
    | abc         | weak     |
    | Abcd1234    | medium   |
    | Abcd1234!@# | strong   |
```

Do not use an outline for a single row — use a plain `Scenario`.

## Background

`Background` is for setup shared by **every** scenario in the file. If only some
scenarios need it, move it into those scenarios (or split the file). Keep Background
short (1–3 steps) and free of assertions.

## Tags

- Use tags for selection/filtering only (`@smoke`, `@regression`, `@wip`).
- Mark work-in-progress with `@wip` and exclude it from CI runs.
- Remove tags no runner or filter uses.

## Step Reuse

Parameterize instead of duplicating:
```gherkin
# Instead of two steps:
#   Given the cart contains a book
#   Given the cart contains a pen
Given the cart contains a "book"
Given the cart contains a "pen"
```
One step definition with a string argument serves both.

## Naming

- `Feature:` names the capability ("Checkout", not "CheckoutTests").
- `Scenario:` names the behavior/outcome, not the mechanics.
- File name mirrors the feature (`checkout.feature`).
