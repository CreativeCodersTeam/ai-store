# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

A distribution of **Agent Skills** — there is no application, no build system, and no
package manifest. The deliverables are `SKILL.md` files plus their `references/` and `scripts/`
siblings, consumed by Claude Code and other agents via `npx skills add …` (see README). Tests are
not a skill sibling — they live under `skills/<category>/tests/` (see below).
Everything is Markdown and Bash; "shipping" means merging to `main`.

## Commands

Only the `dotnet-reviewer` scripts have an automated test suite; it lives in
`skills/dotnet/tests/dotnet-reviewer/`, not inside the skill. Run from the repository root:

```bash
bash skills/dotnet/tests/dotnet-reviewer/run-tests.sh                 # all unit tests (builds fixtures on first run)
bash skills/dotnet/tests/dotnet-reviewer/unit/test-detect-version.sh  # a single test file
bash skills/dotnet/tests/dotnet-reviewer/clean-fixtures.sh            # drop generated repo-*/ fixtures
```

Requires `bash` 3.2+, `git`, `jq`, `python3`. The `dotnet` SDK is **not** needed — `run-checks.sh`
is exercised against `…/tests/dotnet-reviewer/unit/mock-dotnet/dotnet` (behavior via
`MOCK_DOTNET_MODE`). `…/tests/dotnet-reviewer/integration/test-skill-flow.md` is a manual checklist
and is not run by `run-tests.sh`. Unit tests resolve `TESTS_DIR` (fixtures, `helpers.sh`, mock) and
`SKILL_DIR` (`skills/dotnet/dotnet-reviewer/`, the scripts under test) separately; `run-tests.sh`
exports both and each test derives them from its own location when run directly.

The `angular-reviewer` and `gherkin-bdd-reviewer` scripts have no test suite; verify them by hand.

## Skill anatomy

```
skills/<category>/<skill-name>/SKILL.md          # required; name in frontmatter MUST equal the directory name
                              references/*.md    # depth material, loaded on demand
                              scripts/*.sh       # only for skills that run tools
skills/<category>/tests/*-test.md                # skill-behavior test artifacts (see below)
skills/<category>/tests/<skill-name>/            # Bash test suite for that skill's scripts/
```

Frontmatter is `name` + `description` only. The **description is load-bearing** — it is the sole
trigger for auto-loading, so it must read as a precise "Use when …" and, for reviewer skills,
must actively exclude wrong activations ("Must NOT activate on generic 'review my code'").

## Skill archetypes

Four recurring shapes; when adding or editing, match the archetype rather than inventing a layout.

- **Router** (`dotnet`, `angular`) — holds *no* best-practice content; maps a request to a
  specialized skill and documents which skills compose with which. Update it whenever a skill is
  added, removed, or renamed in its family.
- **Knowledge** (`dotnet-fundamentals`, `dotnet-aspnet`, `dotnet-ef-core`, `angular-*` peers) —
  `SKILL.md` + `references/` only, no scripts, no workflow gates.
- **Workflow** (`dotnet-dev`, `angular-dev`, `implementer`) — strict phase-gated pipelines
  (Requirement Review → Clarification → Task Breakdown → Implementation → Code Review → Summary)
  with a "Skill Map — Mandatory Bindings" table dispatching to the knowledge skills, plus explicit
  `n/a` / waiver rules and red flags.
- **Reviewer** (`dotnet-reviewer`, `angular-reviewer`, `gherkin-bdd-reviewer`) — numbered steps
  driving `scripts/`, checklist `references/`, a `severity-taxonomy.md`, a `report-format.md`, and
  a report written to `docs/reviews/YYYY-MM-DD-<branch>-<mode>.md`. Explicit invocation only;
  never auto-commit, never overwrite.

## Cross-cutting conventions that are easy to break

**Family parity.** The .NET and Angular families are deliberate mirrors — `dotnet-dev`/`angular-dev`,
`dotnet-fundamentals`/`angular-fundamentals`, `dotnet-xmldocs`/`angular-tsdoc`,
`dotnet-sdk-builder`/`angular-library-builder`, `dotnet-reviewer`/`angular-reviewer`. A structural
change to one side is normally mirrored to the other; if it is not, say why.

**Single-sourcing of rules.** A rule lives in exactly one canonical home (usually the family's
`*-fundamentals/references/`); every other mention is a short context hook that restates the rule
identically and links to that home. Divergent restatements of the same rule are the defect class
this repo has repeatedly fixed (see `docs/analysis/2026-08-02-dotnet-skills-review.md`). After
editing a rule, grep the whole family for other mentions and align them.

**Script contracts.** Reviewer scripts print JSON on stdout and signal outcomes via documented
exit codes (e.g. `detect-dotnet-version.sh`: 0 ok / 1 usage / 4 SDK<10 / 5 malformed;
`collect-diff.sh`: 0 / 1 / 2 not-git / 3 baseline-missing; `run-checks.sh` always exits 0 and
reports tool failures inside the JSON). The consuming `SKILL.md` enumerates every exit code, so
changing a script means updating its `SKILL.md` step **and**
`skills/dotnet/tests/dotnet-reviewer/unit/test-<name>.sh`.

**Interactive vs. non-interactive.** Skills that ask the user questions must also define the
sub-agent path: never stall, never guess — fall back to documented defaults and record the
parameter origin in the report.

## Testing skill behavior

`skills/<category>/tests/*-test.md` are the test artifacts for behavior that cannot be asserted in
Bash. They follow `superpowers:writing-skills` (RED → GREEN → REFACTOR): baseline evidence
(usually grep output showing the gap), the fix, and a verification probe run by a **fresh subagent
given only the passage under test and no file access**, which answers scenario questions and
accuracy-checks the claims. Behavior changes to a skill should add or amend one of these, and an
artifact that says "re-run this probe when X changes" means exactly that.

## When adding or renaming a skill

Update `README.md` — both the category counts table and the per-category "Available Skills" table —
and the family router `SKILL.md`. Both are hand-maintained and drift silently.
