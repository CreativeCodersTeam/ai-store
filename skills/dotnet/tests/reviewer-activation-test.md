# Reviewer Activation Contract Test (Finding C-4)

Test artifact per `superpowers:writing-skills` (RED → GREEN → REFACTOR → Verify)
for the 2026-07-22 fix of Finding C-4 in
`docs/reviews/2026-07-21-dotnet-skills-review.md`: the `dotnet-reviewer`
activation contract was scattered across three places and contradictory — the
body's "When to Use" section carried only the generic trigger ("A Code review
for a .NET 10+ project is needed"), the restrictive exact-phrase rule lived
only in the router, and the automatic invocation by `dotnet-dev` Phase 5 was
nowhere legitimized.

## Method

A fresh general-purpose subagent receives the contract texts verbatim (no file
access) and answers activation questions: (a) may the skill activate on
"review my code" in a .NET 10 repo, judged from the body section alone;
(b) is the `dotnet-dev` Phase 5 invocation permitted; (c) do the sources
describe the same contract?

## RED — Baseline (old texts), 2026-07-22

All three failure modes confirmed, plus one sharper than reported:

- (a) **Yes** — the body alone permitted generic activation: "SOURCE 1 contains
  no requirement that the skill be named explicitly, no phrase list, and no
  exclusion for generic review requests."
- (b) **Forbidden** — worse than the report's "unclear": the router's "'only'
  makes the phrase list exhaustive … an automatic invocation mandated by
  dotnet-dev's Phase 5 is exactly the automatic, non-user-phrased triggering
  the contract excludes." The old router text outlawed the workflow's own
  mandatory Phase 5.
- (c) "Materially different contracts … the activation semantics — who
  triggers, on what wording, and under what conditions — diverge on every
  axis." Including the visibility asymmetry: "the restriction is unenforceable
  in exactly the case it matters."

## GREEN + REFACTOR — New texts, 2026-07-22

Changes: the body's "When to Use This Skill" now carries the full contract
(exact phrases, dotnet-dev Phase 5 as explicit invocation, generic-request
exclusion, .NET 10+ as a Step 2 gate rather than an activation trigger); the
router note sanctions the dotnet-dev pathway.

First verify pass found one residual **material** divergence (REFACTOR
trigger): the frontmatter description — the layer that drives skill
selection — still omitted the dotnet-dev pathway, so an indirect workflow
invocation had "no textual basis" at the selection boundary. Fixed by adding
"or when invoked by the dotnet-dev workflow (Phase 5)" to the description.

## Verify — Final state

Re-probe across all three sources (body, description, router note):

> **No material divergence. The three sources describe the same activation
> contract.** Trigger set — identical … Exclusion set — identical in behavior.

Remaining differences were classified non-material (scope details, the
router-only "does not trigger automatically" restatement).

## Result

Contract is now self-describing in the skill it governs and consistent across
all three locations; the dotnet-dev Phase 5 invocation is explicitly
legitimized end-to-end. Re-run this probe whenever the reviewer description,
its "When to Use" section, or the router note changes.
