# diagnose-bug evals

Test artifacts for `skills/development/diagnose-bug`. Each eval is a small project with one
seeded bug whose root cause differs from its symptom; the skill is run against it with and
without the skill and graded against the assertions in `evals.json`.

| Eval | Fixture | Seeded root cause | What it tests |
|------|---------|-------------------|---------------|
| 0 `state-leak-across-calls` | `monthly-report` (Python, unittest) | mutable default argument accumulates across calls | state leaking between calls; German bug report → German report |
| 1 `runtime-upgrade-regression` | `bank-statement` (Node, `node --test`) | boolean sort comparator; tests only use sorted input; Node 10→24 bump exposed it | verifying library/runtime behavior against the installed version, trigger vs. cause, release-deadline handling |
| 2 `misleading-stack-trace` | `expense-importer` (Python, unittest) | `except Exception: return None` in the parser, triggered by a comma-decimal amount | going past the top stack frame; not stopping at a None check |

## Running

Requirements: `python3` (3.9+, unittest only), `node` (≥ 18), `git`, and the
`skill-creator` skill for grading and the viewer.

1. `bash setup-fixtures.sh <workspace>/fixtures` — creates the three projects with git history.
2. For each eval and each configuration (`with_skill` / `without_skill`), copy the fixture to a
   fresh directory and replace `<project>` in the prompt with that path. Run a fresh sub-agent
   on the prompt (with-skill runs get the path to `SKILL.md`; baseline runs get nothing else)
   and have it save the report, its final reply, and `git status --short && git diff` to an
   `outputs/` directory.
3. Grade each run against `expectations` in `evals.json` with the skill-creator grader, then
   aggregate and review as described in the skill-creator skill.

Eight further cases (evals 3-10) use real bugs — two published CVEs in the libraries that carry
them, plus six fixtures reproducing well-known failure classes. Their fixtures are in `fixtures/`,
their prompts and assertions in `cases/`, and the yargs-parser case needs a clone of that
repository at tag `v18.1.0` with `npm install --ignore-scripts`.

`ISOLATION.md` records what must stay separate when the two configurations run in parallel; the
short version is that each run needs its own copy of the fixture and its own scratch directory.

Results across all three rounds are in `RESULTS.md`. Re-run when the skill's phases, the report
template, or the verification playbook change.
