---
last_mapped_commit: 2fa42ff6f8d70bead8b4bfd03323b316950340f8
last_mapped_at: 2026-10-09
---
# Codebase Concerns

**Analysis Date:** 2026-10-09

Evidence base: `bash scripts/validate-skills.sh` (run 2026-10-09: "OK — 46 SKILL.md checked, 1 warning(s)"), directory listings, grep over `skills/`, `README.md`, `.github/workflows/validate-skills.yml`. Findings marked **FACT** were verified against files; anything else is labelled unverified.

## Tech Debt

**Superseded `implementer` skill still shipped:**
- Issue: `skills/general/implementer/SKILL.md` (13.8 KB) is still present and listed in `README.md:224`, although project memory states `implement-dev-plan` replaces it. CLAUDE.md still names `implementer` as a Workflow archetype example. **FACT** (file and README row exist).
- Files: `skills/general/implementer/`, `README.md`, `CLAUDE.md`
- Impact: Two overlapping language-agnostic implementation workflows; `npx skills add` users get the stale one, which auto-activates (no explicit-invocation guard).
- Fix approach: Delete the directory, remove the README row and General count (7 -> 6), update the archetype list in `CLAUDE.md`. Note: the word "implementer" in `skills/development/implement-dev-plan/` and `implement-direct/` refers to a sub-agent role, not this skill — leave those.

**Empty category directory:**
- Issue: `skills/agents-tooling/` exists and is empty. **FACT**
- Files: `skills/agents-tooling/`
- Impact: Not tracked by git if truly empty (unverified whether a placeholder is intended); confuses "every category dir holds shippable skills".
- Fix approach: Remove, or add skills plus README row.

**Hand-maintained README tables (no automated guard):**
- Issue: Category counts (`README.md:11-16`), plugin table (`README.md:27-29`) and per-category skill tables are typed by hand. Currently they match the filesystem (11/11/7/11/4/2) **FACT**, but `scripts/validate-skills.sh` does not check README at all (no README reference in the script) **FACT**.
- Files: `README.md`, `scripts/validate-skills.sh`
- Impact: Drift is silent; the Development row in the categories table duplicates the full plugin description and must be edited in three places (`README.md:14`, `.claude-plugin/marketplace.json`, `skills/development/.claude-plugin/plugin.json`).
- Fix approach: Add a validator check that each `skills/<cat>/*/SKILL.md` name appears in the README table for that category and that counts match.

**Plugin description duplicated between catalog and plugin manifest:**
- Issue: The same long `description` string is copied verbatim in `.claude-plugin/marketplace.json` and each `skills/<cat>/.claude-plugin/plugin.json`. **FACT** (identical for all three plugins). Keywords already diverge: `cc-ai-dev` plugin.json has `code-design`, `github-actions`, `supply-chain`; marketplace.json does not. **FACT**
- Files: `.claude-plugin/marketplace.json`, `skills/development/.claude-plugin/plugin.json`
- Impact: Violates the repo's single-sourcing principle; catalog search keywords lag the plugin.
- Fix approach: Sync keywords now; have the validator assert description equality.

## Known Bugs

**Uncovered script exit codes in reviewer SKILL.md files:**
- Symptoms: Agent meets an exit code its SKILL.md never enumerates and has to guess.
- Files:
  - `skills/general/gherkin-bdd-reviewer/SKILL.md:77-78` only handles `collect-diff.sh` exits 2/3; `detect-framework.sh` and `locate-artifacts.sh` exit 1 and 2 (**FACT**, grep of `exit N`) are not enumerated, and usage exit 1 is never mentioned.
  - `skills/dotnet/dotnet-reviewer/SKILL.md:66-69` and `skills/angular/angular-reviewer/SKILL.md:56-60` list `collect-diff.sh` exits 0/2/3(/4) but not exit 1 (usage), which both scripts emit. **FACT**
- Trigger: Wrong argument or invalid path passed to the script.
- Workaround: None documented.
- Fix approach: Add an "Exit 1 (usage): bug — report and abort" line per step; mirror in both families.

**`run-checks.sh` contract vs. CLAUDE.md:**
- Symptoms: `CLAUDE.md` states `run-checks.sh` "always exits 0", but `skills/dotnet/dotnet-reviewer/scripts/run-checks.sh:30,34` and the angular copy `exit 1` on usage errors. **FACT**
- Fix approach: Reword CLAUDE.md to "exits 0 except on usage error (1)".

## Security Considerations

**CI uses mutable action tags and an unpinned CLI:**
- Risk: `.github/workflows/validate-skills.yml` uses `actions/checkout@v5` (tag, not SHA) and `npx --yes @anthropic-ai/claude-code@latest`. **FACT** A compromised tag/release runs in CI. This repo ships `upgrade-gh-wf-actions`, whose whole premise is SHA-pinning — the repo does not follow its own skill.
- Files: `.github/workflows/validate-skills.yml`
- Current mitigation: None; no write permissions or secrets are used in the workflow (no `permissions:` block declared — unverified what default token scope the org applies).
- Recommendations: Pin `actions/checkout` to `@<sha> # v5.x.y`, pin the CLI to a version, add `permissions: contents: read`.

**Auto-activating general skills overlap with explicit-only reviewers:**
- Risk: `skills/general/code-review/SKILL.md` description ("Use when asked to review a pull request, audit code changes...") has no exclusion clause **FACT**, so it competes with `dotnet-reviewer`/`angular-reviewer`/`gherkin-bdd-reviewer` and with harness built-in `code-review` skills of the same name (Copilot does not namespace — see CLAUDE.md).
- Files: `skills/general/code-review/SKILL.md`
- Recommendations: Add "Must NOT activate when a stack-specific reviewer is requested by name" or rename.

## Performance Bottlenecks

**Large workflow SKILL.md bodies:**
- Problem: Always-loaded body size. Largest: `skills/development/implement-direct/SKILL.md` (513 lines), `skills/dotnet/dotnet-dev/SKILL.md` (435), `skills/angular/angular-dev/SKILL.md` (422), `skills/development/implement-dev-plan/SKILL.md` (400), `skills/development/claude-md-downstream/SKILL.md` (395). **FACT** (`wc -l`)
- Cause: Phase detail kept inline instead of in `references/`.
- Improvement path: Move per-phase depth into `references/*.md` loaded on demand; keep validator warnings in mind.

## Fragile Areas

**Description length near the 1024-char limit:**
- Files: `skills/development/code-design/SKILL.md` (970 chars — the only validator warning on 2026-10-09). **FACT** CLAUDE.md claims "three Development skills" are within 120 chars; the validator flags only one at its default threshold (unverified which default threshold is used; run `--warn-at 904` to re-check the 120-char claim).
- Why fragile: Copilot drops over-long skills silently.
- Safe modification: Run `bash scripts/validate-skills.sh` after any description edit; it is in CI.
- Test coverage: Guarded by validator.

**Family parity (.NET <-> Angular mirrors):**
- Files: `skills/dotnet/dotnet-reviewer/scripts/*.sh` vs `skills/angular/angular-reviewer/scripts/*.sh`
- Why fragile: Exit-code sets already differ deliberately (angular `collect-diff.sh` adds exit 4 for no-commits repo; `detect-angular-version.sh` uses 2 for not-a-directory where dotnet uses 1). **FACT** A fix in one side (e.g. the no-commits case) is not mirrored to dotnet.
- Safe modification: When changing a reviewer script, diff against its mirror and update both SKILL.md steps.
- Test coverage: Only the dotnet side has a suite.

**Router skills:**
- Files: `skills/dotnet/dotnet/SKILL.md`, `skills/angular/angular/SKILL.md`
- Status: Every sibling skill name currently appears in its router. **FACT** No automated check.
- Safe modification: Add a validator check mirroring the plugin.json completeness check.

**Plugin `skills` arrays:**
- Files: `skills/{angular,dotnet,development}/.claude-plugin/plugin.json`
- Status: All 11/11/11 skill directories listed. **FACT** Validator enforces this.
- Gap: `general`, `java`, `typescript` have no plugin at all **FACT** — 13 skills unreachable for plugin users (only via `npx skills add`). Not mentioned as a deliberate decision in README (unverified intent).

**Example reference documents with dead relative links:**
- Files: `skills/general/create-readme/references/*-readme.md`, `skills/general/convert-plaintext-to-md/references/*.md`
- Why fragile: ~22 relative links (`LICENSE`, `./docs/...`, `image-url.png`) resolve to nothing. **FACT** They are copied sample READMEs/placeholders, so this is expected, but any future link-checker must exclude these paths.

## Scaling Limits

**Manual multi-file sync per new skill:**
- Current capacity: 46 skills, 3 plugins.
- Limit: Each new skill touches SKILL.md, README (3 places), router, plugin.json, possibly marketplace keywords; only plugin.json and frontmatter are machine-checked.
- Scaling path: Generate README tables from frontmatter, or extend the validator.

## Dependencies at Risk

**`@anthropic-ai/claude-code@latest` in CI:**
- Risk: A CLI schema change breaks CI with no code change here (the workflow comment states this is intended as an early warning). **FACT**
- Impact: Red CI on unrelated PRs.
- Migration plan: Pin and bump deliberately, or keep `@latest` in a separate non-blocking job.

**CLI manifest validation covers only one plugin:**
- Risk: `.github/workflows/validate-skills.yml` runs `plugin validate .` and `plugin validate ./skills/development` only **FACT**; `./skills/angular` and `./skills/dotnet` are never validated by the CLI directly (unverified whether `validate .` recurses into them).
- Migration plan: Add the two missing `plugin validate` lines.

## Missing Critical Features

**CI runs only one of three script test suites:**
- Problem: CI job `dotnet-reviewer-tests` runs `skills/tests/dotnet/dotnet-reviewer/scripts/run-tests.sh`; the `claude-md-downstream` and `upgrade-gh-wf-actions` suites (both self-contained, no network) are not in any workflow. **FACT**
- Blocks: Regressions in `skills/development/claude-md-downstream/scripts/` and `skills/development/upgrade-gh-wf-actions/scripts/` reach `main` unnoticed.
- Fix: Add two jobs calling `skills/tests/development/{claude-md-downstream,upgrade-gh-wf-actions}/scripts/run-tests.sh`.

## Test Coverage Gaps

**Reviewer scripts without a suite:**
- What's not tested: `skills/angular/angular-reviewer/scripts/{collect-diff,detect-angular-version,run-checks}.sh`, `skills/general/gherkin-bdd-reviewer/scripts/{collect-diff,detect-framework,locate-artifacts}.sh`. **FACT** (no `scripts/` under `skills/tests/angular/angular-reviewer/`, no `skills/tests/general/` at all)
- Risk: Exit-code contract drift vs. SKILL.md; Angular mirror diverges from tested dotnet side.
- Priority: High (angular-reviewer — invoked by `angular-dev` Phase 5), Medium (gherkin-bdd-reviewer).

**No behavior-test artifacts for General, Java, TypeScript skills:**
- What's not tested: All 13 skills in `skills/general/`, `skills/java/`, `skills/typescript/`; `skills/tests/` has only `angular`, `development`, `dotnet`. **FACT**
- Risk: Activation overlap (`skills/typescript/rxjs` vs `skills/angular/angular-rxjs`; `skills/typescript/jest` vs `skills/angular/angular-tester`) never probed.
- Priority: Low-Medium.

**Manual integration checklist:**
- What's not tested: `skills/tests/dotnet/dotnet-reviewer/scripts/integration/test-skill-flow.md` is manual, not run by `run-tests.sh`.
- Priority: Low.

---

*Concerns audit: 2026-10-09*
