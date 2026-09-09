# Step Protocol (Phase 5)

Snapshot, change, verify, and — when anything is red — roll back. The commands here exist so that a
failed step costs one minute and nothing else: no lost earlier steps, no half-applied refactoring,
no user's own work destroyed.

## Snapshot

Phase 0 guaranteed a clean working tree at the start of the run, so everything uncommitted at this
moment is work this run produced: the earlier approved steps. The snapshot has to preserve *all* of
it, not just the current file.

```bash
STAMP="refactor/R-3/step-2"                      # candidate ID and step number
git stash push -u -m "$STAMP"                    # capture everything, tracked and untracked
git stash apply                                  # put it straight back — the entry is the snapshot
SNAP=$(git stash list --format='%gd %gs' | grep -F "$STAMP" | head -1 | cut -d' ' -f1)
```

`push` followed by `apply` is deliberate: `push` alone would empty the working tree. The pair leaves
the tree exactly as it was and gives you a named restore point.

**First step of the run:** the tree is still clean, so `git stash push` reports "No local changes to
save" and creates nothing. That is correct — the restore point is `HEAD`. Record `SNAP=HEAD` and use
the `HEAD` variant of the rollback below.

Only ever touch stash entries whose message carries your `refactor/…` stamp. The user may have
stashes of their own; they are none of this workflow's business.

## Verify

All three, in this order, after every step — a failure in an earlier one makes the later ones
meaningless:

1. **Build / compile.** Skip only where the language has no build step; say so in the report.
2. **Tests.** The same command as the Phase 0 baseline, so the results are comparable. Run the full
   suite unless it is genuinely too slow — in which case run the affected projects plus anything
   touching the changed symbols, and record what you narrowed it to and why.
3. **Linter**, on the changed files only. A repository-wide lint or format run buries the step's
   actual diff and makes the review worthless.

Then compare the diff against the plan:

```bash
git diff --stat
```

A file the plan did not name, or a diff much larger than described, is a failed step even when
everything is green — the change was not the one that was approved. Roll back and re-plan.

## Roll back

Immediately, on the first red. Not "fix it on top": a red state means the step reached further than
it looked, and repairing on top of it makes the next rollback larger and less certain.

```bash
# 1. discard this step's changes (everything uncommitted is in the snapshot)
git restore --worktree --source=HEAD -- .
rm -f <files this step created>                  # only files you created yourself

# 2. restore the earlier approved steps
git stash apply "$SNAP"                          # skip this when SNAP=HEAD
```

Then report what failed, with the failing test names or compiler errors, and propose a smaller step.
After the second failure on the same candidate, stop it, mark it `blocked — <reason>` in the report,
and move to the next candidate.

## Release the snapshot

After a green, verified step, the snapshot has done its job — the working tree state it protected is
now the state you want.

```bash
SNAP=$(git stash list --format='%gd %gs' | grep -F "$STAMP" | head -1 | cut -d' ' -f1)
[ -n "$SNAP" ] && git stash drop "$SNAP"
```

Re-resolve the reference by stamp before dropping: `stash@{n}` indices shift whenever another entry
is created. Never use `git stash clear` — it would delete the user's stashes too.

At the end of the run, check for leftovers and remove them:

```bash
git stash list --format='%gd %gs' | grep -F 'refactor/'
```

Report anything you could not clean up rather than leaving it for the user to find.

## Recording the step

Every green step adds one row to the report's step log, and that row is what a reviewer reads
instead of the chat:

```
| Step | Candidate | Refactoring | Site | Diff | Build | Tests | Lint | Note |
|---|---|---|---|---|---|---|---|---|
| 4 | R-3 | Extract Function | src/orders/OrderExport.cs:88 | 2 files, +31/-24 | ok | 214/214 | ok | test helper import renamed (mechanical) |
```

Mechanical test adjustments are named in the note column, always. A reviewer who sees a test file in
a refactoring diff needs to know within one line why it is there.

## Offering a commit point

After a green step, say plainly that this is a clean commit point and what it would contain — and
then stop. Committing is the user's decision; this workflow never takes it.
