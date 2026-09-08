# diagnose-bug — benchmark results

Every case was run twice by a fresh sub-agent on its own copy of the fixture: once with the skill
loaded, once with nothing but the bug report. An independent grader agent then scored each run
against that case's assertions, re-running the executor's own scripts and tests rather than
trusting its prose.

## Headline

| Round | Cases | With skill | Without skill |
|-------|-------|------------|---------------|
| Iteration 1 (seeded bugs, first draft) | 3 | 31/32 = 97 % | 17/32 = 53 % |
| Iteration 2 (seeded bugs, after fixes) | 3 | 39/40 = 98 % | 19/40 = 48 % |
| Iteration 3 (real-world bugs) | 8 | 110/113 = 97 % | 81/113 = 72 % |

Iteration 3 used Opus 5 for executors and graders; iterations 1 and 2 used Fable 5.1. Assertion
counts differ per round, so the percentages compare configurations within a round, not across.

## Iteration 3 — real-world cases

| Case | Fixture | Root cause | Skill | Baseline | Time |
|------|---------|-----------|-------|----------|------|
| yargs-parser prototype pollution | real repo @ v18.1.0 | CVE-2020-7608, `setKey` walks into `__proto__` | 14/14 | 9/14 | 13 vs 11 min |
| node-fetch redirect header leak | asset-mirror | CVE-2022-0235, `Authorization` forwarded cross-host | 12/14 | 7/14 | 21 vs 16 min |
| dayjs billing-day drift | subscription-billing | schedule chained off already-clamped dates | 14/14 | 9/14 | 7 vs 3 min |
| Java SimpleDateFormat race | ledger-export | one static formatter shared by 8 threads | 14/14 | 11/14 | 13 vs 5 min |
| .NET captive dependency | tenant-pricing | singleton captured the scoped context | 14/14 | 10/14 | 26 vs 4 min |
| Python money rounding | invoicing | float below the tie + half-to-even + unrounded sum | 15/15 | 15/15 | 11 vs 7 min |
| Python logging handler leak | feed-sync | a handler added per call to a cached logger | 13/14 | 11/14 | 8 vs 4 min |
| argparse abbreviation regression | deploy-tool | CI relied on `--vers`; a new option made it ambiguous | 14/14 | 9/14 | 9 vs 3 min |

Mean cost per run: 13.6 min and 105k tokens with the skill, 6.6 min and 72k without.

## What the numbers mean

**Both configurations found the correct root cause in all eight cases.** The skill does not make
the diagnosis smarter; it makes it checkable. The gap is entirely in evidence and hand-over.

Baseline failures (32) by category:

| Count | Failure |
|-------|---------|
| 6 | no report file, only a chat reply |
| 6 | a cited experiment cannot be re-run from the deliverables |
| 4 | no alternative cause refuted with evidence |
| 4 | no prediction check |
| 3 | **the fix was implemented in production code** although only a diagnosis was asked for |
| 3 | no reproduction that fails on unmodified code |
| 2 | only one fix proposal |
| 2 | library behaviour asserted from memory, not checked against the installed version |

The three baseline runs that edited production code did so unprompted; one swapped out a library
and hand-edited the lockfile.

Skill failures (3) were all one rule — an experiment cited as evidence that was not saved — and
twice it was a *side* experiment (a version comparison, a hypothesis-refuting check), never the
main reproduction. That pattern drove the post-series skill changes.

## Findings the skill produced that the baseline missed

- **yargs-parser**: `require('yargs-parser')` inside the repo resolves to a patched copy in
  `node_modules`, so the reporter's snippet prints `undefined` there. The run caught that it was
  about to test code other than the code under investigation.
- **Java**: the job log under-reports the damage by roughly 200:1 — one run corrupted 8 481 rows
  while printing zero log lines, so remediation cannot be scoped to the logged rows.
- **Rounding**: the obvious fix (`Decimal(str(x))` with `ROUND_HALF_UP`) is still wrong for about
  0.4 % of line items; a counterexample was found by searching 200 000 value pairs.
- **argparse**: `allow_abbrev=False` alone does not restore deploys, it only swaps one error
  message for another.

## Changes made to the skill because of these runs

1. *After iteration 1*: experiments cited as evidence must be reproducible; the reproduction test
   must be independent of test order; report length follows the investigation, not the template.
2. *After iteration 3*: the reproducibility rule now names the cases that kept getting missed
   (differential runs, library micro-tests, and above all refuting checks); the prediction check
   must leave a saved patch plus before/after output; "since when / trigger" became a required
   report field.

## Re-running

See `README.md` for the mechanics. `setup-fixtures.sh` builds the seeded-bug fixtures; the
real-world fixtures in `fixtures/` are copied per run, and the yargs-parser case needs a clone of
that repository at tag `v18.1.0` with `npm install --ignore-scripts`. Prompts and assertions for
the real-world cases are in `cases/`; `ISOLATION.md` documents what must be kept separate when the
two configurations run in parallel.
