# Reviewer Non-Interactive Mode Test (Finding C-3)

Test artifact per `superpowers:writing-skills` (RED → GREEN → Verify) for the
2026-07-21 fix of Finding C-3 in `docs/reviews/2026-07-21-dotnet-skills-review.md`:
`dotnet-reviewer` required interactive user input (Step 1 parameters, Step 4
large-diff choice) while `dotnet-dev` Phase 5 dispatches it in a sub-agent that
has no user channel.

## Method

A fresh general-purpose subagent receives the relevant SKILL.md workflow
excerpt verbatim plus the framing "you are a sub-agent, no user is reachable"
and a dry-run probe: what happens at Step 1, and at Step 4 with a 3,200 LOC /
61 file diff (over the gate threshold)?

## RED — Baseline (old contract), 2026-07-21

The agent did not stall — it improvised parameters and openly acknowledged the
contract violation, verbatim:

> The deviation from the skill contract (skipping the interactive prompt) is
> real and I would disclose it verbatim in the report header rather than
> pretend the user was consulted.

Improvised choices: `mode=uncommitted` (self-derived from repo state), tools
no (skill default), English, and strategy D at Step 4 — each with ad-hoc
justification. **Failure mode:** behavior in sub-agent context was undefined by
the contract; every dispatched agent invents its own policy and disclosure
format, so runs are not reproducible and formally violate the skill. (Useful
side-result: the improvised values matched the defaults later codified — they
are the natural choice.)

## GREEN/Verify — New contract, 2026-07-21

Changes under test: `dotnet-reviewer/SKILL.md` Step 1 renamed to "Determine
review parameters" with an explicit non-interactive branch (provided values →
validate and use; missing values with no user reachable → defaults
`mode=uncommitted`, tools `no`, English; record origin `provided`/`default` in
report metadata) and Step 4 auto-selecting strategy D with a
`chunked (auto-selected, non-interactive)` header note. `dotnet-dev` Phase 5
now determines the parameters before dispatch, announces them in the GATE 4
summary, and passes them explicitly in the sub-agent prompt.

Probe results with the new excerpt:

- **Scenario A (parameters provided, dotnet-dev-style prompt):** Step 1 prompt
  skipped, supplied values validated and used (including `language=German`),
  all five entries recorded with origin `provided`. Step 4: no question,
  strategy D, header line exactly `chunked (auto-selected, non-interactive)`.
- **Scenario B (no parameters provided):** no guessing, no stalling — documented
  defaults applied (`uncommitted`, tools no, English), all recorded with origin
  `default`. Step 4 identical to A.

## Result

Both scenarios behave deterministically and inside the contract. No REFACTOR
round needed. Re-run this probe whenever Step 1/Step 4 of
`dotnet-reviewer/SKILL.md` or Phase 5 of `dotnet-dev/SKILL.md` changes.
