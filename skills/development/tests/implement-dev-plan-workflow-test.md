# implement-dev-plan — Workflow Test (intake guards, consistency, runtime skills, sub-agent verification, review, report)

**Date:** 2026-09-05
**Subject:** `skills/development/implement-dev-plan/` (`SKILL.md`, `references/consistency-check.md`,
`references/skill-selection.md`, `references/subagent-brief.md`, `references/verification.md`,
`references/review-and-rework.md`, `references/report-template.md`) at its initial version
(iteration 1) and after the first revision (iteration 2, see below).
**Question:** Does the skill (a) stop on a draft-only plan, (b) find spec drift after plan freeze and
put it to the user before any code, (c) discover skills from the runtime list and let the user shape
the set and the task mapping, (d) run one sub-agent per task with a brief that carries the task
block, spec text and mandatory skill loads, and verify each task itself, (e) confine plan edits to
ticks, Status and Change Log rows, (f) review through a sub-agent that writes a Plan Conformance
report to `docs/reviews/`, (g) let the user pick rework findings and loop, (h) write
`docs/implementation/<slug>.md` and commit nothing — and does an agent *without* the skill fail on
those points?

Method follows `CLAUDE.md` → "Testing skill behavior": a baseline without the skill (RED), the skill
(GREEN), per-assertion grading. Because the workflow is interactive, the "user" in every probe is a
**scripted persona** relayed by the main agent, never answered by the runner.

## Harness

- Runner sub-agent (`general-purpose`) in a copy of a fixture project (`shop-api`: Express 4 +
  TypeScript strict ESM, vitest + supertest, in-memory repository, RFC 9457 problem details,
  `requireCustomer` middleware, one existing route with 3 tests). The fixture carries a
  `create-dev-spec` spec `docs/specs/order-history-export.md` (FR-1…5, NFR-1…3, AC-1…8, IF-1) and an
  approved `create-dev-plan` plan `docs/plans/order-history-export.md` (3 tasks, 20 matrix rows,
  Change Log frozen 2026-09-04, spec commit in the header). Runner sub-agents can spawn sub-agents
  and see the session's skill list (97 skills), so the sub-agent mode is testable.
- The structured question tool is replaced by a protocol: end the turn with a `QUESTIONS:` block;
  answers arrive in the next message. Every runner appends an evidence log (`RUN-LOG.md`: commands,
  file changes, questions and answers, skills loaded, verbatim sub-agent prompts and report
  summaries). Mechanical assertions (HEAD unchanged, nothing staged, spec unchanged, plan diff
  limited to ticks/Status/Change Log rows, `it('<ID>: …')` per matrix ID, build and full suite) are
  checked by a script over the fixture copy after the run.
- Persona script fixed before any question was seen: "Recommended" for everything unscripted;
  scripted picks per scenario below. The baseline gets the same prompt, persona and protocol.

## Scenarios

| # | Prompt (verbatim) | Fixture state | Persona |
|---|---|---|---|
| 0 | "Implement docs/plans/order-history-export.md." | clean tree, approved plan @ 58487b3, spec @ 920942a | Keep every proposed skill, no overrides, review set as proposed, mapping adopted, sub-agents, sequential. Iteration 1: rework only Critical/Major (none → accept). Iteration 2: select every finding of the two highest severities present (Minor when there is nothing above), fix, then accept round 2. |
| 1 | "Implement docs/plans/order-history-export.md." | spec commit 6e0bcd1 changes FR-2 "365 days" → "90 days" after the plan freeze; `README.md` dirty (uncommitted "Deployment" section) | Working tree → continue. Spec-drift finding → "Ignore — proceed as planned". Skills, mapping → recommended. Mode question → "Stop here — abort the run. I only wanted the pre-checks." |
| 2 | "Implement the plan for the order history export." | plan moved to `docs/draft/plan_order-history-export.md` with `Status: DRAFT`; no `docs/plans/` | none expected |

Scenario 1 and 2 ran with the skill only (baseline waived by the user: the guards under test do not
exist without the skill).

## Assertions and results

`✓` = passed, `✗` = failed, `–` = not exercised. One run per cell. `i1` = initial version, `i2` = after
the revision described under *Changes made after iteration 1*.

| # | Assertion | skill i1 | skill i2 | base i1 | base i2 |
|---|---|---|---|---|---|
| 0 | Consistency check (coverage, spec commit freshness, constraints, contracts, self-check) reported before any file under `src/` or `test/` changes | ✓ | ✓ | ✗ (requirement review only) | ✗ |
| 0 | QUESTIONS to keep/drop proposed skills; names from the runtime list with category and reason; workflow skills excluded with nested-workflow warning | ✓ | ✓ | ✗ (agent filled "slots" itself; `jest` for a vitest project) | ✗ (no skill loaded at all) |
| 0 | Task → skills mapping table presented and confirmed before implementation | ✓ | ✓ | ✗ | ✗ |
| 0 | Direct vs. sub-agents (and sequential vs. parallel) asked before implementation | ✓ | ✓ | ✗ | ✗ |
| 0 | One sub-agent per task in order; brief carries the verbatim task block, spec text of the verified IDs, mandatory skill loads, fixed report format | ✓ | ✓ | ✗ (rules restated in the main agent's words, no skill loads, free-form report) | ✗ (#3 done by the main agent itself) |
| 0 | Main agent runs build and full test suite itself after every task | ✓ | ✓ | ✓ | ✓ |
| 0 | Plan diff limited to ticked Todos, `Status`, appended Change Log rows | ✓ (28 ticks, 3× done, 4 rows) | ✓ (28 ticks, 3× done, 8 rows) | ✓ (3 rows, no ticks) | ✓ (4 rows, no ticks) |
| 0 | Spec unchanged | ✓ | ✓ | ✓ | ✓ |
| 0 | Every matrix ID present as `it('<ID>: …')`, full suite green | ✓ (13 IDs, 21/21) | ✓ (13 IDs, 23/23) | ✓ (13 IDs, 21/21) | ✓ (13 IDs, 23/23) |
| 0 | Review by a sub-agent that loads reviewer/refactoring/tester skills; report in `docs/reviews/` with a Plan Conformance table | ✓ (20/20 rows) | ✓ (2 rounds, 20/20 rows) | ✗ (review only in the transcript) | ✗ (no review at all) |
| 0 | Findings by severity, multi-select rework question, selected fixed, second round before the report | –¹ | ✓ (4 selected → R-1…R-4 → round 2, repeated finding called out) | ✗ (fixed Minor findings without asking) | ✗ |
| 0 | `docs/implementation/<slug>.md` with Decisions Log, Skills, Change Log rows, review rounds | ✓ | ✓ | ✗ | ✗ |
| 0 | Nothing committed or staged | ✓ | ✓ | ✓ | ✓ |
| 0 | Every mapped skill loaded before code in each task, proven in the sub-agent report | ✓ | ✓ | ✗ | ✗ |
| 1 | First QUESTIONS block is the working-tree question, alone, before any consistency finding | ✗² | ✓ | | |
| 1 | Blocking finding names FR-2 365 → 90 days with commits 920942a → 6e0bcd1 and the affected planned tests; options fix documents / ignore / abort | ✓ (also flagged the spec's internal inconsistency) | ✓ (plus: AC-4's 110-day example breaks under 90 days) | | |
| 1 | "Ignore" recorded as `D-n`, origin `user's own` | ✓ | ✓ | | |
| 1 | Skill proposal and mapping asked before the mode question | ✓ | ✓ | | |
| 1 | Abort at the mode question → no code changed, only the pre-existing `README.md` dirty, no `docs/reviews/`, no `docs/implementation/` | ✓ | ✓ | | |
| 1 | Plan and spec unchanged, nothing committed | ✓ | ✓ | | |
| 2 | Stops: only a draft exists, points to the `create-dev-plan` gate | ✓ | ✓ | | |
| 2 | No skill/mapping/mode questions, no implementation attempted | ✓ | ✓ | | |
| 2 | Working tree clean, no files created | ✓ | ✓ | | |

Totals: iteration 1 skill 21/23 (one not exercised), baseline 5/14; iteration 2 skill 23/23, baseline
5/14. Cost, scenario 0: iteration 1 skill 35 min wall clock and ~200k tokens vs. baseline 20 min and
~140k tokens (RUN-LOG timestamps; that baseline loaded the old `implementer` skill and used one
sub-agent per task); iteration 2 skill ~45 min including two review rounds and one rework round,
~280k tokens, vs. baseline ~7 min and ~100k tokens with no skill, no questions and no review.

¹ The review found 0 Critical / 0 Major / 4 Minor / 8 Info; the iteration-1 persona accepted, so the
rework loop (Phase 7 → 5 → 6 → 7) never ran. The question itself was correct: severity counts,
report path, F-1…F-4 with proposed fixes, multi-select, explicit accept option. Iteration 2 uses a
persona that selects findings.
² The runner ran Phase 1 first and batched the working-tree question with the K-1 finding in one
block. Harmless here (only `README.md` was dirty) but against Phase 0's order; fixed in the revision.

## Changes made after iteration 1

- `SKILL.md` Phase 0 step 4: the working-tree question is asked alone, before Phase 1, with the
  reason (dirty files may be the plan or the spec, which would distort the consistency check).
- `SKILL.md` Phase 1 and `references/consistency-check.md`: notes are never asked, not even appended
  to a blocking question; a note that needs an answer is a misclassified blocking finding. (In
  iteration 1 the skill run asked note K-2 — a 365-day boundary reading — as a question.)
- `SKILL.md` Critical Rule 1: up to four independent questions per call.
- Two new Red Flags for both cases.

## Observations worth keeping

- Both runs in scenario 0 produced the same code shape and the same 18 planned test names; the
  skill's value showed in what surrounds the code: the user chose the skills (and could see that no
  Node/Express/TypeScript baseline skill is installed), every task was verified by the main agent
  against its Verifies block and spec text, four technical deviations became Change Log rows, and
  the review's Plan Conformance table checked all 20 matrix rows against the suite.
- The skill's sub-agent reports stated "loaded before first edit" for every mapped skill; the main
  agent checked them against the mapping (verification check 0). No rejection was needed, so the
  retry path for a missing skill is still untested.
- Non-discriminating assertions (passed in every scenario-0 run): "main agent runs the suite",
  "plan diff limited", "spec unchanged", "matrix IDs present and green", "nothing committed".
  Sharpen or drop when re-running.
- The protocol replacement for the question tool has no four-option or four-question limit; the
  iteration-1 skill run asked nine questions in one block. After the revision (Critical Rule 1: up to
  four independent questions per call) the iteration-2 runs asked at most four per block and put the
  dependent parallel question in a separate call.
- Iteration 2 exercised the rework loop: all four Minor findings became `R-1…R-4`, one rework
  sub-agent got a brief with the same mandatory skill loads and "fix exactly these", the main agent
  verified (build, suite, test names, files) and added three Change Log rows, round 2 was scoped to
  the delta and re-checked each `R-n`. Round 2 found `F-4` again as `F-7` and the skill said so before
  asking — the plan-bookkeeping rule for private helpers was applied once instead of stated as a
  rule. Worth a sentence in `verification.md` if it recurs.
- Task #3 carried five skills in both iterations; the mapping rule's "five skills is a smell" note made
  the runner justify it explicitly (three concerns by the plan's own cut) rather than trim silently.
- Without a stack baseline skill installed (no Node/Express/TypeScript knowledge skill in this
  runtime) the skill said so in the proposal and fell back to the plan's Codebase Findings and Global
  Constraints, as `skill-selection.md` prescribes. A fixture with a matching family (e.g. .NET) would
  test the baseline row properly.

## Re-run this test when

- Phase 0 (draft detection, plan-only decision, working-tree question) or the precondition changes;
- the consistency checks, the blocking/note split, or the question options change;
- the skill classification, the multi-select flow, or the mapping rules change;
- the sub-agent brief template, the report format, or verification checks 0–6 change;
- the review brief (Part A / Part B), the rework question, or the report template changes;
- `create-dev-plan`'s task format, Change Log rules, or freeze rule changes.
