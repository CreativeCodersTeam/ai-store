# Design Moves

The moves available while writing new code (Step 2), tightening it after green (Step 4), and
removing what does not pay rent (Step 5). The names are the common ones (Fowler lineage) on
purpose: they are shared vocabulary, and a design-notes row that names its move can be checked
against the diff.

Each move applies to **code in the change's scope** — new code, and the part of existing code the
change touches. Restructuring code outside the scope is the `refactor` skill's job, with its own
coverage gate and approval steps.

Every move in Step 4 is followed by a test run. A red run means roll the move back.

## Contents

- [Placing new behaviour (Step 2)](#placing-new-behaviour-step-2)
- [Tightening after green (Step 4)](#tightening-after-green-step-4)
- [Removing what does not pay rent (Step 5)](#removing-what-does-not-pay-rent-step-5)

## Placing new behaviour (Step 2)

| Move | Apply when | Do not apply when | Verify |
|---|---|---|---|
| **Pin before moving** (characterization tests) | a function your change extends must be restructured, and some of its paths have no test | the path cannot be reached without live I/O or global state — leave it and record the gap (rule in `SKILL.md`, Step 2) | the new tests pass against the unchanged code before the first move |
| **Extend existing unit** | the new behaviour shares the unit's reason to change, needs no new dependency, and the unit's name stays truthful | any one of the three fails | the unit's tests still need no new setup for unrelated behaviours |
| **Reuse existing unit** | a helper, value object, or service already encodes the knowledge | the similarity is coincidental (different reasons to change) | no second implementation of the same rule in the diff |
| **New unit + delegate** | the responsibility is distinct from every existing unit | the new unit would only forward (Middle Man) | the new unit is tested directly, without the host |
| **Split phase** | one operation gathers input, decides, and acts | the operation is trivial I/O with no rule | the decision is a function of its inputs and testable without I/O |
| **Port for an external system** | domain logic needs an external system (HTTP, database, file, clock, bus) | the code is pure logic, or the project already has an abstraction for that system (reuse it) | the domain test uses a fake; the adapter is the only place the external API appears and is constructed only where the application is assembled; the adapter has a timeout, a failure behaviour, and a plan for call frequency |
| **Value object** | a primitive carries rules (format, range, currency, unit) and would be validated at several sites | the value is used once and has no rules | invalid values cannot be constructed |
| **Parameter object** | the same group of values travels together through several new signatures | the group appears in one signature | signatures shrink; no caller unpacks it just to pass the parts on |

## Tightening after green (Step 4)

| Move | Signal | Watch out for |
|---|---|---|
| **Extract Method / Function** | a function mixes levels of abstraction, needs comments to divide itself, or grows past ~20 lines | variables written in the block and read after it must become return values, not shared state |
| **Decompose Conditional** | a condition or its branches need a moment to read | preserve short-circuit evaluation |
| **Guard Clauses** | nested conditionals where one path is the normal one | the order of exits decides which one wins |
| **Extract Class** | a unit you extended now has two groups of members with disjoint dependencies | shared mutable state between the two halves; dependency registration |
| **Extract Interface** | a second implementation exists, or a test must replace an external system | one implementation and no second caller is Speculative Generality |
| **Replace Conditional with Polymorphism** | the same type or kind switch appears at two or more sites | one site with a closed set of cases stays a conditional |
| **Consolidate Duplicate** | the logic you wrote exists elsewhere (search the codebase, not only the diff) | coincidental similarity — two rules that change for different reasons |
| **Rename** | a name does not say what the thing is or does in the domain's words | names that are part of a public or serialised contract — user decision |
| **Move Function** | a new function uses another unit's data more than its own | dependency direction between layers |

## Removing what does not pay rent (Step 5)

| Move | Signal | Keep instead when |
|---|---|---|
| **Inline Interface** | one implementation, no external system behind it, no test double needs it | the project convention requires the interface, or it is a module boundary the architecture enforces |
| **Inline Class (Remove Middle Man)** | the unit only forwards calls | it is the seam to an external system |
| **Inline Function** | the body says as much as the name | the name carries domain meaning the body does not |
| **Remove Unused Parameter / Option** | no caller supplies a meaningful value | it is part of a public contract — user decision |
| **Split a premature merge** | a shared function grew a flag to serve two callers differently | the callers really share the knowledge and the flag is data, not mode |
| **Collapse a pattern** | a Factory, Strategy, Builder, or registry with exactly one product or entry | a second entry is part of the current requirement |
