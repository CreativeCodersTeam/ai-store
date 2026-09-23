# Report format

What to put in front of the user for each outcome. Everything here goes in the conversation — this
skill writes no report file, only the `CLAUDE.md` it was asked to update.

Read this before writing any report.

## Contents

- [Common rules](#common-rules)
- [`identical`](#identical)
- [`known-older-version`](#known-older-version)
- [`diverged`](#diverged)
  - [The 1:1 confirmation](#5-the-11-confirmation)
- [`no-local-file`](#no-local-file)
- [`empty-template` / `no-template`](#empty-template--no-template)
- [Closing report](#closing-report)

## Common rules

- **Name the file you looked at**, absolute path, every time. In `repo` mode the target is the
  repository root, which may not be the directory the user is sitting in, and a report that says
  only "your CLAUDE.md" leaves that ambiguous.
- **Every upstream commit gets a link where one exists.** This bullet is the single home for the
  missing-link rule; SKILL.md and the per-status sections below point here rather than restating it.
  Short SHA, date, subject and URL all
  come from the script's JSON. A SHA without a link cannot be checked; a link without a subject
  says nothing. When `url` is `null` — the upstream is a mirror, a fork on an unknown host, or a
  local path, so no web address can be derived — print the SHA and say once that this upstream
  has no browsable commit view. Never invent a URL to fill the column.
- **Lead with the stale warning** when `fetch-upstream.sh` reported `stale: true`, before any
  verdict. The result is then a comparison against a cached snapshot, and the user needs that
  before they read "up to date".
- **Language follows the user.** If they are working in German, report in German. The skill's own
  files stay English.
- **No file is written before Step 9**, so no report before then may imply one was.

## `identical`

Three lines, no offers — there is nothing to decide:

```
CLAUDE.md is current.

  File:      /path/to/repo/CLAUDE.md
  Template:  claude/claude-md-template.repo.md @ 87d4623 (2026-09-18)
             "Harden the commit rule and require verification of changes"
```

The SHA is `matched.sha` — the commit that last changed the template. Do not print the branch tip
here: upstream's newest commit is usually about something else entirely, and naming it invites the
user to go read a change that has nothing to do with their file.

Resist adding anything after these lines. An outline of the template, a note that the project has
added nothing of its own, an offer to review the file — each is work nobody asked for, and it
turns a one-word answer into something the user has to read and dismiss.

## `known-older-version`

The file is an older template verbatim, so the update is a straight replacement. The report has to
show what the replacement would bring:

```
CLAUDE.md matches an older version of the template.

  File:      /path/to/repo/CLAUDE.md
  Matches:   281930c — "Add general instructions and coding guidelines" (2026-09-21)
             https://github.com/CreativeCodersTeam/ai-store/commit/281930c...
  Behind by: 2 commits that touched the template

Since then:
  a1b2c3d  2026-09-25  Harden the commit rule against bulk staging      <link>
  e4f5g6h  2026-10-02  Add the verification rule                        <link>

Those 2 commits carry 4 rule changes — behind_by counts commits, not rules:
  changed  Comment-language rule — gains "unless another specific language is requested"
  new      Verification rule — verify that changes are complete and work correctly
  new      Commit rule — stage by name, refuse .env / credentials.json / *.pem
  removed  The ponytail reference in the simplicity rule

Nothing local was added on top, so taking the current version loses nothing.

<the resulting file, in full>

Take the current template?
```

Three things carry their weight here:

- **"Nothing local was added on top."** It is the reason no conflict resolution follows, and
  without it the straight replacement looks careless.
- **The rule-level breakdown.** Commit subjects are headlines. "Harden the commit rule" does not
  tell the user that `.env` files are now refused, and that is the part they have to live with.
  The commits-versus-rules caveat from the `diverged` section applies here just as much.
- **Showing the file before the write.** "Nothing local is lost" is a claim about ownership, not a
  licence to overwrite unseen a file that governs every later session.

When the commits have no `url`, apply the common missing-link rule above: drop the link column
rather than printing empty brackets, and say once above the list that this upstream has no
browsable commit view. The `Matches:` line loses its URL too — the rule is about the report, not
about one table in it.

## `diverged`

This is the long one. Four parts, in this order — the user needs the shape of the divergence
before they can rule on any single conflict — and a fifth that appears only if they decide to take
the template 1:1 instead.

### 1. The situation

```
CLAUDE.md has diverged from the template.

  File:        /path/to/repo/CLAUDE.md
  Closest to:  281930c — "Add general instructions..." (2026-09-21), 87% similar
               https://github.com/CreativeCodersTeam/ai-store/commit/281930c...
  Upstream:    87d4623 (2026-09-18), 2 commits touched the template since that base

So: the file started from 281930c, this project changed 3 rules and added 4 of its own,
and upstream changed 2 rules in the meantime.
```

State the similarity as a percentage and, when it is low, say what that means for the confidence
of everything below.

Mind the two units: `behind_by` counts **commits**, the change table counts **rules**, and the two
rarely match — one commit can carry three rule changes. Name the unit every time. "2 changes" in
one paragraph and "3 changes" in the next reads like an error in the report, and the user cannot
tell which number to trust.

### 2. What would change

One table, one row per difference, grouped by category. Keep each rule to one line — the full text
comes later, in the proposal and in the conflict questions.

```
Apply (no local counterpart):
  upstream-new       Verification rule: verify changes are complete       a1b2c3d
  upstream-changed   Comment language rule: adds "unless requested"       e4f5g6h

Needs your decision:
  conflict           The git commit rule                                  a1b2c3d

Kept as-is (yours, untouched):
  local-own          "## Build and test" (3 rules)
  local-own          "## Deployment" (1 rule)
  local-changed      Simplicity rule — you removed the ponytail reference

Or say so at any point and I take the current template 1:1 instead — that drops both sections
above and your changes to 2 template rules.
```

That last line is the whole-file option, and one line is its whole budget. It belongs here because
this is the first point where the user can see what the merge costs them in questions and what it
protects — but a project that wrote those sections on purpose should not have to read a paragraph
arguing for their deletion. Print it, move on, and repeat it only as the `T` line on each conflict.

### 3. Problems found

Only if Step 6 found any. Each one gets the shape from
[merge-classification.md](merge-classification.md#presenting-a-conflict) — a problem the user
cannot see the two halves of is not actionable.

If nothing was found, say so in one line. Silence reads as "the check was skipped".

### 4. The proposal

After the conflicts are resolved: the change table with the decisions filled in, the `local-own`
sections listed by heading so the user can confirm nothing of theirs vanished, and then the
complete resulting file in a fenced block.

Then the approval question — a single, direct one. Not "shall I proceed?" buried under a summary.

### 5. The 1:1 confirmation

Only when the user took that route (SKILL.md Step 7a). They have asked for the template verbatim,
so the report's job is no longer to explain the merge — it is to show what leaving the merge
behind costs, once, before it happens:

```
Taking the current template 1:1 would remove these, in full:

  "## Build and test" (3 rules)
      Build with `./gradlew build` before every push
      Integration tests need `docker compose up -d db`
      Never skip the contract tests
  "## Deployment" (1 rule)
      Deployments run from CI only
  Commit rule, your clause: "Never commit on main — branch first."
  Simplicity rule: you had removed the ponytail reference; it comes back.

Everything else in your file is in the template anyway.

The removed text stays in the backup (CLAUDE.md.bak-<timestamp>) and in git history for the
committed version, so this is reversible.

Take the template 1:1?
```

Quote the local rules rather than counting them. The user chose this route to save time, which
makes them exactly the person who has not re-read their own `CLAUDE.md` in months — "4 local rules
would be dropped" is a number they can accept without knowing what they agreed to. The reversibility
line is not reassurance for its own sake: it is true, and it is what lets someone decide in one
step instead of reopening the merge.

A yes here is the approval; go to Step 9. A no returns to the conflict the user was on, with the
decisions already made still standing — say that, so declining does not look like starting over.

## `no-local-file`

```
No CLAUDE.md at /path/to/repo/CLAUDE.md.

The current template (87d4623, 2026-09-18) is <n> lines and covers:
  - General instructions
  - Git commit instructions
  - Coding guidelines

Create CLAUDE.md from it?
```

Show the outline rather than the whole file — the user is deciding whether they want a
`CLAUDE.md` at all, not reviewing its wording yet. They will see the full text at Step 8.

## `empty-template` / `no-template`

Say what was looked for, where, and that the run stops there:

```
The upstream template is not usable.

  Looked for:  claude/claude-md-template.user.md
  On branch:   main @ 87d4623
  Result:      the path does not exist upstream

Stopping — comparing against nothing would produce a proposal that empties your file.
If you expected content here, check the branch (--branch) or the path (--template-path).
```

Distinguish the two causes: `no-template` means the path is absent, `empty-template` means the file
exists but has no content. They lead to different fixes.

## Closing report

After a write, every time:

```
Done.

  Mode:      repo
  File:      /path/to/repo/CLAUDE.md
  Backup:    /path/to/repo/CLAUDE.md.bak-20260921-143002
  Synced to: 87d4623 (2026-09-18)
             https://github.com/CreativeCodersTeam/ai-store/commit/87d4623...

  Applied:   3 upstream changes
  Resolved:  1 conflict — the git commit rule, merged (both clauses kept)
  Untouched: 4 local rules across 2 sections

Nothing was staged or committed. The backup is not in .gitignore — remove it once you are happy.
```

The last line earns its place: a stray `.bak-*` file is exactly the kind of thing that gets
committed by accident by the next `git add`.

After a 1:1 take, the `Applied` / `Resolved` / `Untouched` block does not describe what happened —
no change was applied individually and nothing was kept. Replace those three lines:

```
  Taken:     the current template, verbatim — no local rules remain
  Dropped:   4 rules in 2 local sections, plus local changes to 2 template rules
             (all of it is in the backup)
```

Name the drop even though the user just approved it. This report is the line a later session, or a
colleague reading the diff, has to reconstruct the decision from, and "synced to 87d4623" alone
does not say that the project's own instructions are gone.
