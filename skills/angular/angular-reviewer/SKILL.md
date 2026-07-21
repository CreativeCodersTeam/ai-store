---
name: angular-reviewer
description: Performs structured code reviews on Angular 17+ projects. Reviews either uncommitted working-tree changes or committed changes on the current feature branch (vs. main). Produces a Markdown report under docs/reviews/ with severity-tagged findings ([Critical|Major|Minor|Suggestion|Nitpick][Security|Performance|Architecture|Code-Quality|Tests|Angular-Idioms]) and fix suggestions. Must NOT activate on generic "review my code" requests; other-language reviewers must not be hijacked.
---

# angular-reviewer

Structured code review for Angular 17+ projects.

## When to Use This Skill

A code review for an Angular 17+ project is needed.
The user may add language preferences (e.g., "in German") — apply that to the report only. The skill itself remains in English.

## Prerequisites

- `git` repo with `main` branch (for branch mode).
- Node.js + npm and the Angular CLI (`ng`, via `npx` or a local devDependency) if any of build/lint/test will run.
- `bash` 3.2+ available (macOS default works).
- `python3` available (used by scripts for safe JSON encoding).

## Workflow

Follow these steps in order.

### Step 1 — Interactive prompt

Ask the user three things:

1. **Mode:** `uncommitted` (working-tree vs HEAD, includes staged/unstaged/untracked) or `branch` (current branch vs `main`).
2. **Tools:** for each of `build`, `lint`, `test` — yes or no. Default no for all three.
3. **Report language:** default English. If they want another language, capture it.

Validate inputs against the whitelist. Re-prompt on invalid input.

### Step 2 — Detect Angular version

Run `scripts/detect-angular-version.sh --repo-root <repo>`.

- Exit 0: parse JSON `{version, projects, project_files}`. Use the detected Angular major to drive checklist selection.
- Exit 4 (Angular < 17 or none): abort. Tell the user "this skill targets Angular 17+; detected `<X>`."
- Exit 5 (malformed): show the offending file. Ask the user whether to proceed without version-awareness. If yes, fall back to general checklists only.
- Exit 2 (not a directory) or 1 (usage): bug — report and abort.

### Step 3 — Collect diff

Run `scripts/collect-diff.sh --repo-root <repo> --mode <mode> --baseline main`.

- Exit 0 with `files == 0`: report "no changes to review" and exit.
- Exit 0 with `files > 0`: continue.
- Exit 2: not a git repo — abort.
- Exit 3 (branch mode, missing `main`): abort, tell user.

### Step 4 — Large-diff strategy gate

If `loc > 2000` OR `files > 50`, ask the user to choose:

- **(B) Review everything** — note token cost in report header.
- **(C) Prioritize** — review files matching `*.service.ts`/`*-service.ts`, `*.component.ts`, `*.store.ts`/`*-store.ts`, and (under the v20 suffix-less convention) the non-spec `.ts` files that declare a `@Component`/`@Injectable`/`@Directive`; review files without a sibling `*.spec.ts` first; summarize the rest.
- **(D) Chunk file-by-file** — review each file independently; group findings by file.

If C is chosen but no files match the priority heuristics, fall back to D and note the fallback transparently in the report.

### Step 5 — Run requested tool checks

For each tool the user selected, invoke `scripts/run-checks.sh --repo-root <repo>` with the appropriate flag(s). Parse JSON.

If a tool isn't installed/configured, the script reports the failure inside the JSON — log "X not available, skipping" and continue. Don't abort.

### Step 6 — Review

Walk the diff against:
1. The Angular idioms checklist (`references/review-checklist-angular.md`).
2. `references/review-checklist-security.md`.
3. `references/review-checklist-performance.md`.
4. `references/review-checklist-architecture.md`.
5. `references/review-checklist-code-quality.md`.

Fold tool findings into the issue list using the severity mapping defined in `references/severity-taxonomy.md`:
- `ng build` errors → Critical
- `ng build` warnings → Minor
- `ng test` failures → Critical
- `ng lint` violations → Suggestion

Each finding MUST include a fix suggestion as a code block (`typescript` fenced) — no auto-patching.

### Step 7 — Render report

Generate the report following `references/report-format.md` exactly:
- Title + metadata block
- Detailed Executive Summary (counts, top-3 risks, LOC, scope)
- Findings ordered by severity desc, then file path asc
- Tool Output Appendix

### Step 8 — Write report

Path: `docs/reviews/YYYY-MM-DD-<branch>-<mode>.md`. Branch name is sanitized (replace `/` with `-`).

If the path exists, append `-2`, `-3`, … until unique. Create `docs/reviews/` if missing. **Never auto-commit. Never overwrite.**

Output to chat: the file path and a one-line summary (e.g., `"Wrote review with 2 Critical, 5 Major findings to docs/reviews/…"`).

## Output Contract

- Single Markdown file under `docs/reviews/`.
- Format strictly per `references/report-format.md`.
- Severity and area tags from `references/severity-taxonomy.md`.

## Resource Index

- `scripts/detect-angular-version.sh` — Angular version / workspace project detection
- `scripts/collect-diff.sh` — diff collection with exclusions
- `scripts/run-checks.sh` — optional `ng build`/`ng lint`/`ng test`
- `references/severity-taxonomy.md`
- `references/report-format.md`
- `references/review-checklist-angular.md`
- `references/review-checklist-security.md`
- `references/review-checklist-performance.md`
- `references/review-checklist-architecture.md`
- `references/review-checklist-code-quality.md`

## Things This Skill Never Does

- Auto-patches or auto-commits the report.
- Bypasses git hooks (`--no-verify`, `--no-gpg-sign`).
- Runs destructive operations as "fixes" (no `git reset`, no deletions).
- Includes secrets in logs or the report.
- Reviews Angular versions below 17 — aborts with a clear message.

## Related Skills

- **[angular-fundamentals](../angular-fundamentals/SKILL.md)** — Review findings reference DI scopes, the `provide`/config pattern, and modern idioms
- **[angular-tsdoc](../angular-tsdoc/SKILL.md)** — Code-quality checklist references TSDoc documentation conventions
- **[angular-tester](../angular-tester/SKILL.md)** — Test-quality findings reference this skill's expectations
- **[angular-state](../angular-state/SKILL.md)** — State/data findings reference these best practices
- **[angular-components](../angular-components/SKILL.md)** — UI/accessibility/routing findings reference this skill's conventions
- **[angular-package-manager](../angular-package-manager/SKILL.md)** — Surfaced outdated/vulnerable packages are addressed via this skill
