# Description Selection Test (Finding C-1)

Test artifact per `superpowers:writing-skills` (RED → GREEN → Verify) for the
2026-07-21 rewrite of all `skills/dotnet/*/SKILL.md` frontmatter descriptions
(Finding C-1 in `docs/reviews/2026-07-21-dotnet-skills-review.md`).

## Method

A fresh general-purpose subagent receives **only** the 11 `name: description`
pairs (no file access, no tools) plus 8 task scenarios and must name the one
skill it would load per scenario. Scenario 1 additionally asks which process
the agent would expect to follow based on the description alone — this probes
the CSO trap where a description that summarizes the workflow replaces reading
the skill body.

## Scenarios and expected selections

| # | Request | Expected |
|---|---|---|
| 1 | "Write unit tests for OrderService" | `dotnet-tester` |
| 2 | "Review my code" (in a .NET repo) | none (reviewer must not activate) |
| 3 | "Run a dotnet code review please" | `dotnet-reviewer` |
| 4 | "What types does the package System.CommandLine export?" | `dotnet-inspect` |
| 5 | "Bump Newtonsoft.Json to 13.0.4 in this solution" | `dotnet-nuget-manager` |
| 6 | "Wrap the Stripe REST API in a typed C# client" | `dotnet-sdk-builder` |
| 7 | "Register a scoped service in my Worker Service" | `dotnet-fundamentals` |
| 8 | "I need help with something in .NET, not sure exactly what yet" | `dotnet` (router) |

## RED — Baseline (old descriptions), 2026-07-21

Selection: **8/8 correct.** The old descriptions did not primarily fail on
selection accuracy.

Scenario 1c (process expectation) — **failure confirmed.** From the old
description ("Writes, executes, and completes unit tests … Uses a second agent
to identify missing test cases") the agent constructed its own five-step
workflow, verbatim:

> (1) analyze the OrderService class …; (2) write unit tests using the
> prescribed stack …; (3) dispatch a second agent to identify missing/uncovered
> test cases; (4) fill in the additional tests …; (5) execute the tests and
> iterate until they pass/complete.

This diverges from the actual skill body: the skill requires executing tests to
green in Phase 2 **before** the missing-case analysis (Phase 3); the inferred
workflow runs tests last. Exactly the trap described in
`superpowers:writing-skills`: a workflow-summarizing description becomes a
shortcut and the skill body gets skipped or misremembered.

## GREEN/Verify — New descriptions, 2026-07-21

Selection: **8/8 correct** (same scenarios, fresh subagent).

Scenario 1c — **fixed.** Verbatim:

> The description does not tell me the process — it only states when to use the
> skill … and which frameworks it supports …, not the steps to follow; I would
> need to read the skill content first to know the actual process.

## Result

All 10 rewritten descriptions pass. No REFACTOR round needed. Re-run this test
whenever a description under `skills/dotnet/` changes.

---

## Re-Run 2026-08-02 (Finding N-2)

Re-run for the `dotnet-fundamentals` description change fixing Finding N-2 in
`docs/analysis/2026-08-02-dotnet-skills-review.md`: the frontmatter description
listed only the topical triggers (DI, Options, configuration, idioms) and did
not carry the baseline role that the SKILL.md body states (the verified F-1
wording, see `fundamentals-facts-test.md`) — risking undertriggering on plain
C# production-code tasks with no DI/Options keyword.

**Change:** two sentences appended to the description, mirroring the F-1 body
wording: "Also use as the baseline whenever any C# production code is written
or modified — dotnet-aspnet, dotnet-ef-core, and dotnet-sdk-builder build on
it; load it alongside them, not instead of them."

**Method:** same probe as above (fresh subagent, only the 11 `name:
description` pairs, no file access), scenarios 1–8 unchanged (single choice),
plus a new scenario probing exactly the N-2 gap:

| # | Request | Rule | Expected |
|---|---|---|---|
| 9 | "Add a PriceCalculator class with business logic to my console app" | list every licensed skill with citation | `dotnet-fundamentals` licensed (alongside `dotnet-dev`) |

**RED — old description:** Scenarios 1–8 safe (7 → `dotnet-fundamentals`; the
reviewer did not activate on scenario 2 — the agent chose the router instead of
"none", which preserves the guarded property). Scenario 9 — **failure
confirmed**, verbatim:

> **dotnet-fundamentals is NOT among them.** … A plain "add a class" request
> matches no fragment of that description.

Only `dotnet-dev` was licensed; the baseline knowledge skill would not have
been loaded for its core case.

**GREEN — new description:** Scenarios 1–8: **8/8 correct**, scenario 2 now
exactly "none"; `dotnet-fundamentals` still wins only scenario 7 — the
appended baseline clause did not turn it into a catch-all magnet (the
"alongside them, not instead of them" phrasing keeps it out of single-choice
wins). Scenario 9 — **fixed**, verbatim:

> **dotnet-fundamentals** — **yes, it is among them.** … Adding a
> PriceCalculator class writes C# production code, so this baseline clause
> licenses loading it regardless of whether DI/configuration/idioms are
> explicitly requested.

## Result (Re-Run)

N-2 fixed and verified; no REFACTOR round needed (the rollback criterion —
fundamentals winning a foreign single-choice scenario — did not trigger).
Scenario 9 is now part of this test's scenario set for future re-runs.
