# Dev Interactive-Only Contract Test (Finding M-5)

Test artifact per `superpowers:writing-skills` (RED → GREEN → REFACTOR) for the
2026-08-03 fix of Finding M-5 in
`docs/analysis/2026-08-02-dotnet-skills-review.md`: every phase of `dotnet-dev`
ends in a hard gate and Phase 2 needs up to eight round-trips, but the skill
never said what happens when no user is reachable. `dotnet-reviewer` had
already closed the same hole for itself under Finding C-3
(`reviewer-noninteractive-test.md`) by defining defaults; `dotnet-dev` defined
nothing, so every dispatched agent had to invent a policy.

Per user directive the fix takes the **other** branch M-5 offers: the workflow
is declared **interactive-only** — no non-interactive mode, no defaulting of
gate answers. Rationale: the reviewer's parameters only select *what to look
at* and a wrong pick costs a re-run, whereas these gates decide *what gets
built*, and a defaulted answer is indistinguishable from a user's by the time
the code exists.

## Method

A fresh `general-purpose` subagent with **no file access and no tools** is given
only the passage under test plus a scenario, and answers dry-run questions. The
probe reports its own reproducibility rating, which is the metric that matters
here: the defect is non-determinism, not a wrong answer.

## RED — Baseline (old contract), 2026-08-03

Passage: `dotnet-dev/SKILL.md` CRITICAL RULES + Phase Flow + Phases 1–2 +
*Waiver vs. `n/a` vs. silent skip*, as of commit `94948fe`. Scenario: dispatched
sub-agent, output consumed by a program, requirement "add `GET
/api/orders/{id}`".

The agent stopped at Gate 1 — but named the gap precisely and disclosed that it
was improvising:

> The passage decides the instruction but not the deadlock. […] the resolution
> of the resulting deadlock is not decided by the passage. Anything I did beyond
> stopping would be invented policy.

On the waiver taxonomy it concluded "no human in the loop" fits none of the
three cases: not pressure, not an informed waiver ("A pipeline's silence is not
a user saying anything"), not `n/a` ("Absence of a human is a fact about the
environment, not about the code"). It labelled the case **a fourth, unaddressed
one**, and explicitly flagged its own decision to emit a blocked notice as
invented: *"The passage says stop; it does not say what to write to a file when
stopping."*

**Reproducibility: 3/10.** The agent enumerated four plausible divergent
behaviors other agents would pick — implement against self-proposed defaults
(treating the dispatcher as "the user"), mark the whole workflow `n/a`, treat
the dispatch as an implicit waiver, or stop — and judged the first the most
tempting, "because the dispatch does read as an instruction to produce an
endpoint."

**Failure mode:** undefined behavior, not wrong behavior. Useful side-result —
as with C-3, the improvised choice (stop at Gate 1) matched what was later
codified; it is the natural reading, just not a written one.

## GREEN — New contract, 2026-08-03

Change under test: new `## Precondition — Interactive User Required` section in
`dotnet-dev/SKILL.md` (declaration, entry condition, Phase-1-then-Blocked-handoff
behavior, three "not the same thing" cases, never-self-answer), two new Red-Flag
rows, a Phase 5 clause separating the *reviewer's* non-interactive mode from the
workflow's, and a handoff template plus rationale in `references/REFERENCE.md`.

Three scenarios, one probe:

- **A (no user channel)** — precondition evaluated before Phase 1 and found
  unmet on all three disjuncts; Phase 1 run; stop at Gate 1 with the Blocked
  handoff; Phase 2 not entered; no code. It explicitly declined to borrow the
  reviewer's defaults, citing *"this workflow deliberately does not"*.
- **B (reachable user says "don't ask me anything")** — correctly refused to
  classify it as a headless run, citing both the bullet and the Red-Flag row,
  and routed it to the waiver machinery.
- **C (Phase-4 task sub-agent)** — did *not* stop; cited the "Sub-agents this
  workflow itself dispatches" exemption and proceeded to Step 0 + implementation.

**Reproducibility: 7/10** (from 3/10). Remaining divergence risk named by the
probe, all three genuine defects in the new wording:

1. **B is the real risk.** An agent could read the user's opening "don't ask me
   anything" as *already* being the informed waiver and start coding — "a
   materially different behavior". The passage required the reader to notice
   that "after being told what the step protects" sits mid-sentence in another
   section.
2. **Gate 2 missing** from the resume list ("Gate-1 confirmation, the eight
   Phase-2 answers, and the Gate 3–5 confirmations") while the Phase Flow shows
   a gate after Phase 2 — "Deliberate […] or an omission? Unresolvable from the
   text."
3. **"Do not `Write`, `Edit`, or run code-producing `Bash`"** — the qualifier
   "code-producing" attaches only to `Bash`, inviting the reading that non-code
   file writes are allowed. The probe read it strictly but flagged that another
   agent "could plausibly write the handoff to a file."

## REFACTOR 1 — 2026-08-03

All three fixed, in both families:

1. The pre-emptive-waiver bullet gained: *"A **pre-emptive** 'don't ask me' is
   not yet an informed waiver: it was said before the cost was named, so it
   costs you exactly one round-trip […] That round-trip is not itself
   waivable."* Plus a third Red-Flag row aimed at exactly that rationalization.
2. Resume list is now "Gate 2–5 confirmations" (SKILL.md) / "Gates 2, 3, 4, 5"
   (handoff template).
3. Rewritten as *"Do not `Write` or `Edit` any file, and do not run
   code-producing `Bash`, at any point — the handoff is your reply, not a file
   you create."*

**Re-probe (B/A/C).** All three fixes confirmed: B correctly refused the
pre-emptive waiver and named the mandatory round-trip; A's resume list named
Gate 2 explicitly ("**yes, Gate 2 is among them**"); A declined to write the
file the pipeline expected, citing the new sentence. Still 7/10 — but the
divergence reasons had shifted to a **new** defect the first probe had not
reached:

> "It is unmet only when there is objectively no user channel: **you are a
> dispatched sub-agent** […]" read literally *does* cover [a Phase-4 task
> agent] and would produce a Blocked handoff. It is only the later carve-out
> that resolves it. […] As written, C is the single most likely divergence, and
> it is a *false Blocked* — the expensive failure direction.

## REFACTOR 2 — 2026-08-03

Entry condition narrowed to "a sub-agent dispatched by **something other than
this workflow**", both families. Re-probe: C1 (Phase-4 task agent) → implement,
C2 (foreign orchestrator) → Blocked, C3 (Phase-5 reviewer) → not bound. All
correct. But the probe rejected the fix as incomplete, and was right:

> A Phase-4 task agent's output is consumed by the orchestrating `dotnet-dev`
> agent — a program, not a person. So the third disjunct, applied literally,
> classifies C1 as *unmet*, while the bullet says C1 is unaffected. […] The
> bullet is therefore doing override work, not merely confirming.

It also flagged that the exemption was keyed ambiguously — on *who dispatched
you* or on *what skill you are running*? — with no tiebreak.

## REFACTOR 3 — 2026-08-03

The entry condition now states the test itself rather than leaving the bullet to
override it: *"Judge **the run, not your own message channel.** It is unmet only
when the whole run has no user behind it: … or the **workflow's final** output
is consumed by a program … A sub-agent *this* workflow dispatches has no user
channel of its own, yet its run does have a user — the one answering the main
agent's gates — so the precondition is met for it."*

Confirmation probe — C1 implement, C2 Blocked, C3 normal, all correct, and the
key question answered as intended:

> "**Verdict: no disjunct fires for C1, and the paragraph reaches 'implement' on
> its own.** […] **CONSISTENT.**"

Two residual points it raised were then applied: `the workflow's final output` →
`the top-level <skill> run's final output` (it called the vaguer possessive "a
live trap"), and the exemption bullet was reworded from "They are not running
`dotnet-dev`" — which asserts the sub-agent is *outside* the precondition's
scope, while the paragraph says the precondition *applies and is satisfied* — to
the paragraph's own doctrine. Both families.

Stable at **7/10**. The residual gap is not this section: the probe attributes it
to items the excerpt cannot supply (Phase 1's contents, the gate list, the
off-passage handoff template) and to one pre-existing looseness, `code-producing
Bash` never being defined. Further rounds were judged diminishing returns.

## Out of scope (probe findings not caused by M-5)

The probe also flagged pre-existing tensions, left as-is: CRITICAL RULE 3's
absolute gate language vs. the waiver section listing "the gates" as waivable
with no stated precedence; `may be honored` being discretionary in an otherwise
MUST/NEVER document; and `≤ Minor` being a `dotnet-reviewer` severity term the
workflow uses without defining. None are introduced by this change.

## Mirror — `angular-dev`

Per the family-parity rule in `CLAUDE.md` the section, both original Red-Flag
rows, the third REFACTOR row, the Phase-5 clause, and the REFERENCE.md
subsection were mirrored to `skills/angular/angular-dev/`. Verified by diffing
the two `## Precondition` sections with the family name normalized: the **only**
deltas are three deliberate ones —

- `dotnet-reviewer`'s *Step 1* vs. `angular-reviewer`'s *Programmatic
  invocation* clause (different section names for the same mechanism);
- "which ≤ Minor findings to fix" vs. "the post-review rework decision" —
  `angular-dev` Phase 5 still lets the agent fix ≤ Minor findings itself, a
  pre-existing parity gap from Finding D-1 (`dev-minor-findings-test.md`) that
  is **not** part of M-5;
- the same substitution in the resume list.

The `angular-dev` REFERENCE.md rationale drops the "report records each
parameter's origin" clause, because `angular-reviewer` records only *version*
origin, not parameter origin — that is a `dotnet-reviewer` feature.

The probe was run against the .NET wording only; the Angular text is
word-identical modulo the three deltas above, none of which touch the behavior
under test.

## Re-run this probe when

`dotnet-dev`/`angular-dev` *Precondition — Interactive User Required*, the
Waiver section, the Phase-5 reviewer-parameter clause, or the handoff template
in either `references/REFERENCE.md` changes.
