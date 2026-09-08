# Diagnosis report template

Write the report to `docs/bugs/YYYY-MM-DD-<slug>.md`. Every section is mandatory; write "none"
rather than dropping a section, so the reader knows it was considered. The report must let
someone with no other context reproduce the bug, see what was already ruled out, follow the
causal chain, and choose a fix.

Write the report in the language the bug was reported in. Keep code, commands, paths, and
error messages verbatim.

```markdown
# Bug diagnosis: <short symptom>

| Field | Value |
|-------|-------|
| Date | YYYY-MM-DD |
| Status | CONFIRMED / PROBABLE / INCONCLUSIVE |
| Repository / commit | `<repo>` @ `<sha>` on branch `<branch>` |
| Reported by / source | issue #, chat, monitoring, … |
| Reproduction | `<exact command>` → fails / `not reproduced` |
| Since when / trigger | commit, deploy, version bump, or external change that made it visible — VERIFIED or OPEN |
| Root cause (one sentence) | … |
| Recommended fix | Proposal <n>: <one sentence> |
| Open claims | <count> — see "Open questions" |

## 1. Symptom

- **Observed:** exact message / output / effect, verbatim.
- **Expected:** what should happen, and the *source* of that expectation (spec, test, docs,
  reporter). Say whether the expectation itself was verified.
- **Where / when:** environment, config, data, frequency, since when.

## 2. Environment

Runtime, language and framework versions actually installed (with the file you read them
from), relevant configuration, test framework and how tests are run.

## 3. Reproduction

Exact steps or the test, verbatim, plus the output as observed. Include the reproduction test's
full source and its path in the working tree. For intermittent bugs, the observed failure rate
and what made it deterministic. If not reproduced: every attempt and its outcome.

## 4. Investigation log

Chronological. What was checked, in what order, what it showed, and what was decided next.
Include dead ends — they are the part the next person would otherwise repeat. Reference ledger
entries by number.

## 5. Evidence ledger

| # | Claim | Status | Method | Evidence |
|---|-------|--------|--------|----------|

All claims, including the reporter's statements and any assumptions made in non-interactive
mode (Method: `assumed (non-interactive)`). Evidence is concrete: `file:line`, command and
output, library source path and version, git commit.

## 6. Excluded causes

One entry per refuted hypothesis:

- **Hypothesis:** …
- **Why it seemed plausible:** …
- **Refuted by:** ledger #n — what was checked and what it showed.

## 7. Causal chain

From root to symptom, one link per line, each link pointing at its ledger entry. Then the
completeness check: which observed details the chain explains, and any it does not.

## 8. Root cause

- **Root cause:** the deepest cause within the project's control whose correction prevents the
  class of failure.
- **Contributing factors:** things that made it worse or harder to detect but would not have
  caused it alone.
- **Why it was not caught earlier:** missing test, swallowed error, silent default, …
- **Confirmation:** the prediction check that confirmed it (what was changed temporarily,
  what was predicted, what happened, and that it was reverted), referencing the saved
  `prediction-check.patch` and the before/after output.

## 9. Solution proposals

One subsection per proposal. Fill every row.

### Proposal 1 — <name> (Mitigation / Root-cause fix / Structural fix)

| Aspect | Assessment |
|--------|------------|
| What changes, where | files/modules, blast radius |
| Why it works | link to causal chain link(s) it breaks |
| Risk | what could go wrong, likelihood, impact |
| Advantages | |
| Disadvantages | |
| Pitfalls | mistakes that are easy to make while implementing it |
| Robustness | does it hold when inputs, load, config, or library versions change? |
| Effort | rough size |
| Reversibility / compatibility | data migration, API consumers, config, rollback |
| Verification | which tests prove it — reproduction test first, plus new ones |

## 10. Recommendation

Which proposal and why, in a few sentences. Which constraints would change the choice
(deadline, ownership, consumers). What to do regardless of the choice (e.g. keep the
reproduction test).

## 11. Open questions and assumptions

Every OPEN ledger claim, what would resolve it, and who can. If none: "none".

## 12. Working tree after diagnosis

Output of `git status --short` and `git diff --stat`. Must show only this report, the
reproduction test, and any experiment scripts under `docs/bugs/<slug>/`. List every temporary
change that was made and reverted.

## 13. How to continue

The concrete next step for whoever picks this up: run the reproduction test, implement the
chosen proposal, make the test pass, add the tests listed under Verification, resolve open
questions. If INCONCLUSIVE: the ranked next checks.
```
