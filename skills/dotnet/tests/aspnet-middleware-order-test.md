# ASP.NET Middleware Order Single-Source Test (Finding A-3)

Test artifact per `superpowers:writing-skills` (RED → GREEN → Verify) for the
2026-07-22 fix of Finding A-3 in
`docs/reviews/2026-07-21-dotnet-skills-review.md`: `dotnet-aspnet/SKILL.md`
carried its own middleware-order chain ("… → rate limiter → endpoints") that
diverged from the canonical pipeline in `references/middleware.md` (which
additionally contains `UseOutputCache()` between rate limiter and endpoint
mapping) — two "canonical" orderings of different scope, kept in sync by hand.

## Method

A fresh general-purpose subagent receives both passages verbatim and answers:
(a) where does `UseOutputCache()` belong, and what does an agent with only the
SKILL.md loaded do; (b) can the sources diverge, and is canonicality stated?

## RED — Baseline (old texts), 2026-07-22

Divergence and its consequence confirmed, verbatim:

> An agent that has loaded only SOURCE 1 … gets zero guidance … It would
> either omit the call, or place it from its own prior knowledge … The Core
> Principles bullet reads as a complete ordering ("→ endpoints" terminates
> it), so the agent has no cue that the list is a lossy summary.

> Canonical list: nowhere stated. … the always-loaded summary silently drops
> an element (`UseOutputCache`) present in the on-demand reference, with no
> cross-reference telling agents the reference is the complete/authoritative
> ordering.

Four divergences catalogued (missing `UseOutputCache`, lossy HSTS/HTTPS and
authN/authZ granularity, abstract "endpoints" vs. concrete `MapControllers`).

## GREEN — Fix, 2026-07-22

Single-source-of-truth variant: the SKILL.md bullet no longer carries any
sequence — "Middleware order matters — never order the pipeline from memory;
references/middleware.md holds the single canonical sequence."
`references/middleware.md` is unchanged (its pipeline was correct; A-3 was
about the divergence, not the ordering itself).

## Verify — 2026-07-22

Same probe against the new texts:

> An agent that has loaded only SOURCE 1 has a defined path, not a guess …
> any guess is a rule breach, not an ambiguity in the skill.

> The two sources cannot diverge on middleware ordering content, because the
> ordering exists in exactly one place … This is single-sourcing by
> construction. And yes, canonicality is explicitly stated.

Residual risk correctly identified as reference-vs-reality staleness only —
outside the scope of internal consistency.

## Result

Duplication removed structurally; future pipeline changes have exactly one
edit site. No REFACTOR round needed. Re-run this probe if a middleware
sequence ever reappears in `dotnet-aspnet/SKILL.md`.
