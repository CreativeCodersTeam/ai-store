# Skill Selection — Discovery, Question, Mapping, Hand-over

The skills that shape the code have to be the ones installed in *this* runtime, chosen for *this*
requirement, and confirmed by the user. Two things go wrong otherwise: a skill named from memory
does not exist here and the task runs without guidance; or a skill is loaded because it sounds
related and the code follows rules for the wrong layer. This file keeps the selection tied to
evidence: the criteria come from the requirement analysis and the codebase, never from memory.

Nothing in this file names a skill. The names come from the runtime at the moment of the run.

## Runtime discovery

Take the list of skills your runtime exposes right now — in Claude Code, the available-skills
listing in your context, the same list the skill tool accepts names from — and the agent types
available to the agent tool. That is the complete set of candidates. Do not:

- scan `.claude/skills/`, `~/.claude/skills/`, or a repository of skills on disk — a directory the
  runtime did not register is not invocable;
- take names from the requirement, a README, or another project;
- assume a family exists because one member does (a `foo-tester` does not imply a `foo-reviewer`).

If the runtime exposes no skill list, say so at the checkpoint, record it as `S-n`, and let the
impl-skill proceed with the codebase conventions as the only guidance.

## Match criteria

Build the criteria before looking at the list, so the list does not suggest them. Take what the
impl-skill's analysis already established; read the rest yourself and cite `file:line`.

| Source | Criteria |
|---|---|
| Build and dependency manifests (`*.csproj`, `package.json`, `pyproject.toml`, `go.mod`, `pom.xml`, …) | language, framework(s), runtime version, package manager, build tool |
| Test layout and configuration | test framework, runner, test types in use |
| Documentation tooling | doc-comment convention, API doc generator |
| Scope of the requirement | file types and directories, layers touched (HTTP, data access, UI, messaging, CLI, packaging) |
| Requirement and the impl-skill's decisions so far | concerns: an endpoint, a migration, a UI component, a background job, a public API, a dependency change |

## Classification

Read each candidate's whole description and place it in one category:

| Category | Description says… | Use |
|---|---|---|
| **knowledge** | rules, patterns, best practices for a language, framework, or layer | implementation — loaded by implementer and verifier |
| **tester** | writing or extending tests for a stack | implementation — every task with tests |
| **documentation** | doc comments, API documentation conventions | implementation — tasks with public API or documentation items |
| **tooling** | adding/updating packages, inspecting libraries, scaffolding | implementation — only tasks that change dependencies or scaffold |
| **reviewer** | structured code review, explicit invocation, report | review set — only if the impl-skill has a review phase |
| **review agent** | an agent type whose description is code review | review set — as above |
| **workflow** | multi-phase pipeline with its own clarification, gates, or review | **excluded** with the nested-workflow warning; user may override |
| **router** | "entry point", "routes to", "directs you to the right skill" | not listed — the skills it routes to are candidates in their own right |
| **unrelated** | nothing in the description overlaps a criterion — not the language, not the family, not a layer | excluded silently |

Always excluded and never offered: the impl-skill itself and `run-with-skills`. Agent types other
than review agents are not candidates.

**Listed or silent.** Workflow skills that produce code are always listed as *excluded —
nested workflow*. Any other skill that shares the language, the ecosystem, or a layer with the
criteria but is wrong for this run — another framework of the same ecosystem, a tooling skill when
no dependency changes — is listed as *excluded — <reason>*, so the user can override the reason.
Only a skill with no such overlap is silent. A candidate whose description is too thin to classify is listed as *excluded — cannot
classify from its description*.

The nested-workflow warning, in the option description: *loading this inside a task runs its
phases — its own clarification, review, and gates — inside a workflow that is already running.
Recommended: exclude.*

A skill can match on one line and be wrong on another ("for framework X 21+"; the project is on X
15). Put the conflict in the *why* column and propose *excluded*.

## Mandatory bindings of the impl-skill

Read the impl-skill for skills it requires **by name**: a "Mandatory Bindings" or "Skill Map"
table, "always load X", "baseline — load X alongside". The main agent evaluates each binding
against the match criteria at the checkpoint:

| Binding | Outcome |
|---|---|
| Unconditional ("always", "for production code") | proposed as kept, *mandatory — <impl-skill>* |
| Conditional, condition holds ("when ASP.NET Core is touched" and the requirement adds an endpoint) | proposed as kept, *mandatory — <impl-skill>*, mapped to the tasks where it holds |
| Conditional, condition does not hold | listed as *excluded — <condition> not met*; becomes mandatory through a delta selection if the condition starts to hold |
| Conditional, cannot tell yet | proposed as kept, *mandatory if <condition>*, with the open question in the *why* |
| A reviewer skill | goes to the review set, labelled "(mandatory)" there |
| A router ("tie-breaker", "when the right sub-skill is not obvious") | not offered, like every router; the skills it routes to are the candidates |
| Read-only lookup bound to an early phase | may run before the checkpoint (SKILL.md, Critical Rule 2); proposed again for the phases that write code |

A named skill that does not exist in the runtime list is reported as *required by <impl-skill>,
not installed* and recorded. A requirement by category only ("the tester skill for every task")
marks nothing; it is served by the mapping rules.

**Informed deselection.** The option description of every mandatory skill carries what it guards,
in a few words: "mandatory — dotnet-dev; guards DI, options, and C# idioms in production code".
Unticking it is then an informed waiver, recorded as in SKILL.md *Precedence*.

## Proposal table

```
Skills for <requirement slug> (Node 20, Express, TypeScript, vitest — package.json:1, vitest.config.ts:1)
impl-skill: <name>   checkpoint: <(a) its skill step | (b) before first code write>

| Skill / agent | Category | Why it fits | Proposed use |
|---|---|---|---|
| <name> | knowledge | TypeScript strict, tsconfig.json:5 | all tasks — mandatory (<impl-skill>) |
| <name> | tester | vitest + supertest in test/ | all tasks |
| <name> | documentation | requirement adds a public export | tasks with public API |
| <name> | reviewer | TypeScript reviewer | review set |
| <name> | workflow | full pipeline for this stack | excluded — nested workflow |
| <name> | knowledge | Angular UI rules; scope has no UI files | excluded — no matching files |
```

Excluded-unrelated skills are not in the table; excluded-with-reason skills are, so the user can
override the reason.

## The multi-select flow

The structured question tool (in Claude Code: `AskUserQuestion`) takes two to four options per
question and at most four questions per call, and adds a free-text answer to every question on
its own. Build the questions like this:

1. **Keep / drop.** The proposed-for-implementation skills, sorted by category, in `multiSelect`
   questions — across categories, not one question per category. Label = skill name (with
   "(mandatory)" where it applies); description = category and the one-line *why*. Question text:
   "Tick every skill to keep — all are recommended; use the free-text answer to add skills the
   proposal missed." Unselected = dropped. If only one skill is proposed at all, ask a
   single-select *keep (Recommended)* / *drop*.

   **An answer with nothing ticked is not "drop all".** Options are not pre-selected, so a user who
   only typed an addition may have ticked nothing. If none of the keep/drop questions (or the
   review-set question) comes back with an option ticked, ask once more for that list: *keep all
   proposed (Recommended)* / *drop all proposed* — the latter's description naming the mandatory
   skills among them and what each guards, so choosing it stays an informed waiver; any free text
   they already gave is still processed as additions.
2. **Excluded overrides.** `multiSelect` over the excluded-with-reason skills, reason and any
   warning in the description: "Include any of these anyway? None is recommended." Skip it if at
   most one skill is excluded-with-reason and mention that one in the keep/drop question text
   instead.
3. **Review set** — only if the impl-skill has a review phase. `multiSelect` over the reviewer
   skills and review agent types: "Use these for the review — all are recommended". With a single
   candidate, a single-select *use (Recommended)* / *don't use*. They are not loaded now; the
   impl-skill's review phase uses them. Note in the description of a review agent type whether the
   agent-type listing shows it has the skill tool — without it, it cannot load reviewer skills.
4. **Additions** arrive as free text on any of the questions. Each name is checked against the
   runtime list. Present → added, origin *user's own*. Absent → *not in this runtime's skill list,
   cannot be loaded*, not added, recorded. Free text that names no skill ("I know the
   fundamentals") is a comment, not an addition: record it as the user's reason next to the
   choice it explains.

**Splitting.** Every list in 1–3 is split into questions of two to four options, as evenly as
possible — six skills become 3 + 3, not 4 + 2. More than four skill questions in total → a second
call for the rest, in the order 1 → 2 → 3.

If the impl-skill asks other questions at the checkpoint step (confirming its decision table, for
example), put them in the same call while the total stays at four or fewer; otherwise ask the skill
questions first and the impl-skill's questions in a second call right after.

If the tool has no multi-select, ask one yes/no question per proposed skill instead — never a
prose list to answer in free text.

Record `S-n`: found n, proposed n, kept (names), dropped (names), added (names), waived mandatory
(names), review set (names).

## Mapping

Per task of the impl-skill, derive the skills from the task's own fields, in this order:

| Rule | Applies to |
|---|---|
| Baseline knowledge skill(s) — descriptions say "baseline", "fundamentals", or that the family builds on them | every task with production code |
| Tester skill for the test framework found | every task with tests |
| Layer or framework knowledge skill | tasks whose files or goal touch that layer |
| Documentation skill | tasks with a documentation item on public API |
| Tooling skill | tasks that add, remove, or upgrade a dependency, or scaffold |
| Test-type-specific skill (BDD, contract testing) | tasks whose planned tests have that type |
| Mandatory skill of the impl-skill | the tasks where its binding's condition holds; all tasks if it has no condition |

An impl-skill without tasks is one task. Six or more skills on one task means the task is too broad
or the rules were applied loosely — check before presenting.

## Sub-agent block

Paste this into every brief the impl-skill writes for a sub-agent that writes, verifies, or reviews
code, filled with that brief's list — the task's mapped skills for implementer and verifier, the
reviewer *skills* of the review set for the reviewer (never an agent type). It takes the place of
any skill-load section the brief template already has, or goes before the brief's own rules if
there is none. Keep the line for the sub-agent's role and delete the other two. Add the two report
fields at the end of the block to the template's required report structure.

```
## Mandatory skills — selected by the user, binding
Load ALL of these with the skill tool, one call per skill:
  implementer: BEFORE your first file write
  verifier:    BEFORE you read any code or run any check
  reviewer:    BEFORE you read the diff
<name> — <why it is on this list>
…
- The list is final. Do not add, drop, or substitute a skill, and load no other skill. If you need
  one — even a read-only lookup — say so under "Skill concerns" instead.
- If you believe a skill is missing or wrong, say so under "Skill concerns" in your report and
  continue with the list as given.
- Report under "Skills loaded": each skill with the step at which you loaded it, and the first
  action of your role it preceded (implementer: the first file you wrote; verifier: the first
  code file you read or check you ran; reviewer: the first read of the diff or a changed file).
  Reading instructions such as CLAUDE.md or this brief does not count. A skill loaded after that
  point does not count.
```

## Delta selection

The rules — triggers, candidates, when not to ask, and when *keep* is recommended — live in
SKILL.md *Step 5 — Delta selection*. The question shape is the flow above for just the delta's
candidates, with one change: the question text drops "all are recommended".
