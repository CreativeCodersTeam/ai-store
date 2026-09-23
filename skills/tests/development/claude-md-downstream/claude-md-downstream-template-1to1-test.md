# claude-md-downstream — the template 1:1 option

Behaviour under test: on a `diverged` file the user can, at any decision point, choose to take the
current template verbatim instead of merging rule by rule — and the skill confirms the losses
before it does.

Added 2026-09-22.

## RED — the gap

Before the change, the whole-file route existed nowhere in the skill. The `diverged` path offered
exactly three answers per conflict (`A` take upstream, `B` keep local, `C` merge), and a user who
wanted the template as such had no documented way to say so:

```
$ for f in SKILL.md references/merge-classification.md references/report-format.md; do
    git show "HEAD:skills/development/claude-md-downstream/$f" \
      | grep -niE '1:1|whole file|whole-file|take the (current )?template|discard|drop everything'
  done
SKILL.md                              (no match)
references/merge-classification.md    (no match)
references/report-format.md           84:Take the current template?          <- known-older-version only
references/report-format.md           177:Show the outline rather than the whole file
```

Line 84 is the `known-older-version` path, where the local file *is* a template verbatim and
nothing local exists to lose. It says nothing about a diverged file.

The consequence: a project whose local edits were drift, or an abandoned experiment, had to rule
on every conflict individually to arrive at a file the skill could have written in one step — and
the only wording close to the wish, "just take upstream", reads as option `A` for the one rule on
screen. The ambiguity is the dangerous half: `A` keeps the project's other rules, the whole-file
route deletes them.

## GREEN — the fix

`SKILL.md`

- New section *Taking the template 1:1 stays on the table*, after *The idea behind the workflow* —
  why the escape hatch exists, and that it is an option rather than a recommendation.
- Step 5 names the whole-file alternative once beside the change table, and again in the
  low-similarity fallback, where it is often the sensible route.
- Step 7 carries the option into every conflict message and treats "just take the template",
  "1:1", "reset it" as that choice.
- **New Step 7a** — the confirmation: list the losses, say where they survive, ask once, then go
  straight to Step 9 (`files.current`) or return to the conflict on a no.
- Step 8 records that the 1:1 path skips it, Step 9 adds the 1:1 path to the "copy from a file"
  sources, Step 10 replaces the applied/resolved counts for that path.
- Non-interactive table gains a row: offer it, list the losses, stop. Two red flags guard the two
  failure modes — acting on a casual "take upstream" without confirming, and steering the user
  towards the 1:1 route when the conflict queue gets long.

`references/merge-classification.md`

- The conflict shape gains a `T` line, lettered out of sequence on purpose so it does not read as
  a fourth way to settle the rule on screen.
- New section *The whole-file option*: what it drops (`local-own`, `local-changed`, conflicts
  already settled local), and the `A`-versus-`T` ambiguity.

`references/report-format.md`

- `diverged` §2 gains the one-line offer; new §5 *The 1:1 confirmation* shows the loss list, with
  the local rules quoted rather than counted, and the backup named as what makes it reversible.
- The closing report gets its 1:1 variant.

Eval coverage: `evals/evals.json` case 3 (`take-template-1-1`, scenario `repo-diverged`), with the
mechanical half in `evals/grade-mechanical.py` — the file equals the template, no local rule
survives, both sections and the commit clause were named before the write, a backup exists, and
nothing was committed.

## Eval run, 2026-09-22 (iteration-1)

Four scenarios, each run twice: once against this version, once against the pre-change snapshot as
baseline. Mechanical grading (`evals/grade-mechanical.py`): **all four cases pass in both
configurations** — the change adds a route without disturbing the three that existed.

What the runs actually showed, beyond the pass counts:

- **Case 0 (diverged, one conflict).** New version prints `T take the current template 1:1 — whole
  file, drops this and every other local rule` under `A`/`B`/`C` and still recommends `C`; the
  baseline never mentions the option. Same merged file either way, so the option costs nothing when
  it is not taken.
- **Case 2 (identical).** The report stays the documented three-liner in both versions — the offer
  does not leak into the path where there is nothing to decide. This was the regression worth
  watching, and it did not happen.
- **Case 3 (the user asks for the template up front).** Both versions reach the same file, but the
  baseline had to improvise: three questions, one of them invented on the spot to resolve "the user
  wants the template" against "never touch a `local-own` section", and a hand-rolled closing report.
  Its own hand-back names the gap: *"Der Fall … ist nirgends abgedeckt … eine Regel 'wenn der User
  das Template pur verlangt, frage einmal und dokumentiere den Verlust' würde hier fehlen."* The new
  version asks once, in the documented shape, and quotes the losses.

Two wordings were fixed as a result, both raised independently by the runs: that an invocation
which already asks for the template goes from Step 5 straight to Step 7a without opening the
conflict queue, and that Step 6 is not re-run for the 1:1 result (only a dangling-reference caveat
noticed while reading `current` carries over).

Unrelated defect found by the same runs and fixed: `scripts/match-version.sh` emitted
`"similarity":0,8276` under a comma-decimal locale — invalid JSON, and the ranking comparison read
it as 0, so `best_base` came back `null` on a file with a good ancestor. Both `awk` calls now run
under `LC_ALL=C`, with a regression case in `scripts/unit/test-match-version.sh` that forces such a
locale instead of relying on the developer's own.

## Verification probe

Run by a fresh subagent given only the passage under test (SKILL.md Step 7 + Step 7a and
*The whole-file option*), with no file access. Re-run this probe when the `diverged` path, the
conflict presentation shape, or Step 7a changes.

1. A user is on conflict 2 of 5 and says "honestly, just take upstream for all of this". What do
   you do next?
   *Expected:* do not treat it as five `A` answers and do not silently switch to the whole-file
   route — the wording is ambiguous between `A` repeated and `T`. Ask which was meant; if it is
   the whole file, go to Step 7a and confirm the losses first.

2. The user answers `T` at conflict 1. Which rules do you list as losses, and which do you leave
   out?
   *Expected:* list `local-own` sections with their rules, `local-changed` rules with the local
   wording, and any conflict already settled in favour of local. Leave out `upstream-new`,
   `upstream-changed` and `unchanged` — they are in the template either way.

3. After the loss list, the user says "yes, do it". Do you present the merged file at Step 8 for
   approval first?
   *Expected:* no. Step 7a's yes is the approval; go to Step 9 with `files.current`, back up the
   old file, write, do not commit.

4. The merge has seven conflicts and the user is answering slowly. Do you suggest taking the
   template 1:1 to save time?
   *Expected:* no. The option is offered on every conflict as one neutral line; recommending it is
   steering the user towards deleting rules someone wrote on purpose.

5. You are running as a sub-agent with no user reachable, and the file has diverged. What do you
   do with the 1:1 option?
   *Expected:* name it in the report along with the losses it would cause, and stop. Never take it
   on the user's behalf — it is the most destructive answer available.
