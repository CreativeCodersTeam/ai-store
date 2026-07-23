# Tester Missing-Test-Project Creation Test (Finding T-2)

Test artifact per `superpowers:writing-skills` (RED → GREEN → REFACTOR → Verify)
for the 2026-07-22 fix of Finding T-2 in
`docs/reviews/2026-07-21-dotnet-skills-review.md`: `dotnet-tester/SKILL.md`
Phase 1 Step 2 only described *finding* an existing test project, while
`dotnet-dev` explicitly rules "`n/a — no test project exists` is NOT valid
(creating it is part of the task)" — the workflow mandated creation, but the
responsible skill never described it.

## Method

A fresh general-purpose subagent receives the Step 2 passage plus the
Conventions section and a scenario (single-project solution, no test project)
and must enumerate every decision/command it would have to improvise to create
one.

## RED — Baseline (old step), 2026-07-22

"The guidance ends exactly there … Everything from this point forward is
improvised." Six improvised areas: naming, location, template bootstrap
(including TFM), solution membership ("forgetting it means `dotnet test` at
solution level silently runs nothing"), project reference, and the package
path. Sharpest find — a compliance trap set up by the skill's own wording:

> An agent's prior strongly associates `Should()` with FluentAssertions, so
> when improvising the install command it may "helpfully" run `dotnet add
> package FluentAssertions` — installing the wrong package, which since v8
> carries a paid commercial license … introduced silently while every test
> still compiles and passes.

## GREEN — New creation path, 2026-07-22

Step 2 gained "**No test project found → create one.**" with five sub-steps:
naming (`<ProductionProject>.Tests`), placement rule, `dotnet new xunit`,
`dotnet sln add` (with the silent-no-tests rationale), project reference, and
packages via the `dotnet-nuget-manager` skill — including the explicit guard
"Install `AwesomeAssertions`, NOT `FluentAssertions` — … FluentAssertions v8+
carries a commercial license", taken directly from the baseline finding.

## Verify + REFACTOR — 2026-07-22

Re-probe: the full creation walk cited the skill for every step. Two
substantive residuals triggered a REFACTOR: TFM matching was a requirement
without a mechanism (fixed: `dotnet new xunit -o <path> -f <tfm>` with the
SDK-default pitfall explained) and template housekeeping (fixed: "Delete the
generated `UnitTest1.cs`"). Follow-up verdict:

> no core decision in the creation path remains improvised — every step is now
> a command or a determinate rule.

Accepted as designed/deferred: CPM handling and version verification live in
the delegated `dotnet-nuget-manager` skill; post-setup verification is the
skill's own Phase 2; a fallback for an absent delegate skill is a
collection-level assumption. Surviving trivia: multi-target TFM choice,
sibling-placement reading.

## Result

The creation path is now fully specified and consistent with `dotnet-dev`'s
"creating it is part of the task" rule; the FluentAssertions licensing trap is
explicitly guarded. One REFACTOR round. Re-run this probe whenever Phase 1
Step 2 changes.
