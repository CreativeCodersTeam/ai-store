# implement-direct — Triggering Test (explicit invocation only, and never instead of implement-dev-plan)

**Date:** 2026-09-17
**Subject:** the `description` frontmatter of `skills/development/implement-direct/SKILL.md` and
the **Explicit invocation.** paragraph in its body, measured against the other six descriptions of
the category.
**Question:** does the skill load on the forms of its own name and on nothing else — in particular
not on the implementation phrasings its description lists as exclusions, not on a paraphrase that
merely contains the word "direct", and not in place of `implement-dev-plan` when a plan is named?

## Why this is a separate artifact

Triggering is decided from the skill list alone, before any file is read, so the test is the skill
list. `implement-direct-workflow-test.md` measures what the skill does once loaded; it cannot
measure whether it loads. The method follows `skills/tests/development/_shared/explicit-invocation-test.md`,
which covers the category as a whole; this artifact covers the seventh skill added to it and the
one confusion the other six could not produce — two implementation workflows side by side.

## The probe

A fresh sub-agent with no file access and no tools sees the seven `development` descriptions
exactly as Claude Code lists them, and classifies twelve requests as `load <skill>` or `load none`
with a half-sentence reason. It is told not to do the work the request asks for.

Four requests name the skill in one of its accepted forms. One names `implement-dev-plan`. Seven
must load nothing, and they carry the weight: six are phrasings the description lists verbatim as
exclusions, and two are the hard cases — a `docs/plans/` path without a skill name (9 in the
category artifact's numbering, 7 here), and "direct implementation", a paraphrase that shares a
word with the name without being it.

| | Request | Expected | Result |
|---|---|---|---|
| 1 | `/implement-direct Add PUT /todos/{id}/done: 404 unknown, 409 already done, 200 updated todo.` | implement-direct | ✓ |
| 2 | "add a PUT endpoint to mark todos done — 404 for unknown ids, 409 if already done" | none | ✓ |
| 3 | "run implement-direct on the mark-as-done button, it needs the full treatment" | implement-direct | ✓ |
| 4 | "implement this feature: as a user I want to tick off todos …" + acceptance criteria | none | ✓ |
| 5 | `/cc-ai-dev:implement-direct` followed by a three-paragraph requirement | implement-direct | ✓ |
| 6 | "run implement-dev-plan on docs/plans/mark-todo-done.md" | implement-dev-plan | ✓ |
| 7 | "implement docs/plans/mark-todo-done.md, the plan is approved" | none | ✓ |
| 8 | "implement direct the done endpoint please, I want the questions up front" | implement-direct | ✓ |
| 9 | "direct implementation of the done endpoint please, no plan needed" | none | ✓ |
| 10 | "Can you just build the mark-as-done button? Don't ask me any questions, I'm in a hurry." | none | ✓ |
| 11 | "The done endpoint returns 200 even when the todo was already done. Why?" | none | ✓ |
| 12 | "implement the plan we discussed yesterday" | none | ✓ |
| 13 | `/run-with-skills implement-direct Add PUT /todos/{id}/done: …` (from the 2026-09-27 re-run) | run-with-skills | ✓ |
| 14 | "implement direct with skills: the done endpoint, and I want to see the skills first" (from the 2026-09-27 re-run) | implement-direct | ✓ |

**12 of 12 correct.** The probe's own summary of the pattern it found: the only loads are the
requests that literally contain the skill name or one of its slash forms; every paraphrase, task
description or file path, however close in intent, resolves to none.

## The two cases worth keeping

**9 versus 8.** "Implement direct the done endpoint" loads, "direct implementation of the done
endpoint" does not, and the two are one word apart. This is the line the description draws and it
held: an accepted form of the name is an invocation, a sentence that describes directness is not.
If a future description edit blurs this, 9 is the case that will show it.

**10 as a near-miss of a different kind.** "Don't ask me any questions" is the opening of the
waiver scenario in `implement-direct-workflow-test.md`, and it is the phrase most likely to look
like a reason to reach for a workflow that specialises in asking questions. It must not load,
because nobody named it. The probe's reason was exactly that, and it noted the second point too:
the request is the opposite of what the workflow does.

## Relationship to the category artifact

`_shared/explicit-invocation-test.md` measures the six original descriptions on thirteen requests
and remains the authority for the category rule. This artifact adds the seventh description and
the one interaction the six could not produce — `implement-direct` and `implement-dev-plan` are
both implementation workflows whose names begin with the same word, and requests 6, 7 and 12 are
the three ways that pair can be confused: the plan skill named, a plan path without a name, and a
plan mentioned in prose.

## Re-run 2026-09-27 — `run-with-skills` added to the category

Required by the rule below: a skill was added. Same harness, the nine current descriptions inline,
requests 1–12 unchanged, two added for the new skill's confusions with this one. **14 of 14
correct**; none of the twelve earlier answers moved.

- **13** — two skill names in one request. `run-with-skills` loads, `implement-direct` is its
  argument. The probe also checked implement-direct's "must not be started by another skill …
  on the user's behalf" and found it not violated, because the user named implement-direct
  themselves — the argument `run-with-skills` makes in its Step 2.
- **14** — "implement direct" is a listed form; "with skills" is not "run with skills". The probe
  loaded implement-direct and worried the user's wish to see the skills first would go unmet,
  since the description only promises "runtime-discovered mandatory skills". That worry does not
  hold against the body: Gate 2 lets the user keep, drop, and add skills by multi-select
  (`skills/development/implement-direct/SKILL.md:248-250`). The description need not say it.

Cases for `run-with-skills` itself are in
`skills/tests/development/run-with-skills/run-with-skills-triggering-test.md`.

## Re-run this when

- Any word of `implement-direct`'s `description` changes, including the exclusion list.
- A skill is added to the `development` category, especially one whose name begins with
  "implement" — add its confusions to the twelve.
- `implement-dev-plan`'s description changes in a way that touches its own exclusions, since
  requests 6, 7 and 12 are scored against both descriptions at once.
