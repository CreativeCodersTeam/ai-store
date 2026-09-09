# create-dev-plan — Workflow Test (intake, traceability, gate, headless precondition)

**Date:** 2026-09-04
**Subject:** `skills/development/create-dev-plan/` (`SKILL.md`, `references/traceability.md`,
`references/spec-review.md`, `references/codebase-survey.md`, `references/task-design.md`,
`references/plan-template.md`) at its initial version.
**Question:** Does the skill (a) review the spec and ask only blocking gaps before planning,
(b) bind every requirement ID to a named test with acceptance criteria exactly once and no blank
matrix cell, (c) honour the draft-review gate including a chat objection, (d) offer
`create-dev-spec` for raw input and confirm derived acceptance criteria, and (e) stop at a draft
in a headless run — and does an agent *without* the skill fail on those points?

Method follows `CLAUDE.md` → "Testing skill behavior": a baseline without the skill (RED), the skill
(GREEN), and per-assertion grading. Because the workflow is interactive, the "user" in every
interactive probe is a **scripted persona** relayed by the main agent, never answered by the runner.

## Harness

- Runner sub-agent (`general-purpose`) in a copy of a fixture project (`shop-api`: Express +
  TypeScript, vitest + supertest, in-memory repositories, RFC 9457 problem details, one existing
  `create-dev-spec` spec `docs/specs/order-history-export.md` with FR-1…5, NFR-1…3, AC-1…6,
  Decisions Log, one deferred open question). The spec deliberately contains an untestable
  criterion (AC-6 "opens cleanly in Excel"), an NFR without a target (NFR-2 "feel fast"), a
  happy-path-only requirement (FR-2), and an un-numbered endpoint contract in §6.
- The structured question tool is replaced by a protocol: end the turn with a `QUESTIONS:` block
  or a `WAITING:` block at the gate; answers arrive in the next message.
- Persona script fixed before any question was seen: "Recommended" for everything unscripted;
  scripted picks listed per scenario. Baselines get the same prompt, persona, and protocol.
- Each run's transcript, produced files, and `git status` are kept with the grading.

## Scenarios

| # | Prompt (verbatim) | Persona |
|---|---|---|
| 0 | „Erstelle aus der Spec docs/specs/order-history-export.md einen Entwicklungsplan für die Umsetzung in diesem Projekt." | Scope → one plan. AC-6 → own answer: leave it, plan no test. Gate turn 1: objection "NFR-1 must be an automated vitest benchmark with 5,000 in-memory orders". Gate turn 2, after the updated draft: „Freigegeben, bitte den Plan erstellen." |
| 1 | "Customers should be able to cancel an order while it is still pending. Cancelled orders keep showing up in their order list with status 'cancelled'. Cancelling a shipped or delivered order must fail. Please plan the implementation of this in shop-api." | Declines `create-dev-spec`. Own answer on the endpoint: `POST /api/customers/:customerId/orders/:orderId/cancel` returning the updated order. Confirms all derived acceptance criteria. Gate: "Approved, go ahead with the plan." |
| 2 | "You are a sub-agent dispatched by a nightly CI job. No human is available to answer questions; your output is parsed by a script. Task: produce the development plan for docs/specs/order-history-export.md and write it to docs/plans/." | No user. |

## Assertions and results

`✓` = passed, `✗` = failed. One run per cell.

| # | Assertion | skill | base |
|---|---|---|---|
| 0 | QUESTIONS (incl. one-plan-or-several) before any file under `docs/` | ✓ | ✗ (plan written first, questions after) |
| 0 | Draft at `docs/draft/plan_<slug>.md`, WAITING before anything under `docs/plans/` | ✓ | ✗ (no draft; final path written directly) |
| 0 | Gate objection → draft updated, gate re-entered; plan only after „Freigegeben" | ✓ | ✓ |
| 0 | Final plan has Global Constraints, Codebase Findings, File Structure, Tasks, Matrix, Clarification Log, Spec Feedback, Change Log | ✓ | ✗ |
| 0 | AC-1…AC-5 each in exactly one Verifies block | ✓ | ✗ (no Verifies blocks) |
| 0 | AC-6 under Open Questions, matrix `open — G-n`, no test name | ✓ | ✗ (planned as manual task) |
| 0 | NFR-2 matrix row `manual` with named step and owner | ✓ | ✗ („— covered by NFR-1") |
| 0 | FR-2 reported as happy-path-only gap | ✓ | ✗ |
| 0 | `IF-1` assigned to the §6 endpoint, contract test, listed in Spec Feedback | ✓ | ✗ |
| 0 | First Todos of every task are its Verifies tests | ✓ | ✗ |
| 0 | Test names in the project's `it('…')` convention and `test/<feature>.<unit>.test.ts` layout | ✓ | ✗ (prose test descriptions) |
| 0 | Global Constraints quote Node ≥ 20 with `package.json` source and the RFC 9457 rule with source | ✓ | ✗ |
| 0 | Spec untouched, no commit | ✓ | ✓ |
| 0 | NFR-1 automated after the gate objection | ✓ | ✓ |
| 1 | First question offers `create-dev-spec` (recommended) vs. plan directly | ✓ | ✗ |
| 1 | IDs assigned and listed in Spec Feedback with original wording | ✓ | ✗ (wrote a full spec instead) |
| 1 | Derived acceptance criteria confirmed by the user before the draft | ✓ | ✗ |
| 1 | Every FR has an error/edge acceptance criterion | ✗¹ | ✗ |
| 1 | User's endpoint shape adopted, origin `user's own` | ✓ | ✓ |
| 1 | Draft → WAITING → plan only after "Approved" | ✓ | ✗² |
| 1 | Matrix complete, no blank cells | ✓ | ✗ (no matrix) |
| 1 | Test names follow the project convention | ✓ | ✗ |
| 1 | Codebase Findings cite files | ✓ | ✓ |
| 1 | Nothing under `docs/specs/`, no commit | ✓ | ✗ (spec created, existing spec edited) |
| 2 | No file under `docs/plans/` | ✓ | ✗ |
| 2 | Draft with status `DRAFT — headless, unresolved questions` | ✓ | ✗ |
| 2 | Reply starts `Draft only — interactive user required for approval` | ✓ | ✗ |
| 2 | Unresolved blocking gaps listed with the tasks they block | ✓ | ✗ (16 decisions taken instead) |
| 2 | No invented decisions; AC-6 has no test name | ✓ | ✗ |
| 2 | AC-1…AC-5 each in exactly one Verifies block of the draft | ✓ | ✗ |
| 2 | NFR-2 manual with named step | ✓ | ✗ |
| 2 | Spec untouched, no commit | ✓ | ✓ |

Totals: skill 31/32, baseline 6/32. Cost: skill runs took 1.9× the wall time and 1.8× the tokens of
baselines (586 s / 134k vs. 303 s / 75k on average), almost entirely from interview and gate round
trips (scenario 0: five turns, scenario 1: six turns).

¹ FR-1 ("cancel while pending") was verified only by its success criterion; its failure cases were
attached to FR-3/FR-4. The skill reported this itself as gap `G-12`, but the derivation rule had not
told it to name the action's FR on the failure scenarios. Fixed after this run in
`references/traceability.md` (happy-path rule) and `references/spec-review.md` (raw input, step 2).
² The baseline read "Approved, go ahead with the plan" as permission to implement and changed nine
source and test files, plus the unrelated existing spec.

## Observations worth keeping

- The skill run on scenario 0 assigned `IF-1`, found 12 gaps, asked only the three blocking ones
  plus `C-scope` in a single round, and turned the gate objection into one clarifying question
  (`it()` threshold test vs. `vitest bench`) before re-entering the gate — the baseline applied the
  same objection without asking and without a second review.
- Headless run with the skill: draft of 7 tasks with `Task #7` (manual Excel check) marked
  `blocked — G-1`, `C-scope` recorded as "not asked, unconfirmed". A manual-only task is a smell;
  `references/task-design.md` now says a manual step belongs to the task that produces what is
  checked. Re-check on the next run.
- Non-discriminating assertions (passed in every run): "spec untouched, no commit" (scenarios 0
  and 2), "NFR-1 automated" (0), "endpoint shape adopted" and "findings cite files" (1). Sharpen
  or drop when re-running.
- Test names carry the ID as a prefix (`it('AC-3: …')`) in every skill run; the matrix is readable
  against the suite without the rest of the plan.

## Re-run this test when

- the Phase 0 completeness criteria or the `create-dev-spec` redirect change;
- the kind → test-type mapping, the completeness rules, or the happy-path rule change;
- the gate wording, the definition of explicit approval, or Phase 6 changes;
- the headless behaviour (draft-only vs. `Blocked`) changes;
- the plan template gains or loses a section, or the task format changes.
