---
name: angular-reviewer
description: Use only when a structured Angular code review is explicitly requested by name — "angular-reviewer", "angular code review", or "angular review" — on an Angular 17+ project, or when invoked by the angular-dev workflow (Phase 5). Must NOT activate on generic "review my code" requests, and must not take over reviews of non-Angular code.
---

# angular-reviewer

Structured code review for Angular 17+ projects.

## When to Use This Skill

Only when explicitly requested by name — "angular-reviewer", "angular code review", or "angular review" — on an Angular 17+ project, or when invoked programmatically by the `angular-dev` workflow (Phase 5). Do NOT activate on generic "review my code" requests, and do not take over reviews of non-Angular code.

The user may add language preferences (e.g., "in German") — apply that to the report only. The skill itself remains in English.

## Prerequisites

- `git` repo with a baseline branch (default `main`) for branch mode.
- Node.js + npm and the Angular CLI (`ng`, via `npx` or a local devDependency) if any of build/lint/test will run.
- `bash` 3.2+ available (macOS default works).
- `python3` available (used by scripts for safe JSON encoding).

## Workflow

Follow these steps in order.

### Step 1 — Interactive prompt

**Programmatic invocation** (by `angular-dev` or inside a sub-agent, which cannot prompt the user): skip the interactive prompt — the caller supplies mode, tools, and report language in the invocation; anything unspecified uses the defaults (mode `uncommitted`, all tools no, English).

Otherwise, ask the user three things:

1. **Mode:** `uncommitted` (working-tree vs HEAD, includes staged/unstaged/untracked) or `branch` (current branch vs a baseline branch, default `main` — capture a different baseline if the user names one).
2. **Tools:** for each of `build`, `lint`, `test` — yes or no. Default no for all three.
3. **Report language:** default English. If they want another language, capture it.

Validate: mode ∈ {uncommitted, branch}; each tool ∈ {yes, no}; the report language is free text. Re-prompt on an invalid mode or tool value.

### Step 2 — Detect Angular version

Run `scripts/detect-angular-version.sh --repo-root <repo>`.

- Exit 0: parse JSON `{version, projects, project_files}`. Use the detected Angular major to drive checklist selection.
- Exit 4 (Angular < 17 or none): abort. Tell the user "this skill targets Angular 17+; detected `<X>`."
- Exit 5 (malformed): show the offending file. Ask the user whether to proceed without version-awareness. If yes, fall back to general checklists only.
- Exit 2 (not a directory) or 1 (usage): bug — report and abort.

### Step 3 — Collect diff

Run `scripts/collect-diff.sh --repo-root <repo> --mode <mode> --baseline <baseline>` (default `main`).

- Exit 0 with `files == 0`: report "no changes to review" and exit.
- Exit 0 with `files > 0`: continue.
- Exit 2: not a git repo — abort.
- Exit 3 (branch mode, baseline not found): tell the user, ask for the correct baseline branch, and re-run.
- Exit 4 (uncommitted mode, repo has no commits yet): abort, tell user.

### Step 4 — Large-diff strategy gate

If `loc > 2000` OR `files > 50`, ask the user to choose:

- **(A) Review everything** — note token cost in report header.
- **(B) Prioritize** — review files matching `*.service.ts`/`*-service.ts`, `*.component.ts`, `*.store.ts`/`*-store.ts`, and (under the v20 suffix-less convention) the non-spec `.ts` files that declare a `@Component`/`@Injectable`/`@Directive`; review files without a sibling `*.spec.ts` first; summarize the rest.
- **(C) Chunk file-by-file** — review each file independently; group findings by file.

If B is chosen but no files match the priority heuristics, fall back to C and note the fallback transparently in the report.

### Step 5 — Run requested tool checks

For each tool the user selected, invoke `scripts/run-checks.sh --repo-root <repo>` with the appropriate flag(s). Parse JSON. The script detects the configured test runner (Karma/Jest/Vitest) from `angular.json` and applies runner-specific flags itself (e.g. `--browsers` only for Karma).

If a tool isn't installed/configured, the script reports the failure inside the JSON — log "X not available, skipping" and continue. Don't abort.

### Step 6 — Review

Walk the diff against:
1. The Angular idioms checklist (`references/review-checklist-angular.md`).
2. `references/review-checklist-reactivity.md` — leaks, race conditions, side effects; run its Detection Sweep actively over the diff, don't just read it.
3. `references/review-checklist-security.md`.
4. `references/review-checklist-performance.md`.
5. `references/review-checklist-architecture.md`.
6. `references/review-checklist-code-quality.md`.

Fold tool findings into the issue list using the "Mapping from Tool Outputs" table in `references/severity-taxonomy.md`.

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
- `references/review-checklist-reactivity.md` — observable/subscription leaks, memory leaks, race conditions, side effects
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
- **[angular-rxjs](../angular-rxjs/SKILL.md)** — Fix patterns for Reactivity findings (operator choice, error-surviving streams, signal interop)
- **[angular-tsdoc](../angular-tsdoc/SKILL.md)** — Code-quality checklist references TSDoc documentation conventions
- **[angular-tester](../angular-tester/SKILL.md)** — Test-quality findings reference this skill's expectations
- **[angular-state](../angular-state/SKILL.md)** — State/data findings reference these best practices
- **[angular-components](../angular-components/SKILL.md)** — UI/accessibility/routing findings reference this skill's conventions
- **[angular-package-manager](../angular-package-manager/SKILL.md)** — Surfaced outdated/vulnerable packages are addressed via this skill
- **[angular-dev](../angular-dev/SKILL.md)** — Gated end-to-end implementation workflow that invokes this skill as a mandatory binding
