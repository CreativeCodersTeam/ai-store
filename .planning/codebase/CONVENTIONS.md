---
last_mapped_commit: 2fa42ff6f8d70bead8b4bfd03323b316950340f8
last_mapped_at: 2026-10-09
---
# Coding Conventions

**Analysis Date:** 2026-10-09

This repository ships Agent Skills: Markdown (`SKILL.md`, `references/*.md`) plus Bash helper scripts. It has no application code, no package manifest, and no build. "Code" here means three things: skill Markdown, Bash scripts under `skills/<category>/<skill>/scripts/`, and the JSON plugin manifests.

## Naming Patterns

**Files:**
- The skill entry file is always `SKILL.md` (upper case). Example: `skills/dotnet/dotnet-reviewer/SKILL.md`.
- Reference files use kebab-case `.md` names under `references/`. Examples: `skills/dotnet/dotnet-reviewer/references/severity-taxonomy.md`, `review-checklist-security.md`, `report-format.md`.
- Scripts use kebab-case, verb-first `.sh` names. Examples: `collect-diff.sh`, `run-checks.sh`, `detect-dotnet-version.sh`, `fetch-upstream.sh`, `apply-pins.sh`.
- Behavior-test artifacts end in `-test.md` and keep the prefix they were first written with (`aspnet-auth-gap-test.md`, not `auth-gap-test.md`) so the review documents under `docs/` that cite them stay searchable.
- Bash unit tests are named `test-<script-name-without-verb-noise>.sh`. Example: `skills/tests/dotnet/dotnet-reviewer/scripts/unit/test-detect-version.sh` covers `detect-dotnet-version.sh`.

**Directories:**
- Skills: `skills/<category>/<skill-name>/`. **FACT** (enforced by `scripts/validate-skills.sh`): the directory name must equal the frontmatter `name`, 1-64 chars, regex `^[a-z0-9]+(-[a-z0-9]+)*$`.
- Families prefix their skills with the family name: `dotnet-*` (`skills/dotnet/`), `angular-*` (`skills/angular/`). The family router carries the bare name (`skills/dotnet/dotnet/`, `skills/angular/angular/`).
- Categories present: `agents-tooling` (empty), `angular`, `development`, `dotnet`, `general`, `java`, `typescript`, plus the non-shipping `tests`.

**Bash functions and variables:**
- Functions: snake_case (`usage`, `assert_eq`, `cleanup`). Private helpers get a leading underscore (`_red`, `_green`, `_ASSERT_PASSED` in `skills/tests/dotnet/dotnet-reviewer/scripts/helpers.sh`).
- Script-level config and parsed arguments: UPPER_SNAKE (`REPO_ROOT`, `MODE`, `BASELINE`, `SCRIPT_DIR`, `SKILL_DIR`, `TESTS_DIR`, `BUILD_JSON`).
- Function locals: lower case, declared with `local` (`local actual=$1 expected=$2 name=$3`).

**Plugins:**
- Plugin names are kebab-case and prefixed `cc-ai-`: `cc-ai-dotnet`, `cc-ai-angular`, `cc-ai-dev` (`skills/<category>/.claude-plugin/plugin.json`).

## SKILL.md Frontmatter

Frontmatter is exactly `name` + `description`, delimited by `---` at the very top of the file:

```markdown
---
name: dotnet-reviewer
description: Use only when explicitly requested by name — "dotnet-reviewer", "dotnet code review", or "dotnet review" — or when invoked by the dotnet-dev workflow (Phase 5), for a structured code review ... Must NOT activate on generic "review my code" requests; other-language reviewers must not be hijacked.
---
```

Rules:
- The `description` is the sole auto-load trigger. Write it as `Use when …` (knowledge skills) or `Use only when explicitly requested by name — "<name>", "/<name>", "/<plugin>:<name>" …` (workflow, reviewer, and all `development` skills).
- Explicit-invocation skills end with an exclusion clause: `Must NOT activate on its own for "<generic phrasing>" …`.
- **FACT**: `description` must be non-empty and at most 1024 characters. `scripts/validate-skills.sh` fails above that and warns above 900 (`--warn-at N` to change). Copilot silently drops an over-long skill.
- **FACT**: the current run of `bash scripts/validate-skills.sh` reports `OK — 46 SKILL.md checked, 1 warning(s)`. The warning is `skills/development/code-design/SKILL.md` at 970 chars. Check the warnings before adding prose to any `development` description.

## Skill Layout and Archetypes

Match an existing archetype. Do not invent a new layout.

| Archetype | Examples | Shape |
|-----------|----------|-------|
| Router | `skills/dotnet/dotnet/`, `skills/angular/angular/` | No best-practice content. Maps requests to sibling skills. Update it whenever a family skill is added, removed, or renamed. |
| Knowledge | `skills/dotnet/dotnet-fundamentals/`, `skills/dotnet/dotnet-aspnet/`, `skills/angular/angular-components/` | `SKILL.md` + `references/` only. No scripts, no gates. |
| Workflow | `skills/dotnet/dotnet-dev/`, `skills/angular/angular-dev/`, `skills/general/implementer/` | Phase-gated pipeline with a "Skill Map — Mandatory Bindings" table and explicit `n/a`/waiver rules. |
| Reviewer | `skills/dotnet/dotnet-reviewer/`, `skills/angular/angular-reviewer/`, `skills/general/gherkin-bdd-reviewer/` | Numbered steps driving `scripts/`, checklist `references/`, `severity-taxonomy.md`, `report-format.md`. Report goes to `docs/reviews/YYYY-MM-DD-<branch>-<mode>.md`. Explicit invocation, never auto-commit, never overwrite. |

Interactive skills must also define the sub-agent path: never stall, never guess, fall back to documented defaults, and record where each parameter came from in the report.

## Single-Sourcing of Rules

- A rule has one canonical home, normally the family's `*-fundamentals/references/` (`skills/dotnet/dotnet-fundamentals/references/`, `skills/angular/angular-fundamentals/references/`).
- Every other mention is a short context hook that restates the rule identically and links to the home.
- After editing a rule, grep the whole family for other mentions and align them. Divergent restatements are the recurring defect class; cross-family artifacts such as `skills/tests/dotnet/_shared/cancellationtoken-rule-test.md` and `options-pattern-consistency-test.md` exist because of it.

## Family Parity

The .NET and Angular families mirror each other:

| .NET | Angular |
|------|---------|
| `dotnet-dev` | `angular-dev` |
| `dotnet-fundamentals` | `angular-fundamentals` |
| `dotnet-xmldocs` | `angular-tsdoc` |
| `dotnet-sdk-builder` | `angular-library-builder` |
| `dotnet-reviewer` | `angular-reviewer` |

Apply a structural change to both sides. If you deliberately do not, state why in the change. Both reviewers carry the same three scripts: `collect-diff.sh`, `run-checks.sh`, `detect-<stack>-version.sh`.

## Code Style (Bash)

**Formatting:**
- No formatter or linter config exists (no `.shellcheckrc`, `.editorconfig`). Follow the existing style: two-space indent, `case` arms aligned in columns, `[[ … ]]` tests, `$(…)` substitution.
- `# shellcheck source=../helpers.sh` directives appear in test files, so keep scripts ShellCheck-clean by convention even though ShellCheck is not run in CI.

**Shebang and strict mode:**
- Always `#!/usr/bin/env bash`.
- Skill scripts use `set -u` (all 15 scripts under `skills/*/*/scripts/`), not `set -e`, because they inspect exit codes themselves.
- `scripts/validate-skills.sh` and `skills/tests/dotnet/dotnet-reviewer/scripts/run-tests.sh` use `set -euo pipefail`; `skills/tests/development/claude-md-downstream/scripts/run-tests.sh` uses `set -uo pipefail` so a failing test does not abort the loop.
- Target bash 3.2+ (macOS default). Do not use associative arrays, `mapfile`, or `${var,,}`.

**Script header:** every script opens with a comment stating purpose, JSON output shape, and exit codes:

```bash
#!/usr/bin/env bash

# collect-diff.sh — collect a unified diff in uncommitted or branch mode.

# Output JSON: {loc, files, file_list, diff}

# Exit codes: 0 ok (incl. empty diff), 1 usage, 2 not git, 3 baseline missing.

set -u
```

**Argument parsing:** long options in a `while`/`case` loop, a `usage()` heredoc that repeats the exit codes, `--help|-h` exits 0, unknown args exit 1 (`skills/dotnet/dotnet-reviewer/scripts/collect-diff.sh`):

```bash
while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-root) REPO_ROOT=${2:-}; shift 2 ;;
    --mode)      MODE=${2:-};      shift 2 ;;
    --help|-h)   usage; exit 0 ;;
    *) echo "unknown arg: $1" >&2; usage >&2; exit 1 ;;
  esac
done
[[ -n "$REPO_ROOT" && -n "$MODE" ]] || { usage >&2; exit 1; }
```

**Path resolution:** resolve directories from the script location, never the caller's cwd:

```bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
```

## Script Contracts

- Machine output is a single JSON object on stdout. Diagnostics go to stderr (`echo "…" >&2`).
- JSON is built with `printf` and pre-encoded fragments, e.g. `printf '{"build":%s,"format":%s,"test":%s}\n' "$BUILD_JSON" "$FORMAT_JSON" "$TEST_JSON"` (`skills/dotnet/dotnet-reviewer/scripts/run-checks.sh:103`). `jq` is a test dependency; check before relying on it inside a shipping script.
- Outcomes are signalled with documented exit codes:
  - `detect-dotnet-version.sh`: 0 ok / 1 usage / 4 no .NET project (skill applies latest-LTS fallback) / 5 malformed project file.
  - `collect-diff.sh`: 0 ok, empty diff included / 1 usage / 2 not git / 3 baseline missing.
  - `run-checks.sh`: always 0; tool failures are reported inside the JSON (`"ok":false`).
  - `scripts/validate-skills.sh`: 0 ok / 1 validation failures / 2 usage or missing dependency.
- The consuming `SKILL.md` step enumerates every exit code. Changing a script means updating three places together: the script, its `SKILL.md` step, and `skills/tests/<category>/<skill>/scripts/unit/test-<name>.sh`.

## Import Organization

Not applicable (no modules). The Bash equivalent: test files `source "$TESTS_DIR/helpers.sh"` after resolving `TESTS_DIR`/`SKILL_DIR`. Markdown cross-references are relative links to the canonical rule home.

## Error Handling

- Guard clauses with a one-line message to stderr and a specific exit code: `[[ -d "$REPO_ROOT/.git" ]] || { echo "not a git repository: $REPO_ROOT" >&2; exit 2; }`.
- Check external dependencies up front and fail with a clear message: `command -v jq >/dev/null 2>&1 || { echo "ERROR: jq is required for tests" >&2; exit 1; }` (both `run-tests.sh` files), `python3` in `scripts/validate-skills.sh` (exit 2).
- Tool-running scripts (`run-checks.sh`) capture the tool's exit code and report it in JSON instead of propagating it.

## Logging

**Framework:** plain `echo`/`printf`.

**Patterns:**
- stdout is reserved for the JSON result. All human-readable text in shipping scripts goes to stderr.
- Colour only when stdout is a TTY (`scripts/validate-skills.sh` blanks its ANSI codes when `not sys.stdout.isatty()`).
- Validator messages are prefixed `ERROR`, `WARN`, `OK`.

## Comments

**When to Comment:**
- Every script has a header comment (purpose, output, exit codes, usage).
- Comment the "why" of non-obvious choices at the point of use, e.g. the fixture-cleanup rationale at the top of `skills/tests/development/claude-md-downstream/scripts/run-tests.sh`, or why CI does not pass `--strict` in `.github/workflows/validate-skills.yml`.
- Mock executables document every supported call and env-var knob in their header (`unit/mock-dotnet/dotnet`, `mock-gh/gh`).

**JSDoc/TSDoc:** Not applicable.

## Function Design

**Size:** short helpers; most scripts are flat top-to-bottom with `usage()` as the only function.

**Parameters:** named long options (`--repo-root`, `--mode`, `--baseline`, `--repo-url`, `--cache-dir`). Test helpers take positional `actual expected name`.

**Return Values:** JSON on stdout plus exit code. Test helpers increment counters instead of exiting so a file reports all failures.

## Module Design

**Exports:** a skill "exports" only its `SKILL.md`; `references/` are loaded on demand from links inside it.

**Barrel Files:** the plugin manifest is the closest equivalent. `skills/<category>/.claude-plugin/plugin.json` lists exactly the shipping skill directories, and `.claude-plugin/marketplace.json` lists every plugin. **FACT** (validator): a skill directory missing from its category's `skills` array, or a plugin missing from the marketplace, fails validation. Do not add `$schema` to `plugin.json` and do not add `version`.

## Change Checklist

When adding or renaming a skill:
1. Directory name equals frontmatter `name`.
2. Update `README.md` (per-category table, plugin table) and the family router `SKILL.md`.
3. Add the skill to `skills/<category>/.claude-plugin/plugin.json` if the category is published (`angular`, `development`, `dotnet`).
4. Run `bash scripts/validate-skills.sh`.

---

*Convention analysis: 2026-10-09*
