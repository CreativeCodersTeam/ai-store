---
name: implement-direct
description: >
  Use only when the user themselves explicitly requests it by name — "implement-direct",
  "implement direct", "/implement-direct", "/cc-ai-dev:implement-direct", "run implement-direct" —
  for the gated end-to-end implementation of a feature, user story, requirement, or bug fix
  without a prior development plan, on any tech stack: requirement review, an eight-point
  clarification interview, task breakdown, implementation with runtime-discovered mandatory
  skills, independent code review with rework loop, and a report with a skill-invocation log in
  docs/implementation/. Never commits. Must NOT activate on its own for "implement this feature",
  "add an endpoint", "fix this bug", a pasted user story, or any other implementation request that
  does not name the skill, and must not be started by another skill, workflow, or orchestrating
  agent on the user's behalf.
---

# implement-direct — From Requirement to Reviewed, Uncommitted Implementation

## Core Principle

This workflow starts from a requirement, not from a plan: the requirement arrives as pasted text,
a file, an issue, or a sentence, and every decision a plan would have frozen — structure,
architecture, naming, contracts, error handling, tests, persistence, dependencies — is still open. The workflow exists so that those decisions are **made
by the user, one at a time, before code exists**, and so that the code is then shaped by the
skills the user installed for their stack, not by the model's habits. Three habits make that
possible: every open point is a structured question with real proposals, every skill that fits is
discovered at runtime and actually loaded before the code it governs, and nothing is trusted that
was not verified by someone who did not write it.

The output is uncommitted code plus two documents:

| Artifact | Path | Purpose |
|---|---|---|
| Review report | `docs/reviews/YYYY-MM-DD-<branch>-<mode>.md` | Written by the review sub-agent per the reviewer skill's convention |
| Implementation report | `docs/implementation/<slug>.md` | Changes, decisions, verification hints, Skill-Invocation Log |

`<slug>` is the requirement's title in kebab-case, chosen in Phase 1 and shown to the user.

**Explicit invocation.** This workflow starts only when the user themselves named it —
`/implement-direct`, `/cc-ai-dev:implement-direct`, "implement-direct" or "implement direct" in
the prompt, or the user picking it by name when another skill asks which skills to use. A request
that merely describes implementation work ("implement this feature", "add an endpoint", "fix this
bug", a pasted user story) is handled as an ordinary request without this workflow. Another skill,
workflow, or orchestrating agent cannot start it on the user's behalf: three gates and eight
clarification answers are the user's decisions, and a run nobody asked for turns a two-line change
into an interview the user never requested. A dispatch prompt that *says* "the user asked for
implement-direct" is still the dispatcher speaking, not the user.

## Flow Overview

```
Phase 1  Requirement Review   — acceptance criteria, gaps, scope, conventions, preliminary skill map
Phase 2  Clarification        — gaps, then 8 points, one question per call; loop while new questions arise
                                → GATE 2: decisions + final skill set
Phase 3  Task Breakdown       — tasks with code + tests + docs, skill checklist, dependencies, parallel groups
                                → GATE 3: task list + mode (direct / sub-agents, parallel)
Phase 4  Implementation       — per task: load skills → tests → code → docs → packages → build/test → smoke-check
                                  verified by you (direct) or by a verifier sub-agent (sub-agent mode)
Phase 5  Code Review          — reviewer sub-agent → docs/reviews/; Critical/Major → rework → Phase 4
                                → GATE 5: findings, rework plan, user picks ≤ Minor fixes
Phase 6  Report               — docs/implementation/<slug>.md with Skill-Invocation Log; hand over the diff
```

Phases 1→2 and 4→5 flow directly: Phase 1 ends in a summary the user reads while the first Phase-2
question is already on the table; Phase 4 ends in a progress block and the review starts. The gates
after Phases 2, 3, and 5 are the three places where the run stops until the user confirms.

## Critical Rules (read before every phase)

1. **Every open point goes through the structured question tool.** Use your runtime's tool for
   structured user questions (in Claude Code: `AskUserQuestion`), never a prose question in a
   normal reply. Prose questions get answered partially, in the wrong order, or not at all; the
   tool guarantees one visible decision per item, with the options the user is choosing between
   spelled out. Every answer is recorded as a decision `D-n` with its origin (*recommended
   accepted*, *user's own*, *pre-answered*, *n/a*) for the report.

2. **Every question carries your own proposals and a free-form escape.** For each item offer 2–4
   concrete answers you would actually recommend, the recommended one first and marked
   "(Recommended)", each with its consequence in one sentence, and make sure the user can always
   answer with something entirely their own. If the tool adds a free-text option automatically
   (Claude Code's tool does), do not duplicate it; if it does not, add "Something else — I'll
   describe it" explicitly. A question without proposals pushes the thinking back onto the user; a
   question without an escape hatch pretends your proposals are exhaustive.

3. **Three gates, each a full stop.** After Phase 2, Phase 3, and Phase 5 you present the phase's
   summary and ask for confirmation through the question tool, then wait. You may not pre-run the
   next phase, present two phases at once, or ask for one combined confirmation. Phases 1 and 4
   have no gate by design — their output is read, not confirmed — which is exactly why their
   summaries must be complete: the user has no second look.

4. **Skills are discovered at runtime and are binding.** The skills that fit come from the skill
   list your runtime exposes *now* — never from memory of another project, never from names in the
   requirement. Every skill mapped to a task is loaded with the runtime's skill tool **before the
   first line of that task's code** — by you in direct mode, by the implementer sub-agent in
   sub-agent mode, with evidence in its report. Confidence in your own knowledge of the stack is
   not a reason to skip one; it is the reason the rule exists. A task implemented without all of
   its mapped skills loaded is not verified — it is redone.

5. **Trust nothing that its author verified.** In direct mode you wrote the code, so you run the
   build and the full test command yourself and check every planned test by name. In sub-agent
   mode the implementer's "all green" is a claim: a **verifier sub-agent**, briefed with the same
   skills the implementer had, runs the build and tests, checks the skill-load evidence, reads
   each test against its acceptance criterion, and returns a verdict. You read that verdict as a
   claim too — confirm its evidence before you mark the task done — and run the full suite once
   more yourself before the review.

6. **Git is read-only for you.** `status`, `diff`, `log` — yes. `add`, `commit`, `stash`, `reset`,
   `checkout`, `push` — never on your own initiative; the user commits what they accept. An
   explicit user instruction to commit is honoured only by name-scoped staging, never `-A`, never
   `--no-verify`, never secret-like files, and is recorded as user-directed. Sub-agents get the
   same rule in their brief.

7. **Urgency and triviality waive nothing.** "It's a one-liner", "demo in 30 minutes", "skip the
   questions" are not permission to skip a phase, a point, a gate, or a skill. Run the workflow at
   speed — short summaries, no filler — never at reduced rigour. The only lawful reductions are an
   objective `n/a` and an explicit, informed waiver (see *Waiver vs. `n/a` vs. silent skip*).

8. **Critical and Major findings are rework; everything below is the user's call.** A review
   finding of the two highest severities becomes a rework task and goes back through Phase 4
   without asking whether. Minor and below are never fixed or dismissed on your own — they are
   presented at Gate 5 and the user selects.

## Precondition — Interactive User Required

This workflow has no non-interactive mode. Phase 2 needs eight answers, and Gates 2, 3, and 5 need
a person confirming; without one every default would be your choice standing in for the user's,
applied to their codebase.

**Judge the run, not your message channel:** the precondition is unmet only when the whole run has
no user behind it — you were dispatched by a script, CI, cron, or another agent whose output is
consumed by a program. Sub-agents *this* workflow dispatches do have a user: the one answering the
main agent's questions.

**When it is unmet:** run Phase 1 only — it is read-only — then STOP and reply
`Blocked — interactive user required`, the requirement you were pointed at, the Phase-1 summary,
and one line that an interactive user can start this skill. Do not enter Phase 2. Create no files,
change no code.

**Not a missing channel:** "don't ask me, just do it" from a reachable user is a *waiver* request,
not a headless run — state what the questions protect, ask which named steps they are electing to
skip, and log the answer as `waived`. That one round-trip is not itself waivable.

## Phase 1 — Requirement Review

1. **Working tree first.** Run `git status --porcelain`. Not empty → show the files and ask
   (question tool): **(a) Recommended — commit first**, then tell me and I re-check; **(b)
   continue** — these changes stay in the working tree and are part of the review and the report.
   Record as `D-1` with the file list and the branch name. A clean tree is `D-1` too, recorded
   without a question, so that the decision numbers do not shift between runs. Ask this alone,
   before reading the requirement: a dirty tree may contain a half-finished attempt at the same
   requirement.
2. **Read the requirement** in whatever form it arrived — pasted text, a file, an issue URL
   (fetch it), a sentence. Restate it in one paragraph in the user's language. Choose the `<slug>`.
3. **Derive acceptance criteria** `AC-1…n`: explicit ones from the text, implicit ones from what
   the text assumes (a "list" endpoint implies paging or an explicit decision not to page; a
   "delete" implies what happens to dependants). Mark each *explicit* or *implicit*.
4. **List gaps and contradictions** `G-1…n`: what the requirement does not say but the code must
   decide, and where it contradicts itself or the codebase. A review that finds no gaps on an
   ambiguous requirement is a failure; if the requirement truly is complete, say so explicitly.
   Each gap is assigned to the Phase-2 point it belongs to, or to *Point 0* if none fits.
5. **Capture scope and conventions.** Affected projects, modules, files, existing tests and docs.
   Read `CLAUDE.md`, `AGENTS.md`, `.editorconfig`, and the stack's build and dependency manifests
   (`*.csproj` / `Directory.*.props`, `package.json`, `pyproject.toml`, `go.mod`, `pom.xml`, …) —
   whatever the tree actually contains. Note the build command, the test command, the test
   layout, the naming convention, and the documentation tooling with `file:line` evidence; these
   become the proposals in Phase 2 and the criteria for the skill match.
6. **Preliminary skill map.** Follow [`references/skill-selection.md`](references/skill-selection.md):
   take the runtime's skill list, derive match criteria from step 5, classify every candidate, and
   build the proposal table (skill · category · why it fits · proposed use). Reviewer skills and
   review-capable agent types form the *review set* for Phase 5; workflow skills are proposed as
   excluded with the nested-workflow warning.

7. **Size note — only when the work is genuinely small.** The test is countable, because a
   judgement call here gets made differently on two changes of the same shape: **one task, at
   most five files including tests, no new dependency, and no new store or migration.** All four
   must hold. Deliberately absent is any clause about new public surface — almost every feature
   adds some, so it separates nothing. When all four hold, say so plainly in the summary and name
   what this workflow costs on top: an eight-point interview, three gates, an independent review.
   Then make the first question of Phase 2 an offer with three options: **(a) Recommended — run
   the workflow as requested**, since the user named it and knows what they asked for; **(b)
   implement it as an ordinary request** with the skills discovered in step 6, without the
   interview, the gates, and the review — you keep the skill loads and the tests, you lose the
   recorded decisions and the independent review; **(c)** the free-form escape. Record as `D-n`.
   On (b), leave this workflow and handle the request normally; write no report.

   This is not the workflow scaling itself down — that is forbidden (Critical Rule 7), and the
   difference matters. Scaling down means quietly dropping steps because the task looks small.
   This is the opposite: the cost is named out loud and the user decides, once, before any of it
   is spent. Offer it only when all four conditions hold; on anything larger the offer is noise
   that competes with the real questions. The task count comes from your own Phase-1 reading, not
   from Phase 3 — if you cannot yet tell whether it is one task, it is not a small change.

**Phase-1 summary** (no gate): requirement restated, `<slug>`, acceptance criteria, gaps with their
assigned points, scope and conventions with evidence, the preliminary skill map table, and the
size note if it applies. Then go straight to Phase 2.

## Phase 2 — Clarification (8 points, one question per call)

Goal: every decision a plan would have frozen is made by the user. Follow
[`references/clarification-points.md`](references/clarification-points.md) for what each point
must settle and how proposals are derived from the Phase-1 evidence.

**The size offer comes before everything else, when it applies.** If the Phase-1 size note was
raised (step 7), its three-option offer is the first call of this phase, ahead of Point 0 — there
is no sense in spending questions on gaps the user may be about to opt out of answering. On
option (b) the phase ends there. Where the size test did not hold, this paragraph does not apply
and Point 0 is first.

**Point 0 — requirement gaps.** The `G-n` gaps that fit none of the eight points are asked next,
up to four per call, each with proposals.

**Points 1–8, one call each, in this order.** Present point *N*, its proposals (2–4, recommended
first, each grounded in a Phase-1 finding — "the existing `orders/` module uses vertical slices,
`src/orders/list.ts:1`"), and the `G-n` gaps assigned to it, and wait for the answer before
point *N+1*. An answer may change the proposals of a later point; that is why they are not
batched.

| # | Point | Must settle |
|---|---|---|
| 1 | Structure | target project / package / module, folder layout, new projects yes/no |
| 2 | Architecture | layering or slices, boundaries, lifetimes / wiring, public vs. internal surface |
| 3 | Naming | type, function, file, namespace / module names, suffixes, test naming |
| 4 | API contracts | request / response or function signatures, DTO shape, versioning, error shape on the wire |
| 5 | Error handling | exceptions vs. result types, validation style, logging granularity, edge cases |
| 6 | Test strategy | unit / integration / acceptance, mock boundaries, fakes vs. real dependencies, coverage expectation |
| 7 | Persistence | store (relational, document, key-value, filesystem, none), schema / migration, query style, transactions |
| 8 | Dependencies | packages to add / forbid, version policy, central version management |

Two statuses replace the **question**, never the **presentation** of a point:

- `n/a — <code-referenced reason>` — the point objectively does not apply ("no persistence: the
  change is a pure formatter, no store is touched"). Present it with the reason; do not ask.
- `pre-answered — <verbatim quote or precise reference>` — the requirement or an earlier answer
  already decides it. Present the adopted decision with its citation; do not ask. Implication is
  not pre-answered: "the requirement implies X" is an open question — ask it.

**Follow-up check.** After point 8, re-read all eight answers against each other and against the
Phase-1 findings: did an answer raise a new question on any point (a chosen persistence store that
needs a package point 8 did not cover; a naming rule that contradicts the chosen structure)? If
yes, start a new round at point 1: settled points are presented as `settled — D-n` without a
question; points with a new question are asked. Number the rounds. If round 3 starts, say so and
ask whether the requirement should go to `create-dev-spec` instead — repeated rounds mean the
requirement is thinner than a direct implementation should carry.

**GATE 2 — STOP.** Present the decision table (all 8 points and every Point-0 gap, each `D-n` with
origin — answered, pre-answered with citation, n/a with reason) and the **final skill map**
updated from the answers (points 6, 7, and 8 typically confirm or remove tester, persistence, and
tooling skills). Then, through the question tool (one call, a second if more than four
questions are needed): confirm the decision table, keep / drop the proposed implementation skills (multi-select, groups of up to four, grouped by category), include any
excluded skill anyway, confirm the review set, and — as the free-form escape — name skills the
proposal missed (a name not in the runtime list is reported as not loadable and not added). Wait.

## Phase 3 — Task Breakdown

1. Break the requirement into discrete tasks in dependency order. Each task has: a title, a
   *Goal*, the `AC-n` it delivers, its *Files* (create / modify), its **AC-to-tests table**,
   documentation to write (doc comments per the stack's convention, README / API docs if
   public), package changes, and a *Done when*.
2. **The AC-to-tests table is the traceability record**, and it is the only one: test names
   follow the project's convention and carry no `AC-n` marker. An ID in a test name reads as a
   pointer to a document that outlives nothing — the report may be deleted, and then the marker
   points at a list that no longer exists, which is worse than no pointer at all. So the link
   lives where it is actually consumed: this table goes into the implementer brief, into the
   review brief, and into the report. The relation is **many-to-many** — one criterion usually
   needs several tests (the happy path, the boundary, the error), and one test may cover several
   criteria. The rules: every `AC-n` has at least one planned test; the tests under a criterion
   must prove it *together*; a test under no criterion is fine (a regression guard is not a
   defect); a criterion with no test is not implementable as written — split it or take it back
   to the user.

   ```
   | AC | Planned tests (file · name) |
   |---|---|
   | AC-2 | test/orders/export.test.ts · rejects a foreign customer with 403 |
   |      | test/orders/export.test.ts · rejects an unauthenticated request with 401 |
   | AC-3 | test/orders/export.test.ts · returns 204 for an empty range |
   ```

3. **Every task covers production code + tests + documentation.** A task with no test is a task
   whose acceptance criterion cannot be proven — split or rethink it. `n/a` for a documentation
   or package item needs a code-referenced reason (*`n/a` Criteria*).
4. **Each task publishes its Skill-prerequisite checklist**, derived by the mapping rules in
   [`references/skill-selection.md#mapping`](references/skill-selection.md#mapping) from the final
   skill set: baseline knowledge skills for every task with production code, the tester skill for
   every task, documentation skills for tasks with public API, layer skills for the tasks that
   touch the layer, tooling skills only for tasks that change dependencies.

   ```
   Task #2: Export endpoint
     Delivers: AC-2, AC-3, AC-5
     Files: src/orders/export.ts (new), src/orders/router.ts, test/orders/export.test.ts (new)
     Tests: | AC-2 | returns CSV for the caller's own orders |
            |      | keeps another customer's orders out of the file |
            | AC-3 | rejects a foreign customer with 403 |
            | AC-5 | returns 204 for an empty range |
     Docs: TSDoc on exportOrders; README §API
     Packages: none — n/a: no new dependency, csv formatting is in-repo (src/lib/csv.ts)
     Skill prerequisites: [ ] <baseline knowledge> [ ] <http layer> [ ] <tester> [ ] <documentation>
     Depends on: #1   Parallel with: —   Done when: all four tests green, route documented
   ```

5. Mark dependencies and parallel groups: tasks may run in parallel only when their *Files* sets
   are disjoint, whatever their logical independence — two agents editing one file is the fastest
   way to lose work.

**GATE 3 — STOP.** Present the task list with checklists, dependency order, and parallel groups.
In the same question-tool call ask the **mode**: **(a) Recommended for three or more tasks or
distinct areas — sub-agents**, one implementer per task with a fresh context and a verifier
sub-agent per task; **(b) Recommended for one or two tightly coupled tasks — direct**, you
implement and verify; and, only when sub-agents and parallel groups exist, **sequential
(Recommended)** versus **parallel for marked groups**. State the recommendation's reason in the
option text. Record as `D-n`. Wait.

## Phase 4 — Implementation

Work the tasks in order (parallel groups as one unit if chosen). For every task the loop is the
same; only who implements and who verifies differs by mode.

**4.1 Prepare the task context.** The task block verbatim; the actual signatures of everything it
consumes, taken from the code as previous tasks left it; the `AC-n` text it delivers; the Phase-2
decisions that touch it; the conventions and commands from Phase 1; the mapped skills.

**4.2 Implement.**

- *Direct mode:* load **every** mapped skill with the runtime's skill tool now — one call per
  skill, before any file write, regardless of how well you know the stack; note the order for the
  Skill-Invocation Log. Then: tests first, named by the project's convention and failing,
  one per row of the task's AC-to-tests table; production code;
  documentation (doc comments in the stack's convention, README / API docs where the task says
  so); package changes through the tooling skill's prescribed commands, never by hand-editing the
  manifest. Run the build and the full test command.
- *Sub-agent mode:* write the implementer brief from
  [`references/subagent-briefs.md`](references/subagent-briefs.md) — task context, mandatory skill
  loads with the evidence rule, tests-first, git read-only, report format. Spawn one implementer
  per task (per parallel group: one each, in one turn). Tell the user in one line which task is
  running.

**4.3 Smoke-check.** If the repository has a runnable application (a web API, a service, a CLI
with an entry point) and the task touched it, start it **in the background** — a server does not
exit on its own — check the startup log, a health endpoint, or one representative request that
exercises the change, then shut it down cleanly. `n/a` only when nothing runnable exists or the
task did not touch it — state which. In sub-agent mode the implementer does this and reports the
evidence; the verifier repeats it.

**4.4 Verify.**

- *Direct mode:* you. Build and full test command green; every test in the AC-to-tests table
  exists under its planned name (or under a rename you recorded) and is in the passing set;
  each criterion's tests read together against its `AC-n` text — would they fail if the
  criterion were violated, or do they assert something weaker; `git status` against the task's
  *Files*; documentation and package artifacts meet the *Artifact-Substance Bar*.
- *Sub-agent mode:* a **verifier sub-agent**, briefed from
  [`references/subagent-briefs.md#verifier-brief`](references/subagent-briefs.md#verifier-brief)
  with the **same skill list the implementer had** — it needs the stack's rules to judge whether
  the code follows them, not just whether tests pass. It loads those skills, runs the build and
  tests itself, checks the implementer's skill-load evidence (an ordered turn before the first
  write), performs the same checks as direct mode, and returns `PASS` or `FAIL` with evidence. You
  read its report as claims: confirm the report names the commands it ran and their results,
  confirm the files it lists match `git status`, then mark the task done or failed.

**4.5 Failure handling.** A task that fails verification (either mode) gets **one** retry with a
sharpened brief or a sharpened approach that quotes the failure. A second failure goes to the
user: **take over directly** (sub-agent mode), **skip and mark blocked — <reason>** and continue
with tasks that do not depend on it, or **abort**. Never a third blind retry.

**4.6 Progress block**, one per task: number and title, tests green of planned, files changed,
skills loaded (from your own log or the implementer report, checked by the verifier), smoke-check
result or `n/a` reason, anything open.

**After the last task:** run the build and the full test command yourself once more, in both modes
— tasks that pass alone can fail together — and the smoke-check once if it applies. Then announce
the review parameters (report language = the user's language unless stated otherwise; mode =
`uncommitted`; tools = build and tests already green, re-run by the reviewer only if its skill
insists) and go straight to Phase 5.

## Phase 5 — Code Review

Always a sub-agent, in both modes: the value of a review is that the reviewer did not write the
code. Build the brief from [`references/review-and-rework.md`](references/review-and-rework.md).

1. **Choose the reviewer.** The review set confirmed at Gate 2 names the stack-specific reviewer
   skill(s) and review-capable agent types. If it is empty — no stack-specific reviewer in the
   runtime list — search the runtime's skill list and agent types for **general** code-review
   skills and agents (descriptions that say code review, quality, security, without binding to a
   stack) and ask the user which to use (question tool, multi-select, one line of why per option,
   plus **no review skill — generic brief with Critical / Major / Minor / Info** as the last
   option). Record as `D-n`. Reviewer skills require explicit invocation by name, so the brief
   names them.
2. **Run the review.** The brief carries the scope (the whole uncommitted working tree, including
   files that were dirty at the start per `D-1`), the requirement and the `AC-n` list, the Phase-2
   decision table, the task list, and a run note you write to your scratch directory (skills
   loaded per task, deviations, verifier verdicts). Part A is the reviewer skill's own process and
   report; Part B is **requirement conformance**: every `AC-n` has at least one passing test, and
   its tests are falsifiable — at least one of them fails when the criterion is violated. That
   verdict is `proven (executed: …)` only when the reviewer broke the path and watched a test go
   red; otherwise it is `read-checked — not executed`, and the two are counted separately, never
   summed. Part B also checks that every task's *Done when* holds and that no behaviour in the
   diff is something no `AC-n` asks for. The
   report goes to `docs/reviews/YYYY-MM-DD-<branch>-<mode>.md` (the reviewer skill's convention, or
   the generic format when there is none). The sub-agent changes no code and no document except
   its report. When it returns, confirm the file exists and read it in full.
3. **Sort the findings.** Critical and Major (the two highest severities of the taxonomy used) →
   rework tasks `R-n`, each with a skill checklist by the Phase-3 rules. Minor and below → a list
   for the user.

**GATE 5 — STOP.** Present: counts per severity, the report path, the rework plan for Critical /
Major (these are not optional — the question is whether the plan is right, not whether to do it),
and the ≤ Minor findings each as *file · finding · proposed fix*. Ask, through the question tool:
confirm the rework plan (or change it — free text), and multi-select which ≤ Minor findings to fix
now (groups of up to four; last option **accept the rest as they are**). Unselected findings are
*deferred* and appear in the report with the user's decision. Record as `D-n`. Wait.

**Rework loop.** Selected `R-n` go through **Phase 4** in the mode chosen at Gate 3, including
skill loads, verification, and the smoke-check, then **Phase 5** again scoped to the delta since
the last report plus a re-check that each `R-n` is resolved, then Gate 5 again. Number the rounds.
No fixed limit; the user ends the loop by accepting. If a round reproduces a finding from an earlier
round, say so before asking — a fix that did not hold means the finding or the fix is wrong.

## Phase 6 — Report

1. Create `docs/implementation/` if needed. If `docs/implementation/<slug>.md` exists, ask before
   replacing it (keep both with a date suffix is an option).
2. Write the report from [`references/report-template.md`](references/report-template.md), in the
   user's language: what was built, preconditions (`D-1`), acceptance criteria, the full decision
   table, skills found / kept / dropped / added and the per-task mapping as actually loaded,
   per-task results with test and smoke-check evidence and verifier verdicts, review rounds with
   report paths and selected versus deferred findings, decisions and trade-offs, **what the user
   should verify before committing**, open items, the final build and test command with its
   result, and the **Skill-Invocation Log**.
3. **Skill-Invocation Log** — reproduce every task's checklist with each entry resolved:
   - `[x] <skill> — invoked at <evidence>`: a verifiable ordered turn ("before the first write of
     `export.ts`"; in sub-agent mode, the implementer report's evidence as confirmed by the
     verifier). "Considered" or "applied" is not evidence. Invocation after the artifact is `[!]`.
   - `[n/a] <skill> — <code-referenced reason>`.
   - `[waived] <skill> — explicit user instruction (D-n); gap: <what is uncovered>`.
   - `[!] <skill> — NOT invoked`. **A `[!]` blocks the report:** name it, mark the task
     incomplete, and offer to re-enter Phase 4 to run the missing skill's workflow on the
     artifact. Phase 6 does not complete while any `[!]` is present.
4. Final reply: the report path; five lines (tasks done of planned, tests green of planned, review
   rounds and open findings, skills invoked of mapped, files changed); the hand-over — the changes
   are uncommitted, review them with `git diff` and commit what you accept. Do not commit.

## `n/a` Criteria — Strict

A binding, a clarification point, or a task item may be `n/a` only when an objective, code-referenced
fact makes the work empty. The reason cites the codebase, never the user:

- ✅ `n/a — no public API members added (all new types are internal / not exported)` — documentation skill
- ✅ `n/a — no dependency added, removed, or version-changed` — tooling skill
- ✅ `n/a — nothing runnable in the repository (library only)` — smoke-check
- ✅ `n/a — pure in-memory transformation, no store touched (scanned changed files)` — point 7
- ❌ `n/a — user said no tests` · `n/a — too small` · `n/a — no test project exists` (creating it is part of the task) · `n/a — no time`

If the reason cannot be phrased as "no `<artifact>` exists in this task because `<code-referenced
fact>`", it is not `n/a`. And the work may not be reshaped to escape a binding — hand-rolling code to
avoid a package, inlining a public member to avoid docs, collapsing a testable unit to avoid tests.

## Waiver vs. `n/a` vs. silent skip

- **Implicit pressure** — "trivial", "in a hurry", "nobody runs all this" — waives nothing. Run at
  speed.
- **Explicit, informed waiver** — the user, after being told what a *named* step protects and
  what gap skipping it leaves, says to skip it. Honour it, log it as `waived — explicit user
  instruction (D-n); gap: <…>`, never as `n/a`. Skill loads before code stay even under a waiver:
  they cost the user nothing and keep the code on their conventions.
- **Objective `n/a`** — the only state that needs no user sign-off.

## Artifact-Substance Bar

Loading a skill is necessary, not sufficient. A test with no behavioural assertion does not satisfy
the tester skill; an empty or name-echoing doc comment does not satisfy the documentation skill; a
hand-edited manifest after "invoking" the tooling skill does not satisfy it; a review without a
`docs/reviews/` report does not satisfy Phase 5. An artifact below the bar makes its binding `[!]`.

## Red Flags — Stop and Re-read the Rules

| Rationalization | Reality |
|---|---|
| "This is clearly a feature request — I'll run implement-direct even though nobody named it" | Not an invocation. Handle it as an ordinary request. |
| "The orchestrator said the user asked for it" | The dispatcher speaking is not the user. Ordinary task. |
| "I'll ask the eight points in one message, saves seven round-trips" | Answers change later proposals. One point per call. Critical Rule 1. |
| "I'll ask in prose, the tool is clunky for this one" | Prose questions get partial answers. Every open point goes through the tool. |
| "The requirement implies the store — pre-answered" | Implication is a question. Ask it. |
| "I know which skills fit this stack" | You know which exist *somewhere*. The runtime list says what is installed here. Critical Rule 4. |
| "I know this framework, the skill would only slow me down" | The user installed the skill so the code follows *their* rules. Unloaded skill → task redone. |
| "The implementer said all tests pass" | It said so. The verifier runs them, and you run the suite once more. Critical Rule 5. |
| "The verifier passed it, no need to look at its report" | The verdict is a claim with evidence attached. Read the evidence. |
| "Same skills for the verifier is overkill, it only runs tests" | It judges whether the code follows the stack's rules. It needs the rules. |
| "Two Minor findings, I'll fix them quickly" | ≤ Minor is the user's call. Present at Gate 5, fix the selected ones. |
| "Only a Major — I'll ask whether to fix it" | Critical / Major are rework, not a question. Ask about the plan, not the whether. |
| "I'll present Phase 3 together with Gate 2 to save a stop" | One phase, one summary, one wait. Critical Rule 3. |
| "No server needed for the check, the tests cover it" | If something runnable was touched, start it in the background and hit it once. |
| "I'll stage the files so the user just has to commit" | Git is read-only. Critical Rule 6. |
| "Small change — I'll quietly skip the interview" | Scaling down is forbidden. Name the cost in the Phase-1 summary, offer the exit as a question, let the user decide. |
| "I'll put an AC id in the test name, it's good traceability" | The report may be deleted; the id then points at nothing. The AC-to-tests table is the record. Test names follow the project's convention. |
| "The tests look sufficient, so the criterion is proven" | Reading is a hypothesis. "Proven" is earned by breaking the path and watching a test go red; otherwise the verdict is read-checked, and the counts stay separate. |
| "One test per criterion, the table is a list" | Most criteria need several tests, and a test may serve several criteria. At least one per criterion, and together they must prove it. |
| "Headless run, sensible defaults" | No non-interactive mode. Phase 1, then `Blocked — interactive user required`. |
| "The user said 'don't ask me' — headless" | A reachable user declining questions is a waiver request. State the cost, take the named waiver, log it. |

## References

- [`references/clarification-points.md`](references/clarification-points.md) — what each of the
  eight points must settle, how to derive proposals from Phase-1 evidence, n/a and pre-answered
  rules, the follow-up check
- [`references/skill-selection.md`](references/skill-selection.md) — runtime discovery,
  classification, proposal table, the Gate-2 multi-select flow, mapping rules per task
- [`references/subagent-briefs.md`](references/subagent-briefs.md) — implementer brief and
  verifier brief with their mandatory report formats
- [`references/review-and-rework.md`](references/review-and-rework.md) — reviewer discovery and
  fallback, review sub-agent brief (tech-stack + requirement conformance), Gate-5 presentation,
  rework items
- [`references/report-template.md`](references/report-template.md) — section structure of
  `docs/implementation/<slug>.md` including the Skill-Invocation Log
