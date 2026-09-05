# Consistency Check (Phase 1)

The plan was frozen on one day against one version of the spec and one state of the code. Any of
the three may have moved since. This check finds the movement before it is discovered halfway
through a task, when the cheapest fix is no longer available.

Every finding is `K-n` with the IDs or tasks it concerns and one of two severities:

- **blocking** — a task cannot be implemented or verified as planned without a decision;
- **note** — the work can proceed; the finding is recorded in the report so nobody rediscovers it.

Spec Feedback items in the plan are *not* findings. The plan already told the user that the spec
lacks an ID, has an untestable criterion, or should absorb a clarification. List them once under
"Known Spec Feedback (not re-checked)" so the reader sees they were seen.

## Checks

### 1. Coverage (spec ↔ matrix)

Extract every ID from the spec (`FR-n`, `NFR-n`, `AC-n`, and any `IF-n` the spec assigns) and every
ID from the plan's traceability matrix.

| Situation | Severity |
|---|---|
| Spec ID missing from the matrix, and not listed under *Not in this plan* (plan set) or *Open Questions* | blocking — nothing will prove it |
| Plan ID absent from the spec and not in Spec Feedback as `assigned by plan` | blocking — the plan verifies something the spec does not ask for |
| Plan ID absent from the spec but listed in Spec Feedback | note — expected; the spec has not absorbed it yet |
| Matrix row `open — G-n` | note unless the task depending on it is in this run's scope, then blocking |

### 2. Freshness (spec commit)

The plan header records `Spec: docs/specs/<slug>.md @ <commit>`. Compare with
`git log -1 --format=%h -- docs/specs/<slug>.md`.

- Same commit → fine.
- Different → `git diff <plan-commit>..HEAD -- docs/specs/<slug>.md`. Read the diff against the
  matrix: a changed sentence inside an ID the matrix verifies is **blocking** (the planned test may
  now prove the wrong thing); changes to Summary, Context, Decisions Log wording, or Open Questions
  are **note**.
- The header has a date instead of a commit (spec not in git, or raw-requirement plan) → compare
  file modification date; a later date is a **note** asking the user whether the source changed.

Do the same for the plan itself only if its Change Log has rows dated after the freeze — that means
an earlier implementation run touched it; see check 6.

### 3. Constraints (plan ↔ code)

Every row of *Global Constraints* has a source. For sources of the form `file:line`, open the file
and confirm the constraint still holds — the version floor is still that version, the dependency
is still (or still not) present, the naming convention is still what the plan says. For sources
that are spec sections, check the code does not contradict them (the spec says one framework, the
project now targets another).

A constraint that no longer holds is **blocking** when a task's Todos rely on it (a target
framework version, a required library), **note** otherwise (a convention that drifted).

### 4. Contracts (task ↔ spec ↔ task)

For every task:

- *Consumes* entries marked `from #k` — does task `#k`'s *Provides* list that exact name and shape?
  A mismatch is **blocking** for the consuming task.
- *Consumes* entries marked `existing, <path>` — does the code at that path still expose it?
  Missing is **blocking**.
- *Provides* that cite an `IF-n` — does the shape match the spec's contract (path, verb, payload,
  status codes, or the equivalent for non-HTTP interfaces)? A difference is **blocking**; the
  Clarification Log may explain it (then it is a **note** citing the `C-n`).

### 5. Plan self-check

The plan skill runs this before the draft; you run it again because the file may have been edited
after approval.

- Every task has every field (`Goal`, `Depends on`, `Parallel with`, `Status`, `Consumes`,
  `Provides`, `Files`, `Verifies`, `Todos`, `Done when`).
- The first Todos of every task mirror its Verifies block one to one.
- No blank matrix cell; every acceptance criterion appears in exactly one Verifies block across the
  plan set.
- A Change Log section exists with the freeze date.

A failure here is **blocking**: a plan that breaks its own rules cannot be verified against. The
fix is the user's, with `create-dev-plan`.

### 6. Progress (partial implementation)

Ticked Todos, tasks with `Status: done`, or Change Log rows dated after the freeze mean this plan
was implemented in part before. That is not a finding to fix; it is a decision to take: ask whether
to **resume from the first task with unticked Todos (Recommended)**, treating done tasks' *Provides*
as existing code and verifying them once with the full test run, or **start over**, in which case
the user resets the code and the plan themselves (git is read-only for you) and tells you.

### 7. Text contradictions

Read each task's *Goal* next to the spec text of the IDs it cites. A Goal that says less than the
spec (one of two cases handled), or different (another status code, another field name), is
**blocking** for that task. This is the slow check; it is also the one that catches what the
mechanical checks cannot.

## Plan-only runs

When there is no spec (Phase 0, `D-1`), the plan's *Clarification Log* and *Spec Feedback* stand in
for it: the derived acceptance criteria listed there with their confirmation status are the
requirement text. Check 1 becomes "every confirmed criterion is in the matrix; no unconfirmed
criterion is" — an unconfirmed criterion in a Verifies block is **blocking**. Check 2 compares the
requirement source named in the header (ticket, file) if it is reachable, otherwise it is skipped
with a note. Check 7 reads each Goal against the derived criteria. Checks 3–6 are unchanged.

## Presenting the findings

One numbered list, blocking first:

```
Consistency check — docs/plans/order-history-export.md vs. docs/specs/order-history-export.md

Blocking
  K-1  FR-4 wording changed in spec since plan freeze (a1b2c3d → e4f5g6h): "within 30 days"
       became "within 90 days". Task #2 test it('AC-3: …') encodes 30 days.
  K-2  Task #3 Consumes CsvFormatter.format(orders) from #2, but #2 Provides
       CsvFormatter.format(orders, options). Signature mismatch.

Notes
  K-3  Global Constraint 2 cites package.json:7 "node >= 20"; file now says ">= 22". Stricter,
       no task affected.

Known Spec Feedback (not re-checked): IF-1 assigned by plan; G-1 happy-path-only FR-2.
```

## Asking

Per blocking finding, in order of how much a wrong guess would cost, one question with 2–4 options.
The generic set, adapted when the finding suggests a sharper one:

| Option | Consequence |
|---|---|
| **Fix the documents (Recommended when the spec moved)** | User updates spec and/or plan (plan via `create-dev-plan`'s Change Log or a re-plan), tells you, you re-run Phase 0–1. |
| **Ignore — proceed as planned** | Recorded as `D-n`, origin `user's own`, repeated in the report. The task is implemented per the plan even though the spec now says otherwise. |
| **Abort** | Nothing is changed. |

For `K-2`-type contract mismatches a fourth option is natural: **implement #3 against #2's actual
signature and log it** — a Change Log row, not a plan edit.

Up to four *independent* findings per question call; findings whose answers affect each other go
in separate calls. Notes are not asked — not on their own and not appended to a blocking question.
They are listed once and carried into the report; a note that turns out to need an answer was a
blocking finding misclassified, so reclassify it rather than asking it as a note.
