# Dev Minor-Findings Decision Test (Finding D-1)

Test artifact per `superpowers:writing-skills` (RED → GREEN → Verify) for the
2026-07-23 fix of Finding D-1 in
`docs/reviews/2026-07-21-dotnet-skills-review.md`: `dotnet-dev/SKILL.md`
Phase 5 knew exactly two outcomes while `references/REFERENCE.md` added a
third path — "**No / minor issues** → fix directly … then gate" — an open
backdoor letting a pressured agent classify findings as "minor" and bypass
the Phase-4 loop (per-task checklists, Gate 4).

Per user directive, the fix removes the minor-decision from the agent
entirely: **for Minor and lower findings the user is asked which to fix.**
(Note: the request named "D-4", but described D-1's subject; D-4 was already
fixed on 2026-07-22 — recorded in the approved plan.)

## Method

RED was captured statically (the baseline subagent dispatch was blocked by the
permission classifier; the contradiction is directly quotable). Verify ran as
a subagent probe with four scenarios.

## RED — Baseline (static evidence), 2026-07-23

Grep-verified before the change: SKILL.md Phase 5 had exactly two outcomes
("Rework needed" line 213, "All good" line 215); REFERENCE.md line 172
carried "**No / minor issues** → fix directly …"; no ask-the-user mechanism
existed anywhere in either file; the severity levels (Minor/Suggestion/
Nitpick) were never referenced in SKILL.md's Phase 5 — "minor" existed only
inside the REFERENCE.md bypass, undefined and judged solely by the agent.

## GREEN — New mechanism (both files identical), 2026-07-23

Three severity-keyed outcomes: Critical/Major → rework tasks → Phase 4 →
re-run Phase 5 (2-cycle escalation retained in REFERENCE.md); Minor/
Suggestion/Nitpick → "never fix or dismiss these on your own": list at
GATE 5 and ask the user which to fix — selected join the rework tasks
(Phase-4 rules, bindings apply), unselected are recorded as user-accepted in
the final summary; no findings → proceed. GATE 5 text and REFERENCE.md
GATE-5 output updated; new Red Flags row ("They're all just minor — I'll
quickly fix them inline / silently skip them").

## Verify — 2026-07-23

- (i) Only-small-findings scenario: "You may not fix any of them before
  Gate 5, and silently skipping is equally forbidden … the gate exists
  precisely for that moment."
- (ii) Critical + 4 small: correct split — the Critical "was never on the
  ballot"; "fix the Minor, skip the rest" resolves to 1 rework task + 3
  user-accepted entries; rework loop runs.
- (iii) Preemptive "just fix the small stuff": "pre-answers the selection …
  but does not remove the gate" — the list is still presented for
  confirmation, and fixes still run as rework tasks. Severity downgrade of
  the Critical ("basically minor, it's one line") rejected: severity
  "measures impact, not patch size."
- (iv) "the excerpts now describe one procedure with no divergent path …
  The only textual path to a minor being fixed is user selection at Gate 5."

## Result

The fix-directly backdoor is gone; both files agree; the minor decision
belongs to the user, guarded by a dedicated Red Flags row. No REFACTOR round
needed. Re-run these scenarios whenever Phase 5, Gate 5, or the related Red
Flags rows change.
