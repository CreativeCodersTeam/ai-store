# Per-Task Verification (Phase 5.3–5.5)

Verification is the main agent's job in both modes, and it is deliberately redundant with what the
implementer already did. In sub-agent mode the reason is obvious: the report is a claim. In direct
mode it is the same reason one step removed — you wrote the code, and the person who wrote the code
is the worst judge of whether it does what the plan says. The checks below are mechanical on
purpose, so that they get done the same way for task #1 and task #9.

## Checks, in order

### 0. Skills loaded

Sub-agent mode: the report's "Skills loaded" section names every skill mapped to the task, each as
loaded before the first edit. Direct mode: your own record from Phase 5.2. A mapped skill missing,
failed, or loaded after the code was written invalidates the attempt — the tests may be green, but
the code was written under the wrong rules, and nothing in checks 1–6 can detect that. Go to
*Failure handling*; do not tick anything.

### 1. Build and full test run

Run the build command and the full test command from Codebase Findings yourself. Capture the
output. Red build or any failing test → the task is not done, regardless of what the report says;
go to *Failure handling*. Do not run only the task's new tests: a task that passes alone and breaks
an existing test has changed behaviour somewhere.

### 2. Planned tests, found by ID

For every line of the Verifies block: a test carrying that ID exists in the planned file and appears
in the passing set of the run you just made. Search by the ID (`AC-3`, `AC3`), not by the full
planned name — the implementer may have adapted the name to the convention.

- Planned name present, passing → ✓.
- Different name, same ID, passing → ✓ plus one Change Log row per task listing every rename
  (`it('AC-2: returns header only') → it('AC-2: returns only the header row for a customer without
  orders')`) with the reason; the matrix still shows the old name and the reader must be able to
  follow it.
- Test present in another file → deviation (technical if the file follows the project layout;
  ask if it does not).
- No test with the ID in its name → the ID is unverified, even if a test with a similar purpose
  exists. Not done: either the name is fixed or the ID is genuinely untested.
- A test present that verifies no ID and is not an obvious helper → note it; the review will ask
  what it proves.

### 3. Files against `Files`

`git status --porcelain`, minus files already accounted for by earlier tasks and minus files that
were uncommitted before the run (`D-2` — they are reviewed in Phase 6, not judged here). Compare
with the task's *Files*.

- Planned file untouched → check whether the Todo that needed it is unticked; if the task is
  "done", something was skipped.
- Unplanned file changed → deviation; the reason must be in the report (or in your own notes in
  direct mode). A generated file (lockfile, snapshot) with a mechanical cause is technical. A
  source file in another feature is a question.

### 4. Tests against spec text

Read each new test next to the spec text of the ID it verifies. Ask one question per test: *if this
criterion were violated in the way the spec describes, would this test fail?* A test that asserts
a 200 where the spec asks for a header and one row per order proves less than its name. A test that
asserts something the spec does not say proves something else. Either is a functional gap →
Phase 5.4 question. This is the slow check and the one that keeps the matrix honest; do not skip
it for "obvious" tests.

### 5. Provides as implemented

Extract the exact signatures (name, parameters, types, return, file:line) of everything the task
*Provides*, from the code. This becomes the "What already exists" section of the next brief and,
where it differs from the plan, a Change Log row. The plan's version is never passed on once the
code exists.

### 6. Done when

Read the task's *Done when* and check each clause literally (build green, full run green, README
updated, migration applied). A clause that is not met is not done.

## Judging deviations (Phase 5.4)

| Kind | Examples | Action |
|---|---|---|
| **Technical** | test name adjusted to the framework; signature reordered or typed more precisely with the same meaning; one planned file split into two in the same directory; a private helper added; a lockfile regenerated | Accept. One Change Log row per deviation. |
| **Functional** | an acceptance criterion not tested or tested weaker; a status code, field, or rule differs from the spec; behaviour added that no ID asks for; an error path silently handled instead of surfaced as specified | Do not accept. Ask the user: **revert and redo as planned** (Recommended — the plan is the contract) / **fix the documents** — the user changes spec/plan and you re-run Phase 0–1 / **accept as a plan change** — recorded `D-n`, origin `user's own`, Change Log row citing the `D-n`. |
| **Ambiguity** | the spec allows two readings and the test picked one; the plan's Goal and the spec disagree and nobody noticed in Phase 1 | Same question as functional; the recommended option is whichever reading the Clarification Log supports, if it does. |

Change Log row format (append to the plan's table; never edit existing rows):

```
| 2026-09-05 | #3 | Test it('AC-2: returns header only…') → it('AC-2: returns header row only for customer without orders') | vitest reporter truncates names with "…"; outcome kept | implement-dev-plan |
| 2026-09-05 | #2 | CsvFormatter.format(orders) → CsvFormatter.format(orders, options?) | delimiter option needed by #3 (C-4) | implement-dev-plan |
```

A row that cites a user decision carries it in the Reason column (`… per D-7`).

## Plan updates (Phase 5.5)

Only after checks 0–6 pass or every failure has a recorded decision:

1. Tick the Todos that are verified. A Todo whose result you could not verify stays unticked with
   a one-line note appended in the plan's Todo line — not a new Todo, not a rewrite.
2. Set the task's `Status`: `done`, `partial — <what is open>`, or `blocked — <reason>`.
3. Append the Change Log rows.

Nothing else in the plan changes. If you find yourself wanting to edit a Goal, a Verifies line, or
the matrix, that is a plan change: it goes to the user, and the fix is theirs, with
`create-dev-plan`.

## Progress message (Phase 5.6)

One block per task, in the plan's language, nothing more:

```
Task #3 — Export endpoint: done
  Skills loaded: <names>, before first edit
  Tests: 4/4 planned green (AC-1, AC-2, AC-3, IF-1); full suite 41 passed
  Files: src/orders/orders.router.ts, test/orders/orders.export.test.ts, README.md
  Deviations: 1 technical → Change Log (test name AC-2)
  Open: none
```

## Failure handling

| Situation | Action |
|---|---|
| Report lists a mapped skill as not loaded, missing, or loaded after coding began | Invalid attempt regardless of test results. One retry whose brief quotes the Skills section verbatim and the rule that they are binding; the code of the first attempt may stay only if the retry re-reads it against every skill and reports what it changed. |
| Sub-agent reports *blocked* | Read the reason. A missing skill or a wrong path in your brief → fix the brief, one retry. A spec/plan problem → it is a Phase 5.4 question, not a retry. |
| Report says *done*, verification fails (red tests, missing names, file mismatch) | One retry with the retry brief (`references/subagent-brief.md`), quoting exactly what failed. |
| Retry fails too | Stop this task. Ask: **take the task over directly (Recommended)** — you implement it in this context with the same skills and the same verification; **skip and mark `Status: blocked — <reason>`**, continue with tasks that do not depend on it, and list it in the report; **abort the run**. |
| Direct mode, your own implementation fails verification | Fix it — you have the context. If the fix needs a functional deviation, Phase 5.4. Two failed attempts at the same check → tell the user what is wrong before trying a third time. |
| Full suite fails on a test from an earlier task after a later task | The later task changed shared behaviour. Treat as that task's verification failure; the retry brief names the broken test. |
| Parallel group: individual runs green, combined run red | Find which pair conflicts (revert one task's files in a scratch copy, or read the failing test). The conflicting task gets a retry brief that names the other task's files as fixed. Do not resolve by editing both. |

Never a third blind attempt. Two failures mean the brief, the plan, or the spec is wrong, and
attempts do not fix documents.
