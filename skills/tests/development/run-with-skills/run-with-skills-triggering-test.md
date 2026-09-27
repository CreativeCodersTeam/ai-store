# run-with-skills — Triggering Test (explicit invocation only, and never instead of the workflow it wraps)

**Date:** 2026-09-27
**Subject:** the `description` frontmatter of `skills/development/run-with-skills/SKILL.md`,
measured against the other eight descriptions of the category.
**Question:** does the skill load on the forms of its own name and on nothing else — in particular
not on requests that describe what it does ("show me the skills first and let me select them"),
not on a near-miss of its name, and not in place of `implement-direct` when only that is named?

## Why this is a separate artifact

Triggering is decided from the skill list alone, before any file is read, so the test is the skill
list. `run-with-skills-workflow-test.md` measures what the skill does once loaded; it cannot
measure whether it loads. The method follows `skills/tests/development/_shared/explicit-invocation-test.md`.

## The probe

A fresh sub-agent, allowed one Read of a scratch file holding the nine `development` descriptions
exactly as Claude Code lists them (`cc-ai-dev:<name>: <description>`), classifies fourteen requests
as `load <skill>` or `load none` with a half-sentence reason. It is told not to do the work.

Four requests name the skill in one of its forms. Three name only `implement-direct` — two of them
while asking for exactly the behaviour run-with-skills adds. Seven must load nothing: a phrase the
description lists as an exclusion (5), a one-word near-miss of the name (7), questions and
instructions about skills in general (8, 9, 13), the skill's behaviour described without its name
(14), and a German paraphrase of the name alongside a named workflow (12).

| | Request | Expected | Result |
|---|---|---|---|
| 1 | `/run-with-skills implement-direct Add PUT /todos/{id}/done: …` | run-with-skills | ✓ |
| 2 | "run with skills: implement-dev-plan on docs/plans/checkout.md" | run-with-skills | ✓ |
| 3 | `/cc-ai-dev:run-with-skills dotnet-dev Add GET /api/orders/{id}/summary` | run-with-skills | ✓ |
| 4 | "run-with-skills auto-loop — all tests in src/parser green, budget 6 rounds" | run-with-skills | ✓ |
| 5 | "Implement the done endpoint and make sure you use the right skills this time." | none | ✓ |
| 6 | "run implement-direct on the mark-as-done button, it needs the full treatment" | implement-direct | ✓ |
| 7 | "run it with skills, whatever fits — add CSV export to GET /orders" | none | ✓ |
| 8 | "Which skills should I use to implement the CSV export?" | none | ✓ |
| 9 | "Load the dotnet skills and add GET /api/orders/{id}/summary." | none | ✓ |
| 10 | `/implement-direct Add CSV export — and let me pick the skills with you before any code is written.` | implement-direct | ✓ |
| 11 | "implement-direct, but I want to choose the skills myself before you write code" | implement-direct | ✓ |
| 12 | "Mit Skills ausführen: implement-direct für den CSV-Export" | implement-direct | ✓ |
| 13 | "run the skills: tests and lint, then tell me what failed" | none | ✓ |
| 14 | "Build the CSV export. Before coding, show me which installed skills apply and let me select them." | none | ✓ |

**14 of 14 correct.**

## The cases worth keeping

**10, 11, and 14 — the behaviour without the name.** Each asks for the checkpoint run-with-skills
provides, and none loads it. That is the line the category draws: describing a workflow is not
invoking it. 10 and 11 lose nothing, because implement-direct's own Gate 2 already asks the user
to keep, drop, and add skills. 14 loads nothing and is handled as an ordinary request. If a future
description edit starts matching on "let me select the skills", 14 is the case that will show it.

**12 — a paraphrase of the name next to a real name.** The probe itself called this the hardest:
the user plausibly means run-with-skills, but only "implement-direct" is a name, so that is what
loads. A less literal model could pick run-with-skills; the category rule (names only, English
forms) is what keeps it deterministic.

**7 — one word off.** "run it with skills" is not "run with skills". It loads nothing, and no
workflow is named either.

## What the probe flagged beyond the table

- **implement-direct's description** says it "must not be started by another skill … on the user's
  behalf". The probe resolved case 1 correctly (the user named implement-direct inside the request),
  but noted that neither description says so. run-with-skills' body carries the argument (Step 2,
  Precedence); the maintainer decided not to amend implement-direct (see the workflow test).
- **No `run run-with-skills` form** in the description, unlike the other eight's `run <name>`.
  Not added: "run run-with-skills" is not a phrase anyone types, and the three listed forms plus
  the slash forms cover the realistic ones.
- **dotnet-dev in case 3** is not in this category's list; the probe correctly left that to the
  skill's Step 1 after loading.

## Re-run this probe when

- the `description` of run-with-skills changes;
- a description in `skills/development/` gains a phrase about selecting or loading skills;
- implement-direct's or implement-dev-plan's description changes its skill-selection wording.
