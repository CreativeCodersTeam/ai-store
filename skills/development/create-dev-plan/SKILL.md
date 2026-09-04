---
name: create-dev-plan
description: >
  Use when the user wants to turn an approved specification (a create-dev-spec document in
  docs/specs/) or any other requirement — pasted text, an issue URL, a requirements document —
  into a development plan before implementation starts: requests like "create a dev plan",
  "plan the implementation", "break this spec into tasks", "what are the tasks for this",
  "Entwicklungsplan erstellen", or when an implementation workflow needs a task list with
  dependencies and tests. Reviews the spec for gaps, clarifies them with the user, surveys the
  codebase, decomposes the work into tasks with explicit interfaces, and binds every requirement
  ID to the test that will prove it (Verifies blocks, traceability matrix). Writes a reviewable
  draft to docs/draft/, waits for explicit approval, then the final plan to docs/plans/. Not for
  writing the spec itself (that is create-dev-spec) and not for implementing anything.
---

# create-dev-plan — From Approved Specification to Reviewed Development Plan

## Core Principle

A plan is the contract between the specification and whoever implements it one task at a time.
The person or agent who picks up Task #4 has not done Tasks #1–3 and will not read the spec end
to end. The plan has to tell them what already exists, what they consume, what they must deliver,
and which test proves it. Two things make that possible: every decision in the plan traces back
to a requirement ID or to a recorded clarification, and nothing that shapes the plan is guessed —
a gap in the spec becomes a question, and the user has the final say at a gate. A plan built on
assumptions is the most common cause of rework; this workflow exists to prevent it.

The output is two files:

| Artifact | Path | Purpose |
|---|---|---|
| Draft | `docs/draft/plan_<slug>.md` | Everything decided so far, written for review |
| Plan | `docs/plans/<slug>.md` | The final document, produced only after explicit approval |

`<slug>` is the spec's slug (`docs/specs/<slug>.md`). For a raw requirement without a spec it is
decided in Phase 2. When the spec is cut into several plans (Phase 2, `C-scope`), each part is
`docs/plans/<slug>-<n>-<part>.md` and every part carries the same *Plan Set* table.

## Flow Overview

```
Phase 0  Intake           — classify the input; complete spec or not; headless check      (step 1)
Phase 1  Spec Review      — read everything, classify every requirement, list the gaps     (steps 2–3)
Phase 2  Clarification    — one structured question per blocking gap; scope decision       (step 4)
Phase 3  Codebase Survey  — constraints, conventions, patterns, test setup, mock boundaries (step 5)
Phase 4  Decomposition    — files → tasks → interfaces → Verifies blocks → matrix           (steps 6–8)
Phase 5  Draft            — self-check, write docs/draft/plan_<slug>.md                     (step 9)
GATE     Plan review      — STOP; user edits, discusses (→ Phase 2 or 4), or approves       (steps 10–11)
Phase 6  Plan             — re-read the draft from disk, write docs/plans/<slug>.md          (step 12)
```

## Critical Rules (read before every phase)

1. **Every open point goes through the structured question tool.** Use your runtime's tool for
   structured user questions (in Claude Code: `AskUserQuestion`), never a prose question. Each
   question carries 2–4 concrete proposals, the recommended one first and marked "(Recommended)",
   each with its consequence in one sentence, and a free-form escape (Claude Code's tool adds
   "Other" itself; add "Something else — I'll describe it" where the tool does not).

2. **The spec is read-only.** Nothing you learn here changes `docs/specs/`. Answers to your
   questions go into the plan's *Clarification Log*; everything the spec should absorb — assigned
   IDs, answered questions, gaps, untestable criteria — goes into *Spec Feedback*. The user decides
   when and whether the spec is updated; the plan makes sure nothing is lost meanwhile.

3. **Every requirement ID lands in a Verifies block and in the matrix.** Acceptance criteria
   exactly once across the whole plan set; functional, non-functional, and interface IDs at least
   once. No empty matrix cell — a non-functional requirement without a measurable target reads
   `manual` with a named check step, never a blank. A draft that fails this self-check is not
   presented; it is fixed first.

4. **The test comes first — in the plan.** A task's Todos begin with one test per ID it verifies,
   then the implementation, then documentation. The order is part of the plan because it is what
   makes the Verifies block honest: a test named before the code is a promise, one named after it
   is a description.

5. **The draft gate is mandatory and only explicit approval passes it.** After writing the draft
   you STOP. "Looks good", "continue", "ok" after a question, or silence are not approvals — see
   the Gate section.

6. **After approval, test names and interfaces are frozen.** The only permitted edits to an
   approved plan are ticking checkboxes and appending to its *Change Log*. Renaming a test,
   changing a signature, or re-cutting a task during implementation is a plan change and is
   recorded as one, with the reason. This is what lets a reviewer check the matrix against the
   test suite at the end.

7. **Never commit, never overwrite silently.** You create the draft and the plan; the user
   commits. If the target file exists, ask before replacing it.

8. **Urgency waives nothing.** "Just give me the task list" is not permission to skip the review,
   the questions, or the gate. Run the workflow at speed: fewer but sharper questions, batched
   where independent, never zero.

## Precondition — Interactive User

Phases 2 and the gate need a person. **Judge the run, not your message channel:** the precondition
is unmet only when the whole run has no user behind it — you were dispatched by a script, CI,
cron, or another agent whose output is consumed by a program.

When it is unmet, what you can do depends on the input:

| Input | Headless behaviour |
|---|---|
| Complete spec (Phase 0 criteria) | Run Phases 1, 3, 4, 5. Every Phase 2 item goes **unanswered** into *Open Questions* as `unresolved — blocks Task #n`, and each affected task is marked `blocked`. Write the draft with status `DRAFT — headless, unresolved questions`. Do **not** write `docs/plans/`. Reply `Draft only — interactive user required for approval`, followed by the path and the list of unresolved items. |
| Anything else | Run Phase 0 and Phase 1 only, then STOP with a `Blocked — interactive user required` handoff: the requirement inventory and the gap list, and one line that an interactive user can resume at Phase 2. Create no files. Deriving acceptance criteria without the user is inventing the requirement. |

## Phase 0 — Intake

1. Identify the input: a spec path, pasted text, an issue URL, or another document. Fetch a URL
   with the runtime's tool; if you cannot fetch, ask the user to paste the content. Never plan
   from a title.
2. Decide whether it is a **complete spec**. All four must hold:
   - numbered functional requirements (`FR-n`) and acceptance criteria (`AC-n`);
   - non-functional requirements (`NFR-n`) present, or the section explicitly `n/a`;
   - every acceptance criterion names the functional requirement(s) it verifies;
   - a Decisions Log or an equivalent record of the decisions behind the requirements.

   A document with some of this is *incomplete*, and takes the same branch as raw text.
3. If it is not complete, ask via the question tool: **(a) Recommended — run `create-dev-spec`
   first** and resume here with the finished spec; the interview there is what turns gaps into
   decisions. **(b) Plan directly from this requirement** — you will assign IDs, propose
   acceptance criteria the user confirms one by one, and list all of it as Spec Feedback. On (a),
   invoke `create-dev-spec` and re-enter this phase with the spec path when it is done. On (b),
   add `L-1` (language) and `L-2` (slug) to the Phase 2 list; with a spec they are inherited.
4. Record the spec source for the plan header: path and commit (`git log -1 --format=%h --
   <path>`) or date, so that a later spec change is detectable.

## Phase 1 — Spec Review

Goal: know every requirement and every hole before deciding anything.

1. Read the whole document once, end to end, before noting anything. Plans written from a
   half-read spec contradict its later sections.
2. Build the **Requirement Inventory**: every ID with its *kind* — behaviour, rule, contract, or
   quality — per [`references/traceability.md`](references/traceability.md#classification). The
   kind, not the prefix, decides the test type later. Assign IDs where they are missing: `FR-n`,
   `NFR-n`, `AC-n` continuing the existing numbering, `IF-n` for every interface or data contract
   in the spec's Design / Data / API section. Each assigned ID is marked `origin: assigned by
   plan` and goes to Spec Feedback.
3. Walk the checklist in [`references/spec-review.md`](references/spec-review.md). Every
   finding becomes a gap `G-n` with the ID it concerns. Some checks are always run:
   - a functional requirement whose acceptance criteria show only the success path;
   - a non-functional requirement without a measurable target and without an explicit
     "no target";
   - an acceptance criterion that cannot be translated into a test as written;
   - a spec *Open Question* whose trigger is "at implementation" — it is due now;
   - a constraint the spec states that the codebase contradicts (checked again in Phase 3).
4. Mark each gap **blocking** (a task cannot be defined or tested without the answer) or **note**
   (recorded in Spec Feedback; the plan proceeds). Post the inventory summary and the gap list as
   one numbered overview. This is not a gate — continue without waiting.

## Phase 2 — Clarification

Goal: every blocking gap becomes a recorded decision.

1. Per blocking gap, in order of how much a wrong guess would cost: one call of the question
   tool, recommendation first, consequences per option, free-form escape. Up to four
   *independent* items per call; dependent items in separate calls.
2. Record every answer at once in the **Clarification Log**: `C-n · question · decision ·
   rationale · origin (proposal / user's own / draft edit)`. The log goes into the plan verbatim
   and into Spec Feedback as a backport list.
3. Fixed items, always asked:

   | ID | Item | Why |
   |---|---|---|
   | `C-scope` | One plan or several? | A spec that covers independent subsystems, each deliverable and testable alone, belongs in several plans. Propose the cut per [`references/task-design.md`](references/task-design.md#scope) — the default recommendation is one plan — and let the user see it. |
   | `C-ac-n` (raw input only) | Confirm each derived acceptance criterion | Raw text rarely has acceptance criteria. Ones you derive are proposals: the user confirms, changes, or drops each. Unconfirmed criteria are not planned. |

4. **Follow-up loop.** After each answered round, check whether an answer opened a new gap,
   contradicted an earlier decision, or made a listed item moot. New items get the next `G-n`
   and are asked; moot items are struck with a note. Gaps marked *note* are not asked — asking
   about everything is how an interview dies; they are reported, not decided.
5. **Exit.** Post the Clarification Log and move on without waiting.

## Phase 3 — Codebase Survey

Goal: a plan that leans on what exists instead of working against it. Follow
[`references/codebase-survey.md`](references/codebase-survey.md). The survey produces two plan
sections:

- **Global Constraints** — version floors, allowed dependencies, naming conventions, platform
  rules. Each one quoted verbatim with its source (spec section or `file:line`). They stand at the
  top of the plan because they apply to every task implicitly. A constraint in the spec that the
  code contradicts (spec says .NET 8, the project targets .NET 10) is a new blocking gap: back to
  Phase 2 for that one item.
- **Codebase Findings** — entry points and layering, the closest existing feature to use as a
  template, the test framework with its naming convention and directory layout, build and test
  commands, existing mock boundaries, and conventions the plan must honour. Every finding has a
  file reference; "the project uses a repository pattern" without a path is an opinion.

**Greenfield.** When there is no code, record `greenfield` and do not choose for the user: test
framework, test naming convention, and mock boundaries become Phase 2 questions, and Task #1 is
the scaffold. The skill never picks frameworks — it records the project's choice or asks.

**Depth.** As far as needed to name the files, patterns, and test conventions the plan will use,
with references. This is orientation for the plan, not a code review.

## Phase 4 — Decomposition

Follow [`references/task-design.md`](references/task-design.md). Work in this order, because each
step fixes decisions the next one depends on:

1. **File structure.** A table of every file the plan creates, changes, or deletes: path, status,
   one responsibility, and the tasks that touch it. Things that change together live together;
   the layout follows the Codebase Findings, not a general principle.
2. **Tasks.** A task is the smallest unit with its own test cycle that a reviewer could accept or
   reject on its own. Setup, configuration, and documentation belong to the first task whose
   result needs them; later tasks declare the dependency. Order tasks so every dependency comes
   first, number them in that order, and mark tasks that can run in parallel.
3. **Interfaces.** Per task, *Consumes* (from which task) and *Provides* (for which task) with
   exact names, signatures, and types. Contracts the spec already fixes in its Design / Data / API
   section are cited by `IF-n`, not re-invented.
4. **Verifies blocks.** Per task, per [`references/traceability.md`](references/traceability.md):
   each ID it proves, the test type from the fixed kind → test-type mapping, and the planned test
   name in the project's convention. Manual checks name the step and the owner. An ID that cannot
   be given a test is not given a vague one — it goes to Open Questions (Critical Rule 3 still
   holds: the matrix row says `open — G-n`, never blank).
5. **Todos.** Derived from the Verifies block: one checkbox per test, then implementation, then
   documentation. Each Todo is one checkbox; sub-bullets are allowed, sub-checkboxes are not.
6. **Traceability matrix.** ID → kind → task → test type → test name or manual step → automated /
   manual.

Run the [self-check](references/traceability.md#self-check) before drafting. A failure means the
decomposition is wrong; fix it, do not annotate it.

## Phase 5 — Draft

1. Create `docs/draft/` if needed. If `docs/draft/plan_<slug>.md` exists, ask whether to replace
   it, keep both with a suffix, or abort.
2. Write the draft from [`references/plan-template.md`](references/plan-template.md), in the
   language of the spec (or `L-1`), with the draft additions: the **status header** (`Status:
   DRAFT — awaiting review`, date, spec source with commit or date, plan set position) and the
   **Review Notes** section (what you are unsure about, cuts you considered and rejected, sections
   you could only fill thinly and why).
3. Every template section is present; a section with nothing to say reads `n/a — <reason>`.
4. Report the path and three lines (number of tasks, IDs covered, number of Spec Feedback items),
   then enter the gate.

## GATE — Plan Review (mandatory)

STOP here. End your reply with exactly this block, translated to the plan's language if it is
not English:

```
Draft written: docs/draft/plan_<slug>.md

Please review it. You can
  (a) edit the file directly — tell me when you are done,
  (b) raise points here in chat — we will go through them together, or
  (c) approve it as-is.

I will only produce docs/plans/<slug>.md after your explicit approval.
After approval, test names and interfaces in the plan are frozen; later changes go to its Change Log.
```

**Outcomes:**

| The user… | You… |
|---|---|
| raises points, questions, or objections in chat | treat each as a new item: a spec question → `G-n`, back to **Phase 2**; a decomposition point (task cut, interface, test name) → back to **Phase 4**. Update the draft, re-run the self-check, re-enter this gate. |
| says they edited the file | go to **Phase 6** only if they also approve; otherwise re-read the file, summarise the changes you see, and ask via the question tool whether the draft is now approved |
| approves explicitly | go to **Phase 6** |
| approves *and* raises points in the same message | the points come first; a draft with known open points is not approved |

**Explicit approval** is an unambiguous statement that the draft as it stands is accepted —
"approved", "genehmigt", "freigegeben", "go ahead with the plan". "Looks good so far", "continue",
"ok" as a reply to a question, or silence are not. When in doubt, ask with two options: "Approve
the plan as it stands" / "Not yet — I have more points".

## Phase 6 — Plan

1. Read `docs/draft/plan_<slug>.md` from disk and compare it with what you wrote. The file wins.
   An edit that contradicts a logged clarification gets a new `C-n` with `origin: draft edit`; an
   edit that breaks the self-check (an ID no longer verified, a test name removed) gets exactly one
   clarifying question, then the fix, then the gate again — a broken plan is not finalised.
2. Create `docs/plans/` if needed; if `docs/plans/<slug>.md` exists, ask before replacing it.
3. Write the plan: same sections as the draft, without the draft status header and without the
   Review Notes, with an empty **Change Log** that states the freeze date. Leave the draft in
   place — deleting it is the user's call.
4. Final reply: the plan path; five lines (what is built, number of tasks and the first one,
   IDs covered, open Spec Feedback items, manual checks); and one line on the next step — handing
   the plan to an implementation workflow skill, which works the Todos in their given order. Do
   not commit.

## Red Flags — Stop and Re-read the Rules

| Rationalization | Reality |
|---|---|
| "The spec is approved, it has no gaps" | Approved means the user stopped asking, not that every criterion is testable. Phase 1 will find something; if it truly finds nothing, say so and still ask `C-scope`. |
| "I'll fill the missing acceptance criteria myself" | That is spec work. Offer `create-dev-spec`; if declined, every derived criterion is confirmed by the user before it is planned. |
| "This NFR has no number, I'll leave the matrix cell empty" | An empty cell means "not verified". Write `manual` with a named step and owner, or make it an open question. |
| "I'll pick test names later, during implementation" | Names chosen after the code describe it; names chosen before it constrain it. The Verifies block is the plan's promise. |
| "The FR is covered by the acceptance test, no unit test needed" | Kind decides: a rule gets a unit test even when an acceptance test passes through it. Rule tables are where regressions hide. |
| "I know the codebase, I'll skip the survey" | The plan is read by someone who does not. File references are for them. |
| "There's no code yet, I'll choose the test framework" | The skill records choices, it does not make them. Ask. |
| "The user said 'fine', that's approval" | Only an explicit approval passes the gate. Ask the two-option question. |
| "Headless run, I'll assume sensible answers" | Complete spec → draft with unresolved items; anything else → `Blocked`. Never invented decisions. |
| "I'll update the spec while I'm at it" | The spec is read-only. Spec Feedback carries the backlog. |

## References

- [`references/spec-review.md`](references/spec-review.md) — Phase 1 checklist, gap categories,
  blocking vs. note, handling raw requirements
- [`references/codebase-survey.md`](references/codebase-survey.md) — Phase 3 search list, output
  format, greenfield rule
- [`references/task-design.md`](references/task-design.md) — scope cut, file structure, task
  sizing, dependencies, interfaces, plan sets
- [`references/traceability.md`](references/traceability.md) — classification, kind → test-type
  mapping, Verifies block, completeness rules, matrix, self-check, change log
- [`references/plan-template.md`](references/plan-template.md) — section structure for draft
  and plan
