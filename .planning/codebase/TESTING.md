---
last_mapped_commit: 2fa42ff6f8d70bead8b4bfd03323b316950340f8
last_mapped_at: 2026-10-09
---
# Testing Patterns

**Analysis Date:** 2026-10-09

Testing happens on three levels:
1. **Static validation** of every `SKILL.md` and manifest (`scripts/validate-skills.sh`).
2. **Bash unit suites** for skill scripts, under `skills/tests/<category>/<skill>/scripts/`.
3. **Skill-behavior artifacts** (`*-test.md`) for behavior Bash cannot assert, plus one eval harness (`skills/tests/development/code-design/evals/`).

## Test Framework

**Runner:**
- Hand-rolled Bash. No bats, no shunit2. Each suite has its own `run-tests.sh` that loops over `unit/test-*.sh`.
- Requires `bash` 3.2+, `git`, `jq`, `python3`. The `dotnet` SDK and a GitHub login are not needed (mocked).
- Validator: `scripts/validate-skills.sh` (Bash wrapper around an inline Python 3 script, stdlib only).

**Assertion Library:**
- `helpers.sh` per suite, sourced by every test file. Provides `assert_eq`, `assert_exit`, `assert_json_eq` (via `jq -r`), `fail`, `summary` (`skills/tests/dotnet/dotnet-reviewer/scripts/helpers.sh`). The other two suites have their own copy at `skills/tests/development/claude-md-downstream/scripts/helpers.sh` and `skills/tests/development/upgrade-gh-wf-actions/scripts/helpers.sh`.

**Run Commands:**

```bash
bash scripts/validate-skills.sh                                        # validate all SKILL.md + manifests
bash scripts/validate-skills.sh --warn-at 800                          # stricter description-length warning

bash skills/tests/dotnet/dotnet-reviewer/scripts/run-tests.sh          # builds fixtures on first run
bash skills/tests/dotnet/dotnet-reviewer/scripts/unit/test-detect-version.sh   # one file
bash skills/tests/dotnet/dotnet-reviewer/scripts/clean-fixtures.sh     # drop generated repo-*/ fixtures

bash skills/tests/development/claude-md-downstream/scripts/run-tests.sh   # rebuilds + removes git fixtures
KEEP_FIXTURES=1 bash skills/tests/development/claude-md-downstream/scripts/run-tests.sh  # keep for debugging
bash skills/tests/development/claude-md-downstream/scripts/clean-fixtures.sh

bash skills/tests/development/upgrade-gh-wf-actions/scripts/run-tests.sh  # static fixtures, nothing to clean
```

No watch mode, no coverage tooling.

## Test File Organization

**Location:** separate tree, never inside the skill. `skills/tests/` mirrors `skills/<category>/<skill>/` so the subject of a test is its path. Category directories hold only shippable skills.

**Naming:**
- Bash: `unit/test-<subject>.sh`.
- Behavior artifacts: `<prefix>-test.md`, prefix frozen at creation.
- Family-wide artifacts (fix touched more than one skill): `skills/tests/<category>/_shared/*-test.md`.

**Structure:**

```
skills/tests/
├── dotnet/
│   ├── _shared/                         # cancellationtoken-rule-test.md, version-cascade-test.md, ...
│   ├── dotnet-aspnet/aspnet-auth-gap-test.md
│   └── dotnet-reviewer/scripts/
│       ├── run-tests.sh  helpers.sh  clean-fixtures.sh  README.md
│       ├── fixtures/make-fixtures.sh    # generates repo-net10, repo-net8, repo-malformed-csproj, ...
│       ├── unit/test-collect-diff.sh  test-detect-version.sh  test-run-checks.sh
│       ├── unit/mock-dotnet/dotnet      # MOCK_DOTNET_MODE-driven fake SDK
│       └── integration/test-skill-flow.md   # manual checklist, not run by run-tests.sh
├── development/
│   ├── _shared/explicit-invocation-test.md
│   ├── claude-md-downstream/scripts/   # unit/test-fetch-upstream.sh, test-match-version.sh; git fixtures
│   ├── upgrade-gh-wf-actions/scripts/  # unit/test-{apply-pins,check-updates,release-notes,scan-actions}.sh
│   │   ├── mock-gh/gh                  # fake gh CLI
│   │   └── fixtures/gh-data/ repo-basic/ repo-empty/ shas.json   # committed, static
│   └── code-design/evals/              # evals.json, grade_mechanical.py, fixtures/{pricing,reports,shop,textkit}
└── angular/
    └── _shared/version-cascade-test.md, angular-dev/, angular-reviewer/, angular-rxjs/
```

**FACT**: 52 `*-test.md` artifacts exist under `skills/tests/`.

## Test Structure

**Suite Organization** (`skills/tests/dotnet/dotnet-reviewer/scripts/unit/test-detect-version.sh`):

```bash
#!/usr/bin/env bash
set -u
TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TESTS_DIR="${TESTS_DIR:-$(cd "$TEST_DIR/.." && pwd)}"
SKILL_DIR="${SKILL_DIR:-$(cd "$TESTS_DIR/../../../../dotnet/dotnet-reviewer" && pwd)}"
FIX="$TESTS_DIR/fixtures"
SCRIPT="$SKILL_DIR/scripts/detect-dotnet-version.sh"

# shellcheck source=../helpers.sh

source "$TESTS_DIR/helpers.sh"

# 1. Happy path: net10

out=$(bash "$SCRIPT" --repo-root "$FIX/repo-net10" 2>/dev/null); rc=$?
assert_exit "$rc" 0 "net10 exit code"
assert_json_eq "$out" '.sdk' "10.0.100" "net10 sdk"

# 3. Malformed csproj

out=$(bash "$SCRIPT" --repo-root "$FIX/repo-malformed-csproj" 2>/dev/null); rc=$?
assert_exit "$rc" 5 "malformed csproj exit code"

summary
```

**Patterns:**
- Resolve `TESTS_DIR` (suite root: fixtures, helpers, mocks) and `SKILL_DIR` (the skill whose `scripts/` are under test) separately. `run-tests.sh` exports both; each test falls back to deriving them from its own location so it runs standalone. `SKILL_DIR` is four levels up and back down into the category.
- Test files use `set -u` only, so one failing assertion does not stop the file.
- Number scenarios with comments (`# 1.`, `# 3b.`). Cover the happy path, then every documented exit code, then `--help`.
- Run the script under test with `bash "$SCRIPT" … 2>/dev/null`, capture `out` and `rc`, then assert exit code and JSON fields.
- Boolean checks without a value: `[[ cond ]] && assert_eq ok ok "name" || fail "name"`.
- End every file with `summary`, which returns 1 on any failure; `run-tests.sh` aggregates to a non-zero exit.

**Setup/Teardown:**
- `dotnet-reviewer`: `run-tests.sh` builds fixtures once if `fixtures/repo-net10/.git` is missing; they persist until `clean-fixtures.sh`.
- `claude-md-downstream`: every test file calls `bash "$TESTS_DIR/fixtures/make-fixtures.sh"` itself (wipe and rebuild); `run-tests.sh` removes fixtures via `trap cleanup EXIT` unless `KEEP_FIXTURES=1`. A new test file in this suite must rebuild fixtures itself, never assume they exist, because `test-fetch-upstream.sh` commits to the upstream fixture.
- `upgrade-gh-wf-actions`: static committed fixtures, no setup/teardown.
- Never leave nested `.git` directories in the repository. Run the matching `clean-fixtures.sh` after running a single fixture-building test directly.

## Mocking

**Framework:** PATH-substituted fake executables controlled by environment variables.

**Patterns:**

```bash

# skills/tests/dotnet/dotnet-reviewer/scripts/unit/mock-dotnet/dotnet

case "${MOCK_DOTNET_MODE:-}" in
  build-ok)     exit 0 ;;
  build-warn)   echo "src/Foo.cs(10,5): warning CS0168: ..."; exit 0 ;;
  build-fail)   echo "src/Foo.cs(12,1): error CS1002: ; expected"; exit 1 ;;
  format-dirty) echo "src/Foo.cs(20,1): IDE0005 ..."; exit 2 ;;
  test-fail)    echo "Failed: 1"; exit 1 ;;
  *) echo "mock dotnet: unknown mode '${MOCK_DOTNET_MODE:-}'" >&2; exit 99 ;;
esac
```

```bash

# skills/tests/development/upgrade-gh-wf-actions/scripts/mock-gh/gh

[[ -n "${MOCK_GH_LOG:-}" ]] && printf '%s\n' "$*" >> "$MOCK_GH_LOG"   # call log for assertions

# gh auth status        -> exit 0, or 1 when MOCK_GH_AUTH=fail

# gh api graphql ...    -> $MOCK_GH_DATA/graphql/<owner>__<name>.json, or NOT_FOUND + exit 1

# gh api repos/O/N/commits/refs/tags/T, .../contents/PATH?ref=REF -> files under $MOCK_GH_DATA

```

**What to Mock:**
- External tools and network: `dotnet` SDK, `gh` CLI / GitHub API. Unknown invocations fail loudly (exit 99 / exit 1) so a test never passes against an unmocked call.
- Document every supported call and env knob in the mock's header comment.

**What NOT to Mock:**
- `git`: use real local git repositories as fixtures (`fixtures/make-fixtures.sh`). Remote URLs point at a local fixture path (`--repo-url "$FIX/upstream"`), so nothing touches the network.
- `jq`, `python3`: real dependencies.

## Fixtures and Factories

**Test Data:**

```bash

# skills/tests/development/claude-md-downstream/scripts/unit/test-fetch-upstream.sh

bash "$TESTS_DIR/fixtures/make-fixtures.sh" >/dev/null
CACHE="$FIX/cache/upstream"
rm -rf "$FIX/cache"
out=$(bash "$SCRIPT" --repo-url "$FIX/upstream" --cache-dir "$CACHE" 2>/dev/null); rc=$?
assert_json_eq "$out" '.action' "cloned" "first run clones"
```

**Location:**
- Generated: `skills/tests/dotnet/dotnet-reviewer/scripts/fixtures/repo-*/`, `skills/tests/development/claude-md-downstream/scripts/fixtures/*` (both via `make-fixtures.sh`, not committed).
- Static: `skills/tests/development/upgrade-gh-wf-actions/scripts/fixtures/` (`gh-data/`, `repo-basic/`, `repo-empty/`, `shas.json`). These contain `action.yml` files that `scan-actions.sh` would find when the skill runs on this repo; exclude `skills/tests` there.
- Eval fixtures: small Python projects under `skills/tests/development/code-design/evals/fixtures/`.

## Skill-Behavior Artifacts (`*-test.md`)

Follow `superpowers:writing-skills` RED → GREEN → REFACTOR/Verify. Sections observed in `skills/tests/dotnet/dotnet-aspnet/aspnet-auth-gap-test.md`:

```markdown

# <Title> (Finding <ID>)

<context: which review finding, which file, what was wrong>

## Method        # how the probe works

## RED — Baseline (<old file>), <date>      # evidence of the gap, often grep output or probe answer

## GREEN — <new file>, <date>               # the fix

## Verify — <date>                           # same probe re-run against the fix

## Result

```

Rules:
- The probe runs in a **fresh subagent given only the passage under test and no file access**. It answers scenario questions and accuracy-checks claims; for references it implements a task and marks every `[INVENTED]` element.
- Any behavior change to a skill adds or amends an artifact. "Re-run this probe when X changes" is binding.
- Put single-skill artifacts in `skills/tests/<category>/<skill>/`; fixes spanning the family go in `_shared/`.

## Coverage

**Requirements:** none enforced; no coverage tooling.

**Actual Bash coverage:**
- Covered: `dotnet-reviewer` (all 3 scripts), `claude-md-downstream` (both scripts), `upgrade-gh-wf-actions` (all 4 scripts).
- Not covered: `skills/angular/angular-reviewer/scripts/*.sh` and `skills/general/gherkin-bdd-reviewer/scripts/*.sh`; verify by hand.
- **FACT** (`.github/workflows/validate-skills.yml`): CI runs only `scripts/validate-skills.sh`, `claude plugin validate .` and `./skills/development` (no `--strict`), and the `dotnet-reviewer` suite. The `claude-md-downstream` and `upgrade-gh-wf-actions` suites are local-only; run them before opening a PR that touches those skills.

## Test Types

**Unit Tests:** per-script Bash tests asserting JSON output and exit codes against fixtures and mocks.

**Integration Tests:** `skills/tests/dotnet/dotnet-reviewer/scripts/integration/test-skill-flow.md` is a manual checklist, not executed.

**E2E Tests:** not used. The closest is the eval harness in `skills/tests/development/code-design/evals/` (`evals.json` scenarios, `grade_mechanical.py` grader).

**Static validation:** `scripts/validate-skills.sh` checks frontmatter, `name` = directory and kebab-case, `description` ≤ 1024 chars, plugin `skills` arrays vs. directories, and marketplace consistency.

## Common Patterns

**Exit-code testing:**

```bash
out=$(bash "$SCRIPT" --repo-root "$FIX/repo-no-project" 2>/dev/null); rc=$?
assert_exit "$rc" 4 "no-project exit code"
```

**Text-contains testing:**

```bash
out=$(bash "$SCRIPT" --help 2>&1); rc=$?
[[ "$out" == *"detect-dotnet-version"* ]] && assert_eq ok ok "--help mentions script name" || fail "--help mentions script name"
```

**Adding a test file:** create `unit/test-<name>.sh` from the header block above, source `helpers.sh`, end with `summary`. `run-tests.sh` picks it up by glob; no registration needed.

---

*Testing analysis: 2026-10-09*
