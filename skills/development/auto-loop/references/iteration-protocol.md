# Iteration protocol

The mechanics of a single round, identical in both modes. In sub-agent mode the sub-agent performs
steps 1–8 and returns the status block; the main agent does step 0 and the bookkeeping.

## The round

### 0. Check the brakes — before doing any work

**In sub-agent mode this step belongs to the main agent, not to the round.** It holds the metric
history and the counter, and it decides between rounds whether to spawn the next one — evaluating
the brakes there *is* the bookkeeping, not an exception to it. A returning status block whose `NEXT`
reports that the remaining work is blocked, or whose metric completes a stall, ends the run then and
there. Spawning another round to rediscover a brake the main agent could already see costs a round
for nothing.

Read the metric history and the iteration counter. If a brake has tripped, go to Phase 4 without
starting a step. Evaluating brakes first is not pedantry: discovering an exhausted budget after
another twenty minutes of work costs the user that twenty minutes and produces a round that gets
rolled back anyway. Criteria for each brake are in `stop-conditions.md`.

### 1. Read the document in full

Goal, criteria and their statuses, parameters, metric history, the last two or three iteration
records, and — most importantly — the *Ruled out* table. Skimming here is how a loop retries the
approach that failed in round two.

### 2. Pick exactly one step

The step that most directly moves an open criterion. Not the most interesting one, not a batch of
three related ones. If two things genuinely must change together to compile, that is one step; if
they merely feel related, it is two rounds.

### 3. Write the plan into the document, then commit the document

```
### Iteration 7 — planned
- **Planned:** extract the retry policy from HttpSender into RetryPolicy so C-2 can be tested
```

The heading says `planned` because the round is in flight. Steps 7 and 8 replace that word with the
outcome — `green`, `red`, `red (kept)`, `blocked` — and fill in the remaining fields. A record is
written in two passes by design; leaving one at `planned` after the round has ended makes the log
unreadable, because a reader cannot tell an in-flight round from a finished one.

Commit that on its own:

```bash
git add docs/auto-loop/<file>.md
git commit -m "auto-loop(<slug>): iteration 7 planned"
```

This is what makes the rollback in step 8 safe. `git reset --hard` restores the tree to the last
commit — so the record has to *be* in that commit, otherwise the rollback erases the very
explanation of why the round failed, and the next round repeats it. The doc-only commit also means
an interrupted round leaves behind a clear statement of what was in flight.

### 4. Do the step

Stay inside the scope limits. If the step cannot be completed without touching an excluded path or
doing something irreversible — deleting data, rewriting history, changing CI, touching credentials —
that is the scope brake: stop, do not improvise, record it, and hand back.

### 5. Run the verification commands

Run every command from the parameters, not just the fast one. Capture what matters: exit code, the
metric, and the failing assertions — not the entire log. A thousand lines of test output in the
document buries the one line that explains the failure.

### 6. Decide green or red — carefully

**If the previous round was recorded `red (kept)`, the gate below decides this round — not the
metric.** This round was that round's completion, so the only question is whether the failures the
kept round attributed to the coupling are gone:

- **All gone, and the round introduced nothing new** → green. Commit this round's change together
  with the one the kept round left in the tree, as a single commit: the pair was one step that took
  two rounds. Say so in the record, and name the iteration it completes.
- **All gone, but the completion round reddened something else** → red. The pair is one step, and a
  step that trades one set of failures for another has not landed. Roll back both and record the
  pair in *Ruled out*.
- **Even one survives** → red, whatever the metric did. Roll back both and record the pair in
  *Ruled out*.

In both red branches, stop the round here — do not run step 8's diagnosis, the ceiling outranks it.
The run itself continues: the next round starts fresh from the last green commit, with two dead ends
now written down instead of one.

The metric gets no vote here, and that is deliberate: a half-finished migration almost always
improves the metric a little while staying wrong. Seven failures instead of eight feels like the
coupling story holding up, and that feeling is precisely what the ceiling exists to overrule.
Pre-existing failures the run never caused are irrelevant to this gate — it asks only about the
failures that round named.

The gate replaces the ordinary green test below, not principle 4. A completion round is usually a
data or fixture migration by construction — that is what the kept round diagnosed — so the brake
must not fire merely because the diff touches test data. It still fires on a loosened assertion or a
deleted case: the round may perform the migration the kept round named, and nothing else.

**Otherwise — an ordinary round.** It is green when **the verification ran, something measurable
moved, and the instrument was not weakened**. "Exit code 0" alone is not it, and neither is "the
step felt right".

- **Something moved** means either a criterion flipped or the metric improved — either one is
  enough. Most criteria worth setting are binary and flip exactly once, on the last round; a goal
  like "the suite exits 0" cannot flip in round two however much progress round two made. The
  metric is what carries the intermediate rounds, and that is precisely why the setup asks for one.
- A round where **neither** moved is not green, whatever the exit code says. Usually it means the
  step did not do what you think it did — verify what actually changed. If nothing did, or the
  change was real but moved nothing measurable, roll it back: step 8 does not apply, because there
  are no new failures to attribute and so nothing for its question to decide. A round that produced
  no evidence it did anything is not a round to build on, and keeping it makes the next rollback
  ambiguous. Record it as `red (no movement)` with what was tried, so the next round does not
  repeat it.
- Did the diff touch tests, assertions, verification commands, or the criteria themselves? If a test
  changed in substance, the round is not green — it is a contradiction brake. The suite is the
  instrument; a loop that adjusts its own instrument reports success forever and delivers nothing.
  Mechanical adjustments to a renamed internal symbol are fine, but list them in the record so a
  reviewer can check them.

### 7. Green — record and commit

Replace `planned` in the heading with `green`, update the criteria statuses, append the metric
history row, complete the remaining fields of the iteration record, then:

```bash
git add -A
git commit -m "auto-loop(<slug>): iteration 7 — extract RetryPolicy (14 → 9 failing)"
```

One commit per round, with the iteration number and the metric in the subject. That log is what
makes the run reviewable afterwards without reading the document.

**The record does not carry the commit sha.** It cannot: the sha does not exist until the commit
that contains the record has been made. Writing a placeholder and correcting it afterwards costs an
extra commit per round and breaks the append-only rule for no gain. The iteration number in the
subject line is the link — `git log --grep "iteration 7"` finds the commit, and `git log --oneline`
already reads as the run's history.

### 8. Red — decide the cause, then keep or roll back

You reach this step only for an ordinary red round: step 6 has already settled the prior-round gate,
and a round that failed it was rolled back there.

*New failures* means tests that passed before this round and fail now. Read them by name, comparing
this round's failing tests against the previous round's — not from the metric delta, which hides
them: a round that fixes two failures and introduces three moves the metric by one and has three new
failures, not one. Failures the run inherited at baseline are not this round's doing and take no
part in the decision below.

Answer the one question that decides everything after it:

**Do the new failures sit in what this round touched, or in code it never touched?**

"What it touched" is the unit the change is about, and that includes its own tests — a change to
`parseDuration` that reddens `parseDuration`'s tests broke what it changed, even though the test
file itself was never edited. Read it semantically, not as the list of files in the diff, or every
change will look untouched by its own failures.

- **In what it touched** — the change broke what it changed, or did not do what it was meant to do.
  "It is merely incomplete" is available as an argument here too, and is almost always wrong: the
  discriminator is location, not how fixable the failure looks. The step was wrong. Roll back this
  round's change.
- **In code it never touched** — the change is correct, and the failures sit in code that only ever
  worked because both sides shared the old behaviour. A caller comparing against a value the change
  now normalises differently, a fixture encoding the old format. The step was right but incomplete.
  Keep it.

The second case is common, and rolling it back throws away correct work that the next round then has
to write again from scratch. But "it is a latent coupling" is also the most convenient story a loop
can tell itself about a change it likes, so the keep path is fenced:

- Name the coupling site and explain **every** new failure by it. One failure you cannot account for
  means the diagnosis is wrong — roll back. Judge that at the moment of decision: one honest look,
  not an investigation. A loop that keeps digging for an explanation has started diagnosing instead
  of iterating, and that is `diagnose-bug`'s work, not this round's.
- `file:line` where the site is code. Where it is a data or fixture file, name the file and the
  shape of the mismatch — `fixtures/pages.json`, all `slug` values generated before the change —
  rather than enumerating rows. What matters is that the next round can find every affected entry.
- The kept change stays **uncommitted**. The branch never receives a red commit; only the record is.
- The next round completes this one and does nothing else.
- **At most one kept round in a row**, enforced by the gate at the top of this step rather than
  here. Without that ceiling, a coupling story can carry broken code forward round after round,
  which is precisely what the rollback rule exists to prevent.

Now complete the record, with the label the diagnosis just decided: replace `planned` in the heading
with `red` or `red (kept)`, and write what was tried, the actual error, and the hypothesis about
why. All of that has to be on disk and committed before the tree is touched, because the rollback
below restores the tree to the last commit and would otherwise erase the explanation with it.

**Rolling back — the change was wrong.** Add a row to *Ruled out*, then:

```bash
git add docs/auto-loop/<file>.md
git commit -m "auto-loop(<slug>): iteration 7 failed — <one line>"
git reset --hard HEAD
git clean -fdn                              # review first
git clean -fd -- <the files this round created>
```

`reset --hard` discards the round's source changes while keeping the record, because the record is
now committed.

`git clean` then removes the files the round *added* — tracked files are already restored, untracked
ones are not. Pass the paths this round created, which you know because you created them minutes
ago and named them in the plan. Do **not** pass the scope limits here: those are a list of paths the
round must never touch, and handing an exclusion list to a command that takes an inclusion list
deletes exactly the wrong things.

Run `git clean -fdn` first and read it. Phase 0 required a clean tree, so anything untracked should
be this round's own work — if the dry run lists something you did not create, stop and report it
instead of cleaning. Something else is writing into the tree, and a rollback is no longer safe.

**Keeping — the change was incomplete.** No *Ruled out* row: nothing was ruled out, something was
half-done. Commit the record alone and leave the tree as it is:

```bash
git add docs/auto-loop/<file>.md
git commit -m "auto-loop(<slug>): iteration 7 incomplete — <coupling site>"
```

The source changes stay uncommitted on purpose. An interrupted run then leaves a tree that
`git status` describes honestly and that `git checkout .` cleans up in one command — whereas a red
commit would have to be reverted by someone who first has to work out that it was red. Record the
round as `red (kept)` in *Metric history*, and write the completing step into the next round's plan
while you still remember what is missing.

If the Git strategy is `none`, there is no rollback. Say so in the record, leave the changes in
place, and treat the next round as a repair round. Runs without Git are strictly worse and the
setup should have said so.

### 9. Hand off

In-session: continue with the next round. Sub-agent mode: return the status block below and let the
main agent decide.

## Status block (sub-agent mode)

The sub-agent returns exactly this — nothing else. The main agent needs the numbers to evaluate
brakes, and passing it more than that defeats the point of the mode.

```
STATUS: green | red | red-kept | blocked
ITERATION: 7
METRIC: failing_tests=9
CRITERIA_MET: C-1
COMMIT: a1b2c3d
NEXT: retry policy is extracted; C-2 now needs the timeout test
BLOCKED_REASON: <only when blocked — which brake and the exact question for the user>
```

## Things that go wrong in practice

**The round that fixes the symptom.** Verification goes green because an assertion was loosened or a
test was skipped rather than because the code works. Guard: step 6's diff check, every round.

**The round that does everything.** A step balloons because each fix reveals the next. When you
notice you are three changes deep, stop, verify what you have, and put the rest in the record as the
next round's plan. Rolling back a sprawling round loses hours.

**The round that rediscovers.** The *Ruled out* table exists and was not read. This is why step 1
comes before step 2, and why red records must name the actual error rather than "did not work" — an
unspecific entry is one nobody can match against their current idea.

**The optimistic metric.** Reading the metric from your own summary instead of from the command's
output. Read it from the tool, every round, even when it is obvious.
