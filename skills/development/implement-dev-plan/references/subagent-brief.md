# Task Sub-Agent Brief (Phase 5, sub-agent mode)

A sub-agent starts with an empty context. Everything it knows about the plan, the spec, the
codebase conventions, and the rules of this workflow is what the brief tells it. A thin brief
produces code that is locally reasonable and globally wrong — the right feature with the wrong test
names, the planned signature ignored because the sub-agent never saw the consumer. The brief below
is long on purpose; every section answers a question the sub-agent would otherwise guess.

Give the sub-agent **paths and excerpts both**: the paths so it can read further when it needs to,
the excerpts so it does not have to read a 400-line plan to find its task. Fill every placeholder;
`none` where empty.

## Template

```
You are implementing exactly one task of an approved development plan. The plan and the spec
are the contract; your job is to fulfil this task as written, report precisely what you did, and
flag — not fix — anything that does not fit.

## Documents
- Plan: <docs/plans/<slug>.md>  (read-only for you)
- Spec: <docs/specs/<slug>.md or "none — plan-only run, see Clarification Log">  (read-only)
- Project conventions: <CLAUDE.md / AGENTS.md path if present, else none>

## Your task (verbatim from the plan)
<the complete task block: Goal, Depends on, Parallel with, Status, Consumes, Provides, Files,
Verifies, Todos, Done when>

## What already exists — actual, not planned
The interfaces you Consume, as they are in the code right now (earlier tasks may have deviated
from the plan; these signatures win over the plan's):
- <name — signature — file:line>
- …

## Spec text for the IDs you verify
<for each ID in the Verifies block: the ID and its full text from the spec, or from the plan's
Clarification Log / Spec Feedback in a plan-only run>

## Global Constraints (apply to every task)
<the plan's Global Constraints table, verbatim>

## Codebase Findings you need
- Build command: <…>
- Test command: <…>          (full suite; run it before you finish)
- Test framework and naming convention: <…, with the plan's real example>
- Test file layout: <…>
- Closest existing feature to use as a template: <files>
- Mock boundaries: <…>
- Other conventions for your files: <…>

## Skills — MANDATORY, load every one before writing any code
<one line per skill: name — why it is mapped to this task>

These skills are binding. Invoke every one of them with the runtime's skill tool before you read or
write a single line of code, and follow what they say over your own habits. You do not get to
decide that you know the stack well enough to skip one — the user selected these skills so that
the code follows their team's rules, and the main agent rejects your result if the "Skills loaded"
section of your report does not list all of them as loaded, no matter how green the tests are.
If a skill fails to load, stop and report it under "Blocked" — do not continue without it.

## Rules
1. Todos in order: the Verifies tests first, and see them fail; then the implementation; then
   documentation. Use the planned test names unless the framework or the project convention
   calls for a different form — then adapt, but keep the requirement ID in the name
   (`it('AC-3: …')`, `Export_AC3_…`) and list every rename in your report; the main agent logs it. Do not tick Todos in the plan — the main agent does
   that after verifying.
2. Stay inside your Files. Touching another file is a deviation you must report with a reason.
3. Deviate from the plan only for a technical reason you can state in one sentence (the planned
   signature cannot compile as written; the framework rejects the test name). A deviation must
   not change what any spec ID means: no dropped criterion, no extra behaviour, no "while I'm
   here". If the plan and the spec seem to require something you cannot do without changing
   behaviour, stop, leave the code compiling and the tests as they are, and report it under
   "Blocked" — the decision is the user's, not yours.
4. Run the full test suite before you finish. Report the exact command and its result. Existing
   tests you did not plan to touch must stay green.
5. Git is read-only: git status / diff / log only. No add, commit, stash, checkout, reset. The
   user commits.
6. Do not edit the plan, the spec, or any document outside your Files.
7. Skills first (see above). Loading them after the code is written does not count; the report
   states the order in which you loaded them relative to your first edit.

## Report — use exactly this structure
### Result
one of: done | done with deviations | blocked

### Skills loaded
- <name> — loaded before first edit (or: failed to load — <error>)
All mapped skills listed here? yes | no — <which is missing and why>

### Tests
| Verifies ID | Planned test name | Actual test name (if different) | File | Written | Result |
|---|---|---|---|---|---|
Full run: `<command>` → <n passed, m failed, skipped>

### Files changed
<git status --porcelain output for your changes>

### Provides — as implemented
- <name — exact signature — file:line>

### Deviations from the plan
| # | What the plan says | What I did | Why | Changes behaviour? (yes/no) |
|---|---|---|---|---|
(none — if none)

### Todos
- [x] / [ ] per Todo, in plan order, with one line where unticked

### Blocked / open
<what stopped you, exact error output, what you tried — or none>
```

## What the main agent does with the report

The report is a set of claims. Phase 5.3 (`references/verification.md`) checks them: the test run
is repeated, names are grepped, `git status` is compared to *Files*, and the *Provides — as
implemented* section becomes the "What already exists" section of the next task's brief. A report
that says *done* and fails verification is treated as a failed attempt (one retry with the failure
quoted, then the user).

## Retry brief

The retry is the same brief plus one section at the top:

```
## Previous attempt — read first
The previous attempt reported <result>. Verification found:
<exact test output / the mismatch: "planned it('AC-2: …') not found in test/orders/…" /
"file src/x.ts changed but not in Files">
Fix these specifically. Do not start over unless the code is unusable; say which it was.
```

## Parallel groups

Sub-agents in a parallel group get identical Codebase Findings and Constraints sections and
*disjoint* Files. Add one line to Rule 2: "Other tasks are running now on <files>; do not touch
them even to fix an import — report the need instead." After the group, the main agent runs the
full suite once for the combination.
