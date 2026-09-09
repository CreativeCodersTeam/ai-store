# CancellationToken Rule Consistency Test (Finding C-6)

Test artifact per `superpowers:writing-skills` (RED → GREEN → Verify) for the
2026-07-21 fix of Finding C-6 in `docs/reviews/2026-07-21-dotnet-skills-review.md`:
three mutually incompatible rules on whether `CancellationToken` parameters get
`= default` — `dotnet-fundamentals/SKILL.md` (always with default),
`dotnet-fundamentals/references/modern-patterns.md` (library code should
require the token — contradicting its own `ct = default` code example), and
`dotnet-sdk-builder/references/di-patterns.md` (always `= default`).

## Method

A fresh general-purpose subagent receives the three excerpts verbatim (no file
access) and answers: (a) does a public async library/service method get
`= default` on its token parameter, and on which rule; (b) are the three
excerpts mutually consistent, including text vs. own code example?

## RED — Baseline (old wording), 2026-07-21

The contradiction was confirmed exactly as reported. The agent answered "yes,
`= default`" but only by discarding one guideline via majority vote, verbatim:

> Excerpt 2's prose is the sole dissenter … I discounted it because (1) it is
> outvoted by the core principle … and (2) it is contradicted by its own
> accompanying code example … For library/SDK code, Excerpt 2's prose directly
> forbids what Excerpts 1 and 3 require.

**Failure mode:** the collection forced the agent to arbitrate between its own
rules; a different agent could just as well have followed Excerpt 2 and removed
defaults from a library's public API.

## GREEN/Verify — New wording, 2026-07-21

Unified rule (applied in `dotnet-fundamentals/SKILL.md` core principle and
`modern-patterns.md`; `di-patterns.md` already matched): **`= default` on
public API surfaces; forward the received token to every downstream async
call — never re-default mid-chain, never substitute `CancellationToken.None`.**

Probe results with the new excerpts:

- (a) Unambiguous "yes — `= default`", grounded in Excerpts 1+2 with 3
  corroborating: "No conflict had to be resolved: all three excerpts point the
  same way."
- (b) "Substantively consistent"; text and code example of the modern-patterns
  bullet now match. The agent noted one residual stylistic divergence —
  parameter *naming* (`ct` in the example vs. `cancellationToken` in the SDK
  rule). This is out of scope for C-6 and already governed elsewhere:
  modern-patterns.md states "Parameter is named `ct` or `cancellationToken`
  consistently within a codebase."

## Result

Contradiction resolved; no REFACTOR round needed. Re-run this probe whenever
the CancellationToken guidance in `dotnet-fundamentals` or
`dotnet-sdk-builder` changes.
