---
last_mapped_commit: 2fa42ff6f8d70bead8b4bfd03323b316950340f8
last_mapped_at: 2026-10-09
---
<!-- refreshed: 2026-10-09 -->

# Architecture

**Analysis Date:** 2026-10-09

## System Overview

```text
┌─────────────────────────────────────────────────────────────────────┐
│          Distribution channels (consumers: Claude Code, Copilot CLI) │
├──────────────────────────────┬──────────────────────────────────────┤
│  npx skills add …            │  Plugin marketplace                   │
│  (any skills/<cat>/<skill>)  │  `.claude-plugin/marketplace.json`    │
└──────────────┬───────────────┴──────────────────┬───────────────────┘
               │                                  │ source: ./skills/<cat>
               ▼                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Category = plugin root  `skills/<category>/`                        │
│  `skills/<category>/.claude-plugin/plugin.json` (skills[] array)     │
│  published: development (cc-ai-dev), dotnet (cc-ai-dotnet),          │
│             angular (cc-ai-angular)                                  │
│  unpublished: general, java, typescript, agents-tooling (empty)      │
└──────────────┬──────────────────────────────────────────────────────┘
               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Skill  `skills/<category>/<skill>/`                                 │
│  SKILL.md (frontmatter name+description = trigger)                   │
│  references/*.md (on-demand depth) · scripts/*.sh (JSON on stdout)   │
│  assets/ (gherkin-bdd only)                                          │
└──────────────┬──────────────────────────────────────────────────────┘
               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Outputs in the *consumer's* repo: docs/specs, docs/plans,           │
│  docs/draft, docs/implementation, docs/bugs, docs/refactoring,       │
│  docs/auto-loop, docs/reviews/YYYY-MM-DD-<branch>-<mode>.md          │
└─────────────────────────────────────────────────────────────────────┘

Quality gates (this repo):
  `scripts/validate-skills.sh`  ◄── `.github/workflows/validate-skills.yml`
  `skills/tests/<category>/<skill>/` (Bash suites + *-test.md artifacts)
```

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| Marketplace catalog | Lists the three plugins and their `source` category dirs | `.claude-plugin/marketplace.json` |
| Plugin manifest | Declares which skill dirs ship (unversioned, no `$schema`) | `skills/{development,dotnet,angular}/.claude-plugin/plugin.json` |
| Router skills | Map a request to a specialized family skill; hold no rules | `skills/dotnet/dotnet/SKILL.md`, `skills/angular/angular/SKILL.md` |
| Knowledge skills | Best-practice content, `references/` only | `skills/dotnet/dotnet-fundamentals/`, `skills/angular/angular-fundamentals/`, etc. |
| Workflow skills | Phase-gated pipelines with mandatory skill bindings | `skills/dotnet/dotnet-dev/`, `skills/angular/angular-dev/`, `skills/general/implementer/`, `skills/development/*` |
| Reviewer skills | Script-driven numbered review steps, report to `docs/reviews/` | `skills/dotnet/dotnet-reviewer/`, `skills/angular/angular-reviewer/`, `skills/general/gherkin-bdd-reviewer/` |
| Validator | Frontmatter, name==dir, description <= 1024, manifest/marketplace consistency | `scripts/validate-skills.sh` |
| CI | Runs validator, `claude plugin validate`, dotnet-reviewer tests | `.github/workflows/validate-skills.yml` |
| CLAUDE.md templates | Upstream templates synced by `claude-md-downstream` | `claude/claude-md-template.repo.md`, `claude/claude-md-template.user.md` |
| Test suites | Bash unit tests + behavior-probe artifacts | `skills/tests/<category>/<skill>/` |

## Pattern Overview

**Overall:** Content distribution of declarative, prompt-based modules (Agent Skills). No runtime application; "execution" is an agent reading Markdown and invoking the Bash scripts it references.

**Key Characteristics:**
- The frontmatter `description` is the only auto-activation trigger; explicit-invocation skills say "Use only when explicitly requested by name" and list must-NOT-activate phrases (e.g. `skills/development/*/SKILL.md`, `skills/dotnet/dotnet-reviewer/SKILL.md`).
- Progressive disclosure: `SKILL.md` is the index, `references/*.md` load on demand.
- Plugin root is the category directory itself; nothing is copied or symlinked.
- Family parity: .NET and Angular families mirror each other (`dotnet-dev`/`angular-dev`, `dotnet-reviewer`/`angular-reviewer`, `dotnet-xmldocs`/`angular-tsdoc`, `dotnet-sdk-builder`/`angular-library-builder`).
- Single-sourcing: a rule lives in one canonical home (usually `*-fundamentals/references/`); other mentions link to it.

## Layers

**Distribution layer:**
- Purpose: Publish categories as plugins
- Location: `.claude-plugin/marketplace.json`, `skills/<category>/.claude-plugin/plugin.json`
- Contains: JSON manifests
- Depends on: Skill directories existing with `SKILL.md`
- Used by: Claude Code and GitHub Copilot CLI plugin installers

**Skill layer:**
- Purpose: Agent instructions
- Location: `skills/<category>/<skill>/SKILL.md`
- Contains: frontmatter (`name`, `description` only) + workflow/knowledge Markdown
- Depends on: sibling `references/`, `scripts/`, and other skills by name (routers, Skill Map tables, hand-offs)
- Used by: agents at runtime

**Script layer:**
- Purpose: Deterministic tooling for reviewer/tooling skills
- Location: `skills/dotnet/dotnet-reviewer/scripts/`, `skills/angular/angular-reviewer/scripts/`, `skills/general/gherkin-bdd-reviewer/scripts/`, `skills/development/claude-md-downstream/scripts/`, `skills/development/upgrade-gh-wf-actions/scripts/`
- Contains: Bash (plus `lib.jq` in upgrade-gh-wf-actions) printing JSON on stdout with documented exit codes
- Used by: the owning `SKILL.md` step, which enumerates every exit code

**Verification layer:**
- Purpose: Keep the distribution valid and behavior correct
- Location: `scripts/validate-skills.sh`, `skills/tests/`, `.github/workflows/validate-skills.yml`

## Data Flow

### Skill activation and execution

1. Agent matches user request against frontmatter `description` (e.g. `skills/dotnet/dotnet/SKILL.md:3`).
2. Agent loads `SKILL.md`; routers redirect to a family skill (`skills/dotnet/dotnet/SKILL.md` "Routing" tables).
3. Workflow/reviewer skill runs its numbered steps, loading `references/*.md` as needed.
4. Reviewer steps call scripts, e.g. `detect-dotnet-version.sh` → `collect-diff.sh` → `run-checks.sh` (`skills/dotnet/dotnet-reviewer/SKILL.md` Steps 2-5), consuming JSON stdout and exit codes.
5. Output written to the consumer repo's `docs/...` directory; never committed by the skill.

### Development pipeline (cc-ai-dev)

1. `create-dev-spec` → draft `docs/draft/`, final `docs/specs/`
2. `create-dev-plan` → draft `docs/draft/`, final `docs/plans/`
3. `implement-dev-plan` (or `implement-direct` without a plan; `run-with-skills` wraps either with a skill-selection checkpoint) → report `docs/implementation/`
4. Side skills: `diagnose-bug` → `docs/bugs/`, `refactor` → `docs/refactoring/`, `auto-loop` → `docs/auto-loop/<slug>.md`

### Validation flow

1. `scripts/validate-skills.sh` (bash wrapper around inline python3) walks every `SKILL.md`, every `plugin.json`, and the marketplace.
2. Exit 0 ok / 1 validation failures / 2 usage or missing dependency.
3. CI additionally runs `npx @anthropic-ai/claude-code plugin validate .` and `./skills/development` (not `--strict`).

**State Management:**
- None in this repo. Skills persist state only as files in the consumer repo (e.g. `auto-loop` uses `docs/auto-loop/<slug>.md` as its only memory).

## Key Abstractions

**Skill archetype (Router / Knowledge / Workflow / Reviewer):**
- Purpose: Fixed shapes new skills must match
- Examples: Router `skills/angular/angular/`; Knowledge `skills/dotnet/dotnet-ef-core/`; Workflow `skills/dotnet/dotnet-dev/`; Reviewer `skills/dotnet/dotnet-reviewer/` (`references/severity-taxonomy.md`, `references/report-format.md`)

**Script contract:**
- Purpose: JSON on stdout + documented exit codes, mirrored in `SKILL.md` and in `skills/tests/dotnet/dotnet-reviewer/scripts/unit/test-<name>.sh`
- Examples: `skills/dotnet/dotnet-reviewer/scripts/collect-diff.sh` (0/1/2 not-git/3 baseline-missing), `run-checks.sh` (always 0)

**Interactive vs. non-interactive path:**
- Skills that ask questions define a sub-agent fallback: documented defaults, parameter origin recorded in the report.

## Entry Points

**Plugin install:**
- Location: `.claude-plugin/marketplace.json`
- Triggers: `claude plugin` / Copilot plugin install
- Responsibilities: Resolve plugin → category dir → `plugin.json` `skills[]`

**Skill install:**
- Location: any `skills/<category>/<skill>/SKILL.md`
- Triggers: `npx skills add …`

**Repo validation:**
- Location: `scripts/validate-skills.sh`
- Triggers: developer before PR; CI on push/PR/dispatch

**Test runners:**
- `skills/tests/dotnet/dotnet-reviewer/scripts/run-tests.sh`
- `skills/tests/development/claude-md-downstream/scripts/run-tests.sh`
- `skills/tests/development/upgrade-gh-wf-actions/scripts/run-tests.sh`

## Architectural Constraints

- **Threading:** Not applicable (no runtime).
- **Global state:** None. Test fixtures (`repo-*/`, nested `.git`) are generated and must be cleaned (`clean-fixtures.sh`).
- **Circular imports:** Not applicable; skills reference each other by name (routers ↔ family skills, workflow Skill Map tables).
- **Description length:** <= 1024 chars or Copilot silently drops the skill; enforced by `scripts/validate-skills.sh` (warns at 900).
- **No `$schema` in `plugin.json`:** declaring it makes Copilot load zero skills.
- **A plugin cannot span categories:** plugin root == category dir.
- **Plugins unversioned:** identified by commit SHA; CI avoids `--strict`.
- **Copilot does not namespace plugin skills:** a project-level skill with the same name wins.
- **Frontmatter is `name` + `description` only;** `name` must equal the directory name.

## Anti-Patterns

### Divergent rule restatement

**What happens:** The same rule is restated with different wording in several family skills.
**Why it's wrong:** Rules drift; this defect class is repeatedly fixed in this repo.
**Do this instead:** Keep the rule in its canonical home (e.g. `skills/dotnet/dotnet-fundamentals/references/`) and link from other skills with an identical short hook.

### Putting tests inside a skill directory

**What happens:** Test files placed under `skills/<category>/<skill>/`.
**Why it's wrong:** Every subdirectory of a category ships with the plugin.
**Do this instead:** Mirror under `skills/tests/<category>/<skill>/`.

### Changing a script without its contract

**What happens:** A script's exit codes/JSON change but `SKILL.md` and unit tests do not.
**Do this instead:** Update the script, its `SKILL.md` step, and `skills/tests/.../unit/test-<name>.sh` together.

### Adding a skill without updating the catalog

**What happens:** New skill dir not listed in `plugin.json`, README tables, or the family router.
**Do this instead:** Update `skills/<category>/.claude-plugin/plugin.json`, `README.md`, and the router `SKILL.md`; run `bash scripts/validate-skills.sh`.

## Error Handling

**Strategy:** Exit-code contracts for scripts; explicit gates and red flags in workflow skills.

**Patterns:**
- Scripts: `set -euo pipefail`, numbered exit codes, tool failures reported inside JSON (`run-checks.sh` always exits 0).
- Validator: collects all failures, exit 1; missing `python3` or bad args exit 2.
- Skills: never auto-commit, never overwrite existing reports; non-interactive fallbacks instead of stalling.

## Cross-Cutting Concerns

**Logging:** Scripts write JSON to stdout, diagnostics to stderr; validator uses ANSI-colored output.
**Validation:** `scripts/validate-skills.sh` + Claude Code CLI `plugin validate` in CI.
**Authentication:** Not applicable; `upgrade-gh-wf-actions` uses the consumer's `gh` login (mocked in tests via `skills/tests/development/upgrade-gh-wf-actions/scripts/mock-gh/gh`).

---

*Architecture analysis: 2026-10-09*
