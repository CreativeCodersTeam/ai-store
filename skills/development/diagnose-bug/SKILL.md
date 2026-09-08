---
name: diagnose-bug
description: Use when asked to diagnose, investigate, debug, troubleshoot, or find the root cause of a bug, error, exception, crash, failing or flaky test, wrong output, regression, performance anomaly, or any unexpected behavior in a codebase — including "why does X happen", "X is broken", "this fails sometimes", "worked yesterday", or a pasted stack trace or log. Also use when the user asks to fix a bug whose cause has not been established yet, so the fix targets the root cause instead of the symptom. Produces a self-contained diagnosis report under docs/bugs/ with a verified causal chain, excluded causes, and ranked fix proposals; it does not implement the fix. Do not use for feature requests, code review, or bugs whose root cause is already verified.
---

# diagnose-bug

Find the root cause of a bug, prove it, and hand over a report that another agent or
developer can act on without redoing the investigation.

## Contract

- **Input:** a bug description in any form — issue text, chat message, stack trace, log excerpt,
  failing test, or "it's broken".
- **Output:** one Markdown report at `docs/bugs/YYYY-MM-DD-<slug>.md` (template in
  `references/report-template.md`) plus a short summary in the conversation.
- **Not in scope:** implementing the fix. The report ends with proposals and a recommendation;
  the user chooses. Never commit. Leave the working tree as you found it, except for the
  reproduction test (see Phase 6).
- **Self-contained report:** a reader with only the report must be able to continue — reproduce
  the bug, see which causes were excluded and why, follow the causal chain to the root, and pick
  a fix. Dead ends are part of the deliverable, because they are exactly what the next person
  would otherwise repeat.

## Principles

**1. The symptom is where the bug becomes visible, not where it lives.** A null dereference in a
formatter is a symptom; the parser that swallowed an exception two calls earlier is the cause.
Fixing the symptom leaves the class of failure open and adds a null check that hides the next
one. Use this stop criterion to decide how deep to go: *the root cause is the deepest cause that
lies within this project's control and whose correction prevents the whole class of failure, not
just this instance.* Deeper ("the language allows null") yields nothing actionable; shallower
fixes one case.

**2. Every claim is a hypothesis until verified.** This includes the bug report itself: the
reporter's "expected behavior" may be wrong, the "obvious" cause in the stack trace is often not
the cause, and what you remember about a library may not match the installed version. Keep an
**evidence ledger** (below) from the first minute. A claim enters the ledger as OPEN and becomes
VERIFIED or REFUTED only with a method and concrete evidence attached. Verify through three
sources, in this order of strength:

1. **Experiments** — a test, a script, a command whose outcome the hypothesis predicts.
2. **Code in this repository** — read the actual call path, config, and data flow; cite `file:line`.
3. **Frameworks and libraries** — the installed version (lockfile, project file), then its source
   in the dependency cache or its changelog for that exact version. Never cite library behavior
   from memory alone. See `references/verification-playbook.md`.

**3. Prediction is the strongest evidence.** A hypothesis is confirmed when it predicts something
you have not yet observed, and the prediction holds — typically: "if this is the cause, then
this minimal temporary change makes the reproduction pass". Observing that a hypothesis is
*consistent* with the symptom is weak; every plausible hypothesis is consistent with it.

**4. Offer choices, then recommend.** Different fixes trade speed, risk, and robustness
differently, and the user knows constraints you do not (release schedule, ownership, API
consumers). Present at least two proposals with honest trade-offs, then name the one you would
pick and why. A menu without a recommendation just moves the work to the reader.

## Evidence ledger

Maintain this table throughout and put it in the report verbatim:

| # | Claim | Status | Method | Evidence |
|---|-------|--------|--------|----------|
| 1 | Bug reproduces on `main` at `a1b2c3d` | VERIFIED | Ran new test `tests/test_x.py::test_repro` | Fails with `AssertionError: expected 3, got 4` |
| 2 | `sort()` comparator returns boolean | VERIFIED | Read `src/report.ts:41` | `.sort((a, b) => a.date > b.date)` |
| 3 | Reporter's expected value 3 is correct | OPEN | — | Spec not found; asked user |

Status values: `OPEN`, `VERIFIED`, `REFUTED`. If the final diagnosis rests on an OPEN claim, the
report status cannot be CONFIRMED (see Phase 6). Mark claims that came from the user or from an
assumption you had to make with their origin in the Method column, e.g. `assumed (non-interactive)`.

## Workflow

Work through the phases in order. Each phase names what must be true before the next starts.

### Phase 0 — Intake

Capture what is known and what is claimed. From the bug report and the repository, establish:

- Observed behavior (exact message, output, or effect) and expected behavior — with the source of
  the expectation (spec, test, docs, reporter's opinion).
- Where it happens: environment, version or commit, configuration, data, frequency
  (always / intermittent / once).
- Since when, if known, and what changed around that time.
- Stack, runtime, test framework, and how tests are run in this repository.

Everything the reporter states goes into the ledger as OPEN. If information needed for
reproduction is missing, ask — see "Interactive vs. non-interactive". Do not start theorizing
about causes yet; a theory formed before reproduction anchors the rest of the investigation.

*Gate:* you can state observed vs. expected behavior in one sentence each, and you know how to
run this project's tests.

### Phase 1 — Reproduce

Get a reliable reproduction before anything else. In order of preference:

1. A failing automated test in the project's own test framework, as narrow as possible.
2. A script or command sequence with deterministic output.
3. A documented manual sequence, if the above are impossible (UI-only, external system).

For intermittent bugs, find what makes it deterministic (fixed seed, forced timing, repeated
runs with a count) — an intermittent reproduction is still a reproduction if you can state the
rate. Record the exact command and its output in the report.

If you cannot reproduce: record every attempt and its outcome, ask the user for the missing
piece (data, environment, steps), and if that is not possible, continue with static analysis but
mark every downstream claim OPEN. The report status will be at best PROBABLE.

*Gate:* a command that fails now and is expected to pass once the bug is fixed.

### Phase 2 — Gather evidence and form hypotheses

Collect evidence *before* choosing a favorite cause:

- Read the full call path from entry point to the failure, not just the frame in the stack trace.
- Check history: `git log -S`/`-G` for the involved identifiers, `git blame` on the failing lines,
  `git bisect` when a known-good commit exists. "Since when" often points straight at the cause.
- Check inputs, configuration, and data that the path depends on; compare the failing case with a
  passing one.
- Check which versions of the involved frameworks and libraries are actually installed.

Then write down every hypothesis that would explain the symptom — usually 2–5. For each, note the
prediction that would confirm or refute it and how cheap that check is. Rank by *cheapest check
that could refute the most*, not by gut likelihood: a five-second check that kills three
hypotheses is worth more than a deep dive into the favorite.

*Gate:* a ranked list of hypotheses, each with a concrete refutation check.

### Phase 3 — Test hypotheses

Run the checks in ranked order. For each:

1. State the prediction before running the check.
2. Run it (test, script, log line, breakpoint, reading the library source at the installed version).
3. Record the outcome in the ledger as VERIFIED or REFUTED with the evidence.
4. Temporary instrumentation (extra logging, asserts, a minimal experimental change) is fine —
   list every such change so you can revert it in Phase 6.
5. Any experiment whose result you cite as evidence must be reproducible from the report alone:
   inline the script or command if it is short, otherwise save it under `docs/bugs/<slug>/` and
   reference it. A number nobody can re-derive ("90 % of pairs ordered") is an OPEN claim, however
   carefully you measured it. This holds for the small checks too, and those are the ones that get
   lost: the differential run against another version, the ten-line micro-test against a library,
   and above all the check that *refuted* a hypothesis. A refutation nobody can re-run is not an
   excluded cause, it is your opinion — and the excluded-causes section is the part of the report
   that saves the next person the most time.
6. Record the prediction check so someone else can see it happened: save the temporary change as a
   patch (`git diff > docs/bugs/<slug>/prediction-check.patch` before reverting) together with the
   reproduction command's output before and after. A clean working tree at the end proves you
   reverted something; it does not show what you tried or what it did.

A refuted hypothesis is a result: it goes into the report's "Excluded causes" section with the
evidence, so nobody re-investigates it. When all hypotheses are refuted, go back to Phase 2 with
the new evidence; do not resurrect a refuted one because nothing else is left.

When a hypothesis survives, do not stop yet — ask "why does *that* happen?" and repeat until the
stop criterion in Principle 1 is met. Every link in the chain needs its own ledger entry.

*Gate:* one hypothesis confirmed by prediction (Principle 3), all others refuted or explicitly
marked OPEN with the reason they could not be tested.

### Phase 4 — Establish the root cause

Write the causal chain explicitly, from root to symptom, one link per line, each link pointing to
its ledger entry:

```
Root cause:   parse_record() catches Exception and returns None          (ledger #4)
      →       build_report() receives None for malformed rows            (ledger #5)
      →       format_row() dereferences None                             (ledger #1, symptom)
```

Then run the completeness check: does this chain explain *every* observed detail — the exact
message, the frequency, the "since when", the environments where it does and does not occur? A
detail the chain does not explain means either a second, independent cause or the wrong cause.
Say which, and investigate before moving on.

Separate three things in the report: the root cause, contributing factors (things that made it
worse or harder to see, but would not have caused it alone), and the symptom. Also answer "why
was this not caught earlier?" — a missing test, a swallowed error, a silent default — because the
answer usually becomes the structural proposal in Phase 5.

*Gate:* causal chain with all links VERIFIED, or a written list of which links are OPEN and why.

### Phase 5 — Solution proposals

Propose at least two options; three tiers cover most bugs and give the user a real choice:

- **Mitigation** — contain the symptom quickly (guard, feature flag, rollback, config change).
  Legitimate when a release is imminent, but say plainly that it leaves the root cause in place.
- **Root-cause fix** — correct the cause identified in Phase 4.
- **Structural fix** — change the design or add the safeguard that makes the whole class of
  failure impossible or immediately visible (type change, invariant, contract test, lint rule).

Skip a tier only if it would be silly for this bug, and say so. For every proposal, fill in
every field of the table in `references/report-template.md`: what changes and where (blast
radius), why it works (link to the causal chain), risk, advantages, disadvantages, pitfalls,
robustness (does it hold when inputs, load, or the library version change?), effort,
reversibility and compatibility (data migration, API consumers, config), and how to verify it
(which test proves it, starting with the reproduction test from Phase 1).

Close with a recommendation and its reasoning, and name the constraints that would change the
recommendation ("if this ships tomorrow, take the mitigation first, then the root-cause fix").

Do not implement any proposal. The temporary experiment from Phase 3 that confirmed the root
cause is evidence, not the fix — even if it looks identical to one of the proposals.

### Phase 6 — Write the report and clean up

1. Write the report to `docs/bugs/YYYY-MM-DD-<slug>.md` using `references/report-template.md`.
   Use today's date and a short kebab-case slug of the symptom. If the file exists, add a `-2`
   suffix rather than overwriting. Create `docs/bugs/` if needed. Every section is present, but
   length follows the investigation, not the template: a section whose honest content is one
   line stays one line. Completeness means nothing is missing, not that everything is long.
2. Set the report status:
   - `CONFIRMED` — every link of the causal chain VERIFIED, prediction check passed.
   - `PROBABLE` — chain plausible but at least one link OPEN; list them.
   - `INCONCLUSIVE` — no surviving hypothesis; the report documents the state, the excluded
     causes, and the next checks to run.
3. Revert all temporary instrumentation and experimental changes; the prediction-check patch and
   its before/after output stay under `docs/bugs/<slug>/` as evidence. Keep the reproduction test in
   the working tree, uncommitted, with a leading comment `// diagnose-bug reproduction: see
   docs/bugs/<file>` (in the language's comment syntax), and list its path in the report. It is
   the only source change that may remain; the user decides whether to commit it with the fix.
   Experiment scripts saved under `docs/bugs/<slug>/` (Phase 3) may remain as well.
4. Run `git status` and `git diff --stat` and confirm the only changes are the report, the
   reproduction test, and any `docs/bugs/<slug>/` experiment scripts. Put that output in the report's "Working tree after diagnosis" section.
5. Reply in the conversation with: report path, status, root cause in one sentence, the
   recommended proposal in one sentence, and any OPEN claims the user should resolve.

## Interactive vs. non-interactive

Ask the user when missing information blocks reproduction or decides between hypotheses you
cannot test yourself (production data, an external system, the intended behavior). Batch the
questions, ask once, and say what you will assume if there is no answer.

When running as a sub-agent, in a pipeline, or when no answer arrives: never stall and never
guess silently. Proceed with the most conservative assumption, enter it in the ledger as OPEN with
Method `assumed (non-interactive)`, and let the report status reflect it. The report's "Open
questions" section lists every such assumption so the user can resolve them in one pass.

## When the investigation stalls

- **No reproduction** — see Phase 1. Static analysis only; status at best PROBABLE.
- **No test infrastructure** — write the reproduction as a standalone script under
  `docs/bugs/repro/` and say so; propose adding test infrastructure as part of the structural fix.
- **Hypotheses exhausted** — write the INCONCLUSIVE report. Its value is the excluded-causes
  list and the ranked next checks; a partial report beats an unfinished investigation nobody can
  resume.
- **Effort out of proportion** — match effort to the bug's impact. If the user set a budget,
  respect it; otherwise, when the next check would cost more than the bug plausibly does, stop
  and report with the ranked remaining hypotheses.

## Red flags — stop and re-check when you notice these

- "Obviously", "probably", "should be", "I'm fairly sure" in your own notes — that is an OPEN
  claim without a ledger entry.
- You are editing the fix before the reproduction exists.
- The stack trace's top frame is your root cause and you have not asked why it received bad input.
- The root cause is "developer error" or "bad input" — those are never actionable; ask what
  allowed the error to reach this point unnoticed.
- You cited a library's documentation without checking the installed version.
- An excluded cause has no re-runnable check behind it, or the report claims a script contains an
  experiment that it does not.
- The causal chain does not explain the frequency or the "since when".
- Only one proposal, or three proposals with no recommendation.
- A refuted hypothesis is back on the table because the alternatives ran out.
- `git diff` at the end shows anything besides the report, the reproduction test, and saved
  experiment scripts.

## References

- `references/report-template.md` — the report structure; every section is mandatory, write
  "none" rather than omitting one.
- `references/verification-playbook.md` — how to verify claims against tests, repository
  history, and the installed versions of frameworks and libraries, per ecosystem.
