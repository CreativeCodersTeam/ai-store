# NuGet-Manager Rules Test (Findings N-1, N-2, N-3)

Test artifact per `superpowers:writing-skills` (RED → GREEN → REFACTOR → Verify)
for the 2026-07-22 fix of Findings N-1/N-2/N-3 in
`docs/reviews/2026-07-21-dotnet-skills-review.md`:
`dotnet-nuget-manager/SKILL.md` mandated hand-editing for version updates while
forbidding it for add/remove (N-1), offered no vulnerability/deprecation audit
despite the reviewer routing "vulnerable packages" here (N-2), and ignored the
CPM special cases `VersionOverride` and `GlobalPackageReference` (N-3).

## Method

A fresh general-purpose subagent works three scenarios against the skill text:
(a) a plain version bump (mechanism + philosophy + rationalization risk),
(b) a reviewer-reported CVE (command availability), (c) a CPM solution whose
target project carries `VersionOverride="12.0.3"`.

## RED — Baseline (old text), 2026-07-22

- (a) Hand-edit mandated; "philosophically it is inconsistent … the skill
  carves out exactly the case the CLI handles fine … and the skill never
  explains why." Rationalization risk rated **moderate-to-high**, with a
  concrete over-extension chain (adding Version attributes → VersionOverride →
  "tidying" adjacent entries) that step 4's restore check mostly cannot catch.
- (b) "No such command exists in the text" — and conflating outdated with
  vulnerable "is wrong in both directions."
- (c) The workflow's either/or model walks straight into the trap: central
  version updated, **project silently stays on 12.0.3**, and "the workflow's
  own success criterion reports the update as complete" because restore
  succeeds — "a literal execution of the workflow produces a false 'done'."

## GREEN — New text, 2026-07-22

- N-1 (report option a): version updates go through the CLI
  (`dotnet add package … --version …`, CPM-aware on modern SDKs); hand-editing
  demoted to a documented fallback with three bounds — conditioned (older
  SDKs that cannot write CPM), scoped (change ONLY the existing
  `Version`/`VersionOverride` string, never add/remove attributes — closing
  the baseline's over-extension chain), checked (immediate restore).
- N-2: new "Auditing Packages" section (`--vulnerable`,
  `--include-transitive`, `--deprecated`, "outdated ≠ vulnerable") with the
  transitive remediation paths; audit trigger added to "When to Use".
- N-3: step 2 now front-loads the `VersionOverride` check with the explicit
  silent-no-op warning ("`dotnet restore` still succeeds") and names
  `<GlobalPackageReference>` as the home of build-wide package versions.

## Verify + REFACTOR — 2026-07-22

- (a) "the CLI, end to end … this version of the skill is consistent"; the
  fallback is "conditioned … scoped … checked" and inapplicable to the
  non-CPM scenario. Residual: an agent could claim "my SDK is old" without
  trying the CLI — REFACTOR added "Always try the CLI first; fall back only
  after it demonstrably wrote the version to the wrong place (or errored)."
- (b) Audit command found, "Transitive case: yes, handled twice" (detection
  and both remediation paths).
- (c) The override is found in step 2 before any change; the fix targets the
  override, not the central version; "the skill warns explicitly and
  precisely" — including why step 4 is blind to this failure mode.

## Result

One mechanism philosophy across add/remove/update, a real audit workflow, and
the CPM silent-no-op trap defused at the correct step. One REFACTOR round.
Re-run these scenarios whenever the Core Rules or the version-update workflow
change.
