# EF Core Bullet Actionability Test (Finding E-1)

Test artifact per `superpowers:writing-skills` (RED → GREEN → REFACTOR → Verify)
for the 2026-07-22 fix of Finding E-1 in
`docs/reviews/2026-07-21-dotnet-skills-review.md`: `dotnet-ef-core/SKILL.md`
contained non-actionable truism bullets ("Use appropriate change tracking
strategies", "Use appropriate query operators", "Implement appropriate data
access permissions", "Be careful with raw SQL queries", "Use meaningful
primary keys", plus the same-pattern "Implement appropriate navigational
properties") that gave an agent no decision criterion.

## Method

A fresh general-purpose subagent rates each bullet: (a) what concrete,
checkable action does it prescribe, (b) could a reviewer cite it to flag a
violation, (c) is anything technically wrong or overgeneralized?

## RED — Baseline (old bullets), 2026-07-22

0 of 6 actionable, 0 of 6 flaggable. Verdict, verbatim:

> these bullets transfer essentially no EF Core knowledge. Each one names a
> topic area … and then delegates the entire decision back to the reader via
> "meaningful," "appropriate" (x4), and "careful." … They function as a table
> of contents for advice that was never written, not as guidance.

## GREEN — Rewritten bullets, 2026-07-22

All six replaced with concrete, flaggable rules: surrogate-key default with a
natural-key exception criterion; navigations only for traversed relationships;
`Where`/`OrderBy`/`GroupBy` before materialization; tracking only on write
paths (`AsNoTracking` / `AsNoTrackingWithIdentityResolution`); least-privilege
app DB account with separate migration identity; raw SQL only parameterized
with the `FromSqlRaw($"…{userInput}")` injection example.

## Verify + REFACTOR — 2026-07-22

Re-probe: 6/6 prescribe checkable actions, 6/6 flaggable with concrete
hypothetical violations, none technically wrong. Two soft caveats triggered a
REFACTOR round: bullet 3's absolute "never" lacked an escape hatch for
untranslatable predicates (now: "restructure the query instead of
materializing early"), and bullet 6 risked wrongly flagging safe
parameterized `FromSqlRaw` and omitted EF Core 7+ `FromSql` (both now named).
Verifier follow-up: "Yes, both caveats are resolved."

Out of scope (not part of E-1): "Add data seeding through migrations when
appropriate" (Migrations section) and "Use appropriate DbContext lifetimes
(scoped for web apps)" — the latter already carries a concrete criterion.

## Result

Every E-1 bullet now transfers a checkable rule instead of deferring to reader
judgment; one REFACTOR round. Re-run this probe whenever bullets in
`dotnet-ef-core/SKILL.md` are added or reworded.
