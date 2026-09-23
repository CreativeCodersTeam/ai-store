# Merge classification

How to turn three files — `base`, `current`, `local` — into a decision per difference, and how to
check that the result still reads as one coherent set of instructions.

Read this before Step 5 of the workflow.

## Contents

- [The three inputs](#the-three-inputs)
- [Working at rule level](#working-at-rule-level)
- [The categories](#the-categories)
- [Deciding the category](#deciding-the-category)
  - [What counts as one rule](#what-counts-as-one-rule)
- [Contradiction checks](#contradiction-checks)
- [Presenting a conflict](#presenting-a-conflict)
- [The whole-file option](#the-whole-file-option)
- [Worked example](#worked-example)

## The three inputs

| File      | What it is                                                   | Where it comes from        |
| --------- | ------------------------------------------------------------ | -------------------------- |
| `base`    | The template version the local file most resembles           | `files.base` (`best_base`) |
| `current` | The template as it stands upstream now                       | `files.current`            |
| `local`   | The file being synchronised                                  | `files.local`              |

`base` is what makes ownership decidable. `base → current` is what upstream did; `base → local` is
what the project did. Everything in the classification follows from those two comparisons.

How far to trust `best_base.similarity`:

| Similarity  | What it means                                    | What to do                          |
| ----------- | ------------------------------------------------ | ----------------------------------- |
| ≥ 0.85      | A handful of rules differ. A solid ancestor.     | Proceed; no caveat needed.          |
| 0.70 – 0.85 | The project has edited substantially, but the    | Proceed, and say in the report that |
|             | shape of the template is still recognisable.     | the base is probable, not certain.  |
| 0.50 – 0.70 | Half the document is unaccounted for.            | Say so and let the user choose      |
|             | Ownership claims start being guesses.            | before you classify anything.       |
| < 0.50      | Calling this an ancestor is not defensible.      | Offer the fallback instead.         |

These are bands, not a formula — the number measures shared lines, so a project that reworded the
whole template without changing a single rule scores low while having changed nothing that matters.
Read the three files before deciding the band is wrong, and when it is, say why in the report.

The fallback for the bottom rows is in SKILL.md Step 5: treat the local file as unrelated and
merely list what the current template has that it lacks. That is a weaker result, and it is the
honest one — a merge built on a base nobody believes in silently attributes the project's own rules
to upstream, and then "helpfully" reverts them.

## Working at rule level

Compare **rules**, not lines. A `CLAUDE.md` is a list of directives; the unit a user can rule on is
"the commit rule", "the comment-language rule", "the section on surgical changes" — not "line 14".

A line-level view also produces false conflicts: upstream rewording a sentence and the project
adding a clause to it look like one contested block, when in truth there are two independent
changes that merge cleanly.

So for each rule, hold three versions in mind — as it reads in `base`, in `current`, in `local` —
and classify from those.

## The categories

| Category           | Condition                                          | What happens                          |
| ------------------ | -------------------------------------------------- | ------------------------------------- |
| `upstream-new`     | In `current`, not in `base`, not in `local`         | Apply                                 |
| `upstream-changed` | Differs `base → current`; `local` still matches `base` | Apply                             |
| `upstream-removed` | In `base`, gone from `current`; `local` matches `base` | Apply the removal — but see below |
| `local-own`        | In `local`, in neither `base` nor `current`         | **Never touched**                     |
| `local-changed`    | Differs `base → local`; `current` still matches `base` | Keep local, report it              |
| `unchanged`        | Same in all three                                   | Nothing                               |
| `conflict`         | Differs `base → current` **and** `base → local`     | Goes to the user, one by one          |

Two categories deserve extra care:

**`upstream-removed`** is the one that quietly deletes rules the project may still rely on. Before
applying a removal, check whether any other part of the local file refers to the removed rule — a
priority list, a "see above", a workflow step. If something does, the removal is not clean and
belongs in Step 7 as a problem, not in the applied set.

**`local-changed`** is not a conflict and needs no decision, but it does need to be *reported*.
The user should see which template rules the project has bent, because that is the list that will
turn into conflicts the next time upstream touches one of them.

## Deciding the category

For each rule:

1. Does it appear in `base`? If not, it is either `upstream-new` (it is in `current`) or
   `local-own` (it is in `local`). Both are unambiguous.
2. If it does appear in `base`, compare it with `current` and with `local` separately.
3. Neither side changed → `unchanged`. One side changed → `upstream-changed`, `upstream-removed`,
   or `local-changed`. Both changed → `conflict`.

A rule that moved to a different section without changing its wording is not a change. Do not
report reordering as a conflict; note it once in the change table if the move is worth mentioning
at all.

### What counts as one rule

Step 1 above turns on "does it appear in `base`", and that question only has an answer once
"rule" is pinned down. The trap: a bullet added by upstream and a bullet added locally are both
*new text*, so read literally they look like `upstream-new` plus `local-own` — two independent
additions, nothing to decide. That reading is wrong whenever the two bullets **extend the same
directive**, and it is wrong in the most common case there is.

So: a clause, sentence or bullet that qualifies an existing directive is part of *that* rule, not
a rule of its own. Ask what the text modifies. "Stage files by name" only means anything as a
qualification of "do not commit unless asked" — it lives under that directive, in that section,
and shares its subject. If the local file qualified the same directive, both sides changed one
rule, and that is a `conflict` even though neither side's words existed in `base`.

`local-own` is for text with no such anchor: a section the template never had, about a subject
the template never covered. "Build and Test" is `local-own`. A second bullet under the template's
own commit rule is not.

When you genuinely cannot tell whether an addition extends an existing rule or stands alone,
treat it as a conflict and ask. A needless question costs the user ten seconds; a missed conflict
silently drops one side's rule.

## Contradiction checks

Run these against the **drafted merged file**, read start to finish as an agent would have to
follow it. They are ordered by how much damage each one does when it slips through.

1. **Opposed directives.** Two rules that cannot both be obeyed. The usual shape is an upstream
   rule stated in absolutes ("never stage files automatically") next to a local rule that permits
   the thing ("stage everything before running the test suite"). These are easy to miss because
   they usually sit in different sections.

2. **Duplicate rules in different words.** Upstream adds a rule the project already stated its own
   way. Nothing breaks, but the file now says the same thing twice with two shades of meaning, and
   the next person to edit one of them will not know the other exists. Propose keeping one and say
   which.

3. **Dangling references.** A rule that names a tool, a skill, a path, a script or a branch the
   project does not have. This is the most common import problem: the template is written for the
   upstream repository, and its examples point at things only that repository owns. Check every
   proper noun an upstream change brings in.

4. **Priority rules that no longer fit.** Many `CLAUDE.md` files end with a "when rules conflict"
   section. If the merge added or removed rules, check that the ordering still covers them, and
   that a newly imported rule is not silently outranked by a local one it was meant to override.

5. **Scope drift.** An upstream rule phrased for the whole repository landing in a file whose
   local rules are scoped to one area — or the reverse. The wording applies cleanly, the intent
   does not.

Report every finding through Step 7, with the same structure a conflict gets: what the problem is,
which two pieces of text produce it, and a proposed resolution.

## Presenting a conflict

One conflict per message, then wait. Use this shape:

```
Conflict <n> of <total>: <the rule, in a few words>

Upstream (<short sha>, <date> — "<commit subject>"):
    <the upstream text>
    <link to the commit>

Local:
    <the local text>

Why upstream changed it:  <one or two lines, from the commit subject and the surrounding history>
Why it looks like you changed it:  <your reading of the local intent — say when you are unsure>
Effect of taking upstream:  <what would concretely change for this project>

Options:
  A  take upstream
  B  keep local
  C  merge — <the merged wording, written out>
  T  take the current template 1:1 — whole file, drops this and every other local rule
```

Four things make this work:

- **Name the upstream intent.** Without it the user is comparing two strings. With it they are
  making a decision, which is what was asked for.
- **Write option C out in full.** "Or we could combine them" puts the drafting back on the user.
  Where a merge is not plausible, leave C out rather than offering an empty option.
- **Keep T on every conflict**, and keep it lettered `T` rather than `D` — it is not a fourth way
  to settle *this* rule, it is a decision about the whole file, and a letter in sequence invites it
  to be picked as if it were. One line, no argument for or against; see
  [the whole-file option](#the-whole-file-option) for what happens when it is chosen.
- **Admit uncertainty about the local intent.** You are inferring it from a file, and guessing
  confidently is worse than asking.

If a decision settles other conflicts too, say which, and re-present only those that actually
changed.

## The whole-file option

`T` is the answer for a project that has stopped wanting its divergence: the local edits were
drift, an abandoned experiment, or rules the team has decided the template now covers better. For
them, ruling on six conflicts to arrive at the template is six questions too many — so the option
is on every conflict, not only on the first.

What it does **not** mean is "upstream wins this one". That is `A`, and the two are a single word
apart in casual speech ("just take upstream"). When the wording could be either, ask which was
meant before acting — the cost of the question is one line, the cost of the confusion is the
project's whole set of local rules.

Taking it hands off to SKILL.md Step 7a, which exists because the losses have to be seen before
they are accepted:

- everything classified `local-own` — whole sections the template never had;
- everything classified `local-changed` — template rules the project deliberately bent;
- any conflict already settled in favour of local earlier in the same run.

`upstream-new`, `upstream-changed` and `unchanged` rules need no mention: they are in the template
either way, so listing them buries the three categories that actually disappear.

## Worked example

`base` and `local` share this rule; upstream tightened it:

| Version   | Text                                                                                 |
| --------- | ------------------------------------------------------------------------------------ |
| `base`    | You MUST not git commit files unless explicitly asked to do so by the user.          |
| `current` | You MUST not git commit files unless explicitly asked to do so by the user. Stage files by name (never `git add -A`). |
| `local`   | You MUST not git commit files unless explicitly asked to do so by the user. Commits on `main` are forbidden; branch first. |

Both sides extended the same rule, so this is a `conflict` — but the two extensions are about
different things, and a merge keeps both:

```
Conflict 1 of 2: the git commit rule

Upstream (a1b2c3d, 2026-08-14 — "Harden the commit rule against bulk staging"):
    You MUST not git commit files unless explicitly asked to do so by the user.
    Stage files by name (never `git add -A`).
    https://github.com/CreativeCodersTeam/ai-store/commit/a1b2c3d...

Local:
    You MUST not git commit files unless explicitly asked to do so by the user.
    Commits on `main` are forbidden; branch first.

Why upstream changed it:  bulk staging had been sweeping unrelated files into commits.
Why it looks like you changed it:  to protect `main` in this repository specifically.
Effect of taking upstream:  the branch protection would be dropped — nothing else states it.

Options:
  A  take upstream
  B  keep local
  C  merge — "You MUST not git commit files unless explicitly asked to do so by the user.
     Stage files by name (never `git add -A`). Commits on `main` are forbidden; branch first."
  T  take the current template 1:1 — whole file, drops this and every other local rule
```

C is the right recommendation here, and saying so is part of the job — the two clauses do not
interact, and dropping either loses a rule someone deliberately wrote. T still gets its line:
recommending C is a judgement about this rule, and the user may be sitting on a decision about the
whole file that no per-rule recommendation can reach.
