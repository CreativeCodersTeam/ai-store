# Implementation Report Template (Phase 8)

Written to `docs/implementation/<slug>.md`, in the plan's language, after the user has accepted the
review outcome. The report is for two readers: the user, who is about to run `git diff` and decide
what to commit, and whoever later asks "why does the code differ from the plan here?" — the answer
must be in this file, not in a chat log that no longer exists.

Every section is present; a section with nothing to say reads `n/a — <reason>`. Headings are
translated with the document; field names inside tables and the ID prefixes (`D-`, `K-`, `F-`,
`R-`) stay.

---

```markdown
> **Date:** YYYY-MM-DD
> **Plan:** docs/plans/<slug>.md @ <commit>          <!-- plan set: n of m -->
> **Spec:** docs/specs/<slug>.md @ <commit>          <!-- or: none — plan-only run (D-1) -->
> **Branch:** <branch>
> **Mode:** direct | sub-agents (sequential | parallel)
> **Status:** complete | partial — <what is open> | aborted at <phase>

# <Title — what was implemented, in one line>

## 1. Summary

Three to five sentences: what was built, from which plan, how many tasks of how many are done,
how many review rounds, and what the user has to do next (review the diff, commit).
**Nothing has been committed.**

## 2. Preconditions

- Working tree at start: clean | dirty — decision D-2: committed first / kept, included in review; files: <list>
- Plan-set dependencies: n/a | checked — <parts, state>
- Partial implementation found: no | yes — resumed from Task #n (D-n)

## 3. Consistency Check

| ID | Finding | Severity | IDs / tasks | Decision |
|---|---|---|---|---|
| K-1 | … | blocking | FR-4, #2 | D-3 — fix documents / ignore / … |
| K-2 | … | note | … | recorded |

Known Spec Feedback carried over (not re-checked): <list>.

## 4. Skills

**Runtime discovery:** n skills in the runtime list, n candidates after matching against the plan.

| Skill | Category | Proposed use | Outcome |
|---|---|---|---|
| <name> | knowledge | implementation | kept |
| <name> | workflow | excluded — nested workflow | stayed excluded |
| <name> | tester | implementation | dropped by user (D-5) |
| <name> | — | — | added by user (D-5), not in runtime list — could not be loaded |

**Mapping (as confirmed, D-6) and as actually loaded:**

| Task | Mapped skills | Loaded (from implementer report) |
|---|---|---|
| All | … | … |
| #1 | … | … |

## 5. Implementation

| Task | Title | Status | Planned tests | Green | Files | Deviations | Attempts |
|---|---|---|---|---|---|---|---|
| #1 | … | done | 3 | 3 | … | 0 | 1 |
| #2 | … | done | 2 | 2 | … | 1 (Change Log) | 2 — retry: <one line why> |
| #3 | … | blocked — <reason> | 4 | 0 | — | — | 2, then D-9: skipped |

Final full run: `<command>` → <n passed, m failed> on <date/time>.

## 6. Deviations from the Plan

The Change Log rows added to `docs/plans/<slug>.md` during this run, verbatim:

| Date | Task | Change | Reason | Origin |
|---|---|---|---|---|

Functional deviations accepted by the user as plan changes are marked with their `D-n`.

## 7. Review

| Round | Report | Findings (per severity) | Selected | Deferred | Rework result |
|---|---|---|---|---|---|

Reviewer skills used: <names>. Plan conformance in the final round: <n/n matrix rows verified,
n Change Log gaps, n scope findings>.

## 8. Decisions Log

Every question asked in this run and its answer:

| ID | Phase | Question | Decision | Origin |
|---|---|---|---|---|
| D-1 | 0 | Spec missing — continue plan-only? | … | proposal / user's own |
| D-2 | 0 | Dirty working tree | … | … |
| D-n | 7 | Fix F-1, F-2, F-4? | … | … |

## 9. Open Items

- Deferred review findings: `F-n` — <one line> — decision `D-n`
- Blocked or partial tasks: `#n` — <reason>
- Consistency notes not acted on: `K-n`
- Skills the user asked for that were not loadable: <names>
- Spec Feedback the plan carries that is still open: <list>

## 10. Hand-over

The changes are **uncommitted**. Suggested next steps:
1. `git diff` — review the changes against this report and the plan.
2. `git add` / `git commit` what you accept; the Change Log in the plan explains every
   difference from the frozen plan.
3. Open review findings and blocked tasks are listed in §9.
```

## Final reply after writing the report

The report path, then five lines — tasks done of planned; planned tests green of planned; review
rounds and open findings; Change Log rows added; files changed — then one sentence: the changes
are uncommitted, review them with `git diff` and commit what you accept. Nothing else.
