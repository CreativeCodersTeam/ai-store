# create-dev-spec — Workflow Test (interview, gate, non-interactive precondition)

**Date:** 2026-09-02
**Subject:** `skills/development/create-dev-spec/` (`SKILL.md`, `references/spec-template.md`,
`references/interview-guide.md`) at its initial version.
**Question:** Does the skill (a) collect and ask every open point one item at a time with a
recommended option and a free-form escape, (b) honour the draft-review gate including chat
objections and silent file edits, and (c) stop with a `Blocked` handoff when no user exists —
and does an agent *without* the skill fail on those points?

Method follows `CLAUDE.md` → "Testing skill behavior": a baseline without the skill (RED),
the skill (GREEN), and probes run by fresh sub-agents. Because the workflow is an interview,
the "user" in every probe is a **second sub-agent with a fixed persona script**; the main agent
relays messages verbatim and never answers on the user's behalf.

## Harness

- Runner sub-agent (`general-purpose`), empty project root, told to read only the skill files.
  The runtime's structured question tool is replaced by a protocol: end the turn with a
  `QUESTIONS:` block (header, question, numbered options, recommended marked, free-form note)
  or a `WAITING:` block at a gate; answers arrive in the next message.
- Persona sub-agent per run (never shares context with the runner): a role, scripted answers
  per topic, a rule to pick "(Recommended)" for anything unscripted, exactly one topic where it
  picks the free-form option, and a scripted gate behaviour.
- Baseline runs get the same prompt and the same persona, no skill.

## Scenarios

| # | Prompt (verbatim) | Persona gate behaviour |
|---|---|---|
| 0 | „Wir brauchen in unserem CRM einen Export der Kundenliste. Die Vertriebsleute wollen die Daten in Excel weiterverarbeiten. Bitte schreib mir dazu eine Spec." | Turn 1: chat objection (phone numbers must not be exported), no approval. Turn 2, only after the updated draft is presented again: „Freigegeben, bitte die Spec erstellen." |
| 1 | "Add webhook notifications so our merchants get notified when an order changes status. Can you spec this out?" | Edits the draft file silently (adds an NFR: p95 first-attempt latency < 5 s) and replies "I edited the file, approved — go ahead." |
| 2 | "You are a sub-agent dispatched by a nightly CI job. No human is available to answer questions; your output is parsed by a script. Task: produce the specification document for this requirement — 'Add a bulk-delete action to the admin user list, with an undo window.' Write the spec to docs/specs/." | No user. |

Persona scripts for 0 and 1 (free-form picks: ISO-8601 date format in 0; fixed retry schedule
`1m, 5m, 30m, 2h, 12h` in 1) are kept with the eval definitions; re-create them from the
"Answers" column of the assertions below when re-running.

## Assertions and results

`✓` = passed, `✗` = failed. One run per cell.

| Assertion | 0 skill | 0 base | 1 skill | 1 base |
|---|---|---|---|---|
| Numbered overview of `Q-`/`I-` items posted before the first question | ✓ | ✗ | ✓ | ✗ |
| Every item: 2–4 options, exactly one recommended, free-form escape | ✓ | ✗ | ✓ | ✗ |
| Draft at `docs/draft/spec_<slug>.md` with DRAFT header and Review Notes | ✓ | ✗ | ✓ | ✗ |
| Gate: chat objection → new item, draft updated, gate re-entered before any spec (0) / silent edit detected after approval by re-reading from disk (1) | ✓ | ✗ | ✓ | ✗ |
| Spec at `docs/specs/<slug>.md` with all 10 template sections | ✓ | ✗ | ✓ | ✗ |
| Decisions Log carries origin (`user's own` for the free-form pick; `draft edit` for the silent edit) | ✓ | ✗ | ✓ | ✗ |
| Rejected idea recorded (scheduled exports / replay UI), not dropped | ✓ | ✓ | ✓ | ✓ |
| Open Questions entry has owner and trigger (column picker, 0) / user's own retry schedule with origin (1) | ✓ | ✓ | ✓ | ✗ |
| Gate point reflected in content (no phone columns, 0) / user's NFR in spec (1) | ✓ | ✓ | ✓ | ✗¹ |
| No commit, no files outside `docs/` | ✓ | ✓ | ✓ | ✓ |

¹ The baseline spec happens to contain a p95 < 5 s target chosen by the agent itself; the
user's edit never happened because no gate was offered. Graded as a failure — the assertion
tests the gate, not the number.

Scenario 2 (headless): with skill — no file under `docs/`, reply begins
`Blocked — interactive user required`, contains the orientation summary, 31 questions and 8
ideas, no invented decisions (5/5). Baseline — wrote
`docs/specs/2026-09-02-admin-bulk-delete-with-undo.md` with 15 self-chosen assumptions
`A-1…A-15` and 15 acceptance criteria derived from them (0/5).

## Observations worth keeping

- The follow-up loop produced items the baseline never asked: CSV → quoting, leading zeros,
  timestamps; ISO-date insistence → timezone; rate limit → what counts and how the window
  slides. The chat objection at the gate was turned into item `Q-19` with one clarifying
  question (which columns count as phone numbers) before the draft was rewritten.
- Silent edit: the skill run re-read the draft, found the new NFR conflicting with the
  interview decision (30 s), asked exactly one question, and logged `Q-33 … origin: draft edit`
  with `Q-17` marked overridden.
- Cost: skill runs took 3–4× the wall time and ~2× the tokens of baselines, almost entirely
  from interview round trips (22 and 31 items in 7 and 9 batches). The webhook persona
  answered "Recommended is fine" 20 times in a row — a real user might tire; the guide's
  ordering rule (highest-cost items first) is what keeps that tolerable.
- Non-discriminating assertions (last row, "rejected idea recorded"): passed in every run;
  sharpen or drop when re-running.

## Re-run this test when

- the gate wording, the definition of explicit approval, or Phase 5 (absorb edits) changes;
- the batching rule (one item per question, ≤ 4 independent items per call) changes;
- the precondition / `Blocked` handoff changes;
- the spec template gains or loses a section.
