---
name: refactor
description: >
  Use when the user wants existing code improved in structure without changing what it does:
  "refactor <file/class/module>", "clean this up", "reduce the duplication here", "get rid of the
  dead code in …", "pay down technical debt in …", "diesen Code refactoren", "aufräumen",
  "Refactoring für …", or when code smells — long functions, duplication, deep nesting, primitive
  obsession, dead code — should be found and removed inside a defined scope. Analyses the scope
  with file:line evidence, writes a prioritised report to docs/refactoring/, lets the user choose
  what gets touched, proves test coverage per candidate, then applies one named refactoring at a
  time, verifying build, tests, and linter after each step and rolling back on red. Needs a scope
  and asks for one if none was given. Never changes behaviour, never fixes bugs, adds features,
  tunes performance, or reformats along the way, and never commits. Not for a generic "review my
  code", not for building new functionality, not for finding the cause of a bug.
---

# refactor

Improve the internal structure of existing code without changing what it does — in steps small
enough that each one can be proven safe, with the user deciding what gets touched.

## Contract

- **Input:** a scope (path, file, symbol, open changes, branch, or repository) plus, optionally,
  what bothers the user about it.
- **Output:** one Markdown report at `docs/refactoring/YYYY-MM-DD-<slug>.md` that grows through the
  run, plus uncommitted changes in the working tree.
- **Not in scope:** bug fixes, new behaviour, performance tuning, dependency upgrades, repository-wide
  formatting. Each of those changes behaviour or the diff in ways this workflow cannot verify.
- **Never commits.** The user reviews the diff and decides what enters history. Offer commit points;
  do not take them.

## The one rule everything else serves

**Behaviour must not change.** This is not purity for its own sake — it is what makes verification
possible. The whole safety net of this workflow is "the tests were green before and they are green
after". The moment a step also fixes a bug, tightens validation, or renames a public method, a red
test becomes ambiguous: regression, or the intended new behaviour? Nobody can tell, and the net is
gone.

So: a condition that is obviously inverted stays inverted. A missing null check stays missing. Both
get written into the report's *Found, not fixed* section with `file:line` and a one-line rationale,
mentioned once in the conversation, and left for the user to decide on afterwards — a real bug
deserves its own diagnosis, not a silent ride in a refactoring diff.

## Principles

1. **Evidence, not impression.** Every claim in the report carries `file:line`. "Duplicated" means
   both sites quoted. "Dead" means the reference search was run — including reflection, dependency
   injection, configuration, and string-based lookups, which is where this claim usually goes wrong.
   "Untested" means the evidence from Phase 4, not a guess.
2. **One named refactoring per step.** A step is a single refactoring from
   `references/refactoring-catalog.md`, applied at one site, verified immediately. "Three extract
   functions and a rename" is four steps. Small steps are not a style preference: when a batch turns
   red you have no idea which part did it, and the rollback throws away the good parts too.
3. **The user owns architecture, logic, and quality.** Local work inside a file runs through the
   normal plan gate. Anything that crosses file boundaries, touches a public API, or moves
   responsibility between layers is an architecture decision: mark it as such, present the
   alternatives, and let the user choose. Never decide it yourself because it "obviously" belongs
   elsewhere.

   The one exception is a request that cannot be fulfilled at all without such a decision — a
   duplication spanning two modules cannot be removed without choosing where the shared code lives —
   and nobody is reachable to make it. Then take the most conservative option that satisfies the
   request, record it as a decision with the alternatives you rejected and why, mark the step
   `structural` in the step log, and put *confirm or correct D-n* at the head of the report's open
   items. Deciding in the open and under protest is honest; deciding silently is not, and refusing
   outright would deliver nothing the user asked for. Structural work the request does **not**
   require is still skipped.
4. **Tests are the instrument, not the material.** You do not change tests to make a refactoring
   pass. If a test has to change in substance, the behaviour changed and the step was not a
   refactoring — roll it back. Mechanical adjustments to a renamed internal symbol are allowed and
   must be listed in the report, so a reviewer can check them.

## Decision ledger

Every decision the user makes, and every default you fall back to when nobody can answer, gets an
ID `D-1`, `D-2`, … the moment it is made. Record what was decided, by whom (user / default), and
why. The report's *Decisions* section is this ledger. It is what lets someone reading the report six
months later understand why a promising candidate was skipped.

## Workflow

```
Phase 0: Scope and preconditions
    ↓
Phase 1: Analysis (sub-agents for larger scopes)
    ↓
Phase 2: Report and prioritisation  →  docs/refactoring/<date>-<slug>.md
    ↓
Phase 3: Selection by the user
    ↓
Phase 4: Coverage gate (per candidate)  ──┐
    ↓                                      │ next candidate
Phase 5: Step loop ─ plan → approval →     │
         snapshot → change → verify  ──────┘
    ↓
Phase 6: Closing summary
```

### Phase 0 — Scope and preconditions

**Establish the scope.** Without one this workflow cannot be planned, verified, or reported, and
"refactor my code" is not a scope. If the user gave none, ask — and do not start until you have an
answer. Accepted forms, and what each resolves to:

| The user says | Resolve to |
|---|---|
| a directory | tracked source files below it |
| one or more files | those files |
| a class, function, or module name | the defining file(s), located by search |
| "my open changes", "what I changed" | `git diff --name-only HEAD` |
| "this branch", "everything since main" | `git diff --name-only <default-branch>...HEAD` |
| "the whole repository" | all tracked source files |

Always remove from the resolved list: generated code, database migrations, vendored or third-party
directories, build output, lock files, minified bundles, and test snapshots. Refactoring generated
code is undone by the next generator run, and reformatting a lock file is noise. Name what you
dropped and why — a user who meant to include something can put it back.

**Cap the scope.** Above roughly 40 files, an analysis produces a report nobody reads and a
candidate list nobody can choose from. Say how many files the scope resolved to and offer to narrow
it — the change hotspots from Phase 1 make a good first slice. Proceed with a large scope only if
the user insists, and record it as a decision.

**Two hard gates, both before any analysis:**

1. **Clean working tree.** `git status --porcelain` must be empty. Otherwise stop and list what is
   there. A dirty tree makes the refactoring diff inseparable from the user's own work, so neither
   the review nor the report can tell them apart — and the Phase 5 snapshot would capture their
   changes along with yours.
2. **Green baseline.** Find how this project runs its tests (CI configuration, `package.json`
   scripts, `Makefile`, project files, README), run the suite yourself, and record command, result
   counts, and duration. Red tests stop the run: name them and explain that with a red baseline, a
   red test after a step proves nothing. *A project with no test suite at all is not a stop* —
   record it as a decision and carry it into Phase 4, where the coverage gate offers the ways
   forward.

Also note whether a coverage tool is configured; Phase 4 needs to know.

### Phase 1 — Analysis

Work through the scope piece by piece against `references/smell-catalog.md`. A finding needs three
things or it does not become a finding: a smell name from the catalogue, a `file:line`, and the
evidence that makes it more than an impression.

**Delegate the reading, keep the judgement.** Above roughly 8 files, or when the scope spans several
modules, split it into coherent groups and give each to a sub-agent with this brief:

> Analyse these files for the smells in `<skill-path>/references/smell-catalog.md`. For each
> finding report: smell name, `file:line`, a quote of the relevant lines, and why it qualifies.
> Report only what you can point at. Do not change any file. Do not judge priority — that is
> decided centrally with information you do not have.

Sub-agent findings are claims. Before one enters the report, check the single thing that would make
it wrong: read both sites of a claimed duplication yourself; run the reference search for claimed
dead code yourself. A wrong finding in the report costs the user more trust than a missing one.

**Findings that reach outside the scope.** Duplication especially tends to have its counterpart
somewhere else in the repository. Report it — a duplication cannot be understood from one site — and
name where the other site is, but treat the scope as binding: it is not touched without the user
widening the scope, and the candidate is marked as needing that. Quietly widening the scope yourself
is how a reviewable refactoring becomes a diff nobody asked for.

**Change hotspots.** Code that is edited often is where structural improvement pays back fastest, so
it feeds the priority. Count changes per file over the last 12–18 months:

```bash
git log --since="18 months ago" --format="" --name-only -- <scope paths> | sort | uniq -c | sort -rn
```

Use it only if the history supports it — with fewer than ~30 commits in the window, or after a
recent large move or rename that resets every path, the counts mislead. Say in the report whether
the factor was used and why.

Use the runtime's stack-specific skills for the analysis where they exist — see
`references/skill-selection.md`.

### Phase 2 — Report and prioritisation

Write `docs/refactoring/YYYY-MM-DD-<slug>.md`, with `<slug>` from the scope (`orders-module`,
`payment-service`). Never overwrite an existing file — append `-2`, `-3` instead. The template is
`references/report-template.md`. Write it in the language the user is writing in, unless they ask
for another one.

The report is not a snapshot of the analysis; it is the run's record and grows through Phases 3–6.
Everything a reader needs must be in it, because the conversation it was written in will be gone.

Rank candidates on three axes, each `high` / `medium` / `low`, each with its reason in the table:

- **Benefit** — severity of the smell × change frequency of the file × how far the code reaches
  (how many callers, how central).
- **Risk** — test coverage at the site, number of references, whether a public API or a layer
  boundary is involved. Structural candidates are never low risk.
- **Effort** — how many steps, and whether other candidates have to move first.

Sort by benefit against risk, not by benefit alone: a high-benefit candidate on untested,
widely-referenced code is a worse first step than a medium-benefit one under a green test.

**Candidates dissolve into each other.** Extracting a function removes most of the long function that
contained it; guard clauses remove the nesting that made it long. Where one candidate largely
disappears once another is done, say so in its row and rank it as *re-assess after R-n* instead of
giving it a benefit of its own. Counting the same improvement twice makes the list look longer than
the work is, and the user chooses against inflated numbers.

**The coverage column is provisional.** It is there so the user can choose informed — it is not the
Phase 4 gate, because at this point nobody knows yet which lines a step will actually touch. Say so
in the report, and gather the real evidence per candidate when its turn comes.

### Phase 3 — Selection

Present the ranked candidates and let the user pick. With the structured question tool, offer them
in multi-select groups of at most four, labelled by ID and smell, and recommend a starting set —
the highest-benefit candidates that already have coverage and carry low risk. Mark structural
candidates clearly; picking one is picking an architecture change.

Nothing is refactored that the user did not select. Record the selection as a decision and set each
candidate's status in the report to `selected` or `not selected`.

### Phase 4 — Coverage gate

Per candidate, immediately before its first step, establish what actually tests this code. The
method and what counts as evidence are in `references/coverage-assessment.md`; in short: use the
project's coverage tool if there is one, otherwise map tests to the affected symbols and declare in
the report that this is a mapping, not a measurement.

If the site is covered, go to Phase 5. If it is not — including the case of a project with no test
suite at all — put the choice to the user with these four options, and record the answer:

| Option | What it means |
|---|---|
| **Write tests first** | Proper tests for the intended behaviour, then refactor. The clean path when the behaviour is understood and specified. |
| **Characterization tests first** | Pin down what the code *currently* does, bugs included, without judging it. The standard way into legacy code where nobody can say what the behaviour should be — and the reason those tests must not be "corrected" while writing them. |
| **Proceed without tests** | Only on the user's explicit say-so. The report records the candidate as unverified refactoring, and the closing summary repeats it. Verification is reduced to build and linter, which cannot detect a behaviour change. |
| **Skip this candidate** | Leave it in the report as `not started — no coverage` and move to the next. |

Writing tests is itself a task for the stack's tester skill if the runtime has one
(`references/skill-selection.md`). Tests written here are a separate, verified unit of work: they
must be green against the *unchanged* code before any refactoring starts — a test that only passes
after the change proves nothing about the change.

### Phase 5 — Step loop

Per step, in this order. `references/step-protocol.md` has the exact commands for the snapshot,
verification, and rollback.

1. **Plan the step and get approval.** One named refactoring, one site. Tell the user: which
   refactoring from the catalogue, at which `file:line`, what the code looks like afterwards, which
   tests prove it, and what the step does *not* touch. Keep it to a short paragraph plus the target
   shape — this is a decision aid, not a document. Wait for approval; adjust and re-present on
   objection.
2. **Take a snapshot** so the step is reversible without losing earlier approved steps.
3. **Make the change** — exactly what was approved, nothing carried along. No opportunistic renames,
   no formatting the rest of the file, no repository-wide formatter run: they bury the actual change
   in a diff nobody can review.
4. **Verify.** Build, then the test suite, then the linter on the changed files only. All three must
   be green. If the project has no build or no linter, say so in the report rather than skipping it
   silently.
5. **On red, roll back.** Restore the snapshot immediately. Do not repair on top of a red state —
   repairing widens a change you no longer understand. Then read what the failure is telling you,
   because red means one of two different things:

   - **The step was bigger or less local than it looked.** Propose a smaller step and try once more.
     After a second failure, stop this candidate, mark it `blocked` with the reason, move on.
   - **The test proves the change would alter behaviour.** Then the candidate is not refactorable
     this way at all, and a smaller step is waste — the obstacle is not size. Mark it `blocked`
     immediately, and put the question the failure actually raised to the user: the code they want
     gone is load-bearing, and deciding whether the behaviour behind it should stay is theirs, not
     a thing to retry around.

   Telling the two apart is usually easy: a failure about a value, an order, or an aggregate that
   the test pins deliberately is the second kind. Say which kind you concluded and why, so the user
   can disagree.
6. **On green, record it** in the report: refactoring, site, actual diff summary, verification
   result, any mechanical test adjustments. Then tell the user this is a clean commit point — and
   leave the commit to them.

### Phase 6 — Closing summary

Complete the report: status per candidate, everything found but not fixed, all decisions, the
verification results, and what is left open. Then, in the conversation, give a short summary: what
changed, what is verified and how, what was deliberately left alone, the suggested commit points,
and the reminder that nothing is committed.

Clean up your own leftovers — snapshots, temporary files — and say what remains in the working tree.

## Interactive vs. non-interactive

This workflow has four points where it asks: scope, selection, coverage decision, step approval.

**An answer given in advance is an answer.** A prompt that names the scope has answered the first
question; one that says "you have my approval for all steps" has answered the fourth. Use them, and
record each as a decision with origin *user, in advance*. Two things a blanket approval does not
cover. The **coverage gate**: "proceed without tests" accepts a specific risk on a specific
candidate, which a general go-ahead cannot imply — without an explicit answer there, an uncovered
candidate is skipped and recorded as `not started — no coverage, no risk decision available`. And
the **design of a structural change**: a go-ahead for the steps is not a go-ahead for a particular
architecture; see Principle 3 for the single case where it is decided anyway, in the open.

Where nobody can answer and nothing was given in advance, never stall and never guess. Fall back to
these defaults and record each one as a decision with its origin:

| Point | Non-interactive behaviour |
|---|---|
| No scope | Stop. Report that a scope is required and which forms are accepted. Guessing one produces a report about the wrong code. |
| No selection | Deliver analysis and report, change nothing. The report's status is `analysis only — no approval available`. |
| Coverage gate | Not reached; nothing is refactored without a selection. |
| Step approval | Not reached, same reason. |

The rule behind all four: without a human, this skill analyses and reports. It does not change code.

## Red flags — stop and re-check

- You are about to change a test so a refactoring passes. That is a behaviour change wearing a
  refactoring's clothes.
- The diff of a step is larger than the plan described, or touches a file the plan did not name.
- You are "quickly fixing" a bug you found. Write it into *Found, not fixed* instead.
- A step's verification was skipped "because the change is trivial". Trivial changes are exactly
  where the batching mistake happens.
- The report claims something you did not look at yourself — a coverage number nobody ran, a dead
  symbol nobody searched for.
- You are refactoring towards a design the user never approved. Structural work needs its own yes.
- Nothing has been red for many steps in a row and the steps are getting bigger. Recheck the size.

## References

| File | Read it when |
|---|---|
| `references/smell-catalog.md` | Phase 1 — what counts as a finding and what evidence each smell needs |
| `references/refactoring-catalog.md` | Phase 5 — the named refactorings, their preconditions and verification |
| `references/coverage-assessment.md` | Phase 4 — establishing and evidencing coverage |
| `references/step-protocol.md` | Phase 5 — snapshot, verification, and rollback commands |
| `references/skill-selection.md` | Phases 1, 4, 5 — finding the runtime's stack-specific skills |
| `references/report-template.md` | Phase 2 — the report structure, carried through to Phase 6 |
