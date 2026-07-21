---
name: gherkin-bdd-reviewer
description: Reviews existing Gherkin feature files and BDD step definitions against Gherkin best practices and anti-patterns. Use when asked to review .feature files, audit BDD scenarios, check Given/When/Then quality, or assess step-definition reuse and binding correctness (Reqnroll, Cucumber-JVM, Cucumber.js). Supports full-audit, branch (vs main), and uncommitted scopes. Produces a severity-tagged Markdown report under docs/reviews/ (or inline on request). Must NOT activate on generic "review my code" requests; other-language reviewers must not be hijacked. For writing or implementing BDD tests, use gherkin-bdd instead.
license: MIT
---

# gherkin-bdd-reviewer

Structured review of existing Gherkin `.feature` files and their step definitions,
producing a severity-tagged Markdown report.

## When to Use This Skill

- Reviewing or auditing `.feature` files or BDD scenarios.
- Checking Given/When/Then quality, scenario design, or tag usage.
- Assessing step-definition reuse and binding correctness.

Do **NOT** activate on a generic "review my code" request — that belongs to a code
review skill. Only activate for Gherkin/BDD-focused review. For **writing or
implementing** BDD tests, use `gherkin-bdd`. For a **mixed request** (review existing
scenarios *and* author new ones), review first with this skill, then switch to
`gherkin-bdd` for authoring.

The user may add a language preference (e.g., "in German") — apply that to the report
text only. The skill itself stays in English.

## Prerequisites

- `git` repo with a `main` branch (for `branch` mode only).
- `bash` 3.2+ (macOS default works).
- `python3` (used by `collect-diff.sh` for JSON escaping).
- No language SDK is required — the scripts are static analyzers; the suite is never
  built or run.

## Load Standards First

This skill owns **no rules of its own**. Before reviewing:

1. Load the `gherkin-bdd` skill for the canonical Gherkin best-practice rule set and
   the framework reference for the project under review. If your platform does not
   auto-load it, read `gherkin-bdd`'s `SKILL.md` and `references/gherkin-style.md`
   directly — never review without the rule set.
2. Adopt `gherkin-bdd`'s **Rule Precedence**: judge against repo-local conventions
   first, built-in rules only as fallback. A scenario that breaks a built-in rule but
   matches an explicit repo convention is **not** a finding; breaking an established
   repo convention **is** a finding.

## Workflow

Follow these steps in order.

### Step 1 — Interactive prompt

Ask the user three things, then validate against the whitelist (re-prompt on invalid
input):

1. **Mode:** `all` (audit every `.feature` file — default) · `branch` (changed vs
   `main`) · `uncommitted` (working-tree changes).
2. **Report language:** default English; capture another language if requested.
3. **Output:** write a file under `docs/reviews/` (default) or emit inline in the reply.

### Step 2 — Detect framework

Run `scripts/detect-framework.sh --repo-root <repo>`. Parse JSON `{framework,
config_files, signals}`. Use `framework` to read step-definition syntax correctly
(load the matching `gherkin-bdd/references/` file). `unknown` is valid — note it in the
report and infer step syntax from existing step files.

### Step 3 — Locate or collect artifacts

- **`all`** → `scripts/locate-artifacts.sh --repo-root <repo>` → `{feature_files,
  step_def_dirs, feature_count}`.
- **`branch` / `uncommitted`** → `scripts/collect-diff.sh --repo-root <repo> --mode
  <mode> [--baseline main]` → `{loc, files, file_list, diff}` (already restricted to
  `.feature` + step-definition files).

If there is nothing to review (zero feature files, or zero changed BDD files), report
"nothing to review" and stop. For `branch` mode, exit code 3 means `main` is missing —
abort and tell the user. Exit code 2 means not a git repo — abort.

### Step 4 — Large-set strategy gate

If `feature_count > 40` (mode `all`) OR changed `loc > 2000` (diff modes), ask the user
to choose:

- **(B) Review everything** — note the token cost in the report header.
- **(C) Prioritize** — review the largest / most-recently-changed features first;
  summarize the rest. If nothing matches the priority heuristics, fall back to **(D)**
  and note the fallback transparently in the report.
- **(D) Chunk file-by-file** — review each feature independently; group findings by file.

### Step 5 — Review

Walk each feature file and its step definitions against `references/review-checklist.md`
plus the loaded `gherkin-bdd` rules. Apply Rule Precedence. Step-definition checks are
**static** — match feature steps against binding patterns to find undefined, ambiguous,
dead, or mis-bound steps; never build or run the suite. Tag each finding
`[Severity][Category]` per `references/severity-taxonomy.md`.

### Step 6 — Render report

Generate the report exactly per `references/report-format.md`: title + metadata block,
detailed Executive Summary (counts, top-3 risks, scope), Findings ordered by severity
desc then `file:line` (each with a concrete fix), and a "Conventions Applied" note.

### Step 7 — Write report

Path: `docs/reviews/YYYY-MM-DD-bdd-<mode>.md`. Create `docs/reviews/` if missing. If the
path exists, append `-2`, `-3`, … until unique. **Never auto-commit. Never overwrite.**
If the user chose inline output, emit the report in the reply instead.

Output to chat: the file path (or "inline") and a one-line severity summary (e.g.,
`"Wrote review with 1 Critical, 3 Major findings to docs/reviews/…"`).

## Output Contract

- A single Markdown report (file under `docs/reviews/`, or inline on request).
- Format strictly per `references/report-format.md`.
- Severity and category tags from `references/severity-taxonomy.md`.

## Things This Skill Never Does

- Edits or auto-fixes `.feature` or step-definition files — it only writes a report.
- Auto-commits the report or bypasses git hooks.
- Builds or runs the BDD suite (review is static).
- Authors new scenarios — that is `gherkin-bdd`'s job.
- Includes secrets in the report or logs.
- Activates on a generic "review my code" request, or hijacks another reviewer.

## Resource Index

- `scripts/detect-framework.sh` — Reqnroll / Cucumber-JVM / Cucumber.js detection.
- `scripts/locate-artifacts.sh` — find `.feature` files and step-definition dirs.
- `scripts/collect-diff.sh` — branch/uncommitted diff restricted to BDD artifacts.
- `references/severity-taxonomy.md` — `[Severity][Category]` taxonomy + mapping.
- `references/report-format.md` — report skeleton and rules.
- `references/review-checklist.md` — rule → what-to-look-for → severity (cites `gherkin-bdd`).

## Related Skills

- **`gherkin-bdd`** — the rule authority for this reviewer and the skill to use for
  **writing** feature files and implementing step definitions.
