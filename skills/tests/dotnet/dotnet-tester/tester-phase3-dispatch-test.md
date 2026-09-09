# Tester Phase-3 Dispatch Template Test (Finding T-1)

Test artifact per `superpowers:writing-skills` (RED → GREEN → REFACTOR → Verify)
for the 2026-07-22 fix of Finding T-1 in
`docs/reviews/2026-07-21-dotnet-skills-review.md`: `dotnet-tester/SKILL.md`
Phase 3 said only "Start a **separate agent** that reads the production code
and written tests" — no prompt template, no statement of what context the
stateless sub-agent must receive.

## Method

A fresh general-purpose subagent receives the Phase 3 section verbatim plus a
concrete scenario (OrderService tested, test file path known) and must
(a) write the exact dispatch prompt, (b) classify every element as
[FROM-SKILL] vs [IMPROVISED], (c) judge whether two agents would produce
materially identical dispatches.

## RED — Baseline (old section), 2026-07-22

Core well-pinned (categories, format line, read-both-files), but the agent's
INPUTS were entirely improvised — 10+ [IMPROVISED] elements including: how the
sub-agent learns the file paths at all, absolute-vs-relative handling, whether
fixtures/mocks may be read, the no-code/no-modify prohibitions, priority
semantics (nobody is told what HIGH means), and response hygiene. Verdict:

> the skill's silence on how a stateless agent learns *which* files and *how
> far* it may explore is the biggest underspecification in the Phase 3
> section — the categories and format are well-pinned, but the agent's inputs
> are not.

## GREEN — New section, 2026-07-22

Phase 3 now contains a fill-in dispatch template that absorbs the former
inline category list and format line (no duplication) and pins exactly the
baseline gaps: path slots, read-in-full instruction, fixture/mock read
permission, per-public-method methodology, HIGH/MEDIUM/LOW semantics, sort
order, only-the-list/no-code/no-modify prohibitions, and the empty-list rule
("do not invent low-value cases to fill it").

## Verify + REFACTOR — 2026-07-22

Re-probe: prompt reproduced verbatim from the template with only the two path
substitutions; "(c) Yes — materially identical." Single residual ambiguity:
"full paths" could be read as repo-relative. REFACTOR: template slots changed
to "absolute paths" (the safe reading for a stateless receiver with unknown
cwd). Out-of-prompt dispatch mechanics (agent type, sync/background) remain
unspecified by design — they are harness-, not skill-level concerns.

## Result

The Phase-3 dispatch is now deterministic up to path substitution; one
REFACTOR round. Re-run this probe whenever the Phase 3 template changes.
