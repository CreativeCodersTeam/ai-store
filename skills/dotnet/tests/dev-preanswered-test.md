# Dev Pre-Answered Clarification Test (Finding D-2)

Test artifact per `superpowers:writing-skills` (RED → GREEN → Verify) for the
2026-07-22 fix of Finding D-2 in
`docs/reviews/2026-07-21-dotnet-skills-review.md`: `dotnet-dev` Phase 2
mandated eight individual ask-and-wait round-trips even when the requirement
answered points verbatim — no status existed for source-decided points, `n/a`
was textually invalid for applicable points, batching and silent adoption were
banned. Up to 14 interactions (incl. gates) for a fully specified ticket —
pressure that invites bypassing the whole workflow.

## Method

RED was captured statically (the baseline subagent dispatch was blocked by the
permission classifier; the baseline mechanics are deterministic text facts).
Verify ran as a subagent probe with two scenarios: a thorough ticket answering
points 1/3/6 verbatim, and a vague ticket ("this should be well tested").

## RED — Baseline (static evidence), 2026-07-22

Grep-verified before the change: no `pre-answered` status anywhere in
`dotnet-dev/`; the one-point-at-a-time + wait mandate and the batching ban are
unconditional (SKILL.md:117–119); the Red Flags row demanded "one round-trip
each" (SKILL.md:316); REFERENCE.md stated "the default never replaces the
round-trip" (line 57). Together with the n/a criteria ("only when an objective
technical fact makes the work empty"), the text mechanically forced 8
ask-and-wait round-trips for a ticket whose answers were already on the page.

## GREEN — New mechanism, 2026-07-22

Third point status `pre-answered — <verbatim quote or precise reference>`:
replaces the question, never the presentation; inference explicitly excluded;
Gate 2 lists all 8 points including citations and confirms pre-answered
entries collectively (a correction reopens exactly that point). Red Flags:
the "one round-trip each" row reworded, a new anti-inference row added.
REFERENCE.md distinguishes proposed default (source silent — round-trip
required) from pre-answered citation (source decides — question replaced).

## Verify — 2026-07-22

- Scenario A (points 1/3/6 verbatim in the ticket): correctly processed as 3×
  `pre-answered` with citations + 5 ask-and-wait round-trips — "User
  interactions in Phase 2 (excluding Gate 2): 5" instead of 8. The probe also
  validated the message mechanics: a pre-answered presentation rides atop the
  next open question's message without violating the batching ban, since "at
  most one open question … is ever in flight per message." Gate 2 carries all
  8 entries; a correction "reopens exactly point 6, not the whole phase."
- Scenario B ("this should be well tested"): pre-answered correctly refused —
  "a verbatim quote is necessary but not sufficient: the quoted text must
  itself settle the decision"; the anti-inference Red Flags row catches the
  stretch, and the point is asked with the sentence cited as context.
- Loophole analysis: no new silent-skip path; the residual abuse vector
  (weak citation) is guarded at four layers (citation standard, non-skippable
  presentation, Gate-2 re-review, waiver invalidity) — "the mechanism narrows
  the loophole surface rather than widening it."

## Result

Empty round-trips eliminated for source-decided points while every point
remains visible and twice-reviewed; the abuse path is explicitly red-flagged.
No REFACTOR round needed. Re-run both scenarios whenever Phase 2, Gate 2, or
the related Red Flags rows change.
