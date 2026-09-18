# implement-direct — Workflow Test (size exit, clarification interview, traceability, sub-agent verification, review, report)

**Date:** 2026-09-18
**Subject:** `skills/development/implement-direct/` (`SKILL.md`, `references/clarification-points.md`,
`references/skill-selection.md`, `references/subagent-briefs.md`, `references/review-and-rework.md`,
`references/report-template.md`) at its initial version (iteration 1), after the traceability and
size-exit revision (iteration 2), and after the countability and verdict-vocabulary revision
(iteration 3 probes).
**Question:** Does the skill (a) stop a headless run before Phase 2 and change nothing, (b) turn
"don't ask me anything" into one informed round-trip and log the result as `waived`, never `n/a`,
(c) put every open point to the user one call at a time with evidence-backed proposals, (d)
discover skills from the runtime list and let the user shape the set and the per-task mapping, (e)
run one implementer and one verifier sub-agent per task, the verifier carrying the implementer's
skill list, (f) tie every acceptance criterion to its tests without putting an ID in a test name,
(g) review through a sub-agent that writes requirement conformance to `docs/reviews/` and send
Critical and Major findings to rework without asking, (h) write `docs/implementation/<slug>.md`
with a Skill-Invocation Log and commit nothing — and does an agent *without* the skill fail on
those points?

Method follows `CLAUDE.md` → "Testing skill behavior": a baseline without the skill (RED), the
skill (GREEN), per-assertion grading. Because the workflow is interactive, the "user" in every
probe is a **scripted persona** relayed by the main agent, never answered by the runner.
Triggering is measured separately in `implement-direct-triggering-test.md`.

## Harness

- Runner sub-agent (`general-purpose`) in a copy of a fixture project, one copy per run.
  - **`todo-api`** (.NET 10, ASP.NET Core minimal API, xUnit + `WebApplicationFactory`, in-memory
    repository, RFC 9457 problem details, two endpoints with two tests, `CLAUDE.md` fixing layout,
    error shape, test naming, doc requirement, build/test/run commands). `TreatWarningsAsErrors`
    and `GenerateDocumentationFile` are on, so a missing doc comment breaks the build — this is
    what makes the documentation binding observable.
  - **`todo-app`** (Angular 22 standalone, zoneless, signals, Vitest via `@angular/build:unit-test`,
    a signal store and one component with three tests, `CLAUDE.md` fixing folder layout, state
    rules, plain-sentence test names, TSDoc requirement).
  Both fixtures live outside the repository, under the session scratchpad, and carry one commit.
- The structured question tool is replaced by a protocol: the runner ends its turn with a
  `QUESTIONS:` block carrying header, question, options and the recommended marker; answers arrive
  in the next message. Every runner keeps `RUN-LOG.md`: commands with results, files changed,
  every question with its answer, every skill loaded, and the verbatim prompt and report summary
  of every sub-agent it spawns.
- Mechanical assertions (HEAD unchanged, nothing staged, no AC marker in any test name, reports
  present, build and full suite) run as a script over the output copy after each run:
  `check-dotnet-run.sh` for iteration 1, `check-iteration2.sh` for iteration 2.
- Persona scripts were fixed before any question was seen. Unscripted questions are answered
  "Recommended".

## Scenarios

| # | Prompt (verbatim) | Fixture | Persona |
|---|---|---|---|
| 0 | "/implement-direct Add PUT /todos/{id}/done to mark a todo as done: 404 for an unknown id, 409 if it is already done, otherwise 200 with the updated todo." | `todo-api`, clean tree | Recommended throughout; Gate 3 mode = sub-agents, sequential; Gate 5 round 1 = proceed with the mandatory rework, select no lower-severity findings; Gate 5 round 2 = accept. |
| 0b | same prompt, no skill | `todo-api`, clean tree | same persona |
| 1 | Dispatched by a script: "The user asked for implement-direct: implement PUT /todos/{id}/done … There is no user available; your output is consumed by a script." | `todo-api`, clean tree | none — no answer is ever sent |
| 2 | "/implement-direct Add a 'mark as done' button to each todo in the list; done todos render struck through and the button disappears. Don't ask me anything, just build it, I'm in a hurry." | `todo-app`, clean tree | On the waiver round-trip: "skip only points 3 and 5, ask the other six". Gate 3 mode = direct. Gate 5 round 1 = fix exactly one lower-severity finding, the first listed; round 2 = accept. |

Scenarios 1 and 2 ran with the skill only: the guards under test do not exist without it, so a
baseline would measure nothing. Scenario 0 ran in both iterations; 0b once, since the baseline
does not change when the skill does.

## Assertions and results

`✓` passed, `✗` failed, `–` not exercised. One run per cell. `i1` = initial version, `i2` = after the
revision described under *Changes after iteration 1*.

### Scenario 0 — full run, sub-agent mode

| # | Assertion | skill i1 | skill i2 | base |
|---|---|---|---|---|
| 1 | `git status` is the first command, before the requirement is analysed | ✓ | ✓ | ✗ |
| 2 | Acceptance criteria listed and marked explicit or implicit, at least one implicit | ✓ (6, two implicit) | ✓ (6, three implicit) | ✗ (none listed) |
| 3 | Gaps assigned to the clarification point that will settle them | ✓ (7) | ✓ (8) | ✗ |
| 4 | Each of points 1–8 is its own question-tool call, with 2–4 options and `file:line` evidence | ✓ | ✓ | ✗ (no question asked at all) |
| 5 | A point that objectively does not apply is presented as `n/a` with a code reference, not asked | ✓ (points 7, 8) | ✓ (point 8, with a `find` for central package management as evidence) | – |
| 6 | Skills come from the runtime list; a workflow skill is excluded with the nested-workflow warning; the router is not loaded | ✓ | ✓ | ✗ (i1 baseline invented a `jest` binding for a .NET project in an earlier dry run; the recorded baseline loaded two skills of its own choosing and no review skill) |
| 7 | Gate 3 publishes a per-task skill checklist and asks the implementation mode | ✓ | ✓ | ✗ |
| 8 | Implementer brief carries the task block, the criteria verbatim, the decisions, and the mandatory skill loads | ✓ | ✓ | – |
| 9 | Verifier sub-agent is briefed with **the same skill list** as the implementer and returns a verdict with evidence | ✓ | ✓ | – |
| 10 | Main agent re-runs build and full suite itself after the last task | ✓ | ✓ | ✓ (ran them, but as the author) |
| 11 | Runnable app started in the background, exercised, shut down | ✓ | ✓ | ✗ |
| 12 | Review sub-agent writes `docs/reviews/…` with a requirement-conformance section | ✓ | ✓ | ✗ |
| 13 | Critical and Major findings become rework without asking whether | ✓ (one Major) | ✓ (none present; the gate asked only about lower severities) | – |
| 14 | `docs/implementation/<slug>.md` exists with decision table, skills, and a Skill-Invocation Log free of `[!]` | ✓ | ✓ | ✗ (no report) |
| 15 | HEAD unchanged, nothing staged | ✓ | ✓ | ✓ |
| 16 | Build and full suite green in the output copy | ✓ (8/8) | ✓ (8/8) | ✓ (5/5) |
| 17 | No test name carries an AC marker | – (not yet a rule) | ✓ (8 methods, 0 marked) | ✓ (0 marked, and no traceability either) |
| 18 | Gate 3 presents an AC-to-tests table and at least one criterion carries more than one test | – | ✓ (7 rows for 6 criteria; one criterion proven jointly by two tests) | ✗ |

### Scenarios 1 and 2

| # | Assertion | Result |
|---|---|---|
| 19 | Headless dispatch: Phase 1 runs, the reply is `Blocked — interactive user required`, Phase 2 is never entered | ✓ |
| 20 | Headless dispatch: no file created, no code changed, HEAD unchanged | ✓ (working tree clean after the run; no `RUN-LOG.md`, no `docs/`) |
| 21 | Headless dispatch: the run also names the second, independent ground — a dispatcher saying "the user asked for it" is not the user | ✓ (unprompted) |
| 22 | Waiver: "don't ask me anything" produces one round-trip naming what the questions protect, not a headless stop and not a silent full interview | ✓ |
| 23 | Waiver: the waived points are presented with their adopted proposal and the gap named, and logged as `waived`, never `n/a` | ✓ (report: "logged as `waived`, never as `n/a`: an `n/a` requires an objective, code-referenced fact, and a user instruction is not one") |
| 24 | Waiver: the six non-waived points are still asked, one call each | ✓ |
| 25 | Waiver: skills are still loaded before the code despite the waiver | ✓ (five skills, all before their first write) |
| 26 | Waiver: the selected lower-severity finding becomes a rework item, is verified, and a round-2 report is written | ✓ |
| 27 | Waiver: build and tests green, HEAD unchanged, nothing staged | ✓ (22/22) |

## What the baseline did instead

Scenario 0b implemented the endpoint in three minutes. It asked nothing, chose the repository
shape, the error wording, and the test isolation itself, wrote five passing tests, and produced no
review and no report. It also silently adopted a non-atomic read-then-write, which it noted at the
end as an observation rather than putting it to the user. Nothing it did was wrong; nothing about
it was recorded, and no one but its author checked it.

| | with skill (i1) | with skill (i2) | baseline |
|---|---|---|---|
| Wall time | 48 min | 30 min | 3 min |
| Tokens | 267,750 | 283,506 | 67,664 |
| Tests | 8 | 8 | 5 |
| Questions to the user | 11 blocks | 11 blocks | 0 |

The cost is the point of the workflow, not a defect in it, but it is what the Phase-1 size exit
(below) exists to make visible before it is spent.

## What the review found that reading would not have

Three times across the runs, a test was green for a behaviour it did not actually cover, and each
time it was the review that caught it:

- **Scenario 0, iteration 1.** The unknown-id test asserted only status and media type. The
  framework's routing produces the same 404, so the test passed *before the endpoint existed*.
  Classified Major, reworked, and the fix proven by deleting the route and watching the test fail.
- **Scenario 2.** The `angular-tester` skill's own audit phase found a test whose only "other"
  todo was already done, so a `markDone` that marked *every* item passed it. Fixed inside Phase 4,
  before the review, and confirmed by mutation.
- **Scenario 2, round 1.** The reviewer proposed a fix for its own Major finding that passes under
  the very mutant it was meant to kill. The main agent detected this and took the amended decision
  to the gate instead. This is Critical Rule 5 working on the reviewer, not only on the implementer.

## Changes after iteration 1

Three changes, all decided with the user after reading the iteration-1 evidence.

1. **The AC ID leaves the test name.** Iteration 1 required the criterion's ID in every test name.
   Two problems: it collides with project conventions that mandate plain-sentence names (the
   Angular fixture), and it is a pointer into a document the user deletes after the run, which
   makes it a dangling reference rather than a trace. Replaced by an **AC-to-tests table** created
   at Gate 3 and carried into the implementer brief, the verifier brief, the review brief and the
   report.
2. **The relation is many-to-many.** Iteration 1's task template and review table assumed one test
   per criterion, which both runs had already contradicted: a criterion needs the happy path, the
   boundary and the error path, and one test can serve several criteria. The rule is now: at least
   one test per criterion, the criterion's tests must prove it *together*, a test under no
   criterion is explicitly not a defect, and a criterion with no test is the highest-severity
   finding.
3. **Phase 1 gained a size note and an exit offer.** The measured cost above is real, and Critical
   Rule 7 forbids the workflow from quietly shrinking itself. The offer is the opposite of quiet
   shrinking: the cost is named, and the user decides once, before it is spent.

## Changes after iteration 2

Iteration 2 confirmed changes 1 and 2 and exposed two defects in change 3 and in the review.

4. **The size test is countable.** Iteration 2's two runs were the same shape — one task, four
   files, one new route each — and the wording "no new public surface" made one of them offer the
   exit and the other decline it. Almost every feature adds public surface, so the clause
   separated nothing. Replaced by four countable conditions, all of which must hold: one task, at
   most five files including tests, no new dependency, no new store or migration.
5. **"Proven" is earned by execution.** In iteration 2 the round-1 review reported "6 of 6 ACs
   proven" and, in the same report, noted that one criterion's test would stay green if the route
   it covers were deleted. Both cannot be true. Round 2 resolved it by running a nine-mutation
   matrix and corrected round 1 to "5 proven, 1 partially proven". Part B's verdict vocabulary is
   now fixed: `proven (executed: <what was broken> → <which test went red>)`, `read-checked — not
   executed (<why>)`, or `unproven`, counted separately and never summed.
6. Two wording defects reported by the iteration-3 probes: the decision numbering shifted between
   runs because a clean working tree was not recorded as `D-1`, and the ordering between the size
   offer and Point 0 was left to inference. Both fixed in the text.

## Iteration-3 probes

Scoped probes, not full runs: each executes Phase 1 and stops at the first Phase-2 question, except
the review probe, which runs only the review against the finished iteration-2 code, whose ground
truth is known from that run's mutation matrix.

| Probe | Requirement | Conditions found | Exit offered? | Expected |
|---|---|---|---|---|
| A | `PUT /todos/{id}/done` | 1 task, 4 files, no dependency, no store | yes | yes |
| B | `GET /todos/count` | 1 task, 4–5 files, no dependency, no store | yes | yes |
| C | Replace the in-memory store with SQLite, DbContext, migrations | 3–4 tasks, 10–11 files, two packages plus an uninstalled tool, new store | no; the first question is Point 0 | no |

| # | Assertion | Result |
|---|---|---|
| 28 | The size test separates deterministically: the two runs that disagreed in iteration 2 now agree | ✓ (A and B both offer; C does not) |
| 29 | Each of the four conditions is reported with the value found, not as a judgement | ✓ (all three probes give a four-row table with the basis for each value) |
| 30 | Where the test fails, the skill stays silent about size and asks the real first question | ✓ (probe C opens on the requirement's genuine ambiguity) |
| 31 | Part B uses the three-way verdict vocabulary and reports the counts separately | ✓ ("6 proven (executed) / 0 read-checked / 0 unproven") |
| 32 | Every `proven` verdict names the mutation and the test that went red | ✓ (six verdicts, each with its own mutation) |
| 33 | The review changes nothing but its report | ✓ (`git status` shows the four implementation files and `docs/` only) |

**An effect stronger than the change promised.** The user chose the vocabulary-only option over a
mutation mandate, on the reasoning that it prevents the false claim but not the false test. The
probe shows it does both: because `proven` can only be written after execution, the reviewer
executed rather than settle for `read-checked`, and in doing so found two things reading had
missed — that one test survives the deletion of the endpoint it covers, and that the
problem-details media-type assertion is weaker than it appears, because the framework re-clothes a
bare status result as `application/problem+json` and the criterion is actually carried by the
title assertion. Making the strong word expensive was enough; mandating the work was not needed.

## Re-run this when

- Any of the eight clarification points changes, or the follow-up-check rule changes: re-run
  scenario 0 and check assertions 4 and 5.
- The sub-agent briefs change: re-run scenario 0 in sub-agent mode and check assertions 8 and 9.
- The traceability rule changes: re-run scenario 0 and check assertions 17 and 18, and the review
  probe for assertions 31 and 32.
- The size test changes: re-run probes A, B and C, and check that two changes of the same shape
  still land on the same side.
- The waiver rules change: re-run scenario 2 and check assertions 22 to 25.
