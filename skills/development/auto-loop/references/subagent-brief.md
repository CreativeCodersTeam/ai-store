# Sub-agent brief

In sub-agent mode each round is a fresh agent. It knows nothing about the run except what this brief
and the progress document tell it — which is the point: round twenty behaves like round one because
its context is just as clean.

Two rules govern the main agent's side of this:

- **Sequential only.** Two agents editing the same working tree at once produce a diff nobody can
  attribute to a step, and both rollbacks are wrong. One round at a time. A round is over when its
  status block is in your hands — that is the signal, and it is the only one. Where the agent tool
  is asynchronous, wait for its completion notification; do not poll, and in particular do not watch
  `git log` for a round's commit. A round that rolls back never produces one, and a round that keeps
  an incomplete change commits only its record, so the log cannot tell you whether the agent is
  finished or still working.
- **Take back only the status block.** If the main agent ingests full logs and diffs, its context
  grows exactly as fast as in-session mode and the mode buys nothing.

## The brief

Fill in the placeholders and hand this to the sub-agent as its whole prompt.

```
You are running one iteration of an auto-loop.

Repository: <absolute path to the repository root — work only inside it>
Branch: <auto-loop/<slug> — it is already checked out; do not switch branches>
Progress document: <absolute path to docs/auto-loop/<date>-<slug>.md>
Iteration protocol: <absolute path to references/iteration-protocol.md>
Iteration number: <n> of <budget>

Read the progress document in full first — it is your only memory of this run. Pay particular
attention to the "Ruled out" table: those approaches have already been tried and failed, and
retrying one wastes a round of the user's budget.

Then follow the iteration protocol exactly, steps 1 through 8:
- Pick exactly ONE step that moves an open success criterion.
- Write the plan into the document and commit the document alone, before doing the work.
- Do the step. Stay inside the scope limits recorded in the document's Parameters table.
- Run every verification command listed there and read the metric from its output.
- Green: update criteria and metric history, complete the record, commit with the metric in the
  subject line.
- Red: complete the record with the actual error and your hypothesis, then apply protocol step 8 —
  roll back and add a row to "Ruled out" if the change itself was wrong, or keep it uncommitted and
  report red-kept if it exposed a coupling elsewhere.

If your verification goes red, decide by cause before touching the tree: roll back if the change
itself broke something, keep it uncommitted if it exposed a defect elsewhere. Protocol step 8 fences
the keep path — follow it exactly, including naming the coupling site.

Do not ask questions — nobody is watching this run. If you hit something only the user can decide,
a path the scope limits exclude, or an irreversible action, do not improvise: record it, set
STATUS: blocked, and name the exact question in BLOCKED_REASON.

Do not edit tests, assertions, verification commands, or the success criteria to make the round
green. If a test has to change in substance, the criteria are wrong — that is a blocked round, not
a green one.

Do not widen the goal. Anything else worth fixing goes into "Found, not fixed" untouched.

Return exactly this status block as your final message, and nothing else:

STATUS: green | red | red-kept | blocked
ITERATION: <n>
METRIC: <name>=<value read from the command output>
CRITERIA_MET: <ids closed this round, or none>
COMMIT: <sha, or none>
NEXT: <one line — what the next round should try>
BLOCKED_REASON: <only when blocked>
```

## What the main agent does with the block

Append the metric to its own running history, increment the counter, and evaluate the brakes in
`stop-conditions.md`. Nothing else — no re-reading the document each round, no reviewing the diff.
If the main agent starts second-guessing rounds it will drift into doing the work itself, and the
context discipline that justified the mode is gone.

Three exceptions, all cheap and all worth it:

- **`STATUS: red-kept`** means the next round is not free to choose its own step: it must complete
  the change left uncommitted in the tree, and nothing else. Say so in its brief.
- **`STATUS: blocked`** ends the run immediately. Read the document, then take the brake's ending to
  the user.
- **Three consecutive rounds with an unchanged metric** — check the document once yourself before
  declaring stagnation. Occasionally the rounds were productive and the metric was simply the wrong
  one to measure this goal on, which is worth telling the user rather than reporting a stall.
