---
name: run-with-skills
description: >
  Use only when explicitly requested by name — "run-with-skills", "run with skills",
  "/run-with-skills", "/cc-ai-dev:run-with-skills" — together with the name of an implementation
  workflow skill and a requirement, to run that workflow with an enforced skill-selection
  checkpoint: before the first line of code, the main agent discovers the installed skills that fit
  the requirement and the stack, lets the user keep, drop, and add them through a multi-select
  question, and loads the chosen skills — or binds every implementing sub-agent to load them —
  before implementation starts. Replaces the workflow's own skill selection; everything else
  follows the workflow. Must NOT activate on its own for "use the right skills", "implement this
  feature", a bare workflow name, or any other request that does not name run-with-skills.
---

# run-with-skills — Run an Implementation Workflow Under a Binding Skill Selection

## Core Principle

An implementation workflow decides *how* work proceeds; the skills the user installed decide *what
the code looks like*. Workflows handle the second part unevenly — one discovers skills carefully,
another names a fixed set, a third never mentions them — and a model left to itself writes code
from its own habits because it knows the stack. This skill closes that gap for any workflow: it
wraps a workflow the user names (the **impl-skill**) and guarantees that, before any code exists,
the skills that fit were discovered in *this* runtime, put in front of the user to confirm, change,
and extend, and actually loaded by whoever writes the code.

Invocation: `/run-with-skills <impl-skill> <requirement>` — the requirement as text, a file path,
or an issue reference.

This skill is an overlay, not a second workflow. It adds one checkpoint and one set of rules; the
impl-skill keeps its phases, gates, questions, outputs, and git policy.

## Precedence — which rules win

| Concern | Governed by |
|---|---|
| Discovering, classifying, proposing, selecting, and mapping skills; loading them; passing them to sub-agents | **this skill** — [`references/skill-selection.md`](references/skill-selection.md) |
| Whether the impl-skill counts as invoked by the user | **this skill** — Step 2: the user named it; loading it is their invocation |
| Everything else: phases, gates, clarification, task breakdown, mode, review, reports, commits | **the impl-skill** |

Concretely:

- Every step of the impl-skill that discovers, proposes, asks about, or maps skills is performed
  with this skill's rules instead of its own. An early discovery step (a preliminary skill map)
  runs discovery and the proposal table only — no question; the checkpoint later reuses and updates
  that table instead of starting over. The checkpoint's result counts as the impl-skill's answer
  for its selection step — record it wherever the impl-skill records that step's outcome (its
  decision table, its log) with origin `run-with-skills selection (S-n)`; do not ask the user a
  second time. Other questions the impl-skill asks at the same step stay as they are.
- When the impl-skill links to its *own* skill-selection reference (often also named
  `references/skill-selection.md`), read this skill's reference instead.
- Skills the impl-skill **names** as mandatory (a "Mandatory Bindings" table, "always load X", a
  fixed skill map) are pre-selected and marked *mandatory — <impl-skill>*; a binding with a
  condition ("when EF Core is touched") only when its condition holds for this requirement — see
  [`references/skill-selection.md#mandatory-bindings-of-the-impl-skill`](references/skill-selection.md#mandatory-bindings-of-the-impl-skill).
  Category requirements without a name ("a tester skill for every task") are not mandatory
  markers; they feed the mapping rules.
- **Deselecting a mandatory skill is the user's informed waiver.** The option already states what
  the skill guards, so the choice is informed when it is made — no second question. Record it as
  a waiver — in the impl-skill's waiver format where it has one (its wording, with the user as
  *who*, `S-n` as *when*, and the gap), otherwise as `waived — explicit user choice at the
  run-with-skills checkpoint (S-n); gap: <what it guards>` — and in its skill log under its waiver
  status, or `[waived]` where it has none. A waived skill is never a violation marker (`[!]` or similar)
  and never blocks the impl-skill's completion. Rules of the impl-skill that forbid waiving a skill
  load, or that read "overkill" or "I know this" as pressure that waives nothing, do not apply to
  a deselection at the checkpoint: this is the explicit choice those rules ask for. Where the
  impl-skill's format asks for who and when, fill in the user and `S-n`. A waiver drops the
  *skill*, not work the impl-skill requires (documentation, tests); whether the user's words also
  waive that work is decided by the impl-skill's own waiver rules.
- Where the impl-skill's text and this skill's rules conflict about skills, this skill wins. The
  user invoked this skill precisely to get that behaviour.

## Critical Rules

1. **The main agent selects; nobody else.** Discovery, the proposal, and the user question happen
   in the main agent's context, never in a sub-agent's. Sub-agents receive a finished list.
2. **Selection before code.** No production code, test code, build or dependency manifest, or
   configuration file is written before the Skill Checkpoint has run and the selected skills that
   govern it are loaded. Planning documents the impl-skill writes (specs, plans, drafts, reports)
   are not code. Read-only lookup skills the impl-skill uses before the checkpoint (inspecting a
   library's API, for example) may run; they write nothing and select nothing, and a load before
   the checkpoint does not count for the code that follows.
3. **The user decides through a multi-select question.** Use the structured question tool (in
   Claude Code: `AskUserQuestion`) — `multiSelect: true` for keeping and dropping skills — never a
   prose question. The user can always keep, drop, and add — the proposal is a starting point, not
   a verdict.
4. **Selected means loaded.** Every selected skill is loaded with the runtime's skill tool before
   the first code write it governs — by the main agent in direct work, by the sub-agent in
   delegated work. Knowing the stack well is not a reason to skip one; it is the reason the rule
   exists.
5. **Candidates come from the runtime, not from memory.** Only skills in the skill list the runtime
   exposes now can be proposed or added. A name from the requirement, a README, or another project
   is not a candidate until it appears there.
6. **New need, new question.** When a need arises that no selected skill covers — a decision
   changed after the checkpoint, an unforeseen layer, a dependency change, a new task, a rework
   item — stop before that code and run a delta selection. Never fill the gap silently, never add a
   skill without asking.

## Precondition — Interactive User Required

The selection is the user's decision; without a user it would be the model's choice labelled as
theirs. The precondition is unmet only when the whole run has no user behind it — dispatched by a
script, CI, cron, or an agent whose output a program consumes. Signs: a non-interactive mode (for
Claude Code, `claude -p` / print mode), no structured question tool available, a question-tool
call that errors (a dismissal is not an error — see *The user disappears mid-run*), or a prompt
saying its output is parsed or that another agent dispatched it.

When unmet: run Step 1 without its questions, and items 1–3 of Step 3 (criteria, discovery,
proposal table — from the codebase and the skill list alone), then STOP and reply with exactly:

```
Blocked — interactive user required
impl-skill: <name> | missing | not installed — <name> | invalid — <why>
requirement: <as given> | missing
<proposal table>
An interactive user can start this with /run-with-skills <impl-skill> <requirement>.
```

For a proposal made without the impl-skill's text, write *not evaluated — impl-skill not loaded*
where mandatory markers would go. Load nothing — the impl-skill included — and write nothing, not
even the run note.

**The user disappears mid-run.** If the question tool fails at a later point (at the checkpoint,
for a delta) after the run started with a user, stop there: write nothing further, revert nothing
that already exists, let the impl-skill's own stop or abort rules close its side, and reply with
the template above plus the run note's path. A question the user **dismissed** — as opposed to a
tool call that errors — means the user is present, not gone: ask once more; a second dismissal is
treated the same way as a failure.

A reachable user saying "just pick the skills yourself" is not a headless run. At the checkpoint,
show the proposal, state that the selection guards the code against the model's defaults, and ask
one single-select question: *take the proposal unchanged* / *let me choose*. The first is recorded
as `S-n: proposal accepted unchanged — explicit user instruction`; the second leads to the normal
multi-select flow.

## Step 1 — Validate the inputs

1. **impl-skill.** It must be named by the user — as the first word of the arguments, or by
   picking it in the question below — never inferred from the requirement, even when the
   requirement names a workflow. Check it against the runtime's skill list. Read its description:
   it must describe a workflow that produces code (phases, steps, or a pipeline ending in
   implementation).
   - **Parsing.** If the first word of the arguments is a skill in the runtime list, it is the
     impl-skill candidate and the rest is the requirement — also when the candidate is then
     rejected. Otherwise all arguments are the requirement.
   - Missing, not installed, or not an implementation workflow (a knowledge skill, a router, a
     reviewer, a spec or planning skill that writes no code) → say which of the three in one line,
     then ask through the question tool with up to three installed implementation workflows as
     options, each with its one-line purpose, plus the free-form escape. Mark none as recommended
     — that would be the inference this rule forbids. A free-form answer goes through the same
     check. `run-with-skills` itself is never a valid impl-skill.
   - Several accepted forms of a name (`/cc-ai-dev:implement-direct`, `implement-direct`) resolve
     to the same skill.
2. **Requirement.** Accept pasted text, a file path (read it), or an issue reference (fetch it).
   Missing or empty → ask for it with the options *paste the requirement text* / *give a file path
   or issue reference*, the answer coming through the free-form escape; do not start from a guess.
3. **Git state is not checked here.** The impl-skill does that with its own rules.

Record as `S-1`: impl-skill, requirement source, and how each was obtained.

## Step 2 — Start the impl-skill

1. Announce the overlay in two lines: which impl-skill runs, and that its skill selection is
   replaced by a checkpoint before the first code. Create the run note (Step 3, item 7) now, with
   its first line and `S-1`, so a compaction before the checkpoint does not lose the overlay; name
   its path in the announcement.
2. Load the impl-skill with the runtime's skill tool and pass the requirement as its argument,
   verbatim — the file path or issue reference as given, not a paraphrase. Instructions addressed
   to this skill ("just pick the skills yourself") are not part of the requirement and stay out of
   it. This is the user's own
   invocation of the impl-skill, not a dispatch on their behalf: the user named it — in their
   prompt, or by picking it when this skill asked which workflow to run — and you load it in the
   same context, with no other agent in between. An impl-skill that accepts only explicit
   invocation by the user is satisfied by that — which is exactly why Step 1 never infers the name.
3. Follow the impl-skill from its first step. Keep this skill's rules in force alongside it; when
   the impl-skill reaches anything in the *Precedence* table's first row, apply this skill instead.

## Step 3 — The Skill Checkpoint

**Where it sits:** at the **earlier** of

- (a) the impl-skill's own skill-selection step — the point where it would ask the user to choose,
  keep, drop, or confirm the skill set. A question about something else that merely implies a
  skill (a test strategy, a persistence store) is not that step; its answer feeds the criteria; and
- (b) the first code write (Critical Rule 2) — or, for an impl-skill that runs unattended after a
  setup phase, the last point at which it still talks to the user. Once it runs unattended there
  is nobody to answer a delta selection: a need that would put a question to the user (Step 5) is
  a stop condition for the unattended run — end it by the impl-skill's own stop rules and name the
  need in its closing report. A need Step 5 settles without a question (already covered, or no
  installed skill exists for it) is recorded and the run continues.

At (a) the impl-skill has usually finished its requirement analysis and clarification, which is
what makes the proposal precise. When the impl-skill has no selection step, (b) applies and the
checkpoint interrupts it just before the first code.

If the impl-skill ends or hands the work over before its selection step — an offer to handle a
small change as an ordinary request, an abort — the overlay does not end with it: any code that
still gets written in this run waits for the checkpoint at (b), without a review-set question when
no review phase is left, and the log goes to the final reply. Everything else then follows the
user's standing instructions for an ordinary request.

**What happens there** — details, formats, and question shapes in
[`references/skill-selection.md`](references/skill-selection.md):

1. **Collect the match criteria** from the impl-skill's analysis so far and the codebase:
   language, frameworks and versions, test framework, doc-comment convention, layers the
   requirement touches, dependency changes. Fill gaps by reading the manifests yourself, with
   `file:line` evidence.
2. **Discover** every candidate in the runtime's skill list and agent types, and classify each.
3. **Propose** the table: skill · category · why it fits · proposed use (with the mandatory marker).
4. **Ask** — the multi-select flow: keep / drop, excluded skills to include anyway,
   review set (when the impl-skill has a review phase), additions.
5. **Record** `S-n`: found, proposed, kept, dropped, added, waived mandatory skills, review set.
6. **Map** the selected skills to the impl-skill's tasks, if it has any, by the mapping rules.
   Show the mapping in the impl-skill's own task presentation, not as an extra gate.
7. **Persist.** Add the `S-n` records and the mapping to the run note created in Step 2 — in your
   scratch directory, or next to the impl-skill's own run notes — and keep it current, including
   every load and the impl-skill step you are at. Its first line: *"After a compaction: re-load
   run-with-skills and <impl-skill>, resume <impl-skill> at the step recorded below — not from its
   first step — then re-load the skills mapped to the current task."* Name the note's path in every progress update so a summary keeps
   it. After a compaction — or whenever you cannot tell whether a skill's text is still in your
   context — re-read the note and follow its first line.

## Step 4 — Load the selected skills

- **Direct work** (the main agent writes the code): before the first code write of each task, load
  every skill mapped to it with the skill tool, one call per skill, and note the order — for every
  task, even when a previous task loaded the same skill (impl-skills commonly require exactly that,
  and it survives compaction between tasks). A skill loaded *before* the checkpoint does not count.
- **Main-agent edits in delegated work.** When the main agent itself edits code between sub-agent
  runs (a fix-up, a merge of parallel results), the direct-work rule applies to that edit.
- **Delegated work** (the impl-skill dispatches sub-agents): put the *Mandatory skills* block from
  [`references/skill-selection.md#sub-agent-block`](references/skill-selection.md#sub-agent-block)
  into every brief for a sub-agent that writes, verifies, or reviews code — implementer, verifier,
  reviewer — with the exact list for that brief: the task's mapped skills for implementer and
  verifier, the confirmed reviewer *skills* for the reviewer. The verifier always gets the list the
  implementer it checks had. The block takes the place of whatever skill-load section the
  impl-skill's brief template has (or goes before the brief's rules if there is none), so the
  sub-agent reads one instruction, not two; and its two report fields — *Skills loaded*, *Skill
  concerns* — are added to the template's required report structure, replacing any skill-load
  field it already has. A verifier template without such a field gets it too; otherwise its
  verdict could never count.
- **Which agent type.** A brief that carries skills goes only to an agent type that has the skill
  tool *and* every tool the role needs (an implementer writes files; a reviewer writes its report)
  — read both from the runtime's agent-type listing; a type whose tools are not listed counts as
  without, "all tools except X" counts as listed. Where several types qualify, prefer the
  general-purpose one over specialised search or read-only types. If none has it: an implementer task is done directly (say so in one line — it overrides
  the chosen mode for that task); a verifier or reviewer is still dispatched — its independence
  matters more — with the list as names, logged `✗ no skill tool`. A review *agent type* the user
  confirmed is a dispatch target, not something to load. If it lacks the skill tool while reviewer
  skills were also confirmed, say so and send the skill-carrying brief to an agent type that has
  the tool; the confirmed type is replaced for that review and the replacement is logged. How many
  reviews run, and to whom, is otherwise the impl-skill's review phase.
- **Checking the loads.** When a sub-agent returns, check its report for the skill loads, each at
  the point the block requires — its report is the only evidence, so a verifier or reviewer the
  impl-skill already runs checks it too. What a missing or late load costs depends on whose it was:
  - *Implementer* — a failed verification: the task is redone with the block quoted first,
    reworking the files the failed attempt wrote (git stays read-only; nothing is reverted through
    git). That redo is the impl-skill's retry, not an extra one; if the impl-skill defines no
    retry, it is one redo, and a second failure goes to the user.
  - *Verifier* — its verdict does not count; the verification is re-run once with the block quoted
    first, the implementation stays and no retry is consumed. A second failure: verify the task
    yourself — load the task's list first, as for direct work — and log it.
  - *An unlisted skill loaded* — a deviation, classified by the skill's description, not by what
    the sub-agent says it used it for. A read-only lookup skill (its description: inspecting a
    library, looking up an API) is logged and costs nothing more; any other skill — knowledge,
    tester, documentation, tooling — counts like a missing load for the implementer, because the
    code may follow rules nobody selected.
  - *Reviewer* — its report does not count; the review is re-run once, replacing that report. A
    second failure goes to the user: **re-run with another agent type**, **accept the review
    without the skill** (logged `✗`), or **stop**.
- **Review skills.** Reviewer skills that accept only explicit invocation are covered by the
  user confirming the review set by name at the checkpoint; the brief names them.
- **Sub-agents select nothing.** A sub-agent that believes a skill is missing or wrong reports it
  and does not act on it. The main agent reads the concern as a claim: check it against the code
  first ("validate.ts does not cover length limits" — does it?), then turn a confirmed concern into
  a delta selection with the user, before that task's verifier runs. A concern the code refutes is
  recorded as `S-n: concern not confirmed — <file:line evidence>`, no question, and the task goes
  on to its verifier. Other tasks of a parallel group keep running; their files are disjoint.
- **A skill added after the code exists.** When a delta adds a skill to a task that is already
  implemented, the task is reworked under the new list — a planned rework, not a failed
  verification: it consumes no retry and is no missing load. It runs like the task did (a new
  implementer in sub-agent mode, you in direct mode), with the unchanged task block, the new list
  in the block, and a heading *Rework — skill added by S-n: <skill>, <why>* in place of any
  "previous attempt failed" section. Files outside the task's *Files* are a deviation as usual.
  Then the verifier runs with the new list.

## Step 5 — Delta selection

Triggered by Critical Rule 6, by a sub-agent's report, or by the impl-skill's review phase finding
the review set empty and about to search for reviewers. Stop before the code in question, discover
only candidates not yet offered or offered and rejected for a reason that no longer holds, and ask
the same multi-select shape for just those. Record as `S-n` with the trigger. Then load and
continue. An unchanged need that the user themselves unticked or waived is not asked again; a need is
changed when the code now touches something that was not in scope at the checkpoint (a new public
type after the documentation skill was waived for a change with none, a migration nobody planned).
A skill the *proposal* excluded is asked again when its stated reason turns out wrong ("validation
already covered by src/lib/validate.ts" — and it is not): the user never decided on a true premise.
Mark *keep* as recommended only when your own check confirmed the need; otherwise mark neither.
A skill added for one task is mapped by the mapping rules to every task the need applies to,
including tasks of the same parallel group — each of those goes through the planned rework (Step 4)
if its code already exists.
Whether a changed decision also reopens one of the impl-skill's own gates or clarification points
is the impl-skill's rule, not this one.

If the need is already covered by a selected skill, there is nothing to ask: map that skill to the
task, load it before the code it governs, and record `S-n delta (trigger: …): covered by <skill>,
no question`. The same holds when discovery finds no candidate at all — record it and say in one
line that no installed skill covers the need.

## Step 6 — Close

When the impl-skill finishes, add the **Skill Selection Log** — to the impl-skill's report if it
writes one (as its own section, next to any skill log it already keeps), otherwise to the final
reply:

```
Skill Selection Log — run-with-skills (impl-skill: <name>)
S-1  inputs: <impl-skill> (named in prompt | picked in Step 1 question), requirement from <source>
S-n  checkpoint at <(a) impl-skill step | (b) before first code write>: found n, proposed n,
     kept <names>, dropped <names>, added <names>, waived mandatory <names | none>,
     review set <names | none>
S-n  delta (trigger: <…>): added <names> | none
Loads: <task / scope> — <skill> by <main agent | sub-agent> — before first write of <file> ✓
       | waived (S-n) | late ✗ | missing ✗ | no skill tool ✗
```

A `✗` is reported as such, with the task named, never smoothed over.

## Red Flags — Stop and Re-read the Rules

| Rationalization | Reality |
|---|---|
| "The requirement clearly needs implement-direct, I'll pick it" | The impl-skill is named by the user. Ask. |
| "The impl-skill already selected skills, I'll let that stand" | Its selection step is replaced by this one. Precedence table. |
| "I'll ask about skills now and again at the impl-skill's gate" | One selection, recorded as the impl-skill's answer. No second question. |
| "The sub-agent knows the stack better, let it choose" | The main agent selects, the user decides. Critical Rule 1. |
| "I know this framework, the skill would only slow me down" | The user installed it so the code follows their rules. Critical Rule 4. |
| "This new migration needs the data-access skill, I'll just load it" | New need, new question. Delta selection. |
| "It's one small file, the checkpoint is overkill" | Selection before code, every time. Run it at speed, not at reduced rigour. |
| "Headless — I'll take the proposal as the selection" | No user, no selection. Block. |
| "The skill was loaded earlier in the conversation" | Loaded before the checkpoint is not selected-then-loaded. Re-load. |

## References

- [`references/skill-selection.md`](references/skill-selection.md) — runtime discovery, match
  criteria, classification and exclusions, proposal table, the multi-select flow, mandatory
  bindings, mapping, the sub-agent block, delta selection
