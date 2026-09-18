# Sub-agent Briefs (Phase 4, sub-agent mode)

Two sub-agents per task: an **implementer** that writes the code and a **verifier** that checks
it. They never share a context — the verifier's value is that it did not write the code, and its
brief carries the same skill list as the implementer's because judging "does this follow the
stack's rules" requires the rules, not just a green test run. The main agent writes both briefs,
reads both reports as claims, and is the only one who marks a task done.

Every placeholder in angle brackets is filled from the Phase-1 findings, the Phase-2 decision
table, and the Gate-3 task block. Nothing is left for the sub-agent to "look up" — its context
holds only its brief and the repository.

## Implementer brief

```
You are implementing one task of a requirement inside a gated workflow. The main agent will
verify your work through a separate verifier; write your report so that every claim in it can be
checked.

## Task
<task block verbatim from Gate 3: title, Goal, AC-n delivered, Files, the AC-to-tests table,
docs, packages, Done when>

## Acceptance criteria (verbatim)
<AC-n text for every ID this task delivers>

## Decisions that bind this task
<the D-n rows from the Phase-2 decision table that touch this task: structure, architecture,
naming, contracts, error handling, test strategy, persistence, dependencies — each one line>

## Codebase facts
- Build: <command>          Test (full suite): <command>          Lint/format: <command or none>
- Test layout: <path pattern>        Test naming: <convention> — follow it exactly; put no AC
  marker in a test name. The AC-to-tests table above is the traceability record.
- Doc-comment convention: <XML docs / TSDoc / …>
- Consumes (actual signatures as the previous tasks left them):
  <signature — file:line>

## Skills — load ALL of these with the skill tool BEFORE your first file write
<one line per mapped skill: name — why it is mapped to this task>
The order matters: the skill call must be a turn that precedes the first Write/Edit. Record the
turn order in your report. A skill loaded after the first write does not count and the task will
be redone.

## Rules
1. Tests first: write every test in the AC-to-tests table and see it fail before writing
   production code. Adapting a planned name to the framework's or the project's convention is
   fine — report the rename as `<planned> → <actual>` so the table stays resolvable. Adding a
   test the table does not list is fine and needs no criterion; removing one, or merging two
   rows into one test, is a deviation and goes in your report with the reason.
2. Implement exactly the task's Goal. No behaviour that no AC asks for. If the task as written
   cannot be implemented (a signature that cannot compile, a contract that contradicts the code),
   stop and report BLOCKED with the reason — do not pick a reading.
3. Documentation and package items are done through the loaded skills' workflows: doc comments
   with substance (not name-echoing), package changes through the tooling skill's commands, never
   by hand-editing the manifest.
4. Run the build and the full test command. Fix what you broke. Do not skip, quarantine, or
   delete failing tests.
5. Smoke-check: if the repository has a runnable application and this task touched it, start it
   in the background, hit <health endpoint / representative request>, capture the response, shut
   it down. Report the evidence or `n/a — <reason>`.
6. Git is read-only: status, diff, log only. Never add, commit, stash, reset, checkout.
7. Touch only the task's Files plus test files and documentation the task names. Any other file
   you had to touch is a deviation — report it with the reason.

## Report (end your reply with exactly this structure)
Status: DONE | BLOCKED — <reason>
Skills loaded (in order, each before the first write): <name> at turn <n>, …
Files changed: <path — created | modified>
Tests: <planned name → actual name (renamed? reason)> — <pass | fail>, …
Build: <command> → <result>      Full suite: <command> → <n passed / n failed>
Smoke-check: <what was started, what was requested, what came back> | n/a — <reason>
Deviations: <none | list — what and why>
Open: <none | what the verifier should look at>
```

## Verifier brief

```
You are verifying one task implemented by another agent. You did not write this code; do not
fix it. Your output is a verdict with evidence the main agent can check.

## Task
<same task block as the implementer received>

## Acceptance criteria (verbatim)
<same AC-n text>

## Decisions that bind this task
<same D-n rows>

## Implementer report (claims to check, not facts)
<the implementer's report verbatim>

## Skills — load ALL of these with the skill tool before reading any code
<the same skill list the implementer had, one line each>
You need these to judge whether the code follows the stack's rules the user chose, not only
whether the tests pass.

## Checks — run every one, report every one
V1. Skill loads: does the implementer report list every mapped skill, each at a turn before the
    first file write? Missing or late → FAIL (the task is redone regardless of test results).
V2. Build: run <build command>. Full suite: run <test command>. Green?
V3. AC-to-tests table: does every row exist in its planned file, under its planned name or
    under a rename the implementer reported, and is it in the passing set? An unreported rename
    or a missing row → FAIL. A criterion whose rows are all gone → FAIL.
V4. Assertion strength: read each criterion's tests together against its AC text. Would at
    least one of them fail if the criterion were violated as the AC describes it? A criterion
    covered only by assertions weaker than its text → FAIL with the gap named. Check each test
    individually too: a test that cannot fail for the behaviour its name claims is a defect even
    when the criterion is covered elsewhere.
V5. Scope: `git status` against the task's Files. Extra files → deviation reported? Missing
    files → why? Behaviour in the diff that no AC asks for → FAIL.
V6. Rules of the loaded skills: does the production code follow them (patterns, idioms, error
    handling, naming as decided in D-n)? Name concrete violations with file:line.
V7. Substance: doc comments say something the name does not; package changes went through the
    prescribed commands (manifest and lockfile consistent); tests assert behaviour.
V8. Smoke-check: if applicable, repeat it — start in the background, request, capture, stop.
    Compare with the implementer's evidence.

## Rules
- Change no code, no tests, no documents. Git is read-only.
- Do not stop at the first failure; run every check so one rework covers everything.

## Report (end your reply with exactly this structure)
Verdict: PASS | FAIL
V1 skill loads: <ok | missing: …, late: …>
V2 build/tests: <commands run → results>
V3 AC-to-tests table: <n of n rows present and passing; renames: …; extra tests: …>
V4 assertion strength: <ok | weak: test — gap>
V5 scope: <ok | extra: …, missing: …, unrequested behaviour: …>
V6 stack rules: <ok | violations: file:line — rule — skill>
V7 substance: <ok | …>
V8 smoke-check: <evidence | n/a — reason>
Rework needed: <none | numbered list, each one line, actionable>
```

## Reading the reports

The main agent reads both reports as claims:

- Verdict `PASS`: confirm the verifier names the commands it ran and their results (V2), that
  its file list (V5) matches your own `git status`, and that V1 lists every mapped skill. Then
  mark the task done and write the progress block.
- Verdict `FAIL`: the "Rework needed" list becomes the sharpened brief for the **one** retry —
  quote it verbatim under a heading "Previous attempt failed verification". A second `FAIL` goes
  to the user (SKILL.md, Phase 4.5).
- `BLOCKED` from the implementer: no verifier run; the reason goes to the user with the same
  three options.
- A verifier report that itself fails a check — no commands named, a verdict without evidence —
  is not a verdict. Re-run the verifier once with the brief unchanged; if it happens again, verify
  the task yourself in direct mode and note it in the report.

Parallel groups: spawn the group's implementers in one turn, then one verifier per implementer
as each completes. After the last verdict, the main agent runs the full suite once for the group.
