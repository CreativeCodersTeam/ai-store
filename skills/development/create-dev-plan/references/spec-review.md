# Spec Review — Phase 1 Checklist

Depth material for Phase 1 of `create-dev-plan`. The review has one purpose: find every place
where two competent implementers, given only the spec, would build or test something different.
Each such place is a gap `G-n`. Gaps are *reported*; only blocking gaps are *asked*.

Contents:

- [Reading order](#reading-order)
- [Checks per spec section](#checks-per-spec-section)
- [Gap categories](#gap-categories)
- [Blocking or note](#blocking-or-note)
- [The spec's own open questions](#the-specs-own-open-questions)
- [Raw and incomplete input](#raw-and-incomplete-input)
- [Overview format](#overview-format)

## Reading order

Read the whole document once without taking notes. Then build the Requirement Inventory (every
ID, its kind, its text in one line). Only then walk the checks. A gap found on first reading is
often answered three sections later; a gap found after the inventory is real.

## Checks per spec section

The section names follow `create-dev-spec`'s template. Other requirement documents map onto them
loosely; check the content, not the heading.

| Section | Check | Gap when… |
|---|---|---|
| Goals / Non-Goals | every goal is reachable from at least one `FR-n` or `AC-n` | a goal has no requirement behind it (*unreachable goal*) |
| Context | constraints named here (contracts, platform limits, regulations) are repeated as `NFR-n` or global constraints | a constraint lives only in prose (*constraint in prose*) |
| Functional Requirements | each is one testable statement; classifiable as rule or contract; not two requirements in one sentence | "and/or" compound rules; "should be user-friendly"; a requirement that is a design decision (*not testable*, *compound*) |
| Non-Functional Requirements | each has a measurable target, or an explicit "no target — best effort" | a quality word without a number and without "no target" (*no target*) |
| Design / Data / API | each endpoint, payload, status code, schema, event, migration is a contract with `IF-n`; status codes are listed per error case | a contract without error cases; an endpoint the FRs never mention; a payload field with no requirement (*contract incomplete*, *undocumented contract*) |
| Acceptance Criteria | Given/When/Then; names the FRs it verifies; translates into one test; per FR at least one criterion is an error or edge case | criterion without FR reference; untestable wording; FR covered only on the happy path (*unlinked*, *untestable*, *happy-path-only*) |
| Open Questions | each has an owner and a trigger; no trigger is "at implementation" | see [below](#the-specs-own-open-questions) (*due now*) |
| Out of Scope | nothing listed here is needed by an FR | an FR depends on excluded work (*scope contradiction*) |
| Decisions Log | no decision contradicts an FR, NFR, or AC | contradiction (*decision vs. requirement*) |

Cross-checks, after the sections:

- every `FR-n` is named by at least one `AC-n` (*unverified FR*);
- every `AC-n` names at least one `FR-n` (*unlinked AC*);
- no two requirements say opposite things (*contradiction*);
- terms are used consistently ("customer" vs. "user" vs. "account" for the same actor)
  (*terminology*).

## Gap categories

Use these labels in the gap list; they tell the reader what kind of answer is needed.

| Category | Meaning | Typical answer |
|---|---|---|
| *untestable* | cannot be turned into a test as written | concrete wording, threshold, or observable outcome |
| *happy-path-only* | FR has no error or edge criterion | one more scenario |
| *no target* | NFR without measurable target or explicit waiver | a number, or "no target" + manual step |
| *contract incomplete* | interface without error cases / status codes | the missing cases |
| *unverified FR* / *unlinked AC* | trace missing between FR and AC | the link |
| *contradiction* / *decision vs. requirement* | two statements disagree | which one wins |
| *due now* | spec open question whose trigger has arrived | the decision |
| *missing requirement* | the plan needs a behaviour the spec does not state | a new FR (Spec Feedback) |
| *constraint conflict* | spec vs. codebase (found in Phase 3) | which one wins |
| *terminology* / *constraint in prose* / *compound* | editorial | note only |

## Blocking or note

A gap is **blocking** when, without the answer, a task cannot be defined, its interface cannot be
named, or its test cannot be written. Everything else is a **note**: it goes into Spec Feedback
and the plan proceeds.

| Blocking | Note |
|---|---|
| untestable criterion for a behaviour the plan must deliver | terminology |
| contradiction between two requirements a task must implement | constraint in prose (quote it as a global constraint) |
| contract without error cases when the task produces the contract | unlinked AC whose FR is obvious (link it, report it) |
| NFR without target **only if** the user must choose between automated and manual | NFR without target where `manual` + step is acceptable — plan it manual, report the missing target |
| due-now open question | happy-path-only FR — plan what exists, report the gap |

When in doubt, it is a note. The user sees the full list either way; the difference is only
whether the plan waits for the answer.

## The spec's own open questions

`create-dev-spec` lets the user defer questions with an owner and a trigger. At planning time:

- trigger already passed, or is "at implementation" / "when we build it" → *due now*, blocking;
- trigger in the future and the affected task can be planned without the answer → note; the
  task's Todos get a checkbox "resolve OQ-n before …" at the point where it is needed;
- no owner, no trigger → the spec is unfinished on that point; blocking.

## Raw and incomplete input

When the user chose to plan directly from a raw requirement (Phase 0, option b):

1. Split the text into statements. Each statement that says what the system does becomes an
   `FR-n` (or `IF-n` when it describes an interface); each quality statement an `NFR-n`. Quote the
   original wording next to the ID in Spec Feedback.
2. Derive acceptance criteria — one success and one error or edge scenario per functional
   requirement is the minimum — and ask the user to confirm each (`C-ac-n`, Phase 2). An error
   scenario for an action names the action's `FR-n` as well as the rule's, so the happy-path rule
   sees it. A derived criterion the user drops is recorded as dropped, not deleted.
3. Everything that a `create-dev-spec` interview would have settled (actors, permissions, data,
   integration, rollout) and that the plan needs is a blocking gap. Expect many; that is the cost
   of skipping the spec, and the plan says so in its Summary.
4. The resulting plan cites the requirement's source (issue URL, message) as its spec source.

An *incomplete* spec (has some IDs, missing others, no Decisions Log) is treated the same way for
its missing parts and used as-is for the rest.

## Overview format

Post one numbered overview before Phase 2, so the user sees the shape of what follows:

```
Requirement inventory: 5 FR (4 rule, 1 contract), 2 NFR, 6 AC, 1 IF (assigned)
Assigned IDs: IF-1 (GET /api/customers/{id}/orders/export)

Gaps
  G-1  [happy-path-only]  FR-2 — AC-1 is the only criterion; no edge case (empty total, null date)   note
  G-2  [no target]        NFR-2 — "feel fast" has no number                                        note → manual
  G-3  [untestable]       AC-6 — "opens cleanly in Excel" names no observable outcome              blocking
  G-4  [due now]          OQ-1 — column picker, trigger "when export ships"                        blocking

Blocking: G-3, G-4 → Phase 2. Notes → Spec Feedback.
```
