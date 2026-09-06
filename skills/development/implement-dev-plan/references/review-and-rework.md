# Review and Rework (Phases 6–7)

The review has two questions. The first is the one every code review asks: *is this good code for
this stack?* The reviewer skills installed for the stack answer it, and their process — checklists,
severity taxonomy, report format, report path — is theirs to run. The second question is specific
to this workflow and is what a generic review does not ask: *is this the code the plan promised?*
Every matrix row promised a test with a name; every task promised a Done-when; every deviation
promised a Change Log row. Part B checks the promises.

The review is always run by a sub-agent, in both implementation modes — its value is that it did
not write the code.

## Review sub-agent brief

```
You are reviewing the uncommitted changes of an implementation run that followed an approved
development plan. You change no code and no document except the review report you write.

## Scope
- Branch: <branch>
- Changes under review: the whole uncommitted working tree (`git status`, `git diff`). Files that
  were already uncommitted before the run are in scope too (user decision D-2): <list or none>
- Review mode for the report name: <uncommitted | branch — as the reviewer skill defines it>
- Round: <n>  (round 2+: also re-check that these rework items are resolved: R-1 …, and focus
  the tech-stack part on the delta since <previous report path>)

## Documents (read-only)
- Plan: <docs/plans/<slug>.md>
- Spec: <docs/specs/<slug>.md or none — plan-only run>
- Implementation notes from the main agent: <path to a scratch file with the Change Log rows
  added this run, the D-n decisions that affect code, and the per-task Provides as implemented>

## Skills — load these before reading any code
<reviewer skill(s) for the stack — name each; they require explicit invocation>
<refactoring / quality skill(s)>
<tester skill(s) for the test framework>
Follow the reviewer skill's own steps, scripts, and report format. If it defines a severity
taxonomy, use it for every finding in this review, Part B included. If it prescribes a report
path, write there; the main agent expects <docs/reviews/YYYY-MM-DD-<branch>-<mode>.md>.

## Part A — Tech-stack review
Run the reviewer skill's process on the changes in scope. Include refactoring opportunities and
test-quality findings per the loaded skills. Findings that touch files outside the plan's File
Structure are flagged as such.

## Part B — Plan conformance (add as its own section to the report)
B1. Traceability matrix, one line per row:
    | ID | Task | Planned test name | Actual test name | Change Log row? | Exists (file) | Passes | Asserts the ID's criterion | Verdict |
    Find the test by the ID in its name; the plan's name may have been adapted to the convention.
    "Asserts the criterion" means: read the test against the spec text of the ID; would the test
    fail if the criterion were violated as the spec describes it? Weaker or different → finding.
B2. Per task: Done-when met? Files within the plan's File Structure? Documentation Todos produced
    documentation? Status in the plan matches what you see?
B3. Change Log completeness: compare the plan's Verifies names and Provides signatures with the
    code. Every difference — every renamed test included — must have a Change Log row. A
    difference without a row is a finding (severity: the taxonomy's second-highest — it means the
    plan silently drifted).
B4. Scope: behaviour in the diff that no spec ID asks for; spec IDs in the matrix with no code
    path (a test that passes trivially). Both are findings at the highest severity.

## Output
- The report at the reviewer skill's path, with Part B as a section titled "Plan Conformance".
- A summary block at the end of your reply:
  Report: <path>
  Findings: <n critical / n major / n minor / n info — in the taxonomy used>
  Top findings (all of the two highest severities, max 10): file · finding · proposed fix
  Plan conformance: <n/n matrix rows verified; n Change Log gaps; n scope findings>

## Rules
- Do not modify code, tests, the plan, or the spec. Proposed fixes are text in the report.
- Git is read-only.
- Do not run the reviewer skill's "auto-fix" or "apply suggestions" options if it has any.
```

If the stack has no reviewer skill installed (Phase 2 found none), the brief still runs with the
refactoring and tester skills, uses *Critical / Major / Minor / Info*, and writes the report to
`docs/reviews/YYYY-MM-DD-<branch>-uncommitted.md` in the format: header (date, branch, plan, spec,
round), summary counts, findings by severity (file:line, finding, why it matters, proposed fix),
Plan Conformance section.

## After the review returns

1. Confirm the report file exists at the path given; if not, ask the sub-agent once (send a
   message) to write it — a review that lives only in a reply is lost after this session.
2. Read the report in full. Do not summarise from the sub-agent's summary block alone; the
   Part B table is where silent drift shows.

## Presenting findings (Phase 7.1)

In the plan's language, short:

```
Review round 1 — docs/reviews/2026-09-05-feature-order-export-uncommitted.md
  Findings: 1 critical · 3 major · 6 minor · 2 info
  Plan conformance: 11/12 matrix rows verified; 1 Change Log gap; 0 scope findings

Most important
  F-1  critical  src/orders/orders.router.ts:41 — customer ID from route param not compared with
       the authenticated customer; AC-3 test passes because it uses the same ID for both.
       Fix: compare req.params.id with req.customer.id in requireCustomer; strengthen AC-3 test.
  F-2  major     test/orders/orders.export.test.ts — it('AC-2: …') asserts status only, not
       header-only body. Fix: assert body equals header line.
  F-3  major     Plan Change Log — CsvFormatter.format gained an options parameter; no row.
  F-4  major     src/orders/csv.formatter.ts:18 — dates formatted with local timezone; NFR-3
       requires UTC. Fix: toISOString().
```

Minor and Info findings are not listed here; say how many there are and that they are in the
report.

## Asking (Phase 7.2)

Multi-select over the presented findings, the two highest severities pre-recommended in the
option text ("(Recommended)" on each of them); one question per group of up to four findings,
option label `F-n · severity · file`, description = the proposed fix. A final single-select
question: **Accept the changes as they are — write the report** versus **Fix the selected findings
first**. If nothing is selected and "fix" is chosen, ask once more with two options.

Every finding not selected is *deferred*: it goes into the report under *Open findings* with the
user's decision (`D-n`, origin `user's own`) — not dropped.

## Rework items (Phase 7.3)

Each selected finding becomes a rework item:

```
### R-1 — from F-1 (critical)
Finding: <verbatim from the report>
Files: <from the finding>
Fix: <the proposed fix, or the user's own if they gave one>
Tests affected: <planned test names to strengthen or add; new tests need a name in the project
convention and a Change Log row, since they were not in the plan>
Verifies: <the spec IDs concerned>
```

Rework runs through Phase 5 in the mode chosen in Phase 4. Sub-agent mode: one sub-agent for all
items that share files or a layer; independent items may go to separate sub-agents in one turn
(disjoint files rule applies). The brief is the task brief with the rework items in place of the
task block and an extra rule: *fix exactly these findings; do not refactor beyond them; report per
item*. Verification is the same as for a task (full run, names, files, spec text). New or renamed
tests get Change Log rows with `Reason: review F-n`.

Then Phase 6 again with `Round: n+1`, scoped to the delta and the `R-n` re-check, then Phase 7
again. The loop ends when the user accepts.

## Round record

Keep, for the report:

```
| Round | Report | Findings (c/M/m/i) | Selected | Deferred | Rework result |
|---|---|---|---|---|---|
| 1 | docs/reviews/…-uncommitted.md | 1/3/6/2 | F-1, F-2, F-4 | F-3 (D-12: "log it later") | R-1…3 done, 43 tests green |
| 2 | docs/reviews/…-uncommitted-r2.md | 0/0/4/1 | — | all (D-14: accepted) | — |
```

If the reviewer skill's naming would overwrite round 1's report, append `-r<n>` to the file name
and tell the sub-agent so in the brief — never overwrite a report.
