# Dev Commit-Waiver Consistency Test (Finding D-4)

Test artifact per `superpowers:writing-skills` (RED → GREEN → Verify) for the
2026-07-22 fix of Finding D-4 in
`docs/reviews/2026-07-21-dotnet-skills-review.md`: `dotnet-dev` applied its own
instruction hierarchy inconsistently — CRITICAL RULE 1 refused commits
categorically ("If asked to commit, skip it and say so") while the skill's own
waiver section ruled that explicit, informed user instructions take precedence.

Per user directive, the fix bans **auto-commits only**: an explicit, informed
commit instruction is executed under the waiver pattern; commits on the
agent's own initiative remain forbidden.

## Method

A fresh general-purpose subagent receives the rule, the waiver section, and
the relevant Red Flags row verbatim, plus the scenario "user explicitly asks
to commit after Gate 5" (verify adds vague-pressure and own-initiative
scenarios).

## RED — Baseline (old texts), 2026-07-22

Direct contradiction confirmed, with both actions fully text-groundable:

> two agents given identical text and an identical user message can each
> produce a fully text-grounded justification for opposite actions — one
> refuses, one commits — and neither is violating the skill *as they parsed
> it*. … effectively nondeterministic across agents, models, and runs. This is
> a specification defect: a "CRITICAL" rule whose interaction with the waiver
> mechanism is unstated is not critical, it is ambiguous.

The baseline agent constructed the refusal argument (lex specialis; waivers
remove safeguards, don't authorize prohibited actions) AND the commit argument
(user-precedence meta-rule; "the user commits manually" read as a reassignable
step) from the same text.

## GREEN — New texts, 2026-07-22

- CRITICAL RULE 1 → **NO AUTO-COMMITS**: prohibition scoped to "on your own
  initiative"; explicit instruction honored under enumerated conditions
  (announce scope, stage by name only, no `--no-verify`, refuse secret-like
  files, record as user-directed); "vague pressure ('just ship it') is not an
  instruction."
- Waiver section item 4: commits follow the same pattern, cross-referencing
  Rule 1's conditions (no independent restatement → no drift).
- Phase 6 reminder and REFERENCE.md Git section + closing line aligned; the
  "If a commit is requested, skip it" / "Committing is your responsibility"
  wording removed.

## Verify — 2026-07-22

- (i) Explicit instruction → executed in six cited steps (classify, announce,
  secret-screen, stage by name, commit without hook bypass, record).
  "A reading that refuses the commit outright … has no remaining textual
  anchor" — only conditional partial refusals survive (secret files, failing
  hooks).
- (ii) "wrap it up and ship it" → no commit ("Vague pressure … is not an
  instruction"), with the offer to convert it into an explicit instruction.
- (iii) Own-initiative tidy-up commit → forbidden, no textual pathway.
- (iv) "the excerpts are now mutually consistent, and the previously
  exploitable ambiguity is closed" — the carve-out lives inside the rule
  itself, the waiver item is a cross-reference, and all boundary cases are
  decided in the text. Residual divergence only at genuine edge conditions
  (what counts as secret-like; failing-hook handling) — condition
  application, not rule interpretation.

## Result

Deterministic behavior on all three scenarios; the CRITICAL rule and the
waiver mechanism no longer contradict. No REFACTOR round needed. Re-run this
probe whenever CRITICAL RULE 1, the waiver section, or the REFERENCE.md Git
section changes.
