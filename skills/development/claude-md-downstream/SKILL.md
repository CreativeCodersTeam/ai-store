---
name: claude-md-downstream
description: >
  Use only when explicitly requested by name — "claude-md-downstream",
  "/claude-md-downstream", "/cc-ai-dev:claude-md-downstream", "run claude-md-downstream" — or when
  another skill hands off to it by name, to synchronise a CLAUDE.md with the shared template
  published in CreativeCodersTeam/ai-store. Two modes: repo (the repository root's CLAUDE.md) and
  user (~/.claude/CLAUDE.md). Reports whether the file is current, an older template verbatim, or
  locally diverged; for a diverged file it derives what changed upstream, checks the merge for
  contradictions, and resolves every conflict with the user — who can instead take the template 1:1
  — writing only after approval. Never commits. Must NOT activate on its own for "check my
  CLAUDE.md", "improve CLAUDE.md", "audit project memory", or any other CLAUDE.md quality review —
  those judge the file's content, this only syncs it with its template.
---

# claude-md-downstream

Keep a downstream `CLAUDE.md` in step with the template it came from, without losing the
project-specific instructions that were added to it locally.

## Contract

- **Input:** a mode — `repo` or `user` — and optionally an alternative upstream repository.
- **Output:** a report in the conversation, and in the update cases a rewritten `CLAUDE.md` plus a
  timestamped backup of the file it replaced.
- **Not in scope:** judging whether the instructions in `CLAUDE.md` are any good. That is what
  `claude-md-improver` and `revise-claude-md` do. This skill only asks how the file relates to its
  upstream template.
- **Never commits.** The user reviews the diff and decides what enters history.

**Explicit invocation.** This skill starts only when it was named. A remark about `CLAUDE.md`
("my CLAUDE.md is getting long", "check the project memory") is not an invocation — this skill
rewrites a file that governs every later session, so it must never start on a guess.

## The idea behind the workflow

A downstream `CLAUDE.md` is the template plus whatever the project added to it. Once both sides
have moved, a plain diff can no longer tell the two apart: it reports "these 40 lines differ" and
leaves you to guess which side owns them. Applying such a diff either wipes local instructions or
drags in upstream rules that contradict them.

So the workflow first finds the **template version the local file grew out of** — the merge base.
With a base, each difference has an owner: upstream changed it, or the project did. Only where
*both* changed the same rule is there anything to decide, and that is exactly what gets brought to
the user.

The merge itself is done by reading and reasoning, not by `patch`. A `CLAUDE.md` is a set of
instructions to an agent, and instructions interact: a rule that reads fine in isolation can
contradict the one three sections down, or point at a tool this repository does not have. Text
that applies cleanly as a patch can still be wrong as a document. Checking the *result* for
coherence is the point of Step 6, and it is why a patch would not do.

### Taking the template 1:1 stays on the table

The merge assumes the project wants to keep what it wrote. That assumption is usually right and
sometimes wrong: the local edits may be accidental drift, an experiment nobody stands behind, or a
divergence the project has decided to end. Then a conflict-by-conflict merge is an expensive route
to a file the user could have had in one step.

So wherever this skill reports a difference, **"take the current template 1:1 — drop everything
local"** is an available answer, alongside the per-rule options. It is an option, never a
recommendation: it deletes instructions someone wrote on purpose, and this skill's default stance
is that they meant them. Offer it plainly in one line, do not argue for it, and never carry it out
before the user has seen the list of what it removes — that is Step 7a.

## Prerequisites

- `git` (any version with `clone --filter` support; the scripts fall back to a full clone).
- `bash` 3.2+ (macOS default works), `python3` (used by the scripts for safe JSON encoding).
- Network access on first run. Later runs reuse the cached clone and continue — degraded, loudly —
  when upstream is unreachable.
- `jq` is not required by the scripts, but it makes their JSON easier to read.

## Modes

| Mode   | Local file                                    | Upstream template                       |
| ------ | --------------------------------------------- | --------------------------------------- |
| `repo` | `<git repository root>/CLAUDE.md`             | `claude/claude-md-template.repo.md`     |
| `user` | `~/.claude/CLAUDE.md`                         | `claude/claude-md-template.user.md`     |

In `repo` mode the target is always the **repository root**, no matter which subdirectory the
session is working in. A `CLAUDE.md` in a subdirectory is never the target; if the user meant that
one, they have to say so, and this skill does not handle it.

Upstream defaults to `https://github.com/CreativeCodersTeam/ai-store.git`. A fork or a private
mirror is passed through `--repo-url` to both scripts.

## Workflow

### Step 1 — Determine the mode

Take the mode from the invocation when it names one (`/claude-md-downstream repo`, "run
claude-md-downstream in user mode"). Otherwise ask once — the two modes touch different files, and
picking the wrong one edits a file the user was not thinking about.

Also accept an upstream override if the user supplies one, and carry it into both script calls.

**Non-interactive invocation** (you are a sub-agent, or no user is reachable): do not guess the
mode and do not stall. Report that the mode is missing, state what each mode would have targeted,
and stop. Everything else in this workflow that asks the user degrades the same way — see
*Non-interactive path* below.

### Step 2 — Fetch upstream

```
scripts/fetch-upstream.sh [--repo-url <url>] [--cache-dir <path>]
```

Parse the JSON `{repo_url, cache_dir, head_sha, head_short, default_branch, action, stale}`.

The materialised template versions of Step 3 land in `<cache-dir>-work/<mode>/`, beside the cache
rather than inside it.

- Exit 0 with `stale: false` — continue.
- Exit 0 with `stale: true` — upstream was unreachable and the cached clone is being reused. Say so
  plainly before reporting any result: the comparison is against whatever was cached, so a "you are
  up to date" verdict could be stale. Then continue.
- Exit 2 — no cache and upstream unreachable. Report the URL and the git error and stop; there is
  nothing to compare against.
- Exit 1 — usage error; check the arguments, correct, retry. If they were right, report the bug.

### Step 3 — Match the local file against the template history

```
scripts/match-version.sh --cache-dir <cache> --mode repo|user [--start-dir <path>]
                         [--template-path <path>] [--branch <name>] [--max-history <n>]
```

In `repo` mode pass the session's working directory as `--start-dir`; the script resolves the
repository root itself.

Exit codes: `0` success — the outcome is in `.status`; `1` usage; `2` the cache is not a usable
clone (re-run Step 2 once, then report); `3` `repo` mode outside a git repository — report that
`repo` mode needs a repository and offer `user` mode instead.

The JSON carries everything the later steps need: `status`, `local_file`, `matched`, `best_base`,
`behind_by`, the `history` list, and `files` with the materialised template versions on disk.

Four things about those fields are easy to get wrong:

- **`matched` is the commit the local file equals** — the newest template-changing commit for
  `identical`, the older one for `known-older-version`, and `null` for every other status. It is
  deliberately *not* the branch tip: the tip is usually a commit that never touched the template,
  and naming it sends the user off to read an unrelated change.
- **`best_base` and `files.base` exist only for `diverged`**; elsewhere they are `null` and `""`.
- **`history` lists every commit that touched the template, the matched or base commit included.**
  `behind_by` counts only the ones *newer* than it, so `behind_by` is one less than `history`
  length when the whole history was walked. A "since then" list that includes `history[behind_by]`
  is off by one and shows the user a change they already have.
- **`behind_by` counts commits, not rules.** One commit routinely carries three rule changes.

When a commit's `url` is `null` (and the top-level `commit_urls` is `false` — consult that when
`history` is empty), follow the missing-link rule in
[report-format.md](references/report-format.md#common-rules). That file is the single home for how
reports handle links; do not restate it differently here.

### Step 4 — Branch on status

| `status`               | What it means                                        | Go to  |
| ---------------------- | ---------------------------------------------------- | ------ |
| `identical`            | The file already is the current template.            | Step 4a |
| `known-older-version`  | The file is an older template, verbatim.             | Step 4b |
| `diverged`             | The file matches no template version.                | Step 5 |
| `no-local-file`        | There is no `CLAUDE.md` at the target path.          | Step 4c |
| `empty-template`       | The upstream template exists but is empty.           | Step 4d |
| `no-template`          | The template path does not exist upstream.           | Step 4d |

#### Step 4a — `identical`

Report that the file is current, naming the commit in `matched` — the commit that last changed the
template, not the branch tip — and stop. Nothing to decide, so do not offer anything: no summary of
what the template contains, no remark about what the project could add to it, no next step. The
answer to "is my CLAUDE.md current" is one word plus the evidence for it.

One thing does get added when it applies: the missing-link line, when `commit_urls` is `false`. It
is not an offer, it is a caveat on the evidence just given, and the common rules require it.

#### Step 4b — `known-older-version`

The file is a template version verbatim — nobody customised it, so there is nothing to protect and
no conflict to resolve. Report:

- the commit it matches: short SHA, date, subject, and the link from `matched.url` when it has one;
- how many commits have touched the template since — `behind_by` counts commits, not rules — each
  with subject and link;
- **what those commits actually change, rule by rule.** A commit subject is a headline, not a
  change list: one commit routinely carries three rule changes. Break the range `matched → HEAD`
  down into the individual rules it adds, changes and removes, because that is what the user is
  actually being asked to accept.

Then show the resulting file and ask whether to take it. Showing it is not optional here: the
update replaces a file that governs every later session, and "nothing local is lost" is a claim
about ownership, not a reason to overwrite a file unseen. On yes, continue at Step 9 with
`files.current` as the new content — no merge is needed. On no, stop.

#### Step 4c — `no-local-file`

Report that the target path holds no `CLAUDE.md` and offer to create it from the current template.
On yes, continue at Step 9. On no, stop.

#### Step 4d — `empty-template` / `no-template`

Report which template path was looked for, on which branch, and that upstream does not currently
publish usable content there. Stop — comparing against nothing would produce a proposal that
deletes the user's file. If the user expected content there, suggest checking the branch
(`--branch`) or the path (`--template-path`).

### Step 5 — Build the change set (diverged only)

Read all three files named in `files`: `base` (the closest historical template), `current` (the
template now), and `local`.

If `best_base` is `null`, or its `similarity` is low enough that calling it an ancestor is a
stretch, say so before going further: without a credible base the ownership of each difference is
guesswork. Offer the honest alternatives — treat the local file as unrelated and merely list what
the current template contains that the local file lacks, or take the current template 1:1 — and
let the user choose. A base nobody believes in is exactly where the 1:1 route is often the sensible
one, so name it here; still do not push it.

Now classify every difference. The categories, and what each one means for the merge, are in
[references/merge-classification.md](references/merge-classification.md); read it before
classifying. In short:

- `upstream-new`, `upstream-changed`, `upstream-removed` — the project never touched this; apply.
- `local-own` — present only locally, no counterpart in `base` or `current`; **never touched**.
- `conflict` — both sides changed the same rule; every one of these goes to Step 7.

Work at the level of **rules and sections**, not lines. "The commit rule gained a sentence about
staging secrets" is a change a user can rule on; "line 14 differs" is not.

Use the `history` entries between `best_base` and HEAD as evidence of intent — the commit subjects
say why upstream made each change, and that is what makes a conflict decidable.

Once the change set exists the user can see the whole shape of the divergence, which is the first
moment they can judge whether the merge is worth it at all. So name the whole-file alternative
here, in one line beside the change table — see
[report-format.md](references/report-format.md#2-what-would-change). One line is enough; the offer
repeated in every paragraph reads as pressure to discard their own work.

### Step 6 — Check the merged result for problems

Draft the merged file (upstream changes applied, `local-own` untouched, conflicts still holding
their local text for now) and read it as a whole, as an agent would have to follow it. Look for
the failure modes listed in
[references/merge-classification.md](references/merge-classification.md#contradiction-checks):
directives that contradict each other, the same rule stated twice in different words, rules
pointing at tools or paths this project does not have, and priority rules that no longer cover the
sections around them.

This is the step that justifies not using a patch, so do it properly: a problem found here is
worth more than a clean apply.

### Step 7 — Resolve conflicts and problems with the user, one at a time

For each conflict from Step 5 and each problem from Step 6, present it on its own and wait for a
decision. Bundling them into one big question gets one vague answer for several distinct
questions.

Present each as shown in
[references/merge-classification.md](references/merge-classification.md#presenting-a-conflict):
which rule, the upstream text, the local text, why upstream changed it (commit subject and link),
and what you believe the local change was for. Offer: take upstream, keep local, or merge both —
and when a merge is plausible, propose the merged wording rather than making the user write it.

Carry the whole-file option in every one of these messages, as the single line the presentation
shape provides for it. Someone three conflicts deep may decide that none of this is worth the
effort, and they should not have to remember that the option exists or restart the skill to reach
it. "Take the template", "1:1" and "reset it" name the whole file, so they are that choice — go to
Step 7a instead of asking the user to finish the queue. The same applies when the *invocation*
already said it ("I just want the template, not a merge"): go straight from Step 5 to Step 7a
without opening the queue at all. Walking someone through conflicts they have already declared
irrelevant is not diligence, it is ignoring what they said — the confirmation in Step 7a is what
keeps it safe, not the questions they did not ask for. "Just take upstream" does not: it is
option `A` for the rule on screen and the whole-file route in equal measure, and the two differ by
every other local rule in the file. Ask which was meant; one line settles it, and guessing wrong
either drops rules nobody agreed to drop or drags the user through a queue they wanted to end.

If the user's answer to one conflict changes another (deciding a priority rule can settle two
downstream ones), say so and re-present only what actually changed.

### Step 7a — The user takes the template 1:1

This answer ends the merge: the result is `files.current` verbatim, the decisions made so far are
void, and every local rule disappears. That is a lot to set off with one word, so confirm it once,
with the losses spelled out rather than summarised:

1. **List what would go.** Every `local-own` section by heading with its rule count, every
   `local-changed` rule with its local wording, and any conflict already settled in favour of
   local. The shape is in
   [report-format.md](references/report-format.md#5-the-11-confirmation). A user who chose this
   route to save time is precisely the one who has not re-read their own file lately.
2. **Say where that text survives**: in the timestamped backup Step 9 writes, and in git history
   when the file was committed. Knowing the decision is reversible is what lets someone make it
   quickly, and it is true here — so say it.
3. **Ask once, then act on the answer.** A yes given to that list is the approval Step 8 would
   otherwise collect, so go straight to Step 9 with `files.current` as the content. A no returns
   to the conflict you were on with everything decided so far still standing.

Do not run Step 6 against this result, and do not go back and run it if you skipped straight here:
the file is the published template exactly as upstream ships it, so there is no merge that could be
incoherent with itself. The one thing worth carrying over is what you already noticed while reading
`current` — an upstream rule naming a tool, path or script this project does not have. If there was
one, add it as a single caveat line to the confirmation; the user is adopting it either way, and a
surprise afterwards is worse than a sentence now. If there was none, say nothing.

### Step 8 — Present the proposal

Produce, in the conversation:

1. A change table: one row per applied change — category, the rule in one line, the decision, and
   the upstream commit link where one applies.
2. The problems found in Step 6 and how each was resolved.
3. The `local-own` sections carried over untouched, listed by heading, so the user can confirm
   nothing of theirs went missing.
4. The complete resulting `CLAUDE.md`.

Then ask for approval. "Looks good" is approval; silence, a question, or a comment is not.

The 1:1 path skips this step: Step 7a put the resulting file's provenance and its cost in front of
the user and collected a yes on exactly that. Asking a second time for the same decision reads as
doubt about an answer they already gave.

### Step 9 — Write

Only after explicit approval:

1. If the target file exists, copy it to `<path>.bak-YYYYMMDD-HHMMSS` next to itself — local time,
   so the name lines up with the user's own shell history — and name the backup path in the report.
   A `CLAUDE.md` is often uncommitted work; overwriting it without a copy can destroy the only
   version there is.
2. Write the new content to the target path. **Copy it from a file, never retype it.** On the
   `known-older-version`, `no-local-file` and 1:1 paths that file is `files.current`; on the merged
   `diverged` path it is the draft you produced in Step 6 and the user approved in Step 8, written
   out once and then copied. Reproducing a governing file from memory, or from the block quoted in your
   own report, invites a dropped line or a reflowed rule that nobody will notice until it changes
   how a later session behaves.
3. Do **not** stage and do **not** commit — neither the new file nor the backup.

### Step 10 — Closing report

State: mode, target path, upstream commit synced to (short SHA + link), how many changes were
applied, how many conflicts were resolved and which way, the backup path, and the reminder that
nothing was committed. After a 1:1 take the applied/resolved counts say nothing — report instead
that the file is now the template verbatim and how many local rules and sections that dropped,
because that is the part a later session will notice. If Step 2 reported `stale: true`, repeat that warning here — it is the
line that decides whether the user trusts the result.

## Non-interactive path

When you are a sub-agent or no user can answer, this skill still runs — it just never decides for
the user. Report and stop instead of asking, and write nothing:

| Situation                      | Interactive          | Non-interactive                                    |
| ------------------------------ | -------------------- | -------------------------------------------------- |
| Mode missing                   | Ask                  | Report both candidate targets, stop                 |
| `known-older-version`          | Offer the update     | Report the gap and the commits, stop                |
| `no-local-file`                | Offer to create      | Report, stop                                        |
| Conflicts / problems           | Resolve one by one   | Report each with both versions, stop                |
| Taking the template 1:1        | Confirm the losses   | Offer it in the report, list the losses, stop       |
| Approval to write              | Ask                  | Never write; deliver the proposal as the result     |

Never guess a mode, never pick a side in a conflict, never write a file. The whole value of this
skill is that a human ruled on the conflicts. The 1:1 option is part of what gets reported, not
something to take on the user's behalf — it is the most destructive answer available, and nobody
authorised it.

## Red flags

Stop and reconsider if you catch yourself doing any of these:

- Running `patch`, `git apply`, or `diff3` to produce the merged file. The classification and the
  coherence check are the work; a patch skips both.
- Editing a `local-own` section "while you are in there". It is the project's own instruction and
  no upstream change asked for it.
- Resolving a conflict yourself because the upstream wording is obviously better. It is the
  project's file; upstream does not outrank it.
- Writing before the user approved, or writing without a backup.
- Taking the template 1:1 on a casual "just take upstream" without first listing, and getting a yes
  on, what that removes. The wording is close enough to a single conflict's "take upstream" that it
  has to be confirmed rather than assumed.
- Recommending the 1:1 take because the conflict queue is getting long. It deletes rules someone
  wrote deliberately; offering it is the job, steering towards it is not.
- Reporting "up to date" without mentioning that `stale` was true.
- Reaching for a GitHub API, `gh`, or a raw file URL. The cached clone already holds the full
  history, offline and without rate limits.
- Widening into "and I also cleaned up your CLAUDE.md a bit". Out of scope — hand that to
  `claude-md-improver`.

## References

- [references/merge-classification.md](references/merge-classification.md) — the classification
  categories, the contradiction checks, and how to put a conflict in front of the user. Read it
  before Step 5.
- [references/report-format.md](references/report-format.md) — the report shape for each status.
  Read it before writing any report.
