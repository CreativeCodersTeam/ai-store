# code-design — Workflow Test (placement, refactor pass, counter-check, seams)

**Date:** 2026-10-02
**Subject:** `skills/development/code-design/` (`SKILL.md`, `references/principles.md`,
`references/design-moves.md`), from its initial version through four iterations.
**Question:** When an agent extends existing code, does the skill make it (a) give new
responsibilities their own unit instead of appending to the nearest class, (b) tighten the code it
touched after green — including functions it only extended, (c) remove duplicated knowledge
without merging coincidental similarity, (d) put an abstraction at a real seam and nowhere else,
and (e) stop short of over-engineering — and does an agent *without* the skill fall short on
those points?

Method follows `CLAUDE.md` → "Testing skill behavior": baseline without the skill (RED), skill
(GREEN), per-assertion grading. Every run is **non-interactive**, so decisions that belong to the
user resolve through the skill's documented conservative defaults.

## Why this skill exists

The implementation workflows in this repository bias an agent toward the smallest diff:
`implement-direct/references/subagent-briefs.md` rules 2 ("Implement exactly the task's Goal") and
7 ("Touch only the task's Files … any other file … is a deviation"),
`general/implementer/references/REFERENCE.md:207` ("Do not refactor unrelated code"), plans that
copy "the closest existing feature", and a TDD loop with no refactor step. Design principles exist
only after the fact — the reviewer SOLID checklists and the explicitly invoked `refactor` skill.
`code-design` moves the design decision to before the first line is written. The workflows were
deliberately **not** changed; the skill is loaded by name, or through `run-with-skills`.

## Harness

- Runner sub-agent (`general-purpose`) in a scratch copy of one fixture from
  [`evals/fixtures/`](evals/fixtures/). The copy gets `git init` and one commit so the diff against
  the untouched fixture can be graded. Python 3.9, standard library, `unittest`.
- With-skill prompt: "read and follow `SKILL.md` and its references as if loaded by the skill
  tool" + the request with `/code-design`. Baseline: same request without the skill name, "do not
  load or use any skills". Both: non-interactive, git read-only, final reply written to
  `final_reply.md`.
- Grading: [`evals/grade_mechanical.py`](evals/grade_mechanical.py) for tests, removed test lines,
  function length, and abstract types; the rest by reading the diff and the reply. For the
  exporter case, CSV and HTML output was compared byte for byte against the fixture's original
  functions on 500 random inputs.
- One run per configuration and version. The scores are signals, not statistics.

## Scenarios

| # | Fixture | Request | Trap |
|---|---|---|---|
| 1 | `shop` — `OrderService`, 173 lines: validation, pricing, persistence, mail, reporting; `place_order` 53 lines, partly untested | discount codes: percentage / fixed, expiry, once per customer, after loyalty, before shipping and tax | the obvious place is another block in `place_order` and a few private methods on the service |
| 2 | `reports` — CSV and HTML exporters with copy-pasted filter, sort, totals, and German money format (6×) | Markdown export with the same columns and totals | copy the logic a third time |
| 3 | `textkit` — four pure text helpers | slug function: ASCII, umlaut transliteration, ≤ 60 chars without cutting a word | over-engineering: a class, a strategy for transliteration, a config object; or reusing `truncate_words`, which only looks similar |
| 4 | `pricing` — pure VAT and volume rules, a display function | show prices in the customer's currency using live rates from an HTTP endpoint | HTTP inside domain code; or a seam whose adapter is still wired as a default inside the display code; or one HTTP call per price line |

## Results

| Case | Baseline | Skill v1 | Skill v2 | Skill v3 | Skill v4 |
|---|---|---|---|---|---|
| 1 god-class | 6/10 | 9/10 | 9/10 | **10/10** | — |
| 2 third-exporter | 8/9 | — | — | **9/9** | — |
| 3 kiss-guard | 8/9 | — | — | **9/9** | — |
| 4 seam | 7/9 → 8/10¹ | — | — | 8/9 | **10/10** |

¹ Iteration 4 added one assertion (timeout, failure behaviour, call frequency); the iteration-3
baseline was regraded against it.

Cost, with skill vs. baseline: roughly 1.4× tokens and 2× wall time (case 1 v3: 100k / 327 s vs.
65k / 133 s; case 4 v4: 78k / 200 s vs. 53k / 87 s).

## What the baseline did instead

The baseline (Opus 5.5) is stronger than the motivating complaint suggests in small, clean
fixtures: it extracted `discounts.py` in case 1, extracted the shared report logic in case 2, and
kept the slug function plain in case 3. Where it fell short:

- **Case 1:** the once-per-customer rule went into a private method on `OrderService`;
  `place_order` grew from 53 to 60 lines; the `Order` data shape was extended without comment.
- **Case 4:** the conversion function shares a module with the HTTP adapter, and `display.py`
  imports a module-level live instance as its default — the seam exists, but the display code
  still depends on the network. It also added a cache and a 24-hour stale fallback nobody asked
  for (sensible, but undeclared).
- **All cases:** no record of why anything was placed where it was, no rejected alternatives, no
  list of what was seen and left alone.

## Changes after each iteration

**After v1 (case 1: 7/9).** Two assertions were non-discriminating and were replaced: "service.py
grows by ≤ 25 lines" penalised the skill for Extract Method on existing lines; "no function > 30
lines" failed both runs on a function that was already 53 lines. The skill's own gap: it noted the
untested validation block in `place_order` under *Left alone* and stopped, because the coverage
rule only said "without coverage, do not move". Fix in `SKILL.md` Step 2: untested paths reachable
through the public surface get **characterization tests** first (green against the unchanged code,
then move); only paths that need live I/O or global state stay as they are. Step 4: a function the
change extends counts as changed *as a whole*. Red-flag rows for both rationalizations.

**After v2 (case 1: 9/10).** `place_order` went from 53 to 25 lines behind 11 characterization
tests — but the redemption checks slipped back into a private method on `OrderService`, justified
with KISS and a circular import. Fix in `SKILL.md` Step 2: *A rule stays a rule when it needs
data* — the host fetches facts and passes plain values, the rule unit decides; passing values also
removes the circular import. SoC signal in `principles.md` points to it; red-flag row added.

**After v3 (case 4: 8/9).** Two findings: the run refused a cache as "YAGNI", so every price line
in a foreign currency would make its own HTTP call; and both runs wired the live adapter as a
default argument inside `display.py`. Fixes, canonical in `principles.md`: under *YAGNI*, operational
needs of an integration (timeout, failure behaviour, call frequency) are not speculative; under
*Dependency Inversion and seams*, adapters are constructed where the application is assembled, a
default is a recorded transition only. `SKILL.md` Step 5 got a *Wiring* item and a two-line hook;
`design-moves.md` *Port* row got the matching verify column.

**v4 (case 4: 10/10).** No package code constructs the HTTP adapter (README documents startup
wiring); 2 s timeout, 10-minute cache, 30 s fail-fast, all recorded as unconfirmed defaults; the
counter-check removed an unused `url` parameter.

## Observations worth keeping

- The skill does **not** tip into over-engineering. Case 3 extended the existing module with one
  function and a private helper, rejected a length parameter (YAGNI) and rejected reusing
  `truncate_words` as coincidental similarity — and found that `truncate_words` returns 11
  characters for a limit of 10, which it reported under *Left alone* without fixing.
- Characterization tests are where most of the extra cost goes, and they found real things to
  report: rounding differences between pricing (half-up) and refunds (banker's) in case 1, a
  missing `;` escape in the CSV exporter in case 2.
- Placement of a new domain type varies between runs (`discounts.py` vs. `models.py` in case 1).
  The skill deliberately has no rule for this; the project's layout decides.
- Case 4 v4 falls back to EUR when no rate source is wired or a rate is missing. That is a business
  decision, recorded as an unconfirmed default — not something to tune the skill for.
- `grade_mechanical.py` counts nominal subclasses; a `typing.Protocol` always shows zero
  implementations there. Check Protocols by hand.

## Not covered

- Triggering. The description follows the category's explicit-invocation pattern; the shared probe
  in `../_shared/explicit-invocation-test.md` has not been extended with `code-design` yet.
- The skill inside a workflow (`implement-direct` sub-agent mode under rule 7, or via
  `run-with-skills`). The *Inside another workflow* section is untested.
- Large, grown codebases. All fixtures are under 200 lines per file; the motivating behaviour
  (only ever extending) is likely stronger at scale and under workflow file-scope rules.

## Re-run this test when

- Step 2 (placement, preparatory refactoring, *A rule stays a rule*), Step 4, or Step 5 of
  `SKILL.md` changes — re-run cases 1 and 4.
- The *YAGNI*, *DRY*, or *Dependency Inversion and seams* sections of `principles.md` change —
  re-run cases 2, 3, and 4; case 3 is the over-engineering guard and must stay green.
- A workflow skill starts loading `code-design` — add a scenario for that path first.
