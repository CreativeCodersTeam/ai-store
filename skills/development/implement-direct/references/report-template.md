# Implementation Report Template (Phase 6)

Written to `docs/implementation/<slug>.md`, in the user's language, after the user has accepted the
review outcome at Gate 5. The report is for two readers: the user, who is about to run `git diff`
and decide what to commit, and whoever later asks "why was it built this way?" — without a plan or
a spec, this file is the only record of the decisions, so the decision table is complete here, not
summarised.

Every section is present; a section with nothing to say reads `n/a — <reason>`. Headings are
translated with the document; field names inside tables and the ID prefixes (`AC-`, `G-`, `D-`,
`F-`, `R-`) stay.

---

```markdown
> **Date:** YYYY-MM-DD
> **Requirement:** <source — pasted text | path | URL>
> **Branch:** <branch>
> **Mode:** direct | sub-agents (sequential | parallel)
> **Status:** complete | partial — <what is open> | aborted at <phase>

# <Title — what was implemented, in one line>

## 1. Summary

Three to five sentences: what was built, how many tasks of how many are done, how many review
rounds, and what the user has to do next (review the diff, commit). **Nothing has been committed.**

## 2. Preconditions

- Working tree at start: clean | dirty — D-1: committed first / kept, included in review; files: <list>
- Runtime skill list: available (n skills) | not exposed — conventions only (D-n)
- Size note: n/a — the work was not small | raised (1 task, n files) and the user chose to run
  the full workflow (D-n)

## 3. Requirement and Acceptance Criteria

<Restated requirement, one paragraph.>

Many-to-many: a criterion may have several tests, a test may serve several criteria. Test names
carry no AC marker — this table is the traceability record, and once this report is gone the
link exists only in the tests' own descriptive names.

| AC | Text | Origin | Tests (file · name) | Result | Verdict |
|---|---|---|---|---|---|
| AC-1 | … | explicit | test/orders/export.test.ts · returns CSV for the caller's own orders | pass | proven (executed: route removed → this test red) |
|  |  |  | test/orders/export.test.ts · keeps another customer's orders out of the file | pass |  |
| AC-2 | … | implicit | … | pass | read-checked — not executed (suite runs 6 min) |

Verdicts come from the review's Part B and keep its wording. `proven` means a test of that
criterion was watched going red against a broken version; `read-checked` means the tests were
read and look sufficient but nothing was run against one. Count them separately — a summary line
that merges them tells the reader something that was never established.

## 4. Decisions

Gaps from Phase 1 and the eight clarification points, every round.

| ID | Point | Decision | Origin | Round |
|---|---|---|---|---|
| D-1 | working tree | … | user's own | — |
| D-2 | G-1 <gap> | … | recommended accepted | 1 |
| D-3 | 1 Structure | … | recommended accepted | 1 |
| D-4 | 2 Architecture | … | user's own | 1 |
| … | 7 Persistence | n/a — <reason> | n/a | 1 |
| … | 8 Dependencies | pre-answered — "<quote>" | pre-answered | 1 |
| D-12 | 8 Dependencies | <new question> → … | user's own | 2 |

Waivers: <none | D-n — step, gap left open>

## 5. Skills

**Runtime discovery:** n skills and n agent types in the runtime, n candidates after matching.

| Skill / agent | Category | Proposed use | Outcome |
|---|---|---|---|
| <name> | knowledge | implementation | kept |
| <name> | workflow | excluded — nested workflow | stayed excluded |
| <name> | tester | implementation | dropped by user (D-n) |
| <name> | — | — | added by user (D-n), not in runtime list — could not be loaded |
| <name> | reviewer | review | used in Phase 5 |

**Mapping (as confirmed at Gate 3) and as actually loaded:**

| Task | Mapped skills | Loaded by implementer | Confirmed by verifier |
|---|---|---|---|
| All | … | … | … |
| #1 | … | … | … |

## 6. Tasks

Per task, one block:

### Task #n — <title>  (Status: done | partial | blocked — <reason>)

- Delivers: AC-…  Files: <list>  Tests: <n of n green; renames planned → actual>  Docs: <what>  Packages: <what | n/a — reason>
- Implementer: you | sub-agent (attempt 1 | retry)   Verifier: you | sub-agent — PASS | FAIL → retry → PASS
- Smoke-check: <evidence> | n/a — <reason>
- Deviations: <none | what and why>

## 7. Review

Per round, also carry Part B's conformance line verbatim (n proven / n read-checked / n
unproven), because a later round may correct an earlier one's verdict.

| Round | Report | Critical | Major | Minor | Info | Rework done | Minor selected | Deferred |
|---|---|---|---|---|---|---|---|---|
| 1 | docs/reviews/… | 0 | 1 | 3 | 2 | R-1 | F-4 | F-5, F-6 (D-n) |
| 2 | docs/reviews/… | 0 | 0 | 1 | 0 | — | — | F-7 (D-n) |

Reviewer: <skill / agent, D-n if chosen by fallback>. Repeated findings: <none | which>.

## 8. Verify Before Committing

What the user should look at with their own eyes: the decisions where the recommendation was not
taken, the deferred findings, anything the smoke-check could not exercise, the deviations. One
line each, with the file.

## 9. Open Items

- Deferred findings with the user's decision
- Blocked tasks and why
- Skills the user named that could not be loaded

## 10. Final Verification

- Build: `<command>` → <result>
- Full suite: `<command>` → <n passed / n failed / n skipped>
- Smoke-check: <evidence> | n/a — <reason>
- Files changed: <n> (`git status --porcelain` count)

## 11. Skill-Invocation Log

Per task, the Gate-3 checklist resolved. Evidence is an ordered turn, never "considered".

Task #1 — <title>
  [x] <skill> — invoked before first write of <file> (implementer turn 2; verifier V1 ok)
  [x] <skill> — invoked before first write of <file> (implementer turn 3; verifier V1 ok)
  [n/a] <skill> — no public API members added (all new types internal)
Task #2 — <title>
  [x] …
  [waived] <skill> — explicit user instruction (D-n); gap: <…>
R-1 — <finding>
  [x] …

A `[!]` entry may not appear in a completed report. If one exists, Status is `partial` and the
entry names the task to re-enter Phase 4 for.
```
