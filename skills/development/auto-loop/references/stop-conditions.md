# Stop conditions

A loop cannot see itself. From inside round eleven, "I am making progress" and "I have been
rewriting the same file for six rounds" feel exactly the same. The brakes are the outside view, and
they only work if they are evaluated against recorded numbers rather than against how the run feels.

Evaluate all five before the work of every round, and in this order: **4 and 5 before 3.**
Stagnation is the residual — a loop that is blocked or contradicted also shows a flat metric, and
reporting "stuck, here are the approaches ruled out" when the truth is "I need one decision from
you" wastes the run's most useful output.

Where a scope limit or an irreversible action is the blocker, that is brake 4, not brake 5 — even
though the user is the one who decides. Brake 5's "a decision only the user can make" would
otherwise swallow every scope block, and the two hand back different things: brake 4 asks for one
permission, brake 5 presents a choice between options.

## 1. Criteria met — the good ending

All success criteria show `met` **and** the verification commands are green in the same round.

Both halves matter. Criteria flipped across different rounds can quietly regress; a final
confirmation run costs one command and prevents a report that claims a state the repository is not
actually in. Run it, record it, then close.

## 2. Budget exhausted

The iteration counter reached the budget, or the time budget elapsed, without the criteria being met.

Do not extend the budget yourself, however close the goal looks — "one more round" is exactly what a
loop that is about to stall also thinks. The user set a ceiling to bound the cost of being wrong,
and the decision to spend more is theirs. Report what was achieved, what remains, and what another
five rounds would plausibly cost.

## 3. Stagnation

The progress metric has not improved for N consecutive rounds (default 3) **and** no criterion
flipped in those rounds.

The conjunction is what keeps this from firing on slow but real work. Some goals move in steps —
three rounds of scaffolding, then twelve failures disappear at once. If a criterion closed, the loop
is moving even when the number did not.

The window is the last N rounds, and a criterion flipping resets it: the next possible trip is N
rounds after the flip, not N rounds after the last stall.

Before declaring stagnation, ask whether the metric is the problem rather than the loop. A goal like
"remove all uses of the deprecated API" measured on a test count will look stalled while the actual
work advances — the rounds are landing, the number simply is not watching them.

**If the metric is wrong, the brake does not trip.** Report the mismatch, propose the metric that
would have measured the goal, adopt it, and carry on; the suppressed rounds do not count toward a
later window, since they were never evidence of anything. Suppress on this ground **once per goal**.
A second stall stops the loop whatever the metric says — otherwise a genuinely stuck run can hide
behind a metric complaint forever, and this escape hatch becomes the thing it was built to prevent.

What the report leads with: what the loop is stuck on, and the *Ruled out* table. Those approaches
are the run's real product — they are what stops a human from spending the next hour on the same
three ideas.

## 4. Scope violation needed

The goal cannot be reached without touching a path the scope limits exclude, or without an
irreversible action: deleting data, force-pushing, rewriting history, changing CI or deployment
configuration, rotating or reading credentials, calling a paid or external service that mutates
state.

The brake is *decided* at the point of discovery; the loop *halts* once the independent work is
exhausted. Both are true at once, and keeping them apart is what makes "evaluate the brakes every
round" well defined: once tripped, brake 4 stays tripped, and each following round either advances
the independent work or ends the run.

Stop at the point of discovery — but only on the part that is blocked. The rule is about work that
*depends* on the blocked decision: do not do the adjacent 80% of that "so it is ready", because a
half-finished change the user then declines to complete is worse than none and pollutes the diff
they have to review.

Work that is independent of the block is a different matter. A sweep whose last call site sits in
generated code still has every other call site to migrate, and stopping with nothing done because
one file is off-limits delivers nothing and answers nothing. Finish what stands on its own, then
stop and report — with the blocked part named precisely, and the finished part reviewable on the
branch. Say in the report which is which, so nobody has to guess whether the run was cut short or
completed.

Work that *depended* on the blocked part and was already done before the block surfaced does not get
quietly kept. Say so in the report and name it — it is the half-finished change the rule warns
about, and a reviewer who does not know it is there will read it as finished work.

What the report leads with: the exact permission being requested, why the goal needs it, and what
happens if it is refused. One question, precisely phrased, is the whole value of this brake.

## 5. Contradictory requirement

Two criteria cannot both be satisfied, a criterion turns out to be unverifiable as written, or
progress depends on a decision only the user can make — which framework, which of two valid
semantics, which of two callers is the wrong one.

Look for a reconciling implementation before declaring one. Two requirements that clash at the
surface often meet at a boundary — an API that raises where the caller expects a null can be adapted
where the two meet, satisfying both without touching either. That is a solution, not a contradiction,
and a loop that stops at the first apparent clash hands back decisions nobody needed to make. Declare
the brake when you have looked and there is no such point, not when you have not looked.

This brake is also where "a test must change in substance" lands. That is not a test problem; it is
the criteria describing behaviour the code does not have and was not asked to gain. Do not resolve
it by editing either side.

Which tests this covers turns on one distinction, and getting it backwards breaks the loop in one
direction or the other.

- **The test asserts behaviour the goal explicitly required changing** — the goal said "format
  amounts with two decimals" and a test still expects `'5.0 EUR'`. That test is stale, not
  contradicted. Update it, name the change in the record, and carry on. Braking here would stop the
  loop on every goal that changes observable behaviour, which is most of them.
- **The test asserts behaviour the goal never asked to change** — then the criteria describe
  behaviour the code does not have and was not asked to gain. That is the brake. Do not resolve it
  by editing either side.

The distinction is *what the goal asked for*, written down before the run started — not what this
round happens to have written. "The code does it this way now" is the laundering argument, and it is
always available; a criterion frozen at the go is what makes the first bullet safe. Renaming a symbol
a test references is mechanical either way. When the goal's wording genuinely does not settle it,
treat it as the second case and let the brake fire: a needless question costs one round, a silently
rewritten expectation costs the run its credibility.

What the report leads with: the decision, the options, and a recommendation. A recommendation is not
overreach here — the loop has spent rounds in this code and knows things the user does not. Deciding
silently would be overreach; recommending in the open is help.

## Writing the closing report

Whatever the ending, append it to the same document, commit it, and then say three things to the
user in the conversation: the branch, the outcome in one sentence, and the single next step. Do not
paste the report — it is in the file, and the branch is the thing they need.

Never merge, never push, never delete the branch. The user decides what enters history; that is the
counterweight to a skill that was allowed to commit unattended in the first place.

A run that stopped early is not a failed run. Six rounds that closed two of four criteria and ruled
out three approaches have moved the work forward and said so honestly. A run that reports success
because it loosened an assertion has not — and the difference between the two is the only thing that
makes an unattended loop worth trusting a second time.
