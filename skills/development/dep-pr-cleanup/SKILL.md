---
name: dep-pr-cleanup
description: >
  Use when the user wants to clean up or consolidate the open pull requests of dependency bots
  such as Dependabot or Mend Renovate — finding bot PRs made obsolete by newer or larger PRs of
  the same bot — and whenever it is named: "dep-pr-cleanup", "/dep-pr-cleanup",
  "/cc-ai-dev:dep-pr-cleanup". Reads the manifest diff of every open bot PR on GitHub via gh,
  compares overlapping PRs side by side, lets the user decide globally and per pair whether a
  newer (or newer major) version counts as replacement, proposes a PR as obsolete only when all
  its updates are covered by PRs that stay open, and after confirmation closes the chosen PRs
  with a "superseded by" comment and deletes their branches. Report in docs/dep-pr-cleanup/.
  Never commits. Must NOT activate for configuring Dependabot or Renovate, reviewing, rebasing,
  or merging a single dependency PR, upgrading dependencies directly, or upgrading GitHub
  Actions in workflows (upgrade-gh-wf-actions).
---

# dep-pr-cleanup

Dependency bots open pull requests faster than teams merge them. Renovate opens a minor and a
major PR side by side, a grouped PR repeats updates that single PRs already carry, a security
update targets an older version than the version-update PR next to it. This skill finds the
bot PRs whose every update is already contained in other open PRs of the same bot, shows the
overlaps, and closes the obsolete ones once the user has agreed.

## Contract

- **Input:** a GitHub repository (the working directory's by default); optionally extra bot
  accounts, the replacement options, and `.github/dep-pr-cleanup.json`.
- **Output:** a side-by-side comparison of the overlapping bot PRs and the proposed obsolete
  ones in the conversation; after confirmation, the chosen PRs closed with a comment and their
  branches deleted; a report in `docs/dep-pr-cleanup/`.
- **Not in scope:** merging, rebasing, or approving PRs; changing manifests; configuring the bots.
- **Never commits.** The report is written to the working tree; the user decides about it.

## Why the rules are what they are

Closing a bot PR is not free: Renovate treats a closed PR as "ignore this update" — closing
"Update lodash to v4.17.21" ignores that version, closing "Update lodash to v4" ignores every
future v4 update — and Dependabot answers a closed PR with "I won't notify you again about this
release". An update that was wrongly judged as covered is silently lost. Hence:

- **Obsolete means fully covered by PRs that stay open.** A PR is proposed only when *each* of
  its updates — same ecosystem, same package, same manifest path — is contained in another open
  PR of the same bot against the same base branch, at the same target version or, if the user
  allows it, a newer one. A covering PR is never itself proposed, so closing any subset of the
  proposals is safe.
- **Only the diff counts.** Titles and descriptions are templated and incomplete; the manifest
  lines the PR actually changes are the truth. Lockfiles are ignored (they carry transitive
  noise). A changed manifest line that cannot be interpreted makes the whole PR *unevaluable*:
  it is never proposed and never counts as a cover.
- **The scripts decide, not you.** Coverage is computed by `analyze_prs.py`. Do not move a PR
  between "obsolete" and "kept" by reading the diff yourself; if a result looks wrong, explain it
  with [references/coverage-rules.md](references/coverage-rules.md) or report it.

## Prerequisites

- `gh` (GitHub CLI), authenticated with write access to the repository for closing
  (`gh auth status`). If missing or not logged in, stop and suggest `! gh auth login`.
- Python 3.8+ with the standard library only. Find the interpreter once and reuse it: try
  `python3 --version`, then `python --version`, then `py -3 --version` (Windows) — take the
  first that prints `Python 3.8` or newer. On Windows, `python3` may be a Microsoft Store stub
  that prints nothing; skip it then. Below, `PY` stands for the command found.

The scripts live in this skill's `scripts/` directory; call them by absolute path. They print
JSON on stdout and accept file paths, so they work the same in bash, zsh, PowerShell, and cmd.
Keep intermediate files in the system temp directory, never in the repository.

## Parameters

| Parameter | Default | Changed by |
| --- | --- | --- |
| Repository | the working directory's GitHub repository | "for acme/shop", `--repo` |
| Bots | `dependabot[bot]`, `renovate[bot]` | the prompt ("also my-renovate[bot]") → `--bot`; config `bots`; config `includeDefaultBots: false` drops the defaults |
| Newer version counts as replacement | **yes** | the prompt; config `newerCountsAsReplacement`; the question in Step 4 |
| … also across major versions | **no** | the prompt; config `acrossMajor`; the question in Step 4 |
| Per-pair exceptions | none | Step 5 |

Precedence: the prompt over `.github/dep-pr-cleanup.json` over the default. Record the origin of
every value (`prompt`, `config`, `question`, `default`) — the report states it. The config file
is optional; `collect_prs.py` reads it from the repository root and rejects unknown keys
(exit 4):

```json
{ "bots": ["my-renovate[bot]"], "includeDefaultBots": true,
  "newerCountsAsReplacement": true, "acrossMajor": false }
```

Why "across major versions" defaults to no: Renovate deliberately opens a minor PR next to a
major PR (`separateMajorMinor`), so the user can take the safe update without the breaking one.
Letting the major PR replace the minor PR would close exactly that safe path.

## Workflow

### Step 1 — Collect

```bash
PY <skill>/scripts/collect_prs.py [--repo OWNER/NAME] [--bot LOGIN]... [--output <tmp>/collected.json]
```

Exit codes: **0** ok (also with zero bot PRs) · **1** usage (also: no bots left to look for) ·
**2** `gh` missing or not authenticated — stop, suggest `! gh auth login` · **3** repository or PR
list not readable — report the message and stop · **4** malformed config file — show the message
and ask the user to fix the file; do not ignore it.

Stdout is a summary with `output` (the file to pass on), `bot_prs`, `bots`, `config`,
`diff_errors`, `other_open_prs`, and `truncated`. If `bot_prs` is 0, say so — name the bots
searched and how many non-bot PRs were skipped — and stop without a report. If `truncated` is
true, re-run with a higher `--limit`.

### Step 2 — Analyze

```bash
PY <skill>/scripts/analyze_prs.py --input <collected> [--newer yes|no] [--across-major yes|no] \
   [--pair-mode COVERER:COVERED=exact|newer|any]... --output <tmp>/analysis.json
```

Exit codes: **0** ok · **1** usage (bad option value, a `--pair-mode` naming an uncollected PR) ·
**3** malformed input — re-collect. The script reads no network, so re-run it freely.

Run it first with the values from the prompt or config, else the defaults. The result holds:

| Field | Meaning |
| --- | --- |
| `prs[]` | every bot PR: `status` `obsolete` / `kept` / `unevaluable`, `updates[]` (ecosystem, name, path, from, to, `major_change`), `unevaluable_reasons[]`, `ignored_lockfiles[]`, `flags` |
| `proposals[]` | the obsolete PRs: `covered_by[]`, `details[]` (each update, the PR that covers it, `relation` `equal` / `newer` / `newer-major`), `warnings[]` |
| `overlaps[]` | every PR pair sharing a package: `shared[]` with both targets and the relation (`equal`, `a-newer`, `b-newer-major`, …), `counted` and `not_counted_reason` (`different-bot`, `different-base`, `unevaluable`) |
| `pair_toggles[]` | directed pairs (`coverer`, `covered`) where a newer target exists: the `mode` in effect, whether those newer targets count now (`counts_now` `all` / `some` / `none`), and the `switch_to` mode that flips it — the candidates for Step 5 |

Which manifest lines are understood and why a PR became unevaluable is in
[references/manifest-formats.md](references/manifest-formats.md); read it when the user asks why
a PR was not evaluated.

### Step 3 — Present the comparison

Write in the conversation's language. Group by bot and base branch. Use
[references/report-format.md](references/report-format.md) for the exact tables; in short:

1. **Overview** — repository, bots, options with their origin, counts per status.
2. **Overlaps** — one row per shared package of every *counted* overlap: package, path, the
   target of each PR (`#102 → ^4.17.21 · #103 → ^5.0.0`), the relation in words ("#103 newer,
   crosses a major version").
3. **Proposed as obsolete** — PR, title, covered by, how (`same version` / `newer` / `newer
   major`), warnings.
4. **Unevaluable** — PR, title, the first reason (all reasons go to the report).
5. **Not counted** — overlaps with another bot or base branch, in one line each, so the user
   sees why they were not used.

Show every warning from `proposals[].warnings` next to its PR: an immortal Renovate PR comes back
after closing; closing a Renovate major PR ("to v5") makes Renovate ignore that whole major line;
commits by people are lost with the PR; a covering PR that is a draft, conflicts, or has failing
or pending checks still counts, but the user should know.

### Step 4 — Ask the global options

Skip this step when `pair_toggles` is empty: no pair depends on the options, so asking would be
noise. Otherwise, unless the prompt already settled both values, ask once with
`AskUserQuestion` (two questions in one call):

- "Counts a newer version as replacement?" — options *Yes* and *No*; the current value (config or
  default) first, marked recommended; mention how many pairs depend on it.
- "Also across major versions?" — *No* and *Yes*, same rule; only ask when a toggle has
  `newer_major_updates > 0` and the first answer is yes.

If an answer changes a value, re-run Step 2 with it and present the changed parts again.

### Step 5 — Per-pair exceptions

Offer the `pair_toggles` (multi-select, at most 4 options per question; batch them, and offer
"No exceptions" as an option). Each option is one directed pair, phrased by `counts_now`:
"#103 should replace #102 (lodash ^4.17.21 → ^5.0.0)" when it is `none` or `some`, "#112 should
*not* replace #111 (node 20.12-alpine → 20.15-alpine)" when it is `all`. A chosen option becomes
`--pair-mode <coverer>:<covered>=<switch_to>`; the free-text answer may name pairs too. Re-run
Step 2 with them, show what changed, and repeat until the user takes no further exceptions.
Skip the step when there are no toggles.

### Step 6 — Choose what to close

If `proposals` is empty, say so and go to Step 8. Otherwise ask with `AskUserQuestion`,
`multiSelect: true`, one option per proposal: label `#<n> <short title>`, description "covered by
#…" plus warnings in a few words. More than 4 proposals: batch them (4 per question, 4 questions
per call, successive calls after that); the free-text answer accepts "all", "all except #n", or a
list of numbers. Closing any subset of the proposals is safe — no check between them is needed.
Nothing selected: report that nothing was closed and go to Step 8.

### Step 7 — Verify, then close

Bots push to their branches at any time. Re-run Step 1 into a new file and Step 2 with the same
options and pair modes into `analysis-after.json`, then:

```bash
PY <skill>/scripts/verify_selection.py --before <analysis.json> --after <analysis-after.json> --select 101,104
```

Exit codes: **0** all safe · **1** usage (a number that was not proposed) · **3** malformed input
· **4** some changed — close only the `safe` ones; list the `changed` ones with their reasons and
offer to start over from Step 2 for them.

For each safe PR, in ascending order:

```bash
gh pr close <n> --repo <OWNER/NAME> --delete-branch --comment "<comment>"
```

Drop `--delete-branch` when the PR's `flags.cross_repository` is true. The comment is in English,
because the PR's audience is the whole project:

> Superseded by #102 — every dependency update in this pull request is also contained there
> (same or newer version). Closed by the dep-pr-cleanup skill.

With several covering PRs: "Superseded by #112 and #113 — …". Record each result; a failed close
(permissions, already closed) is reported with gh's message, and the remaining closes continue.
Never retry with other flags or force anything.

### Step 8 — Report

Write the report as specified in [references/report-format.md](references/report-format.md) to
`docs/dep-pr-cleanup/YYYY-MM-DD-<repo-name>.md` (the part after the slash). Never overwrite: if
the file exists, append `-2`, `-3`, …. Do not commit it.

### Step 9 — Summary

In the conversation: what was closed (with the covering PRs), what failed or changed, what stays
open and why (kept, unevaluable, not selected), the options used with their origin, the report
path, and "Nothing was committed."

## Non-interactive use

When `AskUserQuestion` is not available — the skill runs as a sub-agent or in a headless
session — never stall and never guess:

- Options come from the prompt, then the config file, then the defaults; there are no per-pair
  exceptions unless the prompt names them. Record the origins.
- Run Steps 1–3 and 8 only. **Close nothing**, whatever the request says: closing is a write to
  the remote that needs the user's explicit confirmation in this session.
- End with the proposals as a list the caller can act on, e.g. "Obsolete: #101 (covered by
  #102), #104 (covered by #109)", and the report path.

## Red flags

| Thought | Reality |
| --- | --- |
| "#104's title says the same as #109, close it." | Titles are not evidence. Only `analyze_prs.py` decides, from the diffs. |
| "#108 is unevaluable but obviously covered." | Unevaluable means the analysis did not understand a change. It stays open; say why. |
| "The Renovate PR covers the Dependabot PR — same package, same version." | Only PRs of the same bot replace each other. Show the overlap as not counted. |
| "The user said 'close all obsolete ones' in a sub-agent prompt." | Non-interactive runs close nothing. List the proposals instead. |
| "The analysis is ten minutes old, just close." | Re-collect and run `verify_selection.py` first; bots rebase and push constantly. |
| "Closing failed because of the branch, retry without `--delete-branch`." | Report the failure as it is; do not improvise flags. |
| "The major PR replaces the minor PR, that's cleaner." | Only when the user enabled "across major versions" or that pair's exception. |
| "Let me rebase or merge the covering PR while I'm here." | Out of scope. Closing obsolete PRs is the only write. |
| "Done — I'll commit the report." | Never commit. |
