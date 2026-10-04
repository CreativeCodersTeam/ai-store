# upgrade-gh-wf-actions — release-note and runtime hints

Behaviour under test: before the user selects, the table marks rows whose release notes mention
breaking changes or deprecations and rows whose target still declares a runtime GitHub removed;
it flags a version in use that is announced to stop working; and after applying, the skill reads
the release notes of every applied upgrade and reports what they mean for this repository.

Added 2026-10-04, during the skill's first eval iteration.

## RED — the gap

Iteration 1 of the skill offered versions by age and semver only. Eval 1 ("Bring die GitHub
Actions … auf den neuesten Stand, aber bitte keine Major-Upgrades", scenario `repo-outdated`)
passed all nine mechanical assertions of that time, and still left the user with two problems the
response never mentioned:

```
$ jq -c '.groups[] | {repo, rows: [.rows[] | "\(.target_version) \([.target_runtimes[].using] | join(","))"]}' updates.json
{"repo":"actions/cache","rows":["v6.1.0 node24","v3.5.0 node16"]}
{"repo":"actions/checkout","rows":["v7.0.1 node24","v4.4.0 node20"]}
{"repo":"actions/setup-node","rows":["v7.0.0 node24","v4.4.0 node20"]}
{"repo":"actions/setup-python","rows":["v7.0.0 node24","v5.6.0 node20"]}
{"repo":"github/codeql-action","rows":["v4.38.2 node24,node24","v3.38.2 node20,node20"]}
```

(Output of the *fixed* `check-updates.sh` against the same scenario. Iteration 1 had no runtime
data at all, which is the gap.)

1. **Every within-major target declares a removed runtime.** GitHub removed Node 20 from its
   runners on 2026-09-23 and runs such actions on Node 24
   ([changelog](https://github.blog/changelog/2026-09-23-node-20-is-no-longer-available-in-github-actions/)).
   Iteration 1 pinned all five "no major" targets — node16 and node20 — without a word.
2. **The version in use was already broken.** `actions/cache` v3.3.1 predates v3.4.0, whose
   release notes say every older version fails since the legacy cache service was retired on
   2025-02-01. The baseline run without any skill found this from the release notes. Iteration 1
   of the skill did not, because it never read them.

```
$ grep -ciE 'node ?(16|20)|cache service|3\.4\.0' iteration-1/eval-1-no-major-upgrades/with_skill/run-1/outputs/response.md
0
```

## GREEN — the fix

`scripts/check-updates.sh`

- The GraphQL query also fetches release `description`. Two keyword scans, defined in
  `references/version-resolution.md` § *Release-note hints*, produce `rows[].notes_flags`
  (releases in `(current, target]`) and `current_warnings` (releases newer than the current one).
- `runs.using` is read from `action.yml` / `action.yaml` through the contents API, at the ref in
  use (`runtimes[]`) and at every offered target SHA (`rows[].target_runtimes[]`).
- Bug found on the way: `read` with a tab as `IFS` collapses an empty `subpath` field, which
  shifted `ref` into `subpath` and returned no runtime at all. The separator is now `\x1f`.

`scripts/release-notes.sh` (new): the release bodies between two versions, oldest first, with
`truncated` when the 100-release window does not reach back to `--from`.

`scripts/lib.jq` (new): `ts`, `semver`, `pad3`, `matching_lines` shared by both scripts instead of
two copies.

`references/runtime-support.md` (new): the single place that judges `runs.using`, dated and sourced,
because the answer changes over time and the scripts must not hard-code it.

`SKILL.md`

- Step 3 introduces the three fields as keyword matches to be judged, not verdicts.
- Step 4 adds the ⚠ marker and the hint lines below the table, with the explicit instruction to
  skip harmless matches (a dependency bump whose PR title says "breaking").
- Step 5 puts the hint into the option description.
- New Step 8 reads the release notes of every applied `upgrade` row and compares removed or
  renamed inputs with the `with:` block of the changed lines; Step 9 (summary) carries the
  findings and the remaining runtime warnings.
- Non-interactive use: a chosen row with ⚠ is applied as requested, but the summary names the hint
  and the row that would avoid it.
- Two red flags: flagging everything that says "BREAKING", and skipping the runtime of a pin.

Unit tests: `scripts/unit/test-check-updates.sh` § 5 (flags only from `(current, target]`, CR and
Markdown stripped, deprecation of the current version, `action.yaml` fallback, subpath runtimes,
unreadable runtime is `null`) and the new `scripts/unit/test-release-notes.sh`.

## Eval runs, 2026-10-04

Scenario `repo-outdated`, live GitHub API, graded by `evals/grade-mechanical.py` (all runs
re-graded with the final grader). One run per configuration.

| Eval | Iteration 1, skill | Iteration 2, skill | Iteration 2, no skill |
| ---- | ------------------ | ------------------ | --------------------- |
| 1 — no major upgrades           | 9/11 | **11/11** | 9/11 |
| 2 — report only, 14 days        | —    | **8/8**   | 7/8  |
| 3 — two actions, majors allowed | —    | **10/10** | 9/10 |

What the runs showed beyond the counts:

- **Eval 1, iteration 2.** The summary opens with the runtime problem ("Alle fünf Actions laufen
  auch in der neuen Version noch auf Node 16 oder Node 20"), lists per action the major row that
  reaches node24, and reports the cache finding with a quote from the v3.4.0 notes and the check
  that the inputs in use (`path`, `key`) are unchanged. setup-node's cache-key change is reported
  as not applicable because the step sets no `cache:` input — the repository-specific reading
  Step 8 asks for.
- **Eval 2.** The codeql pin row is correctly a downgrade pin (`v3` resolves to v3.38.2, 10 days
  old; the pin goes to v3.38.1), and the 10-day-old v4.38.2 is listed as not offered.
- **Eval 3.** Only the two named actions change; setup-node v5+'s automatic npm caching is flagged
  as conditional (the repository has no `package.json`) with the opt-out input named, not applied.
- **Baseline.** Reads release notes well on its own (it found the cache problem in every run), but
  wrote mutable tags (`@v4.4.0`, `@v7`) in evals 1 and 3, left floating tags unpinned, and missed
  the node20 targets in eval 2. The skill's lasting advantage is the supply-chain half: SHA pins
  resolved from the action's own tags, the minimum age, and the runtime check.
- **Cost.** About +25 s and +22k tokens per run against the baseline (iteration 2 means: 125 s /
  78k vs. 100 s / 56k), mostly the release-note reading and the extra contents calls.

Not covered by the evals: the interactive multi-select (batches of four, the overlap question).
Sub-agents have no `AskUserQuestion`; that path needs a live run.

## Verification probe, 2026-10-04

A fresh sub-agent with no file access received only the passages under test (Step 3 fields, Step 4
hints and the Step 5 description rule, Step 8, the non-interactive excerpt, and
`runtime-support.md`) and answered ten scenario questions:

| # | Scenario                                                        | Answer                                                   | Correct |
| - | --------------------------------------------------------------- | -------------------------------------------------------- | ------- |
| 1 | PIN row, target node20, no flags                                | ⚠, description "PIN · age · still node20"                 | yes     |
| 2 | Only flag is a dependabot "document breaking changes" PR title  | no ⚠                                                      | yes     |
| 3 | codeql deprecation for CodeQL ≤ 2.20.6, default bundle in use    | do not report — judgment call, flagged as such            | yes     |
| 4 | `target_runtimes` `using: null`                                 | "runtime unknown", no guess                               | yes     |
| 5 | Headless "no majors", every target node20                        | apply; summary names hint and the avoiding row            | yes     |
| 6 | Release notes for upgrade, PIN, and unknown-current rows         | only the upgrade with a known current version             | yes     |
| 7 | `release-notes.sh` exit 4                                        | say so, continue with the others                          | yes     |
| 8 | Notes rename an input the step uses                              | report, do not edit                                       | yes     |
| 9 | Composite action                                                 | nothing to report                                         | yes     |
| 10 | `runs-on: ubuntu-latest`                                        | no macOS/ARM32 note                                       | yes     |

Gaps the probe reported, and what happened to them:

- *What to report for an applied upgrade whose current version is unknown* — Step 8 now says
  there is no range to read and to give the `release_url` instead.
- *What if no row avoids the ⚠* — the non-interactive rule now says to state that.
- *Whether the default CodeQL bundle counts as "the version in use"* — left as a judgment call on
  purpose: the rule is "really concerns the version in use", and the agent is expected to read
  the line.

Re-run this probe when Step 3, Step 4's hint rules, Step 8, or `runtime-support.md` change, and
update `runtime-support.md` (and this artifact's RED evidence, if it is reused) when GitHub changes
runtime support again.
