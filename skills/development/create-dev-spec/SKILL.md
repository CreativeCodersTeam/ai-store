---
name: create-dev-spec
description: >
  Use when the user wants to turn an initial requirement, feature idea, user story,
  or change request into a complete specification document before any code is
  written — including requests phrased as "write a spec", "spec this out", "create a
  requirements doc", "let's define this properly first", "I have a rough idea for…",
  or when a requirement arrives that is too vague or too thin to implement as-is.
  Runs a structured interview (open questions, gaps, your own proposals), writes a
  reviewable draft to docs/draft/, waits for explicit approval, then produces the
  final spec in docs/specs/. Not for implementing the feature — hand the finished
  spec to an implementation workflow skill afterwards.
---

# create-dev-spec — From Rough Requirement to Approved Specification

## Core Principle

A specification written alone is a guess with headings. This workflow makes the spec a
**co-authored** document: you bring structure, the questions the user has not asked
themselves yet, and concrete proposals; the user brings intent, domain knowledge, and the
final say. Nothing that shapes the spec is decided silently — every gap becomes a question,
every question gets your best proposal plus room for the user's own answer, and every answer
is recorded as a decision the spec can cite.

The output is two files:

| Artifact | Path | Purpose |
|---|---|---|
| Draft | `docs/draft/spec_<slug>.md` | Everything learned so far, written for review |
| Spec | `docs/specs/<slug>.md` | The final document, produced only after explicit approval |

`<slug>` is a 2–4 word kebab-case description of the requirement (e.g. `customer-csv-export`),
proposed by you and confirmed by the user during the interview.

## Flow Overview

```
Phase 1  Orientation        — understand the requirement                         (step 1)
Phase 2  Collection         — open questions, gaps, own remarks and ideas         (steps 2–3)
Phase 3  Interview          — one structured question per item, with proposals   (step 4)
         ↺ Follow-up loop   — new questions from answers → back into Phase 3     (step 5)
Phase 4  Draft              — write docs/draft/spec_<slug>.md                    (step 6)
GATE     Draft review       — STOP; user edits, discusses (→ Phase 3), or approves (steps 7–8)
Phase 5  Absorb edits       — re-read the draft from disk, reconcile              (step 9)
Phase 6  Specification      — write docs/specs/<slug>.md                         (step 10)
```

## Critical Rules (read before every phase)

1. **Every open point goes through the structured question tool.** Use your runtime's
   tool for structured user questions (in Claude Code: `AskUserQuestion`), never a prose
   question in a normal reply. Prose questions get answered partially, in the wrong order,
   or not at all; the tool guarantees one visible decision per item, with the options the
   user is choosing between spelled out.

2. **Every question carries your own proposals and a free-form escape.** For each item
   offer 2–4 concrete answers you would actually recommend, the recommended one first and
   marked as such, and make sure the user can always answer with something entirely their
   own. If the tool adds a free-text option automatically (Claude Code's tool does), do not
   duplicate it; if it does not, add "Something else — I'll describe it" explicitly. A
   question without proposals pushes the thinking back onto the user; a question without an
   escape hatch pretends your proposals are exhaustive.

3. **The draft gate is mandatory and only explicit approval passes it.** After writing the
   draft you STOP. The user may edit the file, raise points in chat, or approve. Only an
   unambiguous approval of the draft moves the workflow to Phase 5. "Looks good so far",
   "continue", "ok" after a question, or silence are not approvals — see the Gate section.

4. **Re-read the draft from disk before writing the spec.** The user may have edited the
   file without saying so. What is on disk wins over what you remember writing; reconcile
   conflicts explicitly (Phase 5).

5. **Never commit, never overwrite silently.** You create and edit the draft and the spec;
   the user commits. If `docs/specs/<slug>.md` already exists, ask before replacing it.

6. **Urgency waives nothing.** "Just write the spec", "we know what we want", "skip the
   questions" are not permission to skip Phase 2–3 or the gate. Acknowledge the hurry, then
   run the workflow at speed: fewer but sharper questions, batched where independent, never
   zero. A spec that skipped the interview is exactly the guess this workflow exists to
   prevent.

## Precondition — Interactive User Required

This workflow has no non-interactive mode. Phases 3 and the gate need a person answering;
inventing their answers would replace the user's intent with yours, which is the one thing a
spec must not do.

**Judge the run, not your own message channel.** The precondition is unmet only when the
whole run has no user behind it: you were dispatched by a script, CI, cron, or another
agent whose final output is consumed by a program, and no human will read your questions.

**When it is unmet:** run Phase 1 and Phase 2 only — both are read-only — then STOP and reply
with a `Blocked — interactive user required` handoff instead of starting the interview. The
handoff is your reply, not a file: do not create `docs/draft/` or `docs/specs/` content.
Include the Phase 1 summary, the full Phase 2 list of questions and ideas, and one line
stating that an interactive user can resume at Phase 3 with that list.

## Phase 1 — Orientation

Goal: understand what is being asked well enough to see what is missing.

1. Read the requirement as given — message text, linked ticket, attached file, referenced
   docs. If it points at a codebase, look at the affected area only as far as needed to
   understand terms and existing behavior; this is orientation, not analysis.
2. Write a short **orientation summary** (5–10 lines): what the user wants, for whom, why,
   and which parts of the system it touches. State the language the requirement was written
   in — it is the default for the interview and the first thing you will confirm.
3. Do not propose solutions yet and do not ask questions yet. Collect first, ask second;
   a question asked before you have the whole picture is usually the wrong question.

## Phase 2 — Collection

Goal: a complete, numbered list of everything that must be settled before the spec can be
written. Two lists, built separately so neither crowds out the other.

**2a — Open questions, ambiguities, gaps** (`Q-1`, `Q-2`, …). Walk the checklist in
[`references/interview-guide.md`](references/interview-guide.md#question-categories):
scope and boundaries, actors and permissions, inputs and outputs, business rules, edge
cases and error behavior, data and persistence, integration points, non-functional needs,
migration and rollout, testing and acceptance, constraints. For each category ask
yourself: *could two competent engineers implement this differently and both claim to have
met the requirement?* If yes, that is a question.

**2b — Own remarks and ideas** (`I-1`, `I-2`, …). Things the user did not ask for but
should decide on: a simpler alternative, a risk you see, a related capability that is cheap
now and expensive later, a convention in the codebase the requirement conflicts with. Each
idea is a proposal the user may reject; it is listed so the rejection is a recorded decision
rather than an omission.

**Fixed items that are always on the list:**

| ID | Item | Why it is always asked |
|---|---|---|
| `L-1` | Language of the draft and the spec | The user's chat language and the team's documentation language often differ |
| `L-2` | The `<slug>` for the file names | It names the artifacts and is hard to change later |

Present both lists to the user as one numbered overview before the interview starts, grouped
by category, each item one line. This is not a gate — do not wait for confirmation — but it
lets the user see the shape of the interview and add items of their own at the outset.

## Phase 3 — Interview

Goal: turn every item into a recorded decision.

**Per item**, in list order:

1. Call the structured question tool with the item as the question. Give it a short header
   (the item ID or a two-word topic), 2–4 options with your recommendation first and marked
   "(Recommended)", each option with a one-sentence description of its consequence, and a
   free-form escape per Critical Rule 2. See the
   [worked example](references/interview-guide.md#worked-example) for the shape of a good
   item.
2. Record the answer immediately in a running **Decision Log**: `ID · question · decision ·
   rationale (one line) · origin (proposal / user's own)`. The log is carried verbatim into
   the draft and the spec.

**Batching.** One item per question, always. When the tool supports several questions per
call, you may put up to four *independent* items in one call — items whose answers do not
change each other's options. Dependent items (e.g. "which storage?" and "what retention?")
go in separate calls so the second can reflect the first answer. Never merge two items into
one question.

**Follow-up loop (step 5).** After every answered round, before asking the next item, ask
yourself: *did any answer open a question that was not on the list, invalidate an item still
on it, or suggest a new idea?* Typical triggers are in the
[follow-up section](references/interview-guide.md#follow-up-loop). New items get the next
free ID (`Q-n+1`, `I-n+1`), a one-line note on which answer raised them, and are appended to
the list. Items that an answer made moot are struck with a note, not silently dropped. The
interview ends only when the list has no unanswered items.

**Exit.** When every item is decided, post the Decision Log in full and move to Phase 4
without waiting — the user reviews the decisions in the draft, where they can see them in
context.

## Phase 4 — Draft

Goal: a document the user can review and edit directly.

1. Create `docs/draft/` if it does not exist. If `docs/draft/spec_<slug>.md` already exists,
   ask (via the question tool) whether to replace it, keep both with a suffix, or abort.
2. Write `docs/draft/spec_<slug>.md` using the section structure of
   [`references/spec-template.md`](references/spec-template.md), in the language decided at
   `L-1`, with two additions that mark it as a draft:
   - a **status header** at the top: `Status: DRAFT — awaiting review`, date, and the
     requirement source (ticket, message, file);
   - a **Review Notes** section at the end listing anything you are unsure about, ideas the
     user rejected (one line each, so they are not re-proposed later), and any section you
     could only fill thinly and why.
3. Fill every template section. A section with nothing to say gets `n/a — <reason>`, never
   an omission; a missing heading reads as "forgot to think about it".
4. Report the path and a three-line summary of what the draft contains, then enter the gate.

## GATE — Draft Review (mandatory)

STOP here. End your reply with exactly this block, translated to the `L-1` language if the
user chose one other than English:

```
Draft written: docs/draft/spec_<slug>.md

Please review it. You can
  (a) edit the file directly — tell me when you are done,
  (b) raise points here in chat — we will go through them together, or
  (c) approve it as-is.

I will only produce docs/specs/<slug>.md after your explicit approval.
```

**Outcomes:**

| The user… | You… |
|---|---|
| raises points, questions, or objections in chat | treat each as a new interview item (`Q-`/`I-` with next free ID), go back to **Phase 3**, update the draft, and re-enter this gate |
| says they edited the file | go to **Phase 5** only if they also approve; otherwise re-read the file, summarize the changes you see, and ask via the question tool whether the draft is now approved |
| approves explicitly | go to **Phase 5** |
| approves *and* raises points in the same message | the points come first: back to Phase 3, update the draft, re-enter the gate — a draft with known open points is not approved |

**What counts as explicit approval:** an unambiguous statement that the draft, as it now
stands, is accepted — "approved", "genehmigt", "freigegeben", "go ahead with the spec",
"ship it as the spec". **What does not:** "looks good so far", "continue", "ok" as a reply
to a question, a thumbs-up on a partial section, or silence. When in doubt, ask the question
tool with two options: "Approve the draft as it stands" / "Not yet — I have more points".

## Phase 5 — Absorb Edits

Goal: the spec reflects the draft as it is on disk, not as you remember it.

1. Read `docs/draft/spec_<slug>.md` from disk. Compare it with what you wrote and with the
   Decision Log.
2. For every difference: the file wins. If an edit contradicts a logged decision, update
   the Decision Log with a new entry (`origin: draft edit`) rather than reverting the edit.
   If an edit introduces a new ambiguity or removes something the rest of the document
   depends on, ask exactly one clarifying question via the tool, then continue — this is
   not a return to the full interview.
3. Summarize the edits you found in two or three lines so the user sees they were read.

## Phase 6 — Specification

Goal: the final document.

1. Create `docs/specs/` if it does not exist. If `docs/specs/<slug>.md` exists, ask before
   replacing it (Critical Rule 5).
2. Write `docs/specs/<slug>.md` from [`references/spec-template.md`](references/spec-template.md):
   same sections as the draft, without the draft status header and without the Review
   Notes; the Decision Log is included in full; `Open Questions` holds only what the user
   consciously deferred, each with an owner or a trigger for when it must be decided.
3. Leave the draft in place — deleting it is the user's call.
4. Final reply: the spec path, a five-line summary (what, for whom, the three most
   consequential decisions), and one line on the next step — typically handing the spec to
   an implementation workflow skill. Do not commit.

## Red Flags — Stop and Re-read the Rules

| Rationalization | Reality |
|---|---|
| "The requirement is clear enough, I'll skip the interview" | Clear to you is not decided by the user. Phase 2 will find questions; if it truly finds none, say so and ask `L-1` and `L-2` anyway. |
| "I'll ask in plain text, it's faster" | Prose questions get half-answered. Critical Rule 1 — use the tool. |
| "I'll offer options without a recommendation" | Your recommendation is the value you add. Mark one "(Recommended)" and say why in its description. |
| "The user said 'fine', that's approval" | Only an explicit approval of the draft passes the gate. Ask the two-option approval question. |
| "I wrote the draft, I know what's in it" | The user may have edited it. Critical Rule 4 — re-read from disk. |
| "The draft is redundant, I'll write the spec directly" | The draft is the user's editing surface and the gate's object. Without it there is no review. |
| "The user is in a hurry, I'll batch everything into one question" | Batching is for independent items only, four at most. Speed comes from sharper items, not fewer decisions. |
| "This idea of mine is obviously right, no need to ask" | Then the user will confirm it in one click. Unasked, it is an assumption the spec cannot cite. |
| "The user is headless, I'll pick sensible defaults" | There is no non-interactive mode. Emit the `Blocked` handoff after Phase 2. |

## References

- [`references/interview-guide.md`](references/interview-guide.md) — question categories
  for Phase 2, how to write options, worked example, follow-up triggers
- [`references/spec-template.md`](references/spec-template.md) — the section structure for
  draft and spec, with guidance per section
