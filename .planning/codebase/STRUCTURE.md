---
last_mapped_commit: 2fa42ff6f8d70bead8b4bfd03323b316950340f8
last_mapped_at: 2026-10-09
---
# Codebase Structure

**Analysis Date:** 2026-10-09

## Directory Layout

```
ai-store/
├── .claude-plugin/
│   └── marketplace.json        # Plugin catalog (cc-ai-dev, cc-ai-dotnet, cc-ai-angular)
├── .github/workflows/
│   └── validate-skills.yml     # CI: validator, claude plugin validate, dotnet-reviewer tests
├── claude/                     # CLAUDE.md templates consumed by claude-md-downstream
│   ├── claude-md-template.repo.md
│   └── claude-md-template.user.md
├── scripts/
│   └── validate-skills.sh      # Repo-wide SKILL.md + manifest validator
├── skills/
│   ├── development/            # Plugin cc-ai-dev (11 skills)
│   ├── dotnet/                 # Plugin cc-ai-dotnet (11 skills)
│   ├── angular/                # Plugin cc-ai-angular (11 skills)
│   ├── general/                # Unpublished (7 skills)
│   ├── java/                   # Unpublished (4 skills)
│   ├── typescript/             # Unpublished (jest, rxjs)
│   ├── agents-tooling/         # Empty
│   └── tests/                  # Test mirror tree, never shipped
├── CLAUDE.md                   # Contributor/agent guidance
├── README.md                   # Category counts, skill tables, plugin table
└── LICENSE
```

## Directory Purposes

**`skills/<category>/`:**
- Purpose: One technology/workflow family; for published categories it is the plugin root
- Contains: one directory per skill, optional `.claude-plugin/plugin.json`
- Key files: `skills/dotnet/.claude-plugin/plugin.json`, `skills/angular/.claude-plugin/plugin.json`, `skills/development/.claude-plugin/plugin.json`

**`skills/<category>/<skill>/`:**
- Purpose: A single Agent Skill
- Contains: `SKILL.md` (required), `references/*.md`, `scripts/*.sh`, `assets/` (only `skills/general/gherkin-bdd/assets/`)
- Key files: e.g. `skills/dotnet/dotnet-reviewer/SKILL.md`, `skills/dotnet/dotnet-reviewer/scripts/collect-diff.sh`

**`skills/tests/<category>/<skill>/`:**
- Purpose: Tests for that skill, mirrored outside the shipping tree
- Contains: `*-test.md` behavior artifacts, `scripts/` Bash suites (`run-tests.sh`, `clean-fixtures.sh`, `unit/`, `fixtures/`, mocks), `evals/`, `cases/`
- Key files: `skills/tests/dotnet/dotnet-reviewer/scripts/run-tests.sh`, `skills/tests/development/claude-md-downstream/scripts/run-tests.sh`, `skills/tests/development/upgrade-gh-wf-actions/scripts/run-tests.sh`

**`skills/tests/<category>/_shared/`:**
- Purpose: Artifacts whose fix spans multiple skills in the family

## Key File Locations

**Entry Points:**
- `.claude-plugin/marketplace.json`: plugin catalog
- `skills/dotnet/dotnet/SKILL.md`, `skills/angular/angular/SKILL.md`: family routers

**Configuration:**
- `skills/<category>/.claude-plugin/plugin.json`: shipped `skills[]` list
- `.github/workflows/validate-skills.yml`: CI
- `.gitignore`: ignores `.idea`, `.tokensave`

**Core Logic:**
- `skills/dotnet/dotnet-reviewer/scripts/` (`detect-dotnet-version.sh`, `collect-diff.sh`, `run-checks.sh`)
- `skills/angular/angular-reviewer/scripts/`, `skills/general/gherkin-bdd-reviewer/scripts/`
- `skills/development/claude-md-downstream/scripts/` (`fetch-upstream.sh`, `match-version.sh`)
- `skills/development/upgrade-gh-wf-actions/scripts/` (`scan-actions.sh`, `check-updates.sh`, `release-notes.sh`, `apply-pins.sh`, `lib.jq`)

**Testing:**
- `scripts/validate-skills.sh`
- `skills/tests/**/scripts/run-tests.sh`
- `skills/tests/dotnet/dotnet-reviewer/scripts/unit/mock-dotnet/dotnet`, `skills/tests/development/upgrade-gh-wf-actions/scripts/mock-gh/gh`

## Naming Conventions

**Files:**
- `SKILL.md` exactly (uppercase) per skill
- References: kebab-case `.md`, reviewer checklists `review-checklist-<area>.md`, plus `severity-taxonomy.md`, `report-format.md`
- Scripts: kebab-case verb-noun `.sh` (`collect-diff.sh`, `apply-pins.sh`)
- Unit tests: `test-<script-or-topic>.sh` (`test-collect-diff.sh`)
- Behavior artifacts: `<prefix>-test.md`, keep original prefix (e.g. `aspnet-auth-gap-test.md`)

**Directories:**
- Skill dir: kebab-case, `[a-z0-9-]`, 1-64 chars, equal to frontmatter `name`; family prefix (`dotnet-*`, `angular-*`), router named after the family (`dotnet`, `angular`)
- Generated fixtures: `repo-*/` (transient)

## Where to Add New Code

**New skill:**
- Primary code: `skills/<category>/<skill-name>/SKILL.md` (+ `references/`, `scripts/` as the archetype requires)
- Tests: `skills/tests/<category>/<skill-name>/` (`*-test.md`, `scripts/run-tests.sh`)
- Also update: `skills/<category>/.claude-plugin/plugin.json` (if published), `README.md` tables, family router `SKILL.md`; mirror in the parallel family if .NET/Angular
- Verify: `bash scripts/validate-skills.sh`

**New rule/best practice:**
- Canonical home: `skills/<family>/<family>-fundamentals/references/` (or the owning knowledge skill's `references/`); other skills link to it

**New reviewer script:**
- Implementation: `skills/<category>/<reviewer>/scripts/<verb-noun>.sh` (JSON stdout, documented exit codes)
- Tests: `skills/tests/<category>/<reviewer>/scripts/unit/test-<name>.sh`

**New published category:**
- Add `skills/<category>/.claude-plugin/plugin.json` (no `$schema`, no `version`) and an entry in `.claude-plugin/marketplace.json`

**Utilities:**
- Shared repo tooling: `scripts/`; shared test helpers: `skills/tests/<category>/<skill>/scripts/helpers.sh`

## Special Directories

**`skills/tests/`:**
- Purpose: Test mirror tree
- Generated: Partly (`repo-*/` fixtures, nested `.git` in claude-md-downstream fixtures)
- Committed: Yes, except generated fixtures

**`.planning/`:**
- Purpose: GSD planning artifacts
- Generated: Yes
- Committed: Not yet (untracked)

**`.tokensave/`, `.serena/`, `.idea/`, `.claude/`:**
- Purpose: Local tooling state (code index, Serena memories, IDE, local Claude settings)
- Generated: Yes
- Committed: `.tokensave`, `.idea` gitignored

**`claude/`:**
- Purpose: CLAUDE.md templates published upstream for `claude-md-downstream`
- Generated: No
- Committed: Yes

---

*Structure analysis: 2026-10-09*
