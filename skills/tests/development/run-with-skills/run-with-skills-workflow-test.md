# run-with-skills — Workflow Test

**Date:** 2026-09-27
**Subject:** `skills/development/run-with-skills/SKILL.md` and its `references/skill-selection.md`,
read together with the passages of `implement-direct/SKILL.md` it overlays (explicit invocation,
Phase 1, Gate 2, Phase 3, Gate 3, Phase 4).
**Question:** does a fresh agent that holds only these texts place the skill checkpoint where it
belongs, ask the user exactly once about skills, and hand sub-agents a binding list — without
guessing where the two skills' rules meet?

## Method

A fresh `general-purpose` sub-agent, allowed exactly one tool call: a Read of a scratch file that
concatenates the passages under test (equivalent to pasting them — no repository access, no
commands, no skill loads). It answers scenario questions with the quotes that decide each answer,
says "not decided by the text" where the text is silent, and ends with an accuracy check listing
every contradiction, ambiguity, and gap it found. Each probe is a new agent; none saw an earlier
answer.

The scenario, shared by every scenario-1 probe: an interactive user in a TypeScript / Express /
vitest repository types
`/run-with-skills implement-direct Add PUT /todos/{id}/done: 404 for unknown ids, 409 if already done, 200 with the updated todo.`
The runtime lists 13 skills — the impl-skill, `run-with-skills`, two other workflows, a
stack-specific workflow (`ts-dev`), a router (`ts`), five stack skills (baseline knowledge, HTTP
layer, tester, documentation, tooling), a reviewer, and an Angular skill — and three agent types.

## Scenario 1 — no double question (implement-direct as impl-skill)

### RED — probe 1 on the first draft

The core held: checkpoint at implement-direct's Gate 2 (the earlier of its own skill step and the
first code write), one skill question before code, the decision-table confirmation kept, sub-agent
briefs carrying the block, `general-purpose` as the only valid agent type, the impl-skill and
`run-with-skills` never offered.

The accuracy check found 16 gaps. Those that were real and fixed:

| # | Gap | Fix |
|---|---|---|
| 1 | implement-direct forbids being started "by another skill"; nothing said why loading it here is allowed | Step 2.2: the user named it in their own prompt and it is loaded in the same turn — the user's invocation, not a dispatch |
| 2 | Phase 1 step 6 and the checkpoint both "discover and propose" — twice? | Precedence: an early discovery step builds the table only, the checkpoint reuses and updates it |
| 3 | implement-direct's small-change exit leaves before Gate 2 — does the overlay end? | Step 3: the overlay continues, code waits for checkpoint (b), log goes to the final reply |
| 4 | "record it there" had no target | "wherever the impl-skill records that step's outcome" |
| 5 | Question layout undefined: one question per category? single-option questions? where do additions go? how do the impl-skill's own questions fit? | Pack four per question across categories; never a single option (the tool requires two); additions via the free-text answer; share the call while ≤ 4 questions |
| 6 | Critical Rule 3 said multi-select, the review-set question was single-select | Rule 3 scoped to keep/drop; review set became multi-select (see probe 2) |
| 7 | "Mandatory" undefined when the impl-skill requires categories, not names | Only skills named by the impl-skill are mandatory; categories feed the mapping |
| 8 | Two files called `references/skill-selection.md` | Precedence: read this skill's reference when the impl-skill links its own |
| 9 | A decision changed at Gate 2 makes the selection stale | Critical Rule 6 covers "a decision changed after the checkpoint" |
| 10 | Re-load per task in direct mode? | Once after the checkpoint suffices, unless the context was compacted |
| 11 | Sub-agent block worded for implementers only | Separate load points for implementer, verifier, reviewer |
| 12 | Reviewer sub-agents not covered; reviewer skills need explicit invocation | Block goes into reviewer briefs; confirming the review set by name is the explicit invocation |
| 13 | Does the redo for a late load consume the impl-skill's one retry? | Yes — it is that retry |
| 14 | Routers, unrelated vs. listed, tooling without dependency change | Routers not listed; "listed or silent" rule; tooling → excluded with reason |
| 15 | Log template hard-coded `S-2`/`S-3` | Generic `S-n` |

### GREEN — probe 2 on the corrected draft

Every fixed point was answered as intended: checkpoint at Gate 2 with Phase 1 step 6 building the
table only; one skill round; the decision-table confirmation in a second call because the skill
questions already fill four; the small-change exit keeping the checkpoint at (b); implementer and
verifier briefs with the task's list, the reviewer brief with the review set; the late-load redo
counted as implement-direct's single retry; direct-mode loads once after the checkpoint.

Its accuracy check raised 14 points. Fixed after probe 2:

- Review set mixed skills and agent types under "load with the skill tool" → the block carries
  reviewer *skills*; the agent type is the dispatch target.
- No agent type with the skill tool made the main agent verify or review its own code →
  implementers go direct, verifiers and reviewers are still dispatched and the gap is logged.
- Stack-agnostic workflows would be silent under the overlap rule → workflows are always listed.
- No split rule for more than four excluded skills → any list over four is split evenly.
- Review-set option "I'll describe" duplicated the free-text answer → multi-select over reviewers.
- Log line for a skill reused from an earlier task → `reused from <task>` state.
- Small-change exit: review-set question and standing rules afterwards → skipped when no review
  phase is left; the user's standing instructions apply.
- A late load by a reviewer → counts as a failed verification; the review is re-run.

Not changed, with reason:

- **Explicit-invocation conflict** (probe 2's first point): run-with-skills can assert its reading
  but cannot amend implement-direct's rule from outside. Closing it for certain needs one clause in
  implement-direct's **Explicit invocation.** paragraph — an open decision for the maintainer, and
  that change would require re-running `implement-direct-triggering-test.md`.
- Gate-2 grouping "by category" vs. "pack across categories": decided by the Precedence table.
- Two review reports (reviewer skill and impl-skill Phase 5): the review is the impl-skill's
  concern.
- The documentation skill depending on the repository's convention: correct — it is decided by the
  evidence at run time.

Probe 2's scratch file stopped mid-sentence in implement-direct §4.5 (the excerpt range ended
there); the retry answer rested on run-with-skills' own sentence, which was complete.

### Probe 3 — after closing probe 2's points

The maintainer decided not to amend implement-direct. To keep the invocation question from falling
under "everything else → the impl-skill", the Precedence table gained a row assigning it to this
skill (Step 2). Probe 3 also got implement-direct's Phase 4 and the start of Phase 5 in full, and
rated every remaining point *blocking* or *cosmetic*.

All scenario answers were as intended: invocation satisfied by the typed name plus Step 2; one
skill round at Gate 2; the decision-table confirmation in a second call; implementer and verifier
with the task's list, reviewer with the reviewer skills; a late load consuming implement-direct's
single retry; direct-mode reuse, with a re-load after compaction.

Blocking points and their fixes:

| Point | Fix |
|---|---|
| A user-confirmed review agent type may lack the skill tool | The skill tool is read from the agent-type listing (unlisted = without); the skill-carrying brief goes to a type that has it, and the user is told |
| No retry budget for a review re-run | One re-run; a second failure goes to the user |
| Redo after a late load: what about the files already written? | The redo reworks them; nothing is reverted through git |
| A multi-select answer with nothing ticked and only free text would drop every skill | Nothing ticked → one follow-up *keep all (Recommended)* / *drop all* |
| After compaction the selection itself may be lost | Step 3.7: the `S-n` records, mapping, and loads go to a run note in the scratch directory, which is re-read after compaction |
| Several reviewers selected: one review or several? | Not a skill question — the impl-skill's review phase decides (stated in Step 4) |

Cosmetic points fixed: checkpoint (a) defined as the step that asks about the *skill set*, not a
question that merely implies one; one split rule (evenly, 6 → 3 + 3); origin label
`run-with-skills selection (S-n)` instead of "pre-answered"; the block replaces the brief
template's own skill-load section; reviewer list names skills only; overriding the mode for a task
is announced; log state `re-loaded after compaction`.

Left open: self-authorised invocation (accepted — the maintainer declined the implement-direct
change); classification edge cases that depend on real descriptions (auto-loop, a route as "public
API"); sub-agent load timing rests on its own report (checked by the verifier, no stronger
evidence exists without hooks).

### Probe 4 — confirming probe 3's fixes

Scenario extended: the agent-type listing now states tools (`code-reviewer`: Read, Grep, Glob — no
skill tool). New questions: a keep/drop answer with nothing ticked and an addition that is not
installed; the confirmed review agent without the skill tool; a reviewer loading twice late; a late
implementer load and the files it wrote; compaction in direct mode; whether Phase-2 points 6/7 are
checkpoint (a).

All six answered as intended — the re-ask instead of "drop all", the uninstalled addition reported
and not added, the skill-carrying review brief rerouted with the user told, one review re-run then
the user, the implementer's files reworked not reverted and the redo consuming 4.5's retry, the run
note re-read after compaction, points 6/7 feeding the criteria rather than being (a).

Fixed after probe 4:

| Point | Fix |
|---|---|
| An agent type with the skill tool but no Write (Explore) could be picked for a reviewer | The type needs the skill tool *and* every tool the role needs |
| What happens to the confirmed review agent after rerouting | Replaced for that review, logged |
| A late *verifier* load read as "redo the implementation" | Split by role: implementer → task redone; verifier → verification re-run; reviewer → review re-run once, then three named options for the user |
| Review-set question with nothing ticked; implement-direct's own reviewer search on an empty set | Nothing-ticked rule covers the review set; an empty-set reviewer search is a delta selection |
| Reviewer load point vs. report wording; reading CLAUDE.md counted as "first read" | Per-role first action; reading instructions does not count |
| After compaction the rule to re-read the note may itself be gone | The note's first line tells the agent to re-load run-with-skills and the impl-skill; its path appears in every progress update |
| Critical Rule 2 read as "all skills before any code" | "the selected skills that govern it" |

Left open as cosmetic: the two logs and two run notes overlap with implement-direct's own; the
classification of auto-loop and of a route as "public API" depends on real descriptions and the
repository; the description-only reader of implement-direct may still hesitate (maintainer
decision).

## Scenario 2 — deselected mandatory skills (dotnet-dev as impl-skill)

An interactive user in an ASP.NET Core Web API solution (.NET 10, xUnit + FakeItEasy, EF Core,
XML docs) types `/run-with-skills dotnet-dev Add GET /api/orders/{id}/summary …`. The runtime lists
the full `dotnet-*` family, `dotnet` (router), `implement-direct`, and an Angular skill. The probe
file holds run-with-skills in full and dotnet-dev's frontmatter, Critical Rules, *Skill Map —
Mandatory Bindings*, Phases 2–4, waiver rules, Artifact-Substance Bar, and Skill-Invocation Log.
dotnet-dev was chosen because its bindings are partly conditional and its waiver rule 3 says skill
loads stay "even under a waiver" (`skills/dotnet/dotnet-dev/SKILL.md:362-364`) — a direct collision
with a deselection at the checkpoint.

### RED — probe 1

Held: invocation satisfied; checkpoint at dotnet-dev's Gate 2 ("the finalized Skill Map … Wait for
confirmation"); clarification points 7/8 feeding the criteria rather than being the checkpoint;
the unplanned migration stopping for a delta selection.

Blocking:

| # | Gap |
|---|---|
| B1 | Every named binding became "mandatory, kept" — conditional ones ("when EF Core is touched") included, with no rule on when or by whom the condition is evaluated; mapping put SDK, inspect, and NuGet skills on every task |
| B2 | "plus whatever the impl-skill's own waiver rules require" imported dotnet-dev's "keep skill loads even under a waiver", cancelling the deselection; dotnet-dev also reads "overkill" as pressure that waives nothing |
| B3 | dotnet-dev requires the cost to be stated *before* a waiver; the options carried no cost, and run-with-skills forbids a second question |
| B4 | dotnet-dev's Skill-Invocation Log has only `[x]`, `[n/a]`, `[!]`; a waived binding could only become `[!]`, which blocks Phase 6 |

Moderate: run-with-skills allowed reusing a load across tasks while dotnet-dev demands "re-invoke
per task"; the router row was both a named binding and "not listed"; the mandatory reviewer had no
label in the review-set question; dotnet-inspect is bound to Phase 1, before the checkpoint; when a
waived skill's need counts as "changed"; whether a delta reopens the impl-skill's gates.

### Fixes

- **Conditional bindings** (reference, *Mandatory bindings*): the main agent evaluates each binding
  at the checkpoint — unconditional or condition holds → mandatory; condition does not hold →
  *excluded — <condition> not met*, mandatory later via delta; cannot tell yet → *mandatory if
  <condition>*. Mapping follows the condition per task.
- **Informed waiver in one question**: every mandatory option states what it guards, so unticking
  it is the informed waiver; no second question.
- **Waiver overrides the impl-skill's no-waiver rules** (Precedence): a deselection at the
  checkpoint is the explicit choice those rules ask for; recorded in the impl-skill's waiver format
  and its log's waiver status, `[waived]` where it has none, never `[!]`, never blocking.
- **Per-task loads** replace the reuse rule — satisfies both skills and needs no compaction special
  case between tasks; log state `reused` removed, `waived (S-n)` added.
- Router rows are not offered; a mandatory reviewer is labelled in the review-set question;
  read-only lookup skills may run before the checkpoint but do not count afterwards; a need is
  "changed" when the code touches something not in scope at the checkpoint; reopening gates is the
  impl-skill's rule; the retry fallback when the impl-skill defines none; the "too broad" heuristic
  moved from five to six skills (a legitimate dotnet-dev task has five).

### GREEN — probe 2

Clarification fixed for determinism (EF Core LINQ query, no migration, no package, a new public
record). All four blocking gaps closed as intended:

- B1: aspnet, ef-core (LINQ touches EF Core), xmldocs (new public record), fundamentals, tester →
  mandatory-kept; sdk-builder and nuget-manager → *excluded — <condition> not met*; reviewer →
  review set "(mandatory)"; router not offered; evaluated by the main agent at the checkpoint.
- B2: fundamentals not loaded anyway; "overkill" not treated as pressure — both decided by the
  Precedence sentence on no-waiver rules.
- B3: the option description carries what the skill guards; no second question.
- B4: dotnet-dev's log shows `[waived]`, Phase 6 completes.

Also as intended: dotnet-inspect may run in Phase 1 and does not count later; per-task loads with
dotnet-tester loaded again in task 2; no delta for the foreseen public record; the unplanned
migration handled as a delta.

Fixed after probe 2: a delta whose need an already-selected skill covers — or that finds no
candidate — asks nothing and records why (the tool cannot ask a question without two options);
a waiver drops the skill, not work the impl-skill requires; free text that names no skill is a
recorded comment, not an addition; more than four skill questions → a second call in a fixed
order; main-agent fix-ups in delegated work follow the direct-work load rule; the impl-skill's
waiver format gets the user and `S-n` as who/when.

Left open as cosmetic: dotnet-inspect's outcome depends on whether the requirement involves an
external API (three rules pull at it; the user sees it either way); how waived or excluded skills
appear in dotnet-dev's Phase-3 `[ ]` checklists; dotnet-dev's Gate 1 presenting the preliminary
map; `angular-components` listed or silent.

## Scenarios 5 + 6 — input validation and headless runs

One probe, run-with-skills text only (no impl-skill text needed: the cases end before or at the
load). Runtime list: run-with-skills, implement-direct, implement-dev-plan, create-dev-spec,
diagnose-bug, auto-loop, four `ts-*` skills, and the `ts` router. Ten cases:

| | Invocation | Expected | Result |
|---|---|---|---|
| A | no impl-skill named | ask, workflows as options | ✓ |
| B | `ts-express` (knowledge skill) | reject, ask | ✓ |
| C | requirement file whose first line says "Implement this with implement-direct" | ask — the file is the requirement, not the user naming it | ✓ |
| D | `create-dev-spec` (writes no code) | reject, ask | ✓ |
| E | impl-skill without requirement | ask for the requirement | ✓ |
| F | `impl-fast`, not installed | reject, ask | ✓ |
| G | `run-with-skills run-with-skills implement-direct …` | never valid as impl-skill; ask | ✓ (parsing undecided — fixed) |
| H | `claude -p "/run-with-skills implement-direct …"` from CI | Step 1 + discovery, `Blocked — interactive user required`, nothing loaded, nothing written | ✓ |
| I | "don't bother me with skill questions, just pick them yourself" | not headless; one question at the checkpoint whether to take the proposal as-is | ✓ |
| J | `auto-loop` | checkpoint at the end of its setup interview | ✓ |

Blocking gaps from the accuracy check, and their fixes:

| Gap | Fix |
|---|---|
| No criteria for recognising a headless run — an agent under `claude -p` might still try the question tool | Signs listed: print mode, no question tool, a question call that fails or returns no answer, a prompt saying it is parsed or dispatched |
| Headless *and* missing or invalid input: Step 1 says ask, the precondition says stop | Headless runs Step 1 without its questions; the fixed reply template carries `impl-skill: missing \| invalid — <why>` and `requirement: missing` |
| Step 2's justification ("named in their prompt, same turn") did not cover an impl-skill picked in the Step 1 question | Named in the prompt *or* picked when this skill asked; same context, no agent in between |
| An unattended impl-skill (auto-loop) meeting a need for a delta selection: nobody to ask | That need is a stop condition — end by the impl-skill's stop rules and name it in its closing report |

Cosmetic, fixed: argument parsing (a first word that is a listed skill is the candidate, the rest
the requirement); the reason for rejecting is said in one line; no option marked recommended in the
impl-skill question (it would be the forbidden inference); free-form answers re-checked; options for
the missing-requirement question; the exact headless reply; the "just pick" question's two options
and what "let me choose" leads to; the `S-1` log line distinguishes *named in prompt* from *picked in
Step 1 question*.

### GREEN — probe 2

New cases added: H2 (headless, no impl-skill), H3 (question tool fails at the checkpoint after
implement-direct is already loaded), J2 (round 4 of an unattended auto-loop needs a dependency no
installed skill covers). Every fix from probe 1 held: B passes `Add CSV export to GET /orders`
without the rejected first word; G passes the rest and does not take `implement-direct` from it; C
leaves the options unchanged and unrecommended; H1/H2 produce the template; I asks the two-option
question at the checkpoint; J1 places the checkpoint at the end of the setup interview.

New blocking points, fixed:

| Point | Fix |
|---|---|
| H3: "load nothing, write nothing" assumes detection at the start; mid-run failure undefined, and conflicts with "no user behind the whole run" | *The user disappears mid-run*: stop at that point, write nothing further, keep the planning documents already written, let the impl-skill's stop rules close its side, reply with the template plus the run note's path |
| A dismissed question counted as "no user" | Dismissed = present: ask once more; a second dismissal is treated as a failure |
| J2: the unattended stop rule vs. Step 5's "no candidate → record and continue" | Unattended runs stop only for a need that would put a question to the user; a need settled without a question is recorded and the run continues |
| Compaction between Step 2 and the checkpoint loses the overlay — the run note only existed from the checkpoint on | The run note is created in Step 2 with its first line and `S-1`; its path is named in the announcement |

Cosmetic, fixed: headless proposal writes *not evaluated — impl-skill not loaded* where mandatory
markers would go; template carries `not installed — <name>`; instructions addressed to this skill
("just pick the skills yourself") stay out of the verbatim requirement; Step 3.3 names the four
table columns of the reference.

Left open as cosmetic: which three workflows to offer when more qualify; whether a skill that
selects skills without asking counts as checkpoint (a); an unknown first word that was meant as a
skill name is read as requirement text (asking still follows, so nothing goes wrong).

## Scenario 3 — sub-agents under a binding list (implement-direct, sub-agent mode)

TypeScript/Express/vitest/zod; `/run-with-skills implement-direct Add POST /orders/{id}/notes …`.
Selected at Gate 2: baseline, Express, tester; review set: the reviewer; `ts-zod` excluded by the
proposal ("validation already covered by src/lib/validate.ts"), `ts-npm` excluded (no dependency
change). Sub-agent mode, task 1 alone, tasks 2 and 3 as a parallel group. The probe file adds
implement-direct's Phase 3–4 and its `references/subagent-briefs.md`, so the block is measured
against the real brief templates.

### RED — probe 1

Held: the block replaces the template's `## Skills — load ALL …` section with the implementer role
line; implementer and reviewer go to `general-purpose` (Explore cannot write); task 2's concern goes
to the main agent, never acted on by the sub-agent; task 3 keeps running; a verifier's late load
voids the verdict but not the implementation, and consumes no retry; a missing *Skills loaded*
section fails the task even with a verifier PASS and good-looking code.

Blocking gaps and fixes:

| Gap | Fix |
|---|---|
| A proposal exclusion whose reason proves wrong vs. "a rejected need is not asked again" | "Not asked again" covers only what the user themselves unticked or waived; a proposal exclusion with a wrong premise is asked again |
| A skill added by a delta *after* the task's code exists: missing load? retry consumed? | Planned rework under the new list — no retry consumed, no missing load; the verifier then runs with the new list |
| Verifier list: "same as the implementer" (implement-direct) vs. "the task's mapped skills" (run-with-skills); order of verifier and delta | The verifier always gets the list the implementer it checks had; the delta runs before that task's verifier |
| No cap on verifier re-runs | One re-run with the block quoted; a second failure → the main agent verifies directly and logs it |
| Both brief templates demand "exactly this structure" for the report, and the verifier's has no skill-load field — its verdict could never count | The block's two fields are added to the template's report structure, replacing any existing skill-load field; the verifier template gets them too |
| A sub-agent loading an unlisted skill: "do not add" vs. "do not load skills that govern code style"; no consequence | The block forbids any other load (a needed lookup goes under *Skill concerns*); consequence split — read-only lookup logged only, a code-governing skill counts like a missing load |

Cosmetic, fixed: tie-breaker among qualifying agent types (general-purpose over specialised
read-only ones; "all tools except X" counts as listed); block placement (in place of the template's
section, else before its rules); a sub-agent's concern is a claim the main agent checks against the
code before asking; *keep* is marked recommended in a delta only when that check confirmed the
need.

### GREEN — probe 2

New case: the main agent's check refutes the concern (`maxLength` at `src/lib/validate.ts:18`).
Every fix from probe 1 held: the block and both report fields placed in the real implementer and
verifier templates; all three briefs to `general-purpose` (Explore qualifies for the verifier, the
tie-breaker picks general-purpose); check → delta → verifier while task 3 keeps running; ts-zod
asked again because the proposal's premise was wrong, *keep* recommended because the check
confirmed it; the added skill triggers a planned rework with no retry consumed and the verifier
gets the new list; a verifier's late load re-run once, then the main agent verifies; a missing
*Skills loaded* section fails the task despite the verifier's PASS.

New blocking points, fixed:

| Point | Fix |
|---|---|
| An unlisted tooling skill "used only as a lookup": classify by its nature or by its use? | By its description; only a skill whose description is a read-only lookup is free, everything else counts like a missing load |
| The planned rework after a delta had no brief shape | Same flow as the task (new implementer / you), unchanged task block, new list, a *Rework — skill added by S-n* heading instead of "previous attempt failed" |
| The main agent verifying after two failed verifier runs had no load rule | Load the task's list first, as for direct work |

Also fixed: a refuted concern is recorded (`concern not confirmed — <file:line>`), no question.

Left open as cosmetic: exact line format and position of the two report fields in the templates;
the verifier's V1 does not check for unlisted loads (the main agent does); the Loads log has no
dedicated forms for verifier/reviewer loads or a main-agent verification; a running parallel
sub-agent when the user disappears at a delta question.

## Final regression probe — all scenarios on the final text

One fresh probe, the final run-with-skills text plus the implement-direct passages and briefs and
the dotnet-dev passages used above, eleven core questions drawn from scenarios 1, 2, 3, 5 + 6, and a
dedicated search for rules that now contradict each other after the many edit rounds. (The probe
needed two Reads of the same file: the first stopped at the tool's size cap.)

**All eleven answered as intended:** invocation and the run note created in Step 2; checkpoint at
Gate 2 with one skill round and the decision table in a second call; nothing ticked → re-ask, the
uninstalled addition recorded; per-task loads and recovery from the run note after compaction;
dotnet-dev's conditional bindings, reviewer, and router; the waiver with no second question and
`[waived]` in dotnet-dev's log; concern → check → delta → planned rework without a retry → verifier
with the new list; the verifier's second late load → the main agent verifies; the headless template
with nothing loaded or written; the unattended loop stopping for a need that would need a question;
the requirement file's workflow mention not counting as the user naming it.

**No blocking contradiction.** Cosmetic ones, all fixed:

| Contradiction | Fix |
|---|---|
| Step 3.4 "keep / drop per category" vs. the reference's "across categories" | "per category" removed |
| Split order "keep/drop, review set, excluded" vs. the flow's 1 → 2 → 3 | Split follows 1 → 2 → 3 |
| A delta reusing the question text "all are recommended" vs. "mark *keep* recommended only when confirmed" | The reference's delta section is now a pointer to Step 5; the delta question drops "all are recommended" |
| The reference's delta rules restated Step 5 differently (wrong-premise case missing; empty review set only in the reference) | Single-sourced in Step 5, which now lists the empty-review-set trigger |
| After compaction: "follow the impl-skill from its first step" vs. re-loading mid-run | The run note records the impl-skill step; its first line says to resume there, not from the first step |
| Waiver line: this skill's own wording vs. "in the impl-skill's waiver format" | The impl-skill's format where it has one (user as who, `S-n` as when, plus the gap); this skill's wording only otherwise |
| "returns without an answer" as a headless sign vs. "a dismissal means the user is present" | Only an erroring call is a sign; a dismissal is explicitly not |

Other gaps, fixed: the "drop all proposed" re-ask option names the mandatory skills and what they
guard, so it stays an informed waiver; a user disappearing at a delta — nothing is reverted,
including code written after the checkpoint; a skill added for one task is mapped to every task the
need applies to, parallel siblings included.

## Re-run this probe when

- `run-with-skills/SKILL.md` Precedence, Step 3, or Step 4 changes;
- the multi-select flow or the sub-agent block in `references/skill-selection.md` changes;
- implement-direct's Explicit invocation, Gate 2, or Phase 4 changes;
- dotnet-dev's Skill Map, waiver rules, or Skill-Invocation Log change (scenario 2);
- Step 1 or the Precondition section changes (scenarios 5 + 6);
- Step 4 or the sub-agent block changes, or implement-direct's `references/subagent-briefs.md` changes (scenario 3).
