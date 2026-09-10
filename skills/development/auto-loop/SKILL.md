---
name: auto-loop
description: >
  Use only when explicitly requested by name — "auto-loop", "auto loop", "Auto-Loop starten" — to run
  one goal as an unattended iteration loop until measurable criteria are met. A setup interview fixes
  the success criteria, verification commands, iteration and time budget, scope limits, mode, and Git
  strategy; after that the loop runs without asking, each round taking one step against
  docs/auto-loop/<slug>.md as its only memory, committing on green and rolling back on red. Stops on
  met criteria, exhausted budget, stagnation, a needed scope violation, or a contradiction, always
  with a closing report. Stack-agnostic. Must NOT activate on a plain implementation, refactoring, or
  bug request, on "keep going", or on scheduled recurring runs.
---

# auto-loop

Work one goal round after round, unattended, until measurable criteria say it is done — or until a
defined brake stops the run and hands control back with a report.

## Contract

- **Input:** a goal, plus the parameters the setup interview turns it into something verifiable.
- **Output:** one Markdown document at `docs/auto-loop/YYYY-MM-DD-<slug>.md`, written *during* the
  run and closed with a report, plus commits on a dedicated branch.
- **Not in scope:** deciding *what* should be built. auto-loop supplies endurance, not requirements
  work, not architecture, not root-cause analysis. A goal that is not yet clear enough to check by
  command belongs in `create-dev-spec` / `create-dev-plan` first; a goal that asks *why* something
  happens belongs in `diagnose-bug`. See Phase 0.
- **Two interactions, and only two:** the setup interview, and the go. Between the go and a brake,
  the loop does not ask. That is the entire point — and the reason the setup has to be thorough.

**Commits — deliberately, unlike the rest of this family.** Every other cc-ai-dev skill leaves
history to the user. This one cannot. A run of twenty rounds without checkpoints has no "back to
the last good state", and it ends in one sprawling working-tree diff that nobody can review round by
round. So the loop works on its own branch and commits each green iteration. The user's branch is
never touched, nothing is pushed, and nothing is merged — the branch is offered at the end and the
user decides what enters history.

## The one rule everything else serves

**The progress document is the loop's only memory.**

In sub-agent mode this is literal: each round is a fresh agent whose entire knowledge of the run is
that file. In in-session mode it is true in practice — a long run gets compacted, and you do not get
to choose when. And in both modes it is the user's only window into an unattended process they were
promised they would not have to watch.

So anything learned that is not written down is lost, and a loop that forgets rediscovers the same
dead end every round. That is the single most common way a loop like this burns a budget without
moving. Write the plan for a step *before* taking it, and write the outcome the moment it is known —
not at the end of the round, when a crash or a compaction can still eat it.

## Principles

1. **Measurable or it does not count.** A success criterion has to be checkable by a command, or by
   an inspection whose result two people would agree on without discussion. "The code is cleaner"
   cannot end a loop, because nothing can ever decide it. `dotnet test` exits 0, `rg -c TODO src`
   reports 0, "the endpoint returns 201 for a valid payload" — those can.

2. **One step per iteration.** When a round changes five things and verification goes red, you
   cannot tell which one did it, and the rollback throws the four good ones away with the bad one.
   Small rounds also keep the commit log readable, which is what makes the run reviewable afterwards.

   A step is one *change*, not one file. Where something else encodes the behaviour you are
   changing — a caller comparing against the old form, a data file keyed by it — that belongs in the
   same step, because neither half leaves the repository in a verifiable state alone. Foreseeing the
   coupling and doing both at once is the good case; discovering it only when verification goes red
   is what `references/iteration-protocol.md` step 8 handles. Same judgement, two different moments.

3. **A red round is information, not failure.** Its value is the approach it rules out. Record what
   was tried, the actual error, and why you now believe it failed — that record is the most useful
   thing the next round will read. A run of six rounds where four were red and the document explains
   all four is healthy; a run where reds vanish silently is a run that will retry them.

4. **Never weaken the instrument.** Do not edit tests, assertions, verification commands, or success
   criteria to make a round green. A loop that can move its own goalposts always succeeds and never
   delivers. If the criteria turn out to be wrong or contradictory, that is a brake — stop and ask.
   Criteria are frozen at the go.

5. **Never widen the goal.** Something else worth fixing will show up; note it in the document's
   *Found, not fixed* section and leave it. An unattended loop that also does unrequested work is
   unreviewable, and the user agreed to the scope, not to your judgement about it.

6. **The brakes exist because the loop cannot see itself.** From inside round eleven, "I am making
   progress" and "I have been rewriting the same file for six rounds" feel identical. That is why
   progress is measured against a number recorded before the run, not against a feeling.

## Workflow

```
Phase 0: Preconditions           → clean tree, git, baseline run
    ↓
Phase 1: Setup interview         → parameters, each with a recorded origin
    ↓
Phase 2: Loop plan + document    → docs/auto-loop/<date>-<slug>.md, user gives the go
    ↓
Phase 3: The loop ─── read doc → check brakes → one step → verify ───┐
    ↓                   green: commit · red: keep or roll back, record │
    │                        └───────────────────────────────────────┘
Phase 4: Termination + closing report
```

### Phase 0 — Preconditions

Four things have to be true before a setup interview is worth anyone's time.

**A loop-shaped goal — check this first.** auto-loop grinds through a known kind of change until a
number reaches zero. It is the wrong instrument for finding something out: "why does this fail
sometimes", "where is the leak", "which commit broke it". A diagnosis has no metric a round can
move, so the loop would iterate without a hypothesis and neither progress nor stagnation would be
decidable. Route those to `diagnose-bug`; route a goal too vague to check to `create-dev-spec` or
`create-dev-plan`.

Saying so and stopping is a complete outcome, not a failure to start. Write nothing — no branch, no
document, no commit — name the skill that fits, and offer auto-loop for the step after it: once the
cause is known, "apply the fix and prove it across the suite" is exactly loop-shaped.
`references/example-setups.md` section 3 works this distinction through on a flaky test.

**Explicit invocation.** This skill starts only when the user named it. It is not the answer to
"just keep going" — that is a request to continue the current work, not to hand over control of the
working tree for the next hour.

**A clean working tree.** `git status --porcelain` must be empty. Rollback of a red round is a
`git reset --hard`, and uncommitted work of the user's would be destroyed by it. If the tree is
dirty, stop, list what is there, and let the user commit or stash first.

If the directory is not a Git repository, say so plainly: red rounds cannot be rolled back and
green rounds cannot be checkpointed, so the run degrades to "hope". Offer Git strategy `none`
(see Phase 1) only if the user insists after hearing that, and record it as a decision.

**A baseline run.** Run the verification commands once, before anything else, and record the result
in the document. This is not ceremony:

- If a command does not even start — not installed, wrong path, missing dependency — fix it now,
  with the user present. An unattended loop cannot debug its own instrument, and every round would
  report a red that means nothing.
- Read the metric out of the baseline output, then write down *how* you read it — which line, which
  field. A command that starts is not the same as a metric you can parse: `node --test` prints its
  summary counts differently on a terminal than through a pipe, and a round that cannot find the
  number will invent one or report no movement. Discovering that mid-run costs a round; discovering
  it here costs a minute. Where a runner has a machine-readable reporter — TAP, JUnit XML, JSON —
  use it for the loop and record that choice as a decision; parsing human-facing output is how a
  round ends up reading a number that is not there.
- The baseline number (failing tests, warnings, occurrences — whatever the goal is about) is what
  stagnation is later measured against. Without it there is no way to distinguish progress from
  motion.
- If the baseline is already green and all criteria are met, say so and stop. Nothing to loop over.

### Phase 1 — Setup interview

Ask for these in one pass, offering the default alongside each question so the user can accept it
with a word. Record every value in the document's *Parameters* table together with its origin —
`user` or `default`. Six rounds later, that column is what explains why the loop behaved as it did.

| Parameter | What it fixes | Default when unanswered |
|---|---|---|
| Goal | One sentence, in the user's words | none — cannot proceed |
| Success criteria | The checkable conditions that end the run | derive from goal + verification command, present for confirmation |
| Verification command(s) | The objective progress measure, run every round | detect from the repo (`dotnet test`, `npm test`, `pytest`, `cargo test`, `make check`) |
| Progress metric | The single number stagnation is measured on | the count the goal is about — see below |
| Iteration budget | Hard ceiling on rounds | 10 |
| Time budget | Wall-clock ceiling | none |
| Mode | in-session or fresh sub-agent per round | sub-agent above 5 iterations, otherwise in-session |
| Scope limits | Paths the loop must not touch | generated code, migrations, vendored directories, lock files, build output, CI configuration |

| Git strategy | Branch and commit behaviour | branch `auto-loop/<slug>`, one commit per green round |
| Stagnation threshold | Rounds without metric improvement before stopping | 3 |

**The metric must measure the goal, not the verification.** Where the goal is "make the suite
green", failing tests is the right number. Where it is "remove every use of X", "get the warning
count to zero", "migrate every caller" — the metric is occurrences of X, warnings, unmigrated
callers, and the suite staying green is a *criterion*, not the metric. Getting this wrong is quietly
destructive: a sweep measured on failing tests produces round after round of correct migration work
that moves nothing, which the loop then has to treat as a round that did nothing. Ask what number
reaching zero would mean the goal is done, and measure that.

**Data and fixture files need their own answer, and the defaults above do not give one.** A data file
the verification reads is part of the instrument, exactly like an assertion: re-keying
`data/rooms.json` because the normaliser changed is a mechanical migration that preserves what the
data says, and belongs in the step that changed the normaliser. Editing it so a failing lookup
starts succeeding changes what the data asserts, and is the contradiction brake wearing a disguise.
Decide which of the two you are doing before you touch the file, record it as a decision, and name
the file in the closing report — a reviewer who sees only source changes will not think to check it.

**When nobody can answer.** If this skill runs inside a sub-agent or any other context without a
reachable user, do not stall and do not invent: fall back to the defaults above and put *confirm the
parameters* at the head of the closing report. A loop that waits for an answer that will never come
has spent the user's budget on nothing.

The fallback fills gaps in a run that should happen; it never turns a refusal into a run. If Phase 0
found the goal is not loop-shaped, an unreachable user does not make it loop-shaped — report the
routing and stop, exactly as you would with the user present.

Fall back only for what nobody stated. A request like "auto-loop: alle Tests grün, Budget 6 Runden,
du brauchst mich nicht zu fragen" answers three of these parameters outright — goal, budget, and the
fact that unattended is wanted. Those have origin `user`; recording them as `default` misreports the
run and invites a later round to override a number the user actually chose. Only the parameters left
unstated fall back, and only those need confirming afterwards.

### Phase 2 — Loop plan and the go

Create `docs/auto-loop/YYYY-MM-DD-<slug>.md` from `references/progress-document.md`, fill in the
parameters, criteria, and baseline, and create the branch.

Then show the user a compact plan — goal, criteria, budget, branch, mode, and the five brakes — and
ask for an explicit go. This is the last interaction before the loop stops, so it is the last chance
to catch a criterion that cannot be met or a budget that is off by an order of magnitude. State that
plainly rather than treating it as a formality.

**When no user is reachable**, there is no go to wait for — and waiting for one that will never come
spends the run on nothing. Start, but start conservatively: record in the document that the run
began on unconfirmed defaults, cap the iteration budget at 5 where nobody set one, and put *confirm
the parameters* at the head of the closing report. Half a run that reports honestly what it
assumed is recoverable; a loop blocked on a question nobody will answer is not.

The cap applies to a budget **nobody set**. A budget the user stated in the request stands as given —
capping it would override the one parameter they did take the trouble to decide.

**The cap does not choose the mode.** Phase 1's mode default keys off the expected number of rounds,
so a cap of 5 would quietly force in-session on every unattended run — the one situation sub-agent
mode was built for, because nobody is there to notice a context degrading. Decide it the other way
round: an unattended run uses sub-agent mode, and falls back to in-session only where this context
cannot spawn sub-agents at all. Record which of the two applied, and why.

### Phase 3 — The loop

Each round follows the same shape. The full mechanics — the exact rollback sequence, what belongs in
an iteration record, how green is distinguished from "the command exited 0" — are in
`references/iteration-protocol.md`. Read it before the first round.

```
read the document in full
    ↓
check the brakes  ──── tripped? → Phase 4
    ↓
pick exactly one step, write it into the document as planned
    ↓
do the step, inside the scope limits
    ↓
run the verification commands, record the metric
    ↓
green → update criteria, commit          red → record the dead end, roll back
    └──────────────── next round ─────────────────┘
```

Brakes are checked *before* the work of a round, not after. Discovering an exhausted budget after
another twenty minutes of work helps nobody.

**In-session mode** runs these rounds in the current conversation. Simple, and you keep everything
in view — but the context grows with every round, so use it for short runs.

**Sub-agent mode** spawns one fresh agent per round, briefed from `references/subagent-brief.md`.
The sub-agent does the work and writes the iteration record; it returns only a short status block.
The main agent stays thin and does nothing but bookkeeping: iteration counter, metric history,
brake evaluation. This is what makes a twenty-round run behave the same in round twenty as in round
one. Rounds are sequential — two agents editing the same tree at once produce a diff nobody can
attribute.

### Phase 4 — Termination and closing report

The loop ends in exactly one of five ways, all of them normal outcomes:

| Brake | Trips when | Report leads with |
|---|---|---|
| Criteria met | Every success criterion is satisfied and verification is green | what changed, and the branch to review |
| Budget exhausted | Iteration or time ceiling reached, criteria not met | what was achieved, what remains, cost of continuing |
| Stagnation | Metric has not improved for N rounds and no criterion flipped | what it is stuck on, and the approaches already ruled out |
| Scope violation needed | The goal is unreachable without touching an excluded path or doing something irreversible | the exact permission being asked for |
| Contradictory requirement | Criteria conflict, or a decision only the user can make blocks progress | the decision, with the options and a recommendation |

Whatever the reason, append the closing report to the same document — one artefact per run, with the
full history — commit it, and tell the user the branch name, the outcome, and the one thing you
would do next. Never merge, never push, never delete the branch.

In sub-agent mode, Phase 4 belongs to the **main agent**: it sets *Status* to `closing`, runs the
confirmation verification itself, writes the report, and commits it. That is the one place the main
agent runs a command rather than only keeping books, and it should — a report describing the state
of the tree ought to be written by whoever just looked at the tree, not assembled from status blocks.

Details on how each brake is evaluated, and how stagnation is distinguished from slow progress, are
in `references/stop-conditions.md`.

## Choosing the mode

| | In-session | Fresh sub-agent per round |
|---|---|---|
| Best for | up to ~5 rounds, tight feedback | long runs, repetitive goals, migrations |
| Context | grows every round | constant — each round starts clean |
| Failure mode | quality drifts late in the run | a poorly written document starves the round |
| Cost | lower | higher per round, but stable |

The deciding question is not "how big is the task" but "how many rounds do I expect". A run that is
allowed twenty rounds should not be attempted in-session, because the rounds that matter most are
the late ones — and those are exactly the ones a full context degrades.

## Red flags

Stop and reconsider if you catch yourself here — each of these is a run that will produce a
confident report about nothing:

- Starting a round without having read the document top to bottom.
- Editing a test, an assertion, or a success criterion so a round comes out green.
- Changing more than one thing in a round because they "belong together".
- Answering a question you invented, instead of tripping the contradiction brake.
- An iteration record that says "made progress" without a metric.
- Touching a path the scope limits excluded because it was obviously needed.
- Extending the budget yourself because the goal is nearly reached.
- A green round that closed no criterion and moved no metric — verify what actually changed.

## References

| File | Read it |
|---|---|
| `references/progress-document.md` | Phase 2, when creating the document; it is the template |
| `references/iteration-protocol.md` | before the first round — exact round mechanics and rollback |
| `references/subagent-brief.md` | in sub-agent mode, to brief each round |
| `references/stop-conditions.md` | when evaluating brakes, and in Phase 4 |
| `references/example-setups.md` | during the setup interview, for worked parameter sets |
