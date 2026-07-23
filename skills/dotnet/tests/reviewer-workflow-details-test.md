# Reviewer Workflow Details Test (Findings V-1–V-5)

Test artifact per `superpowers:writing-skills` (RED → GREEN → REFACTOR → Verify)
for the 2026-07-22 fix of Findings V-1 through V-5 in
`docs/reviews/2026-07-21-dotnet-skills-review.md`, all in
`dotnet-reviewer/SKILL.md`: an option list starting at (B) (V-1), an undefined
"whitelist" (V-2), a documented exit code the script never produces (V-3), the
tool-severity mapping duplicated in Step 6 and the taxonomy file (V-4), and
diff exclusions undocumented at the workflow layer (V-5).

Per user directive, V-1 was fixed by **renumbering the existing options
ascending to (A)/(B)/(C)** — not by adding a new option.

## Method

A fresh general-purpose subagent audits the verbatim excerpts (steps 1/2/3/4/6,
script exit-code header, taxonomy table) with five targeted questions.

## RED — Baseline (old texts), 2026-07-22

All five confirmed, with two sharpenings beyond the report:

- (1) "the letters are load-bearing — which makes the missing (A) an actual
  defect, not cosmetic."
- (2) "'The whitelist' is a dangling reference … not executable without
  inventing content."
- (3) "Exit code 2 is documented … but never produced by the script" — and the
  misdiagnosis nuance: a bad repo path (user-correctable) "gets reported as an
  internal skill bug."
- (4) SKILL.md declares the taxonomy authoritative and then inlines a copy
  anyway — "the stale mapping wins because it's the one physically present at
  the point of use."
- (5) "It cannot be filled truthfully from SKILL.md alone … the skeleton's
  pre-filled value is doing undeclared load-bearing work."

## GREEN — Fixes, 2026-07-22

- V-1: options renumbered (A) Review everything / (B) Prioritize / (C) Chunk;
  fallback clause B→C; non-interactive auto-select now (C). Cross-references
  updated: `dotnet-dev/references/REFERENCE.md` ("strategy C (chunked)") and
  an addendum in the historical `reviewer-noninteractive-test.md`.
- V-2: valid values enumerated inline (mode/tools/language); non-interactive
  invalid supplied values fall back to defaults with origin
  `default (invalid provided value)` in the report metadata.
- V-3: exit-code doc aligned to the script's real contract {0,1,4,5}; the
  exit-1 branch now prescribes check-correct-retry first, reserving
  "report the bug" for verified-correct invocations (adopting the baseline's
  misdiagnosis point). Script and unit tests untouched.
- V-4: the four mapping bullets removed from Step 6; the taxonomy table is
  named "the single source of truth."
- V-5: Step 3 documents `*.min.js` + `wwwroot/lib/**` (plus `.gitignore`) and
  mandates carrying them verbatim into the report's `Exclusions:` line.

## Verify + REFACTOR — 2026-07-22

- (1) "well-formed … No dangling letters, no letter reused with conflicting
  meaning"; fallback and auto-select semantics confirmed correct.
- (2) executable in both modes; `mode=incremental` supplied non-interactively
  → runs as `uncommitted`, auditable via the origin vocabulary. Residual edge
  (invalid supplied value while a user IS reachable) closed by REFACTOR: ask
  instead of silently defaulting.
- (3) "they now match exactly … That is the right ordering."
- (4) "One place … Authority is unambiguous."
- (5) The `Exclusions:` line is derivable from SKILL.md alone.

The baseline's suggestion to have collect-diff emit its active exclusions in
its JSON (ground-truth instead of hand-maintained doc) was noted but not
implemented — script changes are out of scope; recorded here as a possible
future hardening.

## Result

All five workflow-detail defects fixed; one REFACTOR round. Re-run this audit
whenever steps 1–6 of the reviewer SKILL.md, the script exit codes, or the
taxonomy mapping change.
