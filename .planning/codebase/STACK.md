---
last_mapped_commit: 2fa42ff6f8d70bead8b4bfd03323b316950340f8
last_mapped_at: 2026-10-09
---
# Technology Stack

**Analysis Date:** 2026-10-09

## Languages

**Primary:**
- Markdown - every deliverable: `skills/<category>/<skill>/SKILL.md` (YAML frontmatter with `name` + `description` only), `references/*.md`, test artifacts `skills/tests/**/*-test.md`, docs in `README.md`, `CLAUDE.md`, `claude/claude-md-template.*.md`
- Bash (3.2+ compatible, `set -euo pipefail`) - skill scripts under `skills/*/*/scripts/*.sh`, validator `scripts/validate-skills.sh`, test suites under `skills/tests/**/scripts/`

**Secondary:**
- Python 3 - embedded heredoc in `scripts/validate-skills.sh` (stdlib `json`, `os`, `re` only); eval graders `skills/tests/development/*/evals/grade-mechanical.py`, `skills/tests/development/code-design/evals/grade_mechanical.py`; eval fixture app `skills/tests/development/code-design/evals/fixtures/shop/`
- JSON - plugin manifests `.claude-plugin/marketplace.json`, `skills/{angular,dotnet,development}/.claude-plugin/plugin.json`; all script stdout contracts
- YAML - CI workflow `.github/workflows/validate-skills.yml`

## Runtime

**Environment:**
- Agent hosts: Claude Code (verified 2.1.263) and GitHub Copilot CLI (verified 1.0.83), per `CLAUDE.md`
- Shell: `bash` 3.2+ (macOS default supported); `python3` for validation

**Package Manager:**
- None. No `package.json`, `pyproject.toml`, or lockfile exists (**FACT**, verified by listing repo root)
- Distribution: `npx skills add …` (see `README.md`) and plugin marketplace (`/plugin marketplace add CreativeCodersTeam/ai-store`, `copilot plugin marketplace add …`)

## Frameworks

**Core:**
- Agent Skills specification (https://agentskills.io/specification) - SKILL.md format; name 1-64 chars `[a-z0-9-]`, must equal directory; description <= 1024 chars
- Claude Code plugin / marketplace manifest format - `.claude-plugin/`; deliberately no `version` and no `$schema` field

**Testing:**
- Custom Bash test harnesses: `skills/tests/dotnet/dotnet-reviewer/scripts/run-tests.sh`, `skills/tests/development/claude-md-downstream/scripts/run-tests.sh`, `skills/tests/development/upgrade-gh-wf-actions/scripts/run-tests.sh` (shared `helpers.sh` per suite)
- Mocks: `skills/tests/dotnet/dotnet-reviewer/scripts/unit/mock-dotnet/dotnet` (`MOCK_DOTNET_MODE`), `skills/tests/development/upgrade-gh-wf-actions/scripts/mock-gh/gh`
- Behavior tests: Markdown RED/GREEN/REFACTOR artifacts run by fresh subagents; skill evals with Python graders (viewer needs Python 3.12 via `uv`, per project memory - unverified in repo)

**Build/Dev:**
- `scripts/validate-skills.sh` - frontmatter, description length (warn at 900 via `--warn-at`), plugin and marketplace consistency. Exit 0/1/2
- `npx @anthropic-ai/claude-code@latest plugin validate` - second-opinion manifest validation in CI (non-strict)

## Key Dependencies

**Critical (runtime tools invoked by skill scripts):**
- `git` - all `collect-diff.sh` scripts, `skills/development/claude-md-downstream/scripts/fetch-upstream.sh` (blobless clone)
- `jq` - JSON emission/parsing in reviewer and `upgrade-gh-wf-actions` scripts
- `python3` - validator and some scripts (`python3 -c`)
- `gh` (GitHub CLI, authenticated) - `skills/development/upgrade-gh-wf-actions/scripts/check-updates.sh`, `release-notes.sh`

**Infrastructure (target-project toolchains, optional):**
- `dotnet` SDK 10+ - `skills/dotnet/dotnet-reviewer/scripts/run-checks.sh` (build/format/test), version gate in `detect-dotnet-version.sh` (exit 4 for SDK < 10)
- Angular CLI via `npx --no-install ng` (override `NG_BIN`) - `skills/angular/angular-reviewer/scripts/run-checks.sh`

## Configuration

**Environment:**
- No `.env` files. Script knobs via env vars/flags: `MOCK_DOTNET_MODE`, `NG_BIN`, `KEEP_FIXTURES`, `TESTS_DIR`, `SKILL_DIR`, `--min-age-days` (default 7) in `check-updates.sh`, `--repo-url` in `fetch-upstream.sh`
- Local tool config (not shipped): `.claude/settings.local.json`, `.serena/project.yml`, `.idea/`, `.tokensave/` (gitignored)

**Build:**
- `.claude-plugin/marketplace.json` - catalog (`creativecoders-ai-store`), plugins `cc-ai-dev`, `cc-ai-dotnet`, `cc-ai-angular`
- `skills/<category>/.claude-plugin/plugin.json` - `skills` array must list every skill directory in the category
- Categories `general`, `java`, `typescript`, `agents-tooling` (empty) are not published as plugins

## Platform Requirements

**Development:**
- `bash` 3.2+, `git`, `jq`, `python3`; `gh` for `upgrade-gh-wf-actions`; no `dotnet` needed to run tests

**Production:**
- Merge to `main` = ship. Consumers install from GitHub (`CreativeCodersTeam/ai-store`); plugins tracked by commit SHA. License Apache-2.0

---

*Stack analysis: 2026-10-09*
