---
name: dotnet-reviewer
description: Use only when explicitly requested by name — "dotnet-reviewer", "dotnet code review", or "dotnet review" — or when invoked by the dotnet-dev workflow (Phase 5), for a structured code review of a .NET 10+ project (uncommitted working-tree changes or current feature branch vs. main). Must NOT activate on generic "review my code" requests; other-language reviewers must not be hijacked.
---

# dotnet-reviewer

Structured code review for .NET 10+ projects.

## When to Use This Skill

Activate **only** on explicit invocation:

- The user requests it by name — the phrases `dotnet-reviewer`, `dotnet code review`, or `dotnet review`.
- The `dotnet-dev` workflow invokes it in its Phase 5 — this counts as explicit invocation.

Must NOT activate on generic "review my code" requests; other-language reviewers must not be hijacked. The target is a .NET 10+ project (enforced in Step 2).

The user may add language preferences (e.g., "in German") — apply that to the report only. The skill itself remains in English.

## Prerequisites

- `git` repo with `main` branch (for branch mode).
- `dotnet ≥ 10` SDK if any of build/format/test will run.
- `bash` 3.2+ available (macOS default works).
- `python3` available (used by scripts for safe JSON encoding).

## Workflow

Follow these steps in order.

### Step 1 — Determine review parameters

Three parameters drive the review:

1. **Mode:** `uncommitted` (working-tree vs HEAD, includes staged/unstaged/untracked) or `branch` (current branch vs `main`).
2. **Tools:** for each of `build`, `format`, `test` — yes or no. Default no for all three.
3. **Report language:** default English. If they want another language, capture it.

**Interactive invocation (default):** ask the user for all three. Validate inputs against the whitelist. Re-prompt on invalid input.

**Non-interactive invocation:** when the invocation context already supplies parameters (e.g. the dispatching prompt of a calling workflow such as `dotnet-dev` Phase 5, or a sub-agent prompt), skip the prompt for those parameters and validate the supplied values the same way. When no user is reachable (you are running as a sub-agent) and a parameter is missing, do not guess and do not stall — use the defaults `mode=uncommitted`, all tools `no`, language English. Record every parameter and its origin (`provided` / `default`) in the report metadata block.

### Step 2 — Detect .NET version

Run `scripts/detect-dotnet-version.sh --repo-root <repo>`.

- Exit 0: parse JSON `{sdk, target_frameworks, project_files}`. Pick the highest `net<N>.0` from `target_frameworks` to drive checklist selection.
- Exit 4 (SDK < 10 or none): abort. Tell the user "this skill targets .NET 10+; detected `<X>`."
- Exit 5 (malformed): show offending file. Ask the user whether to proceed without version-awareness. If yes, fall back to general checklists only.
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
- **(C) Prioritize** — review files matching `*Service.cs`, `*Controller.cs`, files without sibling `*.Tests/*Tests.cs` first; summarize the rest.
- **(D) Chunk file-by-file** — review each file independently; group findings by file.

If C is chosen but no files match the priority heuristics, fall back to D and note the fallback transparently in the report.

**Non-interactive invocation:** do not ask — automatically choose **(D) Chunk file-by-file** and note the automatic selection in the `Review strategy` line of the report header (e.g. `chunked (auto-selected, non-interactive)`).

### Step 5 — Run requested tool checks

For each tool the user selected, invoke `scripts/run-checks.sh --repo-root <repo>` with the appropriate flag(s). Parse JSON.

If a tool isn't installed, the script reports the failure inside the JSON — log "X not available, skipping" and continue. Don't abort.

### Step 6 — Review

Walk the diff against:
1. The version-specific checklist (`references/review-checklist-net<N>.md`).
2. `references/review-checklist-security.md`.
3. `references/review-checklist-performance.md`.
4. `references/review-checklist-architecture.md`.
5. `references/review-checklist-code-quality.md`.

Fold tool findings into the issue list using the severity mapping defined in `references/severity-taxonomy.md`:
- `dotnet build` errors → Critical
- `dotnet build` warnings → Minor
- `dotnet test` failures → Critical
- `dotnet format` violations → Suggestion

Each finding MUST include a fix suggestion as a code block (`csharp` fenced) — no auto-patching.

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

- `scripts/detect-dotnet-version.sh` — SDK / target framework detection
- `scripts/collect-diff.sh` — diff collection with exclusions
- `scripts/run-checks.sh` — optional dotnet build/format/test
- `references/severity-taxonomy.md`
- `references/report-format.md`
- `references/review-checklist-net10.md`
- `references/review-checklist-security.md`
- `references/review-checklist-performance.md`
- `references/review-checklist-architecture.md`
- `references/review-checklist-code-quality.md`

## Things This Skill Never Does

- Auto-patches or auto-commits the report.
- Bypasses git hooks (`--no-verify`, `--no-gpg-sign`).
- Runs destructive operations as "fixes" (no `git reset`, no deletions).
- Includes secrets in logs or the report.
- Reviews .NET versions below 10 — aborts with a clear message.

## Related Skills

- **[dotnet-fundamentals](../dotnet-fundamentals/SKILL.md)** — Review findings reference DI lifetime, Options, and configuration best practices
- **[dotnet-xmldocs](../dotnet-xmldocs/SKILL.md)** — Code-quality checklist references XML documentation conventions
- **[dotnet-tester](../dotnet-tester/SKILL.md)** — Test-quality findings reference this skill's expectations
- **[dotnet-ef-core](../dotnet-ef-core/SKILL.md)** — EF Core findings reference these data-access best practices
- **[dotnet-aspnet](../dotnet-aspnet/SKILL.md)** — ASP.NET Core findings reference this skill's conventions
- **[dotnet-nuget-manager](../dotnet-nuget-manager/SKILL.md)** — Surfaced outdated/vulnerable packages are addressed via this skill
- **[dotnet-inspect](../dotnet-inspect/SKILL.md)** — Used to investigate API surface and version diffs during review
