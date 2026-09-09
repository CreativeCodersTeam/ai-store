# .NET Version Cascade Test (K-1, M-7)

Test artifact per `superpowers:writing-skills` (RED → GREEN → REFACTOR → Verify) for the 2026-08-03
unification of .NET version references behind a single resolution cascade, closing Findings **K-1**
and **M-7** in `docs/analysis/2026-08-02-dotnet-skills-review.md`.

## Method

A fresh general-purpose subagent receives the canonical passage
(`dotnet-fundamentals/references/target-framework.md`) verbatim and **no file access, no tools**, and
answers six scenario questions plus an accuracy check: which target wins, what origin is recorded,
whether `(since X)` selects a target, and whether two agents could resolve the same repo differently.

## RED — Baseline, 2026-08-03

No cascade existed. Five sites each named a different version as if it were the baseline, with no
rule ranking them (grep over `skills/dotnet`, `README.md`):

| Site | Claim |
|---|---|
| `dotnet-sdk-builder/references/project-setup.md:18` | template scaffolds `net9.0` |
| `dotnet-nuget-manager/SKILL.md:18` | prerequisite ".NET 8.0 SDK or later" |
| `dotnet-reviewer/SKILL.md:3,8,17,49` | hard-aborts below ".NET 10+" |
| `dotnet-inspect/SKILL.md:26` | example TFM `net8.0` |
| `dotnet-fundamentals` / `dotnet-aspnet` | `(.NET 7+)`, `(.NET 8+)`, `(.NET 9+)`, `(C# 12)` — no statement that these are availability markers rather than targets |

Consequences, both recorded in the analysis doc: **K-1** — `dotnet-dev` Phase 5 mandates
`dotnet-reviewer` ("always"), which refused every project below .NET 10, so the core workflow was
unfinishable on a `net8.0`/`net9.0` repo with no `n/a` reason available. **M-7** — Step 6 referenced
`review-checklist-net<N>.md` generically while only `-net10` existed, with no fallback.

`dotnet-sdk-builder` Step 2 was the only version procedure in the family, and it neither consulted
`global.json`/`Directory.Build.props` nor defined a default: "If versions differ → ask the user."
Non-interactive invocation had no path at all.

## GREEN — 2026-08-03

`dotnet-fundamentals/references/target-framework.md` created as the single canonical home: explicit
user directive → repo directive → latest LTS (currently .NET 10), plus origin recording
(`user` / `repo:<file>` / `default-lts`), the `(since X)` ≠ target rule, and a non-interactive path.
Every other mention reduced to a hook: `dotnet` router Version-baseline note, sdk-builder Step 2,
`project-setup.md` (`net9.0` → `net10.0`), nuget-manager prerequisite, inspect example TFM,
tester TFM fallback, `dotnet-dev` REFERENCE.md Phase 1. All `(.NET N+)` / `(C# N)` markers
normalized to `(since …)`.

Gate removed: `detect-dotnet-version.sh` lost both version gates and gained `resolved_from`;
`dotnet-reviewer` Step 2 treats the version as checklist input rather than an entry condition;
Step 6.1 gained the M-7 selection rule (exact → highest `M ≤ N` → general checklists only, always
named in the report).

## Verify — probe, 2026-08-03

All six scenarios answered correctly, each with the governing sentence quoted:

- (a) user says `net8.0` in a `net10.0` repo → **net8.0**, conflict stated once, origin `user`.
- (b) empty directory → **net10.0**, origin `default-lts`.
- (c) `Api.csproj` net10.0 vs `Legacy.csproj` net8.0, new library → **highest**, survey stated;
  as a sub-agent, same answer and no question ("it does not become a question").
- (d) props `net10.0` vs the project's own `net8.0`, adding a file → **the project's own**.
- (e) "(since .NET 8)" on keyed services → **no**, it is an availability marker.
- (f) target net8.0, feature "(since .NET 9)" → use the documented alternative and say why.

Accuracy check confirmed .NET 10 is the current LTS (GA Nov 2025; .NET 11 would be STS), and
returned five reproducible ways two agents could diverge.

## REFACTOR — 2026-08-03

Four defects the probe found were real and were fixed:

1. **`global.json` was ranked first among TFM sources — factually wrong.** `sdk.version` pins the
   SDK that *builds* the repo and carries no TFM (SDK 10 builds `net8.0`; SDK 8 cannot build
   `net10.0`). As written, a repo with `global.json` = `10.0.100` and `Directory.Build.props` =
   `net8.0` resolved to net10.0 — discarding the only real declaration. It also contradicted the
   file's own "existing project wins" rule. Rewritten: `*.csproj` → `Directory.Build.props` are the
   TFM sources; `global.json` is a **feasibility constraint** (pinned SDK older than the resolved
   target → say so and stop) and a last-resort signal when nothing else declares a TFM. This also
   makes the doc agree with `detect-dotnet-version.sh`, which already preferred csproj → props →
   global.json.
2. **Multi-targeting was unaddressed** despite the table telling readers to parse
   `<TargetFrameworks>`. Added: all listed TFMs are targets, so new code writes to the **lowest**;
   when one value must be named, take the highest and list the rest. Added a comparison rule for
   platform suffixes and the `netstandard` / `net4xx` families, which are not rankable against
   `net<N>.0`.
3. **"use the LTS" had two defensible origin codes** (`user` vs `default-lts`). Resolved: a
   directive naming no concrete version is a *pointer* to a later step; resolve there, record `user`.
4. **Feasibility and conflict reporting were missing.** Added the installed-SDK check
   (`dotnet --list-sdks`), the "no documented alternative" branch for `(since X)` gaps, and a
   requirement to record the discarded signal alongside the origin
   (`user (repo:src/Api/Api.csproj targets net10.0)`).

Also added: test projects match the project under test rather than the repo maximum; MSBuild
property-reference and chained-props TFMs resolve as MSBuild would, else fall through.

Declined as out of scope for a skill reference: `rollForward`/`allowPrerelease` semantics, and
full MSBuild property evaluation — the catch-all clause covers the failure case.

## Result

One rule, one home, one number to bump. K-1 is closed — `dotnet-reviewer` reviews a `net8.0` repo
with the general checklists instead of aborting, so `dotnet-dev` Phase 5 is completable at any
version. M-7 is closed — checklist selection has a defined fallback that is always named in the
report. Bash coverage: `skills/tests/dotnet/dotnet-reviewer/scripts/unit/test-detect-version.sh` (16 assertions, including
the inverted `repo-net8` case, `repo-no-project`, and `repo-props-tfm`).

Re-run this probe whenever `target-framework.md`, the router Version-baseline note, or
`dotnet-reviewer` Step 2/6.1 changes — and when the latest LTS moves past .NET 10.
