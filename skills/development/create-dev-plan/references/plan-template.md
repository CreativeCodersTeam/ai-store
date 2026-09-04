# Plan Template

Used for both the draft (`docs/draft/plan_<slug>.md`) and the final plan
(`docs/plans/<slug>.md`). The draft adds the status header at the top and a *Review Notes*
section at the end; the plan has neither, and its Change Log starts empty with the freeze date.
Every other section appears in both, in this order, always. A section with no content reads
`n/a — <reason>`.

Write the document in the language of the spec (or the language decided at `L-1` for a raw
requirement). Headings are translated too; the structure, the field names inside tasks
(`Consumes`, `Provides`, `Verifies`, `Todos`), and the ID prefixes stay as they are — implementation
workflows parse them.

---

```markdown
<!-- Draft only: -->
> **Status:** DRAFT — awaiting review          <!-- or: DRAFT — headless, unresolved questions -->
> **Date:** YYYY-MM-DD
> **Spec:** docs/specs/<slug>.md @ <commit or date>   <!-- or the requirement's source -->
> **Plan set:** 1 of 1                          <!-- n of m when the spec was cut -->

# <Title — what this plan delivers, in one line>

## 1. Summary

Three to five sentences: what is built, for whom, from which spec, in how many tasks, and what
the first task is. If the plan was made from a raw requirement rather than a spec, say so here
and point to Spec Feedback.

## 2. Global Constraints

| # | Constraint | Source |
|---|---|---|
| 1 | <verbatim> | <spec section or file:line> |

They apply to every task implicitly. Conflicts between spec and code are resolved in the
Clarification Log and cited here.

## 3. Codebase Findings

Build/test commands; entry points and layering; the closest existing feature and its files;
test framework, naming convention (one real example), layout, fixtures; mock boundaries;
cross-cutting patterns; what was looked for and not found. Every item with a file reference.
`greenfield — no existing code` when there is none.

## 4. Scope

**Covered:** the requirement IDs this plan verifies (`FR-1…5, NFR-1…2, AC-1…6, IF-1`).

**Plan Set** (only when the spec was cut):

| Part | File | Scope | IDs covered | Depends on |
|---|---|---|---|---|

**Not in this plan:** IDs deferred to another part or excluded, one line each with the reason.

## 5. File Structure

| Path | Status | Responsibility | Tasks |
|---|---|---|---|
| … | new / changed / deleted / moved | … | #n |

## 6. Tasks

One block per task in the format of `references/task-design.md#task-format`: Goal, Depends on,
Parallel with, Status, Consumes, Provides, Files, Verifies, Todos (checkboxes), Done when.

## 7. Traceability Matrix

| ID | Kind | Task | Test type | Test name / manual step | Automated |
|---|---|---|---|---|---|

Sorted by ID; one row per ID and task; no blank cells (`open — G-n` for unresolved items).

## 8. Clarification Log

| ID | Question | Decision | Rationale | Origin |
|---|---|---|---|---|
| C-scope | One plan or several? | … | … | proposal / user's own / draft edit |
| C-1 | … | … | … | … |

## 9. Open Questions

Only items without a decision: gaps the user deferred (with owner and trigger) and, in headless
runs, every unanswered blocking gap as `unresolved — blocks Task #n`.

## 10. Spec Feedback

What the spec should absorb, one line each, so it can be updated to match the plan:

- IDs assigned by the plan (`IF-1 → "GET /api/…" in §6`)
- clarifications decided here (`C-1 → FR-4 wording`)
- gaps reported as notes (`G-1 happy-path-only FR-2`)
- untestable criteria and the wording that would make them testable
- derived acceptance criteria (raw input), with their confirmation status

## 11. Change Log

<!-- Plan only: -->
Frozen on YYYY-MM-DD (approval). Test names and interfaces above are fixed; changes during
implementation are recorded here, not applied silently.

| Date | Task | Change | Reason | Origin |
|---|---|---|---|---|

<!-- Draft only: -->
## Review Notes

- Points I am unsure about: …
- Cuts I considered and rejected (so they are not re-proposed): …
- Sections filled thinly, and why: …
```
