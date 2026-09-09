# Related-Skills Consistency Test (Finding C-7)

Test artifact per `superpowers:writing-skills` (RED → GREEN → Verify) for the
2026-07-22 fix of Finding C-7 in
`docs/reviews/2026-07-21-dotnet-skills-review.md`: every skill carried a
5–7-line "Related Skills" block duplicating the router tables (11 maintenance
sites for the same relationships), including factually false claims —
`dotnet-aspnet` (a references-only knowledge skill) claimed it "invokes"
`dotnet-nuget-manager`, and `dotnet-nuget-manager` mirrored the claim.

## Method

A fresh general-purpose subagent receives the router's knowledge/workflow
classification, the disputed block entries (baseline) or all nine new blocks
plus the `dotnet-sdk-builder` workflow steps (verify), and audits: can a
knowledge skill invoke anything; does every step-numbered invoke claim match a
real workflow step; do reciprocal entries agree.

## RED — Baseline (old blocks), 2026-07-22

Both disputed claims confirmed indefensible, verbatim:

> SOURCE 3 ("dotnet-aspnet — Invokes this skill …") is flatly wrong under
> SOURCE 1: it asserts dotnet-aspnet, a references-only knowledge skill,
> actively invokes dotnet-nuget-manager. A knowledge skill invokes nothing.

Concrete failure mode identified beyond documentation rot:

> the literal reading promises an automatic delegation the skill cannot
> perform; an agent trusting it could stall (waiting for an invocation that
> never occurs) or wrongly conclude the package step is already covered.

## GREEN — New blocks, 2026-07-22

All nine "Related Skills" blocks replaced (router `dotnet` and `dotnet-dev`
untouched — the full relationship overview now lives only in the router; each
block ends with a pointer to it). Rules applied: "Invoked/Invokes" language
only for real workflow invocations with step numbers (`dotnet-sdk-builder`
Steps 7/8/9); knowledge skills use neutral "Use when …" phrasing; entries
without action relevance dropped (e.g. the reviewer block shrank from 7 entries
to 2 — its checklists already cross-reference the knowledge skills inline).

## Verify — Final state

Three-part audit (invoke-language vs. real steps, knowledge-skill agency,
cross-block reciprocity) over all nine new blocks:

> Overall: no violations found in (a), (b), or (c).

Every step-numbered claim matches `dotnet-sdk-builder`'s actual Steps 7/8/9 on
skill, step number, and purpose; no knowledge skill claims agency; all three
reciprocal pairs (sdk-builder ↔ tester / xmldocs / nuget-manager) agree on
direction, step, and purpose.

## Result

False claims removed, redundancy cut, invoke language verifiable against
workflow text. No REFACTOR round needed. Re-run this audit whenever a
"Related Skills" block or `dotnet-sdk-builder`'s workflow steps change.
