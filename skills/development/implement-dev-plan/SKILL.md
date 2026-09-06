---
name: implement-dev-plan
description: >
  Use when the user wants an approved development plan (a create-dev-plan document in
  docs/plans/, usually with its create-dev-spec specification in docs/specs/) turned into working
  code: requests like "implement the plan", "implement docs/plans/<slug>.md", "work through the
  tasks", "setze den Plan um", "Feature nach Plan implementieren", or when a plan exists and the
  next step is code. Checks plan and spec for consistency, discovers the installed skills that fit
  the tech stack at runtime and lets the user pick them, maps them to tasks, implements task by
  task (directly or with one sub-agent per task), verifies every task against its Verifies block,
  runs an independent review of the uncommitted changes, loops on rework the user selects, and
  writes an implementation report to docs/implementation/. Never commits. Not for requests without
  a plan — a bare "implement feature X" goes to create-dev-spec / create-dev-plan first — and not
  for writing specs or plans.
---

# implement-dev-plan — From Approved Plan to Reviewed, Uncommitted Implementation

## Core Principle

The plan already made the decisions: which files, which tasks in which order, which interfaces,
and which test proves which requirement. Implementation is where those decisions meet reality, and
reality pushes back — a signature does not fit, a test name is wrong for the framework, a spec
criterion turns out ambiguous once the code exists. This workflow exists so that every push-back
is **seen, decided by the user, and recorded**, instead of being absorbed silently into code that
no longer matches its plan. Three habits make that possible: nothing is trusted that the main agent
did not run itself, nothing changes in the plan except checkboxes and Change Log rows, and nothing
is committed — the user reviews the diff and decides what enters history.

The output is uncommitted code plus three documents:

| Artifact | Path | Purpose |
|---|---|---|
| Plan updates | `docs/plans/<slug>.md` | Ticked Todos, task `Status`, and Change Log rows — nothing else |
| Review report | `docs/reviews/YYYY-MM-DD-<branch>-<mode>.md` | Written by the review sub-agent per the reviewer skill's convention |
| Implementation report | `docs/implementation/<slug>.md` | Decisions, skills, results, deviations, review outcome |

`<slug>` is the plan's slug (`docs/plans/<slug>.md`); a plan-set part keeps its full file name.

## Flow Overview

```
Phase 0  Intake            — locate plan and spec, plan-set state, working tree, headless check
Phase 1  Consistency       — plan vs. spec vs. code; blocking findings become questions
Phase 2  Skill Discovery   — runtime skill list → candidates → user keeps / drops / adds
Phase 3  Skill Mapping     — task → skills table; user confirms or changes
Phase 4  Mode              — direct or sub-agents; parallel or sequential
Phase 5  Implementation    — per task: (brief →) implement → VERIFY → tick → Change Log
Phase 6  Review            — one sub-agent: tech-stack review + plan conformance → docs/reviews/
Phase 7  Rework Decision   — top findings; user selects; selected → Phase 5 → Phase 6 again
Phase 8  Report            — docs/implementation/<slug>.md; hand the diff to the user
```

## Critical Rules (read before every phase)

1. **Every decision goes through the structured question tool.** Use your runtime's tool for
   structured user questions (in Claude Code: `AskUserQuestion`), never a prose question. Each
   question carries 2–4 concrete options, the recommended one first and marked "(Recommended)",
   each with its consequence in one sentence. Where the user picks a set (skills, findings), use
   the tool's multi-select. Up to four *independent* questions per call; questions whose options
   depend on an earlier answer go in a later call. Every answer is recorded as a decision `D-n` with its origin for the
   report.

2. **Plan and spec are read-only, with three exceptions in the plan.** You may tick Todo
   checkboxes, set a task's `Status`, and append rows to the Change Log. You never rewrite a task,
   rename a planned test, or "correct" the plan to match what the code ended up doing — that is
   exactly the drift the Change Log exists to make visible. A plan-level problem is a question to
   the user, whose options include fixing the documents with `create-dev-plan`.

3. **Skills are discovered at runtime and actually loaded.** The skills that fit are taken from
   the skill list your runtime exposes *now* — never from memory of another project, never from
   names quoted in the plan. A skill not in that list cannot be invoked; a skill in it is what the
   user installed. The mapped skills are **binding, not advisory**: every one of them is loaded
   before the first line of that task's code — by you in direct mode, by the sub-agent in sub-agent
   mode, and the sub-agent proves it in its report. Confidence in your own knowledge of the stack
   is not a reason to skip one; it is the reason the rule exists. The user chose these skills so
   that the code follows their team's rules, not the model's habits, and the two differ in exactly
   the places nobody checks. A task implemented without all of its mapped skills loaded is not
   verified — it is redone (Phase 5.3, check 0).

4. **Trust nothing you did not run.** A sub-agent's "all tests green" is a claim. After every task
   you run the build and the full test command yourself, check the planned test names against the
   files and the passing set, and compare the changed files with the task's `Files`. Only then is
   a Todo ticked. This is the one place the workflow pays with time, and it is what makes the final
   matrix honest.

5. **Deviations never change behaviour; every deviation is a Change Log row.** Departing from the
   plan is allowed for a good technical reason (a signature that cannot compile as written, a test
   name the framework rejects) and never for scope (dropping an acceptance criterion, adding a
   feature). A deviation that changes what a spec ID means is not a deviation — it is a plan
   change and goes to the user as a question.

6. **Tests first, in Todo order, the ID stays in the name.** The plan's Todos begin with the
   Verifies tests for a reason: a test written before the code constrains it. The plan proposed a
   name for every test; the implementer may adapt it to the framework's or the project's naming
   convention, but the requirement ID stays part of the name (`it('AC-3: …')`,
   `Export_AC3_…`) — it is how the review finds the test for each matrix row without reading the
   whole suite. Every rename is a Change Log row (old → new, reason), because the plan's matrix
   still shows the old name and the reader must be able to follow it.

7. **Git is read-only for you.** `status`, `diff`, `log` — yes. `add`, `commit`, `stash`, `reset`,
   `checkout` — never; the user does those. Sub-agents get the same rule in their brief.

8. **Urgency waives nothing.** "Just implement it" is not permission to skip the consistency
   check, the skill selection, verification, or the review. Run the workflow at speed — batch
   independent questions, keep status messages short — never at reduced rigour.

## Precondition — Interactive User Required

This workflow has no non-interactive mode. Phases 1–4 and 7 need a person deciding; without one,
every default would be your choice standing in for the user's, applied to their codebase.

**Judge the run, not your message channel:** the precondition is unmet only when the whole run has
no user behind it — you were dispatched by a script, CI, cron, or another agent whose output is
consumed by a program.

**When it is unmet:** STOP immediately, before reading beyond what is needed to name the plan.
Reply `Blocked — interactive user required`, the plan path you were pointed at, and one line that
an interactive user can start this skill on that plan. Create no files, change no code.

## Phase 0 — Intake

1. **Locate the plan.** The user names a path, a slug, or just "the plan". Resolve to
   `docs/plans/<slug>.md`. Several plans and none named → ask which one (question tool, one option
   per plan, most recently modified first). Only a draft exists (`docs/draft/plan_*.md`) → STOP:
   a draft is not approved, its test names and interfaces are not frozen, and implementing it
   would leave nothing stable to verify against; point the user to the `create-dev-plan` gate. No
   plan at all → STOP and point to `create-dev-plan` (and `create-dev-spec` if there is no spec
   either). Never implement from a description of a plan.
2. **Locate the spec** from the plan header (`Spec: docs/specs/<slug>.md @ <commit>`). If the
   header points at a requirement source instead of a spec, the plan was made from raw input and
   carries its own confirmed acceptance criteria. Ask: **(a) Recommended — continue plan-only**,
   the Clarification Log and Spec Feedback are the spec surrogate and Phase 1 runs plan-internal;
   **(b) stop** and run `create-dev-spec` first. Record the answer as `D-1`.
3. **Plan set.** If the plan's *Plan Set* table names parts this part depends on, check those
   parts' files: every Todo ticked and every task `Status: done`? If not, ask whether to continue
   anyway (their *Provides* may not exist yet) or stop.
4. **Working tree.** Run `git status --porcelain`. Not empty → show the files and ask: **(a)
   Recommended — commit first**, then tell me and I re-check; **(b) continue** — these changes
   stay in the working tree and are therefore part of the review in Phase 6 and of the report,
   exactly like the code written in this run. There is no separate bookkeeping for them: a file
   that was dirty before and is edited again during a task cannot be told apart reliably, so the
   review sees everything uncommitted. Record as `D-2`, with the file list. Also record the branch
   name for the review report path. Ask this **now, on its own, before Phase 1** — not batched
   with consistency findings: the dirty files may be the plan or the spec themselves, and a
   consistency check run against a half-edited document reports drift that a commit would have
   resolved or hidden. Only after the answer (and, on (a), the re-check) do you read the documents.
5. **Headless check** — see the precondition above.
6. Read the plan and the spec end to end before judging anything. Note the plan's language: the
   report and all status messages to the user follow it.

## Phase 1 — Consistency Check

Goal: find where plan, spec, and code disagree *before* code makes the disagreement expensive.
Follow [`references/consistency-check.md`](references/consistency-check.md). The checks, in short:

- **Coverage** — every spec ID appears in the traceability matrix; every plan ID exists in the
  spec or is listed in Spec Feedback as assigned by the plan.
- **Freshness** — the spec commit in the plan header versus the spec's current commit; if they
  differ, diff the spec between them and see whether any ID the matrix verifies changed.
- **Constraints** — every Global Constraint with a `file:line` source still holds in the current
  code (version floors, dependencies, conventions).
- **Contracts** — each task's *Consumes* / *Provides* against the spec's `IF-n` contracts and
  against the previous task's *Provides*.
- **Plan self-check** — Verifies blocks mirror the first Todos, no blank matrix cell, a Change Log
  section exists. A plan that fails its own rules should not be implemented as-is.
- **Progress** — Todos already ticked mean a partial implementation exists; the user decides
  whether to resume from the first unticked task or start over.

Spec Feedback items are *expected* differences the plan already reported; list them as context, not
as findings. Every real finding is `K-n` with the IDs concerned and a severity: **blocking** (a task
cannot be implemented or verified as planned) or **note** (recorded in the report, work proceeds).

Post the findings as one numbered list. Then, per blocking finding, in order of cost if wrong, one
question with these options unless the finding suggests better ones: **abort**; **fix the
documents** — the user updates spec or plan (with `create-dev-plan` for the plan), tells you, and
you re-run Phase 0–1; **ignore** — recorded as `D-n`, origin `user's own`, and repeated in the
report so a later reader knows it was a choice. Up to four independent findings per call. No
blocking findings → say so in one line and continue. **Notes are never asked**, not even a small
one tacked onto a blocking question — a note is a finding whose answer changes no task, and every
extra question spends the user's attention that the blocking ones need; if you find yourself wanting
the user's opinion on a note, re-check whether it is actually blocking (a planned test depends on
the answer) and reclassify it if so.

## Phase 2 — Skill Discovery

Goal: the set of installed skills that will actually shape the code. Follow
[`references/skill-selection.md`](references/skill-selection.md).

1. **Take the runtime's skill list** — in Claude Code, the available-skills listing in your
   context. Do not scan directories the runtime did not load; do not assume a skill exists because
   the plan or a README mentions it.
2. **Derive the match criteria from the plan**, not from the request: language, framework, test
   framework, build tooling, and conventions from *Codebase Findings* and *Global Constraints*;
   file types from *File Structure*; the concerns of each task from its *Goal* (API, data access,
   UI, documentation, packaging).
3. **Classify every candidate** by reading its description: *knowledge* (rules and patterns for a
   framework or layer), *tester* (writing tests), *documentation* (doc comments), *reviewer*
   (explicit-invocation code review), *workflow* (multi-phase pipelines with their own gates),
   *tooling* (package or dependency management, inspection), *unrelated*. Reviewer skills are not
   used during implementation; they are the review set for Phase 6. Workflow skills carry a
   warning in the proposal: loading one inside a task runs a workflow inside this workflow, with
   its own gates and its own review — usually not wanted, but the user decides.
4. **Propose**, as a table: skill, category, why it fits (which finding, constraint, or task), and
   the proposed use — *implementation*, *review*, or *excluded — reason*.
5. **Let the user shape the set** with the question tool, multi-select: one question per group of
   up to four proposed skills, grouped by category, each option the skill name plus one line of
   why; what the user leaves unselected is dropped. Then one question whether they want to add
   skills the proposal missed; a name that is not in the runtime list is reported as not loadable
   and not added. Record the final set as `D-n` with what was dropped and added.

An empty result is possible (an unfamiliar stack, no matching skills installed). Say so, ask
whether to proceed with the plan's *Codebase Findings* as the only guidance, and record it.

## Phase 3 — Skill Mapping

Goal: every task knows which skills its implementer loads. Rules from
[`references/skill-selection.md#mapping`](references/skill-selection.md#mapping): the stack's
baseline knowledge skill(s) go to every task that touches production code; a tester skill to every
task with a Verifies block; a documentation skill to tasks with a documentation Todo on public API;
layer- or framework-specific skills to the tasks whose *Files* and *Goal* touch that layer; tooling
skills only to tasks whose Todos add or change dependencies.

Present the mapping as a table — `Task # · Title · Skills · Why` — with one row `All tasks` for the
baseline. Then ask: **(a) Recommended — adopt as proposed**; **(b) change** — the user describes
the change (free text), you apply it, re-present the table, and ask again. Record as `D-n`.

## Phase 4 — Mode

Two questions, the second only when it applies:

1. **Direct or sub-agents?** Recommend *sub-agents* when the plan has three or more tasks or the
   tasks touch distinct areas: each task gets a fresh context that holds only its brief, and you
   stay the verifier who never wrote the code. Recommend *direct* for one or two tightly coupled
   tasks, where the hand-over cost exceeds the benefit. State the recommendation's reason in the
   option text; the user decides. Record as `D-n`.
2. **Parallel?** Only if sub-agents were chosen *and* the plan marks tasks `Parallel with`. Options:
   **(a) Recommended — sequential**, one task at a time in plan order, every verification
   unambiguous; **(b) parallel for marked tasks whose `Files` sets are disjoint**, verified
   individually as each completes, with one full test run after the group. Tasks that share a file
   are never parallel, whatever the plan says — two agents editing one file is the fastest way to
   lose work. Record as `D-n`.

## Phase 5 — Implementation

Work the tasks in plan order (dependency order is numbering order). A task whose Todos are all
ticked is skipped with one line. For every task, the loop is the same; only the *implement* step
differs by mode.

**5.1 Prepare the task context.** Collect what the implementer needs: the task block verbatim; the
*actual* signatures of everything it *Consumes*, taken from the code as the previous tasks left it
(not from the plan — the plan may already have a Change Log row on them); the spec text of every ID
in its Verifies block; the Global Constraints; the Codebase Findings relevant to its files (test
layout, naming convention, build and test commands); the mapped skills.

**5.2 Implement.**

- *Direct mode:* load **every** mapped skill with the runtime's skill tool now — all of them,
  before any code, regardless of how well you think you know the stack; note which you loaded for
  the progress message and the report. Then follow the Todos in order — tests first, carrying
  their IDs, failing; implementation; documentation.
  Do not tick anything yet.
- *Sub-agent mode:* write the brief from
  [`references/subagent-brief.md`](references/subagent-brief.md) — it carries the task context,
  the mandatory skill loads, the rules (tests first, no functional deviation, git read-only, report
  format), and the report template. Spawn one sub-agent per task (or per parallel group, one
  each). Tell the user in one line which task is running. When the notification arrives, read the
  report; do not read it as a result — read it as a set of claims to check.

**5.3 Verify** — you, in both modes, per
[`references/verification.md`](references/verification.md): run the build and the full test
command; confirm every Verifies test name exists in its planned file and is in the passing set;
compare `git status` against the task's `Files`; read each test
against the spec text of the ID it verifies — does it assert that criterion, or something weaker; extract the
*Provides* as actually implemented for the next task's context.

**5.4 Judge deviations.** Every difference between plan and result — reported by the sub-agent or
found by you — is one of two things. A *technical* deviation (name, signature shape, file split,
helper added) keeps every spec ID's behaviour: it becomes a Change Log row
`| date | #n | change | reason | implement-dev-plan |`. A *functional* deviation changes what an ID
means, drops a criterion, or adds behaviour the spec does not have: it is not accepted; ask the
user — **revert and redo the task as planned**, **fix the documents** and re-enter Phase 0, or
**accept as a plan change** recorded with origin `user's own`. A consistency problem between the
result and the spec that no one caused (the criterion was ambiguous and the test picked one
reading) takes the same question.

**5.5 Update the plan.** Tick the Todos you verified, set `Status: done` (or `Status: partial —
<what is open>`), append the Change Log rows. Nothing else changes in the plan.

**5.6 Report progress** in one short block: task number and title, tests green out of planned,
files changed, deviations recorded, anything open.

**Failure handling.** A sub-agent that reports *blocked*, or whose result fails verification, gets
**one** retry with a sharpened brief that quotes the failure (test output, the mismatch you found).
A second failure stops the task and goes to the user: **take the task over directly**, **skip it
and mark `Status: blocked — <reason>`** and continue with tasks that do not depend on it, or
**abort**. Never a third blind retry — by then the problem is in the plan or the brief, not in the
attempt.

**Parallel groups** (if chosen): spawn the group's sub-agents in one turn; verify each on
completion as above; after the last one, run the full suite once more — tasks that pass alone can
fail together.

## Phase 6 — Review

Always a sub-agent, in both modes: the value of a review is that the reviewer did not write the
code. Build the brief from [`references/review-and-rework.md`](references/review-and-rework.md).
It has two parts, and the second is what a generic review would miss:

- **A — Tech-stack review.** Load the review set from Phase 2 (reviewer, refactoring, tester skills
  for this stack — reviewer skills need explicit invocation by name, so the brief names them) and
  run the reviewer skill's own process on the whole uncommitted working tree — including
  anything that was already uncommitted when the run started (`D-2`). Its report
  goes where that skill puts it (`docs/reviews/YYYY-MM-DD-<branch>-<mode>.md`); the brief passes
  the branch and the mode.
- **B — Plan conformance.** For every row of the traceability matrix: the test exists under the
  planned name, passes, and asserts the ID's criterion. For every task: *Done when* is met; the
  files touched are within *File Structure*; documentation Todos produced documentation. For the
  Change Log: every renamed test, changed signature, or extra file has a row — an unlogged
  difference is a finding. Findings tagged with the severity taxonomy of the reviewer skill used,
  or *Critical / Major / Minor / Info* when there is none.

Before spawning it, write a **run note** outside the repository (your scratch directory): the
Change Log rows added this run, the `D-n` decisions that affect code, and every task's *Provides* as
implemented. The brief points at it, so the reviewer can tell an accepted deviation from silent
drift. The review sub-agent changes no code and no documents except its report. When it returns,
confirm the report file exists and read it in full.

## Phase 7 — Rework Decision

1. Summarise the review to the user: counts per severity, the report path, and the **most
   important findings** — all Critical and Major, at most about seven lines — each as *file ·
   finding · proposed fix*. Do not list Minor and Info here; they are in the report.
2. Ask with multi-select which findings to fix now, the Critical and Major ones recommended; one
   question per group of up to four, plus an explicit option **accept the changes as they are —
   go to the report**. Findings the user leaves out are *deferred* and appear in the report's
   open items with the user's decision, not silently dropped. Record as `D-n`.
3. Selected findings become rework items `R-n` — finding, file, fix, tests affected — and go
   through **Phase 5** in the mode chosen in Phase 4 (one run for all rework items that touch the
   same area; independent areas may be separate runs), including verification and Change Log
   rows. Then **Phase 6** again, scoped to the delta since the last review plus a re-check that
   each `R-n` is resolved. Then this phase again.
4. Each round is numbered and recorded (findings presented, selected, deferred). There is no
   fixed limit; the user ends the loop by accepting. If a round produces the same finding twice,
   say so before asking — repeating a fix that did not hold is a sign the plan or the finding is
   wrong.

## Phase 8 — Report

1. Create `docs/implementation/` if needed. If `docs/implementation/<slug>.md` exists, ask before
   replacing it (keep both with a date suffix is an option).
2. Write the report from [`references/report-template.md`](references/report-template.md), in
   the plan's language: what was built, preconditions (working tree at start, `D-2`), consistency
   findings and how
   they were decided, skills found / kept / dropped / added and the per-task mapping as actually
   loaded, per-task results with test evidence, the Change Log rows added, review rounds with
   report paths and selected versus deferred findings, the full Decisions Log `D-1…n` with
   origins, open items, and the final build and test command with its result.
3. Final reply: the report path; five lines (tasks done of planned, tests green of planned,
   review rounds and open findings, Change Log rows added, files changed); and the hand-over —
   the changes are uncommitted, review them with `git diff` and commit what you accept. Do not
   commit.

## Red Flags — Stop and Re-read the Rules

| Rationalization | Reality |
|---|---|
| "The plan is approved, it is consistent" | Approved on the day it was frozen. The spec may have moved, the code may have moved. Phase 1 takes minutes; a wrong assumption takes a task. |
| "I know which skills fit this stack" | You know which skills *exist somewhere*. Only the runtime list says what is installed here. Critical Rule 3. |
| "I know this framework well enough, the skill would only slow me down" | The user picked the skill so the code follows *their* rules. A task done without its mapped skills is redone, green tests or not. Critical Rule 3. |
| "The sub-agent said all tests pass" | It said so. Run them. Critical Rule 4. |
| "I'll rename the test in the plan, the new name is better" | The plan is read-only except ticks, Status, and Change Log. The rename is a Change Log row. |
| "This criterion is unclear, I'll pick the sensible reading" | A reading is a decision about the spec, and the user owns the spec. Ask. |
| "The extra endpoint is tiny and obviously useful" | Behaviour the spec does not define is a functional deviation. Not yours to add. |
| "The review will catch it, no need to verify each task" | The review reads the whole diff at the end; per-task verification is what keeps task #5's brief truthful about task #4. |
| "I'll ask the working-tree question together with the consistency findings, saves a round trip" | The dirty files may be the plan or the spec. Phase 0 step 4 comes first and alone. |
| "This note is interesting, I'll just add it to the question" | Notes change no task. If it needs an answer, it was blocking — reclassify; otherwise report it and move on. |
| "Only two Minor findings, I'll skip the rework question" | The user decides what is accepted, including Minor ones. Present, then ask. |
| "I'll stage the files so the user just has to commit" | Git is read-only for you. Critical Rule 7. |
| "Headless run, sensible defaults" | There is no non-interactive mode. `Blocked — interactive user required`. |

## References

- [`references/consistency-check.md`](references/consistency-check.md) — Phase 1 checks,
  blocking vs. note, how to present and ask
- [`references/skill-selection.md`](references/skill-selection.md) — runtime discovery,
  classification, proposal table, multi-select flow, mapping rules
- [`references/subagent-brief.md`](references/subagent-brief.md) — brief template and mandatory
  report format for task sub-agents
- [`references/verification.md`](references/verification.md) — the main agent's per-task checks,
  deviation judgement, plan updates, failure handling
- [`references/review-and-rework.md`](references/review-and-rework.md) — review sub-agent brief
  (tech-stack + plan conformance), finding presentation, rework items
- [`references/report-template.md`](references/report-template.md) — section structure of
  `docs/implementation/<slug>.md`
