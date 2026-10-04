---
name: upgrade-gh-wf-actions
description: >
  Use when the user wants to upgrade, update, or bump the GitHub Actions a repository's workflows
  use — checking `uses:` references in .github/workflows or composite actions for newer versions,
  pinning actions to commit SHAs, or hardening workflows against supply-chain attacks through SHA
  pinning — and whenever it is named: "upgrade-gh-wf-actions", "/upgrade-gh-wf-actions",
  "/cc-ai-dev:upgrade-gh-wf-actions". Finds every remote action with a newer release that is at
  least a minimum age old (default 7 days, adjustable), lists action, current version, new version,
  and age, lets the user multi-select what to upgrade, and rewrites the chosen lines to
  `@<commit-sha> # vX.Y.Z`. Never commits. Must NOT activate for writing, fixing, or debugging
  workflows, configuring Dependabot or Renovate, upgrading npm, NuGet, pip, or other package
  dependencies, or changing runner images.
---

# upgrade-gh-wf-actions

Bring the actions a repository's workflows use up to date — but only to versions that have been
public long enough for a compromise to surface, and pinned to an immutable commit so the version
that was reviewed is the version that runs.

## Contract

- **Input:** the repository (the working directory's git root by default) and optionally a
  minimum age in days (default **7**).
- **Output:** a table of upgradeable actions with release-note and runtime hints in the
  conversation; after the user's selection, rewritten `uses:` lines in
  `.github/workflows/*.yml|yaml` and composite `action.yml|yaml` files, and a summary of what the
  release notes of the applied upgrades mean for this repository.
- **Not in scope:** editing workflow logic, reacting to breaking changes of a major upgrade
  (renamed inputs, new runner requirements), configuring Dependabot or Renovate.
- **Never commits.** The user reviews the diff and decides what enters history.

## Why the rules are what they are

A workflow step runs third-party code with the repository's token and secrets. Two attacks
shape this skill:

- **A malicious release.** A maintainer account or release pipeline is compromised and a new
  version ships with a payload. Such releases are typically spotted and pulled within days.
  Adopting only versions that are at least *N* days old lets that window pass first — hence the
  minimum age, and why the age must come from a timestamp an attacker cannot set.
- **A moved tag.** Tags are mutable: whoever controls the repository can repoint `v4` or even
  `v4.1.1` to another commit, and every workflow referencing the tag runs the new code on its next
  run. A 40-character commit SHA cannot be repointed. Hence every upgrade is written as
  `@<sha> # vX.Y.Z` — the SHA is what runs, the comment keeps it readable and lets Dependabot and
  Renovate continue to track the pin.

The age is the release's `publishedAt`, which GitHub sets server-side. Repositories that publish
no releases only have tag and commit dates, which their author chooses freely; such ages are
shown but flagged as unverified, so the user can weigh them.

**Never write a SHA from memory or from a web page.** Every SHA comes from `check-updates.sh`,
which reads it from the action's own repository tags. A SHA typed by hand can point into a fork
(GitHub resolves fork commits through the parent repository), which is exactly the impostor-commit
attack SHA pinning is supposed to prevent.

## Prerequisites

- `gh` (GitHub CLI), authenticated (`gh auth status`). The scripts use the GraphQL API, which
  requires authentication even for public repositories.
- `jq`, `bash` 3.2+ (macOS default works).

If `gh` is missing or not authenticated, stop and tell the user — suggest `! gh auth login`.
Do not fall back to scraping github.com: the guarantees above depend on the API data.

## Parameters

| Parameter          | Default                         | How the user changes it                                       |
| ------------------ | ------------------------------- | ------------------------------------------------------------- |
| Minimum age (days) | 7                               | "with a minimum age of 14 days", "only 3 days old is fine"    |
| Repository root    | `git rev-parse --show-toplevel` | names another directory                                       |
| Excluded paths     | none                            | names directories to skip (see Step 2 for test fixtures)      |

The user may raise **or lower** the minimum age. Lowering it below 7 is their call — accept it,
but say in one line that it shortens the window in which a malicious release would be caught.
Record whether the value is the default or user-set; the table header shows it.

## Workflow

The scripts live in this skill's `scripts/` directory; call them by absolute path. Keep the
intermediate JSON in a temporary directory, not in the repository.

### Step 1 — Preflight

```bash
ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
gh auth status >/dev/null 2>&1 || echo "gh not authenticated"
```

### Step 2 — Scan

```bash
bash <skill>/scripts/scan-actions.sh --root "$ROOT" [--exclude <path>]... > "$TMP/scan.json"
```

Exit codes: **0** ok (also when nothing was found) · **1** usage · **2** root is not a directory.

`files[]` lists what was scanned: the top-level `.github/workflows/*.yml|yaml` and every
`action.yml|yaml` below the root (excluding `.git` and `node_modules`). If any of those are
plainly test fixtures or examples rather than real workflows (paths under `tests/`, `fixtures/`,
`testdata/`, `examples/`), re-run with `--exclude` for those paths and mention it in the result.

If `occurrences` is empty, report "no remote actions found" with the scanned file list and stop.

### Step 3 — Check for upgrades

```bash
bash <skill>/scripts/check-updates.sh --scan "$TMP/scan.json" --min-age-days <N> > "$TMP/updates.json"
```

Exit codes: **0** ok — per-repository failures (repository not found, no access, rate limit) are
reported in `errors[]` and as groups with `status: "error"`, they do not abort the run ·
**1** usage · **2** `gh` missing or not authenticated · **3** malformed scan input.

The output has one **group** per (action repository, ref) — `github/codeql-action/init@v3` and
`github/codeql-action/analyze@v3` share one group, so they are upgraded together and never end up
on different versions. Each group carries 0–3 **rows**, each with a unique numeric `id`:

| Row                         | Meaning                                                                                  |
| --------------------------- | ---------------------------------------------------------------------------------------- |
| `upgrade`, `major: true`    | Newest eligible version, crossing a major version — may contain breaking changes         |
| `upgrade`, `major: false`   | Newest eligible version within the current major                                         |
| `upgrade`, `major: null`    | Current version unknown (branch ref, unidentifiable SHA) — newest eligible version        |
| `pin`                       | Nothing newer within the current major, but the ref is a mutable tag — pin it to its SHA |
| `pin`, `downgrade: true`    | The version the tag currently resolves to is younger than the minimum age; this pins the newest version that is old enough |

How the current version is determined and which versions count as eligible is specified in
[references/version-resolution.md](references/version-resolution.md). Read it when a result
looks surprising or the user asks why something was or was not offered.

Three more fields feed the hints in Step 4. They are keyword matches and raw values, not verdicts —
read them and judge:

- `rows[].notes_flags` — release-note lines between the current and the target version that
  mention breaking changes, removals, deprecations, or runner requirements.
- `current_warnings` — lines from releases newer than the current one that announce a
  deprecation, sunset, or shutdown, a hint that the version in use may stop working.
- `runtimes` / `rows[].target_runtimes` — `runs.using` at the current and at the target version.
  Judge them with [references/runtime-support.md](references/runtime-support.md).

### Step 4 — Present the table

One row per `rows[]` entry, numbered by its `id`, groups in output order. The header line states
the minimum age and its origin. Write the table in the conversation's language; the English
layout is:

```markdown
Minimum age: 7 days (default)

| #  | Action                               | Current version            | New version        | Age of new version   |
| -- | ------------------------------------ | -------------------------- | ------------------ | -------------------- |
| 1  | actions/checkout                     | v5 (= v5.1.0)              | v7.0.1 · MAJOR     | 76 days              |
| 2  | actions/checkout                     | v5 (= v5.1.0)              | v5.1.0 · PIN       | 76 days              |
| 3  | github/codeql-action (init, analyze) | v3 (= v3.38.2)             | v3.38.1 · PIN ↓    | 16 days              |
| 4  | some-org/tag-only-action             | 1a2b3c4 (v1.2.0)           | v1.4.0             | 30 days (tag date, unverified) |
| 5  | actions/setup-node                   | v4.0.0                     | v4.4.0 ⚠           | 538 days             |
```

Cell rules:

- **Action:** `repo`; when the group's `actions[]` contain subpaths, list them in parentheses.
  For a reusable workflow, the workflow file name.
- **Current version:** `ref` as written; for a floating tag add the resolved version
  (`v5 (= v5.1.0)`); for a SHA the first 7 characters plus the version in parentheses; `unknown`
  when `current_version` is null.
- **New version:** `target_version`, plus `MAJOR` for `major: true`, `PIN` for `kind: "pin"`,
  `↓` for `downgrade: true`, and `⚠` when the row has a hint (see below).
- **Age:** `age_days` days; append `(tag date, unverified)` when `age_reliable` is false.

Below the table, give the **hints** — one short line each, citing the version and the release
note where it came from:

- **⚠ on a row** when its `notes_flags` contain something the user should know before choosing
  (a breaking change, a removed input, a new runner minimum), or when a `target_runtimes` entry
  is a runtime that [runtime-support.md](references/runtime-support.md) lists as removed
  ("v4.4.0 still declares node20"). Skip flags that are plainly harmless — a dependency bump whose
  PR title happens to say "breaking" is not a breaking change of the action.
- **Current version at risk** when a `current_warnings` line really concerns the version in use
  (e.g. "v3 will stop working on …", "releases before 3.4.0 use a retired service"), or when a
  `runtimes` entry is a removed runtime. Leave out warnings about unrelated features.

Then list briefly what is **not** offered, so nothing disappears silently:

- `blocked-by-age` groups and every `too_young` entry: "v4.38.2 exists but is 3 days old —
  eligible in 4 days".
- `error` groups with their message; `unknown-current` and `no-versions` groups.
- `scan_skipped` entries of `updates.json` (the scan's `skipped[]`, passed through: local `./` actions, `docker://` images, malformed lines).
- The number of `up-to-date` groups.
- For each `MAJOR` row, its `compare_url` or `release_url`, since breaking changes need review.

If there are no rows at all, say that everything is current (or blocked by age) and stop.

### Step 5 — Let the user choose

Ask with `AskUserQuestion`, `multiSelect: true`. The tool takes at most 4 options per question and
4 questions per call, so batch the rows:

- One option per row. Label: `#<id> <action> → <target_version>` (shorten long action names).
  Description: the marker (`MAJOR`, `PIN`, `PIN ↓`), the age, "unverified age" when applicable,
  and the ⚠ hint in a few words ("still node20", "removes input `foo`").
- Keep the rows of one group in the same question — they are alternatives to each other.
- A question needs at least 2 options: if a batch would hold a single row, add the option
  "None of these".
- More than 16 rows: ask in successive calls, in table order.
- The automatic "Other" answer is free text: accept "all", "all except MAJOR", or a list of row
  numbers, and resolve it against the table. "all" with two rows of one group is an overlap, see
  below.

Then check the selection:

- **Overlap:** two rows of the same group selected (e.g. the MAJOR row and the PIN row of one
  action). Ask a single-select question which of the two to apply. Never pick one yourself.
- **Nothing selected:** report that nothing was changed and stop.

### Step 6 — Apply

```bash
bash <skill>/scripts/apply-pins.sh --updates "$TMP/updates.json" --select <id,id,...> --root "$ROOT"
```

Exit codes: **0** all applied · **1** usage · **3** malformed input or unknown row id ·
**4** a target line changed since the scan — nothing written; re-run from Step 2 and present
the new table · **5** overlapping rows selected — nothing written; resolve as in Step 5.

The script rewrites every occurrence of each selected row to `@<target_sha> # <target_version>`,
keeps indentation and quoting, replaces an old version comment and keeps any other comment text.
It writes all or nothing. Use it rather than editing lines by hand: it guarantees that the SHA
written is the one `check-updates.sh` resolved from the tag, and that every occurrence of the
group moves together.

### Step 7 — Verify

1. Re-run `scan-actions.sh` and confirm, for every `applied[]` entry, that the occurrence at
   that file and line now has `ref_type: "sha"`, `ref` equal to the entry's `target_sha`, and
   `comment_version` equal to its `target_version`. Report any mismatch as a failure; do not paper
   over it.
2. Show `git diff --stat` and the changed `uses:` lines.
3. If `actionlint` is installed, run it on the changed files and report its result; if not, say
   that no workflow linter was run.

### Step 8 — Read the release notes of what was applied

For every applied `upgrade` row whose current version is known — majors and non-majors alike;
pin rows change no version and are skipped:

```bash
bash <skill>/scripts/release-notes.sh --repo <repo> --from <current_version> --to <target_version>
```

Exit codes: **0** ok (also for an empty range) · **1** usage (`--from`/`--to` must be full
`vX.Y.Z` versions) · **2** `gh` missing or not authenticated · **4** query failed — say that the
notes could not be read for that action and continue with the others.

Read the bodies and extract only what matters for this repository: breaking changes, removed or
renamed inputs and outputs, new permission or runner requirements, and deprecations. Compare
removed or renamed inputs with the `with:` block under each changed `uses:` line — "`cache-path`
was renamed, and `ci.yml:14` uses it" is the finding the user needs; a list of every release
headline is not. If `truncated` is true, say that older notes in the range were not read. Do not
change workflow logic to follow the notes — report what needs doing.

An applied `upgrade` row whose current version is unknown (a branch ref like `main`, an
unidentifiable SHA) has no range to read. Say so and give its `release_url` instead of a
summary.

### Step 9 — Summary

- Table of applied changes: action, old → new, SHA (first 12 characters), files and lines.
- The release-note findings from Step 8 per action, with the release link; "no relevant
  changes" when there were none.
- Runtime warnings that remain after the change (a pinned version that still declares a removed
  runtime).
- What was not offered and why (from Step 4), in one or two lines.
- "Nothing was committed."

## Non-interactive use

When `AskUserQuestion` is not available — the skill runs as a sub-agent or in a headless
session — never stall and never guess a selection:

- If the request already states the selection ("upgrade all", "only non-major upgrades",
  "pin everything", "upgrade actions/checkout"), resolve it deterministically against the table:
  "non-major" = rows with `major` not `true`; "pin" = `kind: "pin"` rows; an action name = that
  group's rows. If that leaves two rows of one group (e.g. "upgrade all"), take the
  `major: true` row only when the request explicitly allowed major upgrades, otherwise the other
  row. Apply, verify, read the release notes (Step 8), and state in the summary how the
  selection was derived from the request. When a chosen row carries a ⚠ hint — most often a
  target that still declares a removed runtime — apply it as requested, but name the hint in the
  summary together with the row that would avoid it, or say that no offered row avoids it.
- Otherwise, present the table (Step 4), write nothing, and end with the row ids the caller can
  pass back.
- The minimum age is the default 7 unless the request names another value; record the origin.

## Red flags

| Thought                                                         | Reality                                                                                      |
| --------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| "I know the SHA for checkout v4, I'll just write it."           | SHAs come only from `check-updates.sh`. A remembered or copied SHA is unverified.            |
| "The newest release is 2 days old, close enough."               | The minimum age is the point. Only the user changes it.                                      |
| "Both rows look fine, I'll take the major one."                 | Overlapping rows go back to the user as a single-select question.                            |
| "The script failed on one line, I'll edit that one manually."   | Exit 4 means the file changed since the scan. Re-scan; do not patch around it.               |
| "The tag-only action's age looks fine."                         | Tag and commit dates are author-controlled. Keep the "unverified" flag visible.              |
| "Let me also fix the deprecated input while I'm here."          | Out of scope. Point at the release notes; do not change workflow logic.                      |
| "The notes say BREAKING somewhere, I'll flag every row."        | Read the flagged line. A ⚠ that fires on everything tells the user nothing.                  |
| "It's only a pin, no need to look at the runtime."              | A pin to a version that declares a removed runtime is the most common trap. Check `target_runtimes`. |
| "Done — I'll commit the pins."                                  | Never commit.                                                                                |
