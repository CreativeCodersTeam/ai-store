# Progress document

The document at `docs/auto-loop/YYYY-MM-DD-<slug>.md` is the loop's memory, the user's window into
an unattended run, and the artefact that survives it. Everything a later round needs must be here,
because in sub-agent mode there is nothing else, and in in-session mode there may be nothing else
left after a compaction.

Two habits make the difference between a document that works and one that only looks complete:

- **Write the plan before the step, the outcome the moment it is known.** A round that dies halfway
  through — crash, interruption, compaction — leaves a working tree that the next round has to make
  sense of. `Iteration 7 — planned: extract the retry policy into its own class` is enough for that.
  A record written only at the end of a round is a record that sometimes never gets written.
- **Record numbers, not impressions.** "Fewer failures" tells the next round nothing and makes
  stagnation undetectable. `failing tests: 14 → 9` tells it everything.

## Template

```markdown
# auto-loop: <goal in one line>

- **Started:** YYYY-MM-DD HH:MM
- **Branch:** auto-loop/<slug>
- **Mode:** in-session | sub-agent
- **Status:** running | closing | criteria-met | budget-exhausted | stagnation | scope-blocked | contradiction
- **Started on unconfirmed defaults:** yes / no — <when yes, which parameters nobody confirmed>

## Goal

<The user's own words, one short paragraph. Not a rewritten, expanded version — the point is that
the user recognises it when they read the report.>

## Success criteria

| ID | Criterion | How it is checked | Status |
|----|-----------|-------------------|--------|
| C-1 | <checkable condition> | <command or unambiguous inspection> | open / met |
| C-2 | … | … | open |

## Parameters

| Parameter | Value | Origin |
|-----------|-------|--------|
| Verification command(s) | `<command>` | user / default |
| Progress metric | <name and how it is read> | user / default |
| Iteration budget | <n> | user / default |
| Time budget | <duration or none> | user / default |
| Scope limits | <excluded paths> | user / default |
| Git strategy | branch + commit per green round | user / default |
| Stagnation threshold | <n> rounds | user / default |

## Baseline

Run before the first iteration.

- Command: `<command>`
- Result: <exit code and the metric, e.g. "exit 1, 14 failing tests">
- Note: <anything the baseline revealed — a broken tool, an unexpected failure, a slow suite>

## Metric history

| Iteration | Metric | Criteria met | Result |
|-----------|--------|--------------|--------|
| baseline | 14 | 0/3 | — |
| 1 | 11 | 0/3 | green |
| 2 | 11 | 0/3 | red |

## Iteration log

### Iteration <n> — <planned | green | red | red (kept) | red (no movement) | blocked>

- **Planned:** <the single step, written before doing it>
- **Did:** <what actually changed, with paths>
- **Verification:** `<command>` → <exit code>, metric <before> → <after>
- **Outcome:** green (committed) | red (rolled back) | red (kept — <coupling site>) | blocked (<brake>)
- **Learned:** <for red rounds, the most valuable field: what was ruled out and why you now think
  it failed. For green rounds, anything that changes what the next round should try.>

## Ruled out

Approaches that were tried and did not work. A round that reads nothing else should still read this
— it is what stops the loop from walking into the same wall twice.

| Iteration | Approach | Why it failed |
|-----------|----------|---------------|
| 2 | <approach> | <the actual error, not "did not work"> |

## Found, not fixed

Things noticed during the run that are outside the goal. Noted, deliberately untouched.

| Where | What | Why it was left |
|-------|------|-----------------|
| `path:line` | <observation> | outside the goal |

## Decisions

Every choice made without the user, with the alternatives rejected. `D-1`, `D-2`, …

| ID | Decision | Alternatives rejected | Why |
|----|----------|----------------------|-----|

## Closing report

<Appended in Phase 4. See stop-conditions.md for what each ending leads with.>

- **Ended:** YYYY-MM-DD HH:MM after <n> iterations
- **Reason:** <brake>
- **Criteria:** <n>/<m> met — <which remain open>
- **Metric:** <baseline> → <final>
- **Branch:** `auto-loop/<slug>`, <n> commits, not pushed, not merged
- **Next step:** <the single most useful thing to do now>
```

## Maintaining it during the run

- The document lives inside the repository and is therefore part of the diff. It is committed
  separately from source changes, so that a rollback of a red round never destroys the record of
  why that round failed. `iteration-protocol.md` has the exact sequence.
- Append, never rewrite. Editing an earlier iteration record to look better destroys the only
  evidence of what the loop actually did — and the *Ruled out* table depends on that history being
  honest. Records deliberately carry no commit sha, so no *finished* entry ever needs patching.
  Completing an in-flight record is not rewriting: a record is written in two passes by design —
  the plan before the step, the outcome once it is known — and the heading moves from `planned` to
  the actual outcome as part of that second pass. What is forbidden is going back to a round that
  already has its outcome.
- An empty table keeps its header and gets one explicit row — `— | no round went red | —` — rather
  than being left bare. A bare header reads as an unfinished document, and a reader cannot tell
  "nothing to report" from "nobody filled this in".
- `closing` is set in the same edit that writes the closing report and lands in the same commit —
  it does not earn a commit of its own. Its value is for the run that dies while Phase 4 is being
  written: the document then says `closing` rather than `running`, so whoever finds it knows the
  rounds are over and only the report is missing.
- Keep the *Status* field at the top current. It is the first thing a user checks when they look in
  on a running loop, and the first thing the next round reads.
