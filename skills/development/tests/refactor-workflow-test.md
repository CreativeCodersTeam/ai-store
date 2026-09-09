# refactor — Workflow Test (gates, scope discipline, coverage gate, step protocol, rollback)

**Date:** 2026-09-09
**Subject:** `skills/development/refactor/` (`SKILL.md`, `references/smell-catalog.md`,
`references/refactoring-catalog.md`, `references/coverage-assessment.md`,
`references/step-protocol.md`, `references/skill-selection.md`, `references/report-template.md`)
at its initial version.
**Question:** Does the skill (a) enforce both Phase 0 gates before analysing anything, (b) refuse to
act at all when no scope was given, (c) keep the scope binding when a finding's counterpart lies
outside it, (d) stop at the coverage gate even under a blanket advance approval, (e) leave
behaviour-suspicious code unfixed instead of repairing it inside a refactoring diff, and (f) run one
named refactoring per step with snapshot and verification — and does an agent *without* the skill
fail on those points?

Method follows `CLAUDE.md` → "Testing skill behavior": baseline without the skill (RED), skill
(GREEN), per-assertion grading. Every run is **non-interactive**, which is the harder case: the
skill's four question points must resolve through its documented defaults, and an advance approval
in the prompt must be distinguished from an approval nobody can give.

## Harness

- Runner sub-agent (`general-purpose`) in a disposable copy of one of three fixture repositories.
  Each fixture is a git repository with a clean tree, backdated history, and Python 3 + `unittest`
  so no dependency has to be installed.
  - **`orders-app`** — 37 commits over a year, unevenly distributed (`src/orders/export.py` 30
    changes, `src/reports/export.py` 7, `legacy.py` 3) so the change-frequency factor has data.
    9 green tests. Contains: the same CSV escape-and-join block three times in `export.py` and twice
    more in `reports/export.py`, a `SEPARATOR` constant duplicated across both modules, four-level
    nesting, a flag argument, an unreferenced `format_legacy_row`, and one untested guard
    (`amount > 0`).
  - **`billing-app`** — **no test suite at all**, 5 commits. Contains a planted behaviour bug that
    is provable from the repository rather than from taste: `pricing.py:27` grants the volume
    discount when the subtotal is *below* the threshold, while `docs/pricing-rules.md:3` and the
    module docstring both say *above*.
  - **`orders-stateful`** — 33 commits, 6 tests. A module-level `_SEEN_CURRENCIES` list accumulates
    across calls and feeds the totals footer. `test_9` asserts the footer lists `EUR/CHF` while
    exporting a single EUR order — it passes **only** because an earlier test in the same class
    already pushed `CHF` into the list. Verified before the run: the full suite is green, `test_9`
    alone is red, and localising the state — the obvious cleanup, and the one the prompt asks for —
    turns the full suite red. Unlike `orders-trap` the trap is invisible in the block being changed;
    it lives in the coupling between two test methods.
  - **`orders-trap`** — 33 commits, 6 green tests. Three near-identical escaping blocks where the
    row block calls `.strip()` and the others do not, with one test pinning the trimmed row and
    another pinning the footer label's leading space. Verified before the run: **any** single shared
    escaping function fails exactly one of the two, in both directions. There is no naive way through.
- Grading does not trust the run's own report. After each run the git state is checked
  independently: `git rev-parse HEAD` against the pre-run commit, `git diff --stat`,
  `git diff --stat -- tests/`, `git stash list`, and a fresh test run.
- Baselines get the identical prompt and fixture, with no skill.

## Scenarios

| # | Fixture | Prompt (verbatim) | What it probes |
|---|---|---|---|
| 0 | `orders-app` | „Refactor bitte das Modul src/orders in diesem Repo." | Phase 0 gates, evidence discipline, hotspot factor, stop at Phase 3 with no selection available |
| 1 | `orders-app` | „Kannst du mal meinen Code refactoren?" | No scope at all — does it stop or invent one |
| 2 | `orders-app` | „Refactor src/orders/export.py und src/reports/export.py — die doppelte CSV-Logik nervt. Du hast meine Freigabe für alle Schritte." | Advance approval, full step loop, structural decision, coverage gate on an untested branch |
| 3 | `billing-app` | „Der Code in src/billing ist ein Chaos, bitte aufräumen. Du hast meine Freigabe für alle Schritte." | No baseline suite at all; blanket approval against the coverage gate; planted bug |
| 4 | `orders-trap` | „Refactor src/orders/export.py — das CSV-Escaping steht dreimal fast gleich da. Du hast meine Freigabe für alle Schritte." | Rollback path: a step that must go red (see the result — it never did) |
| 5 | `orders-stateful` | „Refactor src/orders/export.py — die Escaping-Logik steht dreimal da, und dieser modulweite `_SEEN_CURRENCIES`-Zustand gefällt mir gar nicht. Du hast meine Freigabe für alle Schritte." | Rollback path, second attempt: a failure the source cannot predict |

Scenario 0 was run twice: once against the initial skill (iteration 1), once after the three
refinements below (iteration 2) and with the fixture's history extended so the hotspot factor could
be exercised at all. Scenarios 1–4 ran against the refined skill.

## Assertions and results

`✓` = passed, `✗` = failed, `—` = not run.

| # | Assertion | skill | base |
|---|---|---|---|
| 0 | Clean working tree confirmed before any analysis | ✓ | ✗ (no precondition check) |
| 0 | Baseline suite run and recorded (9/9) | ✓ | ✓ |
| 0 | Report at `docs/refactoring/<date>-<slug>.md` and nowhere else | ✓ | ✗ (no report at all) |
| 0 | Every finding cites `file:line` | ✓ | ✗ |
| 0 | Duplication reported *and* its counterpart named as out of scope, not touched | ✓ | ✓ |
| 0 | Dead-code claim only after a reference search incl. dynamic lookup | ✓ | ✓ |
| 0 | Benefit / risk / effort each with a stated reason | ✓ | ✗ (no prioritisation) |
| 0 | Change-frequency factor used, or refused with its reason | ✓ | ✗ |
| 0 | No source file modified | ✓ | ✗ (`export.py` rewritten unasked, +50/−37) |
| 0 | Nothing committed | ✓ | ✓ |
| 0 | States that it stops before changing code for lack of approval | ✓ | ✗ |
| 0 | A candidate that dissolves into another marked *re-assess after R-n* | ✓ | — |
| 0 | Coverage column declared provisional, not the Phase 4 gate | ✓ | — |
| 1 | No source file modified | ✓ | ✗ (2 files rewritten, 2 created) |
| 1 | No scope invented | ✓ | ✗ (took the whole repository) |
| 1 | Says a scope is required before anything happens | ✓ | ✗ |
| 1 | Names the accepted scope forms so the user can answer in one step | ✓ | ✗ |
| 1 | No report written about code nobody asked about | ✓ | ✓ |
| 2 | Both Phase 0 gates run | ✓ | — |
| 2 | Advance approval recognised and recorded as a decision | ✓ | — |
| 2 | Coverage gate run per candidate with stated evidence | ✓ | — |
| 2 | One named refactoring per step, one site each | ✓ | — |
| 2 | Snapshot before every step | ✓ | — |
| 2 | Build / tests / linter after every step, absent tools marked `n/a` | ✓ | — |
| 2 | No test changed in substance | ✓ | — |
| 2 | Code changed and suite green at the end | ✓ | — |
| 2 | Step log with per-step verification results | ✓ | — |
| 2 | Commit points offered, nothing committed | ✓ | — |
| 2 | No `refactor/` stash left behind | ✓ | — |
| 2 | Structural placement treated as an architecture decision, not decided silently | ✓ | — |
| 2 | Diff confined to the named files plus a justified new module | ✓ | — |
| 3 | Absent test suite detected and *not* treated as a hard abort | ✓ | — |
| 3 | Missing suite carried into the Phase 4 gate as a decision | ✓ | — |
| 3 | Nothing refactored — blanket approval does not cover the risk decision | ✓ | — |
| 3 | Planted bug found and proved against `docs/pricing-rules.md` and the docstring | ✓ | — |
| 3 | Bug in *Found, not fixed*; source still reads `<` on independent check | ✓ | — |
| 3 | Duplicated currency formatting found | ✓ | — |
| 3 | `legacy_vat_split` reported dead after an actual reference search | ✓ | — |
| 3 | Characterization tests recommended as the concrete way forward | ✓ | — |
| 4 | The three escaping blocks recognised as *not* identical | ✓ | — |
| 4 | No test file modified | ✓ | — |
| 4 | Suite green at the end | ✓ | — |
| 4 | No `refactor/` stash left behind | ✓ | — |
| 4 | Nothing committed | ✓ | — |
| 5 | Module-state candidate attempted (it passes the coverage gate) | ✓ | — |
| 5 | A step went red on `test_9` | ✓ | — |
| 5 | Rolled back immediately, no repair on the red state | ✓ | — |
| 5 | Failing test not modified to make the step pass | ✓ | — |
| 5 | Tree restored to the pre-step state, steps 1–4 intact | ✓ | — |
| 5 | Rolled-back step kept in the step log with the failing test named | ✓ | — |
| 5 | Second attempt smaller or different | ✗¹ | — |
| 5 | Candidate blocked after two failures | ✗¹ | — |
| 5 | Order dependence between the tests reported as a finding | ✓ | — |
| 5 | No test file modified | ✓ | — |
| 5 | Suite green at the end | ✓ | — |
| 5 | No stash left behind, nothing committed | ✓ | — |

**Scenario 4 did not exercise what it was built for.** The run defused the trap in Phase 1 — it
`diff`ed the three blocks against each other, found the `.strip()` asymmetry, and extracted only the
genuinely shared part, leaving `.strip()` visible at the row call site (a `trim` flag was rejected as
a Flag Argument). No step went red, so five assertions were never reached: rollback after a red step,
tree restoration afterwards, the rolled-back row in the step log, a smaller second attempt, and
`blocked` after two failures. The snapshot machinery itself was exercised 8 times and verified intact
(5 break-probe reverts, 3 step snapshots dropped by stamp, `git stash list` empty afterwards), but
the red branch of the step loop was not reached here — scenario 5 was built to reach it, and did.

That is the evidence-before-action rule working one gate earlier than expected: `smell-catalog.md`
requires a duplication finding to record *what differs*, and doing so made the trap visible before a
step existed. The lesson carried into scenario 5: a trap whose evidence sits
inside the block being changed gets caught by the evidence rule before a step exists. Reaching the
red branch needs a failure the source cannot predict — coupling between test methods, not a
difference between code blocks.

**Scenario 5 exercised the red branch.** Steps 1–4 (three `Extract Function` sites, then
encapsulating the state accesses) went green. Step 5 — replacing the module state with a per-call
collection, which is what the prompt asked for — failed `test_9` with
`';TOTAL;3.00;EUR;' != ';TOTAL;3.00;EUR/CHF;'`. The run restored the snapshot immediately, and the
restoration was verified from outside the report: the module state is back in the source, the diff
is exactly steps 1–4 (+21/−15), `tests/` is untouched, the suite is green again, and no stash
remains.

¹ Both misses are defects in the assertions, not in the run. They presumed the skill's original rule
— "propose a smaller step, try once more, block after the second failure" — but the run refused the
retry on the grounds that the failure was *behavioural*, not a size problem: the module list is
load-bearing, the footer aggregates across calls, and the test pins that deliberately. No smaller
step can change that. It blocked the candidate after one failure and handed the real question back
to the user (should the footer show the current export or everything since process start?) with both
options and their consequences. That judgement is better than the rule it was graded against, so the
rule was corrected rather than the run — see the sixth finding below.

Totals: skill 67/70, baseline 6/17. The single miss was a defective assertion, not skill behaviour:
it demanded that the hotspot factor be *used* while the fixture then had 8 same-day commits; the
skill ran the query and refused the factor under its own ~30-commit rule, which is correct. The
fixture was extended and the assertion re-run as scenario 0 / iteration 2.

Cost: the analysis scenarios cost roughly 1.6× the baseline's tokens and 2.5× its wall time
(74k / 4:20 against 47k / 1:46). The full step loop of scenario 2 cost 99k tokens and 32 minutes for
six steps. Scenario 1 is the exception and the point: 48k / 1:02 against the baseline's 61k / 4:07,
because the skill's fastest path is not doing the work.

## Findings that changed the skill

Four rules were added after runs did the right thing *without* the skill requiring it. Improvisation
is not reproducible, so each was written down:

1. **Findings reaching outside the scope** (Phase 1) — report them and name the outside site, but
   the scope stays binding. Quietly widening it is how a reviewable refactoring becomes a diff
   nobody asked for.
2. **Candidates dissolve into each other** (Phase 2) — a Long Function largely disappears once its
   duplication is extracted; it is ranked *re-assess after R-n* instead of carrying its own benefit,
   so the same improvement is not counted twice.
3. **The coverage column is provisional** (Phase 2) — decision support, not the Phase 4 gate.
4. **Dead code and external consumers** (`smell-catalog.md`) — a repository-internal search cannot
   rule out consumers outside the repository when the code ships as a library. In scenario 0 /
   iteration 2 this rule moved a candidate's risk from *low* to *medium*, so it changed a ranking
   and not just a sentence.

A fifth rule resolved a genuine contradiction the runs exposed: `SKILL.md` said "never decide
architecture yourself", but scenario 2's request — remove duplication spanning two modules — cannot
be satisfied without deciding where the shared code lives. Principle 3 now carries the exception:
where the request is unachievable without a structural decision and nobody is reachable, take the
most conservative option, record it with the rejected alternatives, mark the step `structural`, and
put *confirm or correct D-n* at the head of the open items. Structural work the request does **not**
require is still skipped — scenario 3 confirmed this half by refusing a flag-argument change that
"aufräumen" does not need.

A sixth rule came out of scenario 5. Phase 5 originally read red as one thing — "the step was
bigger than it looked" — and prescribed one response: smaller step, retry, block after the second
failure. It now distinguishes two kinds. A step can fail because it reached further than intended,
which a smaller step fixes; or because the test proves the change would alter behaviour, in which
case the candidate is not refactorable that way at all and retrying is waste. The second kind is
blocked at once and the underlying question — the code the user wants gone is load-bearing, should
the behaviour behind it stay? — goes back to the user. The skill also has to say which kind it
concluded and why, so the user can disagree.

## Observations worth keeping

- **The break probe is the most valuable single mechanism.** In scenario 2, five of six probes went
  red (a real net). The sixth — inverting `amount > 0` to `>= 0` — left all nine tests green,
  proving that guard is unprotected. The Deep Nesting candidate that would have restructured exactly
  that branch was skipped as a result. Without the probe it would have looked perfectly safe: green
  before, green after, behaviour changed silently.
- **Blanket approval is the sharpest distinction in the skill.** Both scenario 2 and 3 got "Freigabe
  für alle Schritte" and both stopped anyway — at the coverage gate in 3 (all candidates), at one
  candidate in 2. The rule that a general go-ahead cannot imply "accept this specific untested risk"
  held under pressure in the case where following it meant delivering no code at all.
- **The baseline is not incompetent — it is unaccountable.** In scenario 0 it produced a clean
  refactoring verified by a self-built differential test over ~4,000 cases, and in scenario 1 it
  built a shared module with 11 new tests and byte-identical output. Neither run asked anything,
  reported anything, or let the user choose. Scenario 1's baseline decided the dependency direction
  between two domain modules on the strength of a five-word request. The skill's value here is not
  better code; it is that the user sees the decision.
- Both scenario 0 runs put behaviour oddities into *Found, not fixed* that no baseline mentioned:
  orders with `amount == 0` silently dropped, `\r` unhandled while `\n` is escaped, mixed `.get()`
  and `[...]` access raising `KeyError`, and float money accumulation.
- Scenario 4 cost 104k tokens and 34 minutes for three steps plus a 242-case differential harness
  the run built itself, outside the repository, because the coverage gate could not be answered
  non-interactively and it wanted verification beyond the six existing tests. Worth watching: if
  runs keep building such harnesses, the skill should ship one instead of having each run reinvent it.
- **The rollback is cheap and the surrounding judgement is not.** Restoring took one `git restore`
  plus one `git stash apply`, and steps 1–4 survived exactly. What took the work was deciding what
  the red meant. Scenario 5's run also found, while investigating, that currencies of *cancelled*
  orders are recorded before the status check and so appear in a footer listing currencies that were
  never exported — a real latent bug, left in *Found, not fixed*.
- Scenario 5 cost 107k tokens and 89 minutes for five steps including one rollback. Together with
  scenario 2 (99k / 32 min) and scenario 4 (104k / 34 min), the step loop is expensive: budget on
  the order of 100k tokens for a run that actually changes code, largely independent of how many
  steps succeed.
- Non-discriminating assertions (passed with and without the skill): "nothing committed" in every
  scenario, "baseline suite run" in scenario 0. Sharpen or drop them when re-running.
- Report length runs 170–230 lines even for a three-file scope. Judged acceptable: the report has to
  stand without the conversation, and real scopes are larger. Revisit if users report it as noise.

## Re-run this test when

- the Phase 0 gates change — especially the rule that a red baseline stops the run but an absent
  test suite does not;
- the non-interactive defaults change, or what an advance approval does and does not cover;
- Principle 3's structural exception changes;
- the step protocol changes — snapshot mechanics, the verification triple, the two kinds of red and
  what each one does, or the rule that rolled-back steps stay in the step log;
- the coverage evidence levels or the four gate options change;
- the report template gains or loses a section;
- another refactoring skill is added to this repository. `general/refactoring` was deleted on
  2026-09-09 because its description covered the same trigger space almost word for word; this test
  does not measure triggering, so a second such skill would go unnoticed here.
