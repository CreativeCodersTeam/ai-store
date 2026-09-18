# Review and Rework (Phase 5)

The review has two questions. The first is the one every code review asks: *is this good code for
this stack?* The reviewer skill installed for the stack answers it, and its process — checklists,
severity taxonomy, report format, report path — is its own to run. The second is specific to this
workflow: *is this the code the requirement asked for, and only that?* Every `AC-n` promised a
test; every task promised a *Done when*; every Phase-2 decision promised a shape. Part B checks
the promises.

The review is always run by a sub-agent, in both implementation modes — its value is that it did
not write the code. In sub-agent mode the reviewer is a third agent, not the verifier: the
verifier judged one task at a time against its brief; the reviewer sees the whole diff.

## Choosing the reviewer

1. **Review set from Gate 2** — the stack-specific reviewer skill(s) and review-capable agent
   types the user confirmed. Use them; the brief names each skill because reviewer skills require
   explicit invocation.
2. **Empty review set** — search the runtime's skill list and the agent-type list again, this time
   for *general* code-review skills and agents: descriptions that say code review, quality,
   security, or correctness without binding to a stack. Present them through the question tool
   (multi-select, one line of why per option, groups of up to four) with the last option **no
   review skill — generic brief with Critical / Major / Minor / Info**. Record as `D-n`. Do not
   silently pick one, and do not silently skip the review because nothing stack-specific exists.
3. **Nothing at all** — the generic brief below still runs, with the tester skill(s) from the
   implementation set loaded so test quality is judged by the stack's rules.

## Review sub-agent brief

```
You are reviewing the uncommitted changes of an implementation run that followed a clarified
requirement. You change no code and no document except the review report you write.

## Scope
- Branch: <branch>
- Changes under review: the whole uncommitted working tree (`git status`, `git diff`). Files that
  were already uncommitted before the run are in scope too (user decision D-1): <list or none>
- Review mode for the report name: uncommitted
- Round: <n>  (round 2+: re-check that these rework items are resolved: R-1 …, and focus Part A
  on the delta since <previous report path>)
- Report language: <language>

## Requirement (read-only)
- Requirement: <restated paragraph, or path / URL>
- Acceptance criteria: <AC-n list verbatim>
- Decision table: <D-n rows, one line each — structure, architecture, naming, contracts, errors,
  tests, persistence, dependencies, and Point-0 answers>
- Task list: <Gate-3 tasks with Files, Done when>
- AC-to-tests table: <every AC with the tests that prove it, file · name, renames applied — this
  is the traceability record; test names carry no AC marker, so do not search for one>
- Run note from the main agent: <scratch path — per task: skills loaded, verifier verdict,
  deviations, smoke-check evidence>

## Skills — load these before reading any code
<reviewer skill(s) — name each; they require explicit invocation>
<refactoring / quality skill(s)>
<tester skill(s) for the test framework>
Follow the reviewer skill's own steps, scripts, and report format. If it defines a severity
taxonomy, use it for every finding, Part B included. If it prescribes a report path, write there;
the main agent expects docs/reviews/YYYY-MM-DD-<branch>-uncommitted.md.
If it asks the user for parameters, use: mode = uncommitted; build / format / test tools = <no —
already green, or yes if the skill insists>; language = <language>. You have no user channel.

## Part A — Tech-stack review
Run the reviewer skill's process on the changes in scope. Include refactoring opportunities and
test-quality findings per the loaded skills.

## Part B — Requirement conformance (add as its own section to the report)
B1. Acceptance criteria, one line per AC — the relation is many-to-many, so a criterion may
    carry several tests and a test may appear under several criteria:
    | AC | Task | Tests (file · name, one per line) | All exist | All pass | Falsifiable? | Verdict |
    Take the tests from the AC-to-tests table handed to you; do not look for an ID in a name,
    there is none. "Falsifiable" asks the only question that matters: would at least one of this
    criterion's tests fail if the criterion were violated as the AC describes it? If every one of
    them would stay green, the criterion is unproven — a finding at the highest severity,
    whatever the pass count says. A criterion with no test at all is the same finding. A test
    that belongs to no criterion is **not** a finding: regression guards and pre-existing tests
    are expected. A single test that cannot fail for the behaviour its own name claims is a
    finding on its own merit (test quality), even where its criterion holds up elsewhere.

    **The verdict vocabulary is fixed, and "proven" is earned by execution.** Reading a test and
    reasoning about what would break it is a hypothesis, and a plausible one is exactly how a
    criterion ends up recorded as proven while its only test survives the deletion of the code
    it is supposed to cover. So:

    - `proven (executed: <what you broke> → <which test went red>)` — you changed the production
      path the criterion depends on, in a throw-away copy, ran the suite, saw a test of that
      criterion fail, and restored the copy. This is the only verdict that may be called proven.
    - `read-checked — not executed (<why>)` — you read the tests and they look sufficient, but
      nothing was run against a broken version. A legitimate verdict; it simply claims less.
    - `unproven` — the tests would stay green under the violation, or there are none.

    Executing is not required, and it is not rationed either: it is the cheapest way to turn a
    read-checked row into a proven one, and reviewers who do it routinely find what reading
    misses — a framework that re-clothes a bare error result so a status-code assertion passes
    anyway, a 404 the router produces whether or not the route exists. Mutate what you can afford
    to; label honestly what you did not.

    The two verdicts are never summed into one number. A report that says "6 of 6 proven" while
    any row is read-checked is wrong on its face, and so is one whose prose notes a test that
    would survive its own criterion's violation while the table still reads proven.
B2. Per task: Done when met? Files within the task's Files (plus reported deviations)? Docs and
    package items produced with substance?
B3. Decisions honoured: does the code follow the D-n decisions (naming, layering, error shape,
    persistence, dependencies)? A silent departure is a finding at the second-highest severity.
B4. Scope: behaviour in the diff that no AC asks for; ACs with no code path (a test that passes
    trivially). Both are findings at the highest severity.

## Output
- The report at the reviewer skill's path, with Part B as a section titled "Requirement
  Conformance".
- A summary block at the end of your reply:
  Report: <path>
  Findings: <n critical / n major / n minor / n info — in the taxonomy used>
  Top findings (all of the two highest severities, max 10): file · finding · proposed fix
  Requirement conformance: <n proven (executed) / n read-checked / n unproven, of n ACs and n
  tests across them; n decision departures; n scope findings>

## Rules
- Do not modify code, tests, or documents other than the report. Git is read-only.
- Do not run the reviewer skill's "auto-fix" or "apply suggestions" options if it has any.
```

**Generic report format** (no reviewer skill): header (date, branch, requirement, round), summary
counts, findings by severity (file:line, finding, why it matters, proposed fix), Requirement
Conformance section. Severities: Critical / Major / Minor / Info.

## Presenting at Gate 5

When the sub-agent returns, confirm the report file exists and read it in full — the summary block
is the reviewer's claim about its own report.

1. **Counts and path.** One line per severity, the report path, the round number.
2. **Rework plan** — every Critical and Major finding as a rework task `R-n`: finding · file ·
   fix · tests affected · skill checklist (Phase-3 mapping rules applied to the files it touches).
   These are not a question of *whether*; the question at the gate is whether the plan is right.
3. **≤ Minor findings** — each as *file · finding · proposed fix*, at most about ten lines; if
   more, the rest are "n further Minor / Info findings in the report".
4. **The question-tool call:** (a) confirm the rework plan — **proceed as proposed
   (Recommended)** / **change — I'll describe**; (b) multi-select which ≤ Minor findings to fix
   now, groups of up to four, last option **accept the rest as they are**. When there are no
   Critical / Major findings, (a) becomes **accept the review, go to the report** versus **fix
   selected Minor findings first**. Record as `D-n`.

Unselected ≤ Minor findings are *deferred*: they appear in the implementation report with the
user's decision, not silently dropped.

## Rework items

`R-n` items go through Phase 4 in the Gate-3 mode — with skill loads, verification (verifier
sub-agent in sub-agent mode), and the smoke-check when applicable. Group items that touch the same
files into one run; independent areas may be separate runs, parallel only if their files are
disjoint. Then Phase 5 again with the round number incremented and the previous report path in the
brief, then Gate 5 again.

Each round is recorded: findings presented, rework done, Minor selected, deferred. If a round
reproduces a finding from an earlier round, say so before the gate — repeating a fix that did not
hold is a sign the finding, the fix, or a Phase-2 decision is wrong, and the user should know
before choosing again.
