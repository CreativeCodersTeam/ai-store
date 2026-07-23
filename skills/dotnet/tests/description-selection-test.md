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
