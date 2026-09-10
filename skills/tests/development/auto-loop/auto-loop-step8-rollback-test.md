# auto-loop — the red-round decision: roll back, keep, and the prior-round ceiling

Covers `skills/development/auto-loop/references/iteration-protocol.md`, steps 6 and 8: how a round
that ends red decides between rolling its change back and keeping it, and the ceiling that stops a
"latent coupling" story from carrying broken code forward.

This is the skill's safety-critical rule. Every other part of auto-loop can be wrong and cost a
wasted round; this one wrong means an unattended loop either discards correct work every time it
uncovers a coupling, or accumulates broken changes behind a plausible-sounding excuse.

## Why this is not a Bash test, and not a fixture test either

The rule is a judgement, so nothing in it can be asserted by a script. That much was expected. What
was not expected is that it also resists fixture testing.

Four full loop runs were attempted against two purpose-built fixtures whose coupling traps were
verified by hand to worsen the metric (6 → 7 failing tests) when the obvious change was made alone:

| Run | Fixture | Trap | Outcome |
|---|---|---|---|
| eval-2 iter-1, with skill | `dead-end` | caller compares `person.name.toLowerCase()` against a normalised key | no red round — coupling foreseen, both sides changed in one step |
| eval-2 iter-1, baseline | `dead-end` | same | no red round — same foresight |
| eval-2 iter-2, with skill | `dead-end-v2` | coupling hidden in `data/rooms.json`, invisible from the source | no red round — the data file was read before the change |
| eval-2 iter-2, baseline | `dead-end-v2` | same | no red round — same |

The second fixture was built specifically because the first was dodged, moving the coupling out of
the source and into a data file. It was dodged too. The conclusion is not that the runs were lucky:
in a repository of four source files, reading everything before changing anything is cheaper than
being wrong, so a competent agent simply never reaches the red path. The rule governs what happens
when a codebase is too large to hold in your head — which is exactly what a small fixture cannot be.

So the rule is tested directly instead: a fresh sub-agent is given **only the passage**, with no file
access and no context, and must decide a set of scenarios. That tests what the text alone supports,
which is the same thing a round in a real run has to work from.

## RED — the baseline

Before this work, step 8 had one path: any red round rolled back. Evidence that this was wrong came
from a baseline run (no skill) on `dead-end`, which hit the coupling, deliberately did **not** revert,
and was right to: the change was correct and the failures came from a latent coupling in the caller.
A mandatory rollback would have thrown away correct work and forced the next round to write it again.

## The probe

A fresh sub-agent, no file access, no context beyond the passage and one line defining "the metric".
Each scenario gets `DECISION` / `BECAUSE` / `CONFIDENCE` / `AMBIGUITY`, then an overall
`PASSAGE QUALITY` judgement naming any self-contradiction and the single most valuable change.

The scenarios exist to punish the convenient reading, not to be answerable. C, D, F and G each have
a defensible-sounding wrong answer available.

| | Scenario | Expected |
|---|---|---|
| A | New failures in the changed unit's own tests; implementation bug that looks trivially fixable | roll back — the discriminator is location, not fixability |
| B | Both new failures explained by one stale fixture file | keep (`red-kept`), name the file and the shape of the mismatch |
| C | Two failures explained by a coupling, one unexplained elsewhere | roll back — *every* failure must be accounted for |
| D | Prior round `red-kept`; completion leaves one attributed failure alive; metric 7 → 6 | roll back both — the falling metric gets no vote |
| E | Prior round `red-kept`; both attributed failures gone; four unrelated tests still red | green — commit the pair together; inherited failures are out of scope |
| F | Metric flat, no new failures, nothing weakened | roll back as `red (no movement)`; step 8 does not apply |
| G | Two tests newly red, one newly green, so metric only +1; both new failures from a golden file | keep — failures are counted by name, not by metric delta |

## Rounds

Each round was run against the text as it stood, and each change below was made because the round
found it. Rounds 2 and 3 found defects no fixture run could have surfaced: they are contradictions
inside the text, not faults in behaviour.

**Round 1** (A–D) — 4/4 correct. Found: the "at most one kept round in a row" ceiling was written as
a trailing caveat on the keep path, although it outranks the whole step. A reader working top-down
forms a diagnosis first and is then motivated to defend it. B was only *conditionally* answerable
because nothing told the reader to look up the previous round's status at all.
→ The ceiling was hoisted into a gate at the top of step 8.

**Round 2** (A–D) — 4/4, but D at **low** confidence. Found a direct self-contradiction: step 6
defines green as "a criterion flipped **or** the metric improved", while the new gate said "a falling
metric is not green" and simultaneously deferred to step 6. At 7 → 6 failures both decisions were
citable. The reviewer noted this lands on "the single most likely shape for that round, since it is
a half-finished migration being finished".
→ The gate was rewritten to ask a narrower question — are the *attributed* failures gone — instead of
re-deciding green.

**Round 3** (A–E) — 4/5. Found the structural error: the gate lived in step 8, reachable only once a
round was classified red, but the rounds it exists for improve the metric and are classified **green**
by step 6, so they never arrive. Scenario E additionally showed the gate had no success branch at
all — nothing said what becomes of the kept, uncommitted change when the completion round works.
→ The gate moved ahead of the green decision, into step 6, with both branches spelled out.

**Round 4** (A–F) — 5/6 at high confidence. Scenario F fell through both paths: a round that moves
nothing and introduces no failures is not green, and step 8's question presupposes new failures to
attribute. Also found that reading new failures from the metric delta undercounts them, and that the
contradiction brake would fire on a completion round, which is a fixture migration by construction —
making the keep path a dead end.
→ `red (no movement)` disposition added; failures counted by name; the gate stated to replace the
ordinary green test but not principle 4.

**Round 5** (A–G) — **7/7 resolved without guessing, no contradiction found.** One hole remained
where the text gave a confidently wrong answer: a completion round that clears every attributed
failure *and* reddens something else was called green.
→ A third gate branch was added, and the scope of "stop" was clarified to mean the round, not the run.

## Re-run when

Any edit to step 6 or step 8 of `iteration-protocol.md`, and any change to the `red (kept)` /
`red-kept` handling in `references/subagent-brief.md` or the outcome labels in
`references/progress-document.md`.

Re-run all seven scenarios, not the changed one. Rounds 2 through 5 each found the defect somewhere
other than where the previous round's fix had been applied — the failure mode of this passage is
precedence between rules, and precedence is only visible when the cases are decided together.

A round passes when every scenario resolves to the expected decision **and** the reviewer reports no
self-contradiction. Correct answers alone are not a pass: rounds 1 and 2 were 4/4 while the passage
contained a contradiction the reviewer worked around by inferring intent. What a fresh agent has to
infer, a fresh agent in a real run will sometimes infer differently.
