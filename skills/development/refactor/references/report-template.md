# Refactoring Report Template

Written to `docs/refactoring/YYYY-MM-DD-<slug>.md`, in the language the user is writing in (or the
one they asked for). Created in Phase 2 and **updated as the run progresses** — the selection, the
coverage evidence, every step, and the closing summary all land in this same file.

Never overwrite an existing report; if the name is taken, append `-2`, `-3`.

Two readers have to be served: the user, who is about to run `git diff` and decide what to commit,
and whoever asks in six months why a promising candidate was left alone. Both answers must be in
this file, not in a conversation that no longer exists.

Every section is present. A section with nothing to say reads `n/a — <reason>`. Headings are
translated with the document; IDs (`R-n`, `D-n`) stay as they are.

---

```markdown
> **Date:** YYYY-MM-DD
> **Scope:** <as given by the user> → <n files> (<how it was resolved>)
> **Branch:** <branch>
> **Baseline:** <test command> — <n passed / n failed>, <duration>
> **Status:** analysis only | in progress — n of m candidates | complete | aborted at <phase>

# Refactoring — <scope in one line>

## 1. Summary

Three to five sentences: what was examined, what was found, what was actually changed, how it was
verified, and what the user does next. **Nothing has been committed.**

## 2. Scope and preconditions

- **Requested:** <the user's words>
- **Resolved to:** <n> files — <list or directory summary>
- **Excluded:** <generated / migrations / vendor / build output>, reason
- **Working tree at start:** clean
- **Baseline test run:** <command> — <result>. | no test suite found (D-n)
- **Coverage tooling:** <tool> configured | none found
- **Stack skills loaded:** <names> | none available (D-n)

## 3. Candidates

Priority axes: benefit (smell severity × change frequency × reach), risk (coverage, references,
public API or layer boundary), effort (steps, dependencies between candidates).

| ID | Smell | Location | Benefit | Risk | Effort | Coverage | Class | Status |
|---|---|---|---|---|---|---|---|---|
| R-1 | Long Function | src/…:88 | high — 14 changes/12mo, 3 callers | low — covered, local | medium — 3 steps | measured, lines 88-140 | local | done |
| R-2 | Duplicated Code | src/…:45, src/…:120 | high — logic in 2 places | medium — 4 callers | medium | mapping only | structural | not selected (D-4) |
| R-3 | Dead Code | src/…:200 | low | low | low | n/a | local | blocked — see §6 |

Change-frequency data: used (`git log`, 18 months) | not used — <reason>.

One paragraph per candidate below the table: the evidence, quoted, with `file:line`.

## 4. Selection and coverage

| ID | Selected | Coverage evidence | Gate outcome |
|---|---|---|---|
| R-1 | yes | coverlet: lines 88-140 covered by OrderExportTests:22,41 | proceed |
| R-3 | yes | no test reaches the symbol (mapping) | characterization tests written first (D-6), 4 tests, green against unchanged code |

## 5. Steps

| Step | Candidate | Refactoring | Site | Diff | Build | Tests | Lint | Note |
|---|---|---|---|---|---|---|---|---|
| 1 | R-1 | Extract Function | src/…:88 | 1 file, +18/-12 | ok | 214/214 | ok | — |
| 2 | R-1 | Rename | src/…:88 | 1 file, +4/-4 | ok | 214/214 | ok | test helper import renamed (mechanical) |
| 3 | R-3 | Remove Dead Code | src/…:200 | — | fail | — | — | rolled back, see §6 |

Rolled-back steps stay in the table. A step that was tried and failed is information; deleting it
hides why a candidate is blocked.

## 6. Found, not fixed

Behaviour that looks wrong, and everything else deliberately left alone. Nothing here was changed.

| # | What | Location | Why it was not fixed |
|---|---|---|---|
| 1 | inverted condition — `>=` where `>` is meant by the surrounding logic | src/…:97 | a fix changes behaviour; needs its own diagnosis |
| 2 | R-3 blocked | src/…:200 | two rollbacks: symbol is referenced from a DI configuration string |

## 7. Decisions

| ID | Decision | Origin | Reason |
|---|---|---|---|
| D-1 | scope narrowed to src/orders | user | 78 files resolved, above the threshold |
| D-2 | change-frequency factor used | default | 340 commits in the window |
| D-6 | characterization tests before R-3 | user | no coverage at the site |

## 8. Verification

- Baseline: <command>, <result>
- After the last step: <command>, <result>
- Build: <command>, <result> | n/a — <reason>
- Linter: <command> on <n> changed files, <result> | n/a — <reason>
- Not verified: <candidates refactored without coverage, if any> — repeat this in §1.

## 9. Open

What remains: candidates not started, blocked candidates, suggested commit points, and the
recommended next step.
```
