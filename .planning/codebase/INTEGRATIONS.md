---
last_mapped_commit: 2fa42ff6f8d70bead8b4bfd03323b316950340f8
last_mapped_at: 2026-10-09
---
# External Integrations

**Analysis Date:** 2026-10-09

## APIs & External Services

**GitHub API (via `gh` CLI):**
- Used by `skills/development/upgrade-gh-wf-actions/scripts/check-updates.sh` - GraphQL release/tag queries (`gh api graphql`), REST `repos/<repo>/contents/...` (reads action metadata), `repos/<repo>/commits/refs/tags/<tag>` (resolves SHA for pinning); min-age gate `--min-age-days` (default 7)
- Used by `skills/development/upgrade-gh-wf-actions/scripts/release-notes.sh` - GraphQL release notes
  - SDK/Client: `gh` CLI
  - Auth: the user's `gh auth` session (scripts check `gh auth`); no token env var read directly
  - Test double: `skills/tests/development/upgrade-gh-wf-actions/scripts/mock-gh/gh` with data in `skills/tests/development/upgrade-gh-wf-actions/scripts/fixtures/gh-data/`

**GitHub git remote (upstream template):**
- `skills/development/claude-md-downstream/scripts/fetch-upstream.sh` clones/fetches `https://github.com/CreativeCodersTeam/ai-store.git` (blobless, cached; falls back to cache, exit 2 if unreachable with no cache) to diff `claude/claude-md-template.repo.md` / `claude/claude-md-template.user.md`
  - Auth: none (public HTTPS)
  - Tests use local git fixtures from `skills/tests/development/claude-md-downstream/scripts/fixtures/make-fixtures.sh`

**npm registry (CI only):**
- `.github/workflows/validate-skills.yml` runs `npx --yes @anthropic-ai/claude-code@latest plugin validate .` and `./skills/development`

**Agent hosts (consumers):**
- Claude Code and GitHub Copilot CLI read `.claude-plugin/marketplace.json` and `skills/<category>/.claude-plugin/plugin.json`
- `npx skills add` installer (documented in `README.md`)

## Data Storage

**Databases:**
- None

**File Storage:**
- Local filesystem only. Reviewer skills write reports to the target project's `docs/reviews/YYYY-MM-DD-<branch>-<mode>.md`; dev workflow skills write to `docs/draft/`, `docs/specs/`, `docs/plans/`, `docs/implementation/`, `docs/bugs/`, `docs/refactoring/`, `docs/auto-loop/`

**Caching:**
- Local clone cache for upstream repo in `fetch-upstream.sh`

## Authentication & Identity

**Auth Provider:**
- None in-repo. Relies on ambient `gh auth` login and git credentials of the user

## Monitoring & Observability

**Error Tracking:**
- None

**Logs:**
- Scripts emit JSON on stdout, diagnostics on stderr, and documented exit codes (e.g. `detect-dotnet-version.sh` 0/1/4/5, `collect-diff.sh` 0/1/2/3, `run-checks.sh` always 0 with failures in JSON)

## CI/CD & Deployment

**Hosting:**
- GitHub repository `CreativeCodersTeam/ai-store`; `main` is the release channel (plugins unversioned, pinned by commit SHA)

**CI Pipeline:**
- GitHub Actions `.github/workflows/validate-skills.yml` on push, pull_request, workflow_dispatch, `ubuntu-latest`, `actions/checkout@v5` (tag, not SHA-pinned)
  - Job `validate`: `bash scripts/validate-skills.sh` + Claude Code CLI `plugin validate`
  - Job `dotnet-reviewer-tests`: `bash skills/tests/dotnet/dotnet-reviewer/scripts/run-tests.sh`
  - The `claude-md-downstream` and `upgrade-gh-wf-actions` suites are not run in CI (**FACT**, per workflow file)

## Environment Configuration

**Required env vars:**
- None required. Optional: `NG_BIN`, `MOCK_DOTNET_MODE`, `KEEP_FIXTURES`, `TESTS_DIR`, `SKILL_DIR`

**Secrets location:**
- No secrets in repo or CI workflow

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None

---

*Integration audit: 2026-10-09*
