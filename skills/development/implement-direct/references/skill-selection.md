# Skill Discovery and Mapping (Phase 1, Gate 2, Phase 3)

The skills that shape the code have to be the ones installed in *this* runtime, chosen for *this*
requirement. Two things go wrong otherwise: a skill named from memory turns out not to exist here,
and the task runs with no guidance at all; or a skill is loaded because it sounds related, and the
implementer follows rules for the wrong layer. This file keeps the selection tied to evidence: the
match criteria come from the Phase-1 findings, never from the request or from memory.

Nothing in this file names a skill. The names come from the runtime at the moment of the run.

## Runtime discovery

Take the list of skills your runtime exposes right now — in Claude Code, the available-skills
listing in your context, the same list the skill tool accepts names from — and the list of agent
types available to the agent tool (review-capable agents belong in the review set). That is the
complete set of candidates. Do not:

- scan `.claude/skills/`, `~/.claude/skills/`, or a repository of skills on disk — a directory the
  runtime did not register is not invocable;
- take names from the requirement, a README, or another project — they describe what someone else
  had installed;
- assume a family exists because one member does (a `foo-tester` in the list does not imply a
  `foo-reviewer`).

If the runtime exposes no skill list at all, say so in the Phase-1 summary, and proceed with the
Phase-1 conventions as the only guidance, recorded as `D-n` at Gate 2.

## Match criteria — from Phase 1

Build the criteria before looking at the list, so the list does not suggest them:

| Source (Phase 1, step 5) | Criteria |
|---|---|
| Build and dependency manifests | language, framework(s), runtime version, package manager, build tool |
| Test layout and configuration | test framework, runner, test types in use |
| Documentation tooling | doc-comment convention (XML docs, TSDoc, Javadoc, docstrings), API doc generator |
| Scope (affected files, modules) | file types and directories, layers touched (HTTP, data access, UI, messaging, CLI, packaging) |
| Acceptance criteria | concerns: an endpoint, a migration, a UI component, a background job, a public API |

## Classification

Read each candidate's description — the same text the runtime uses to decide triggering — and
place it in one category:

| Category | Description says… | Use |
|---|---|---|
| **knowledge** | rules, patterns, best practices for a language, framework, or layer | implementation — loaded by the task implementer and the verifier |
| **tester** | writing or extending tests for a stack | implementation — every task |
| **documentation** | doc comments, API documentation conventions | implementation — tasks with public API or documentation items |
| **reviewer** | structured code review, explicit invocation, report to `docs/reviews/` | **Phase 5 only** — the review set |
| **refactoring / quality** | improving structure without changing behaviour | Phase 5 — the review set |
| **review agent** | an agent type whose description is code review | Phase 5 — the review set |
| **workflow** | multi-phase pipeline: requirement review, clarification, own review, gates | proposed as **excluded** with a warning; user may override |
| **tooling** | adding/updating packages, inspecting libraries, scaffolding projects | implementation — only tasks whose items add or change dependencies or scaffold |
| **router** | "entry point", "routes to", "directs you to the right skill" | not used — load the skills it routes to instead |
| **unrelated** | none of the criteria match | excluded silently (not shown unless the user asks) |

The workflow warning, in the proposal text: *loading this inside a task means running its phases —
requirement review, its own clarification, its own code review and gates — inside a task that is
already inside this workflow. Recommended: exclude. The user may include it if they want its
implementation phase specifically.*

A skill can match on one line of its description and be wrong for the stack on another ("for
framework X 21+"; the project is on X 15). Read the whole description; put the conflict in the
*why* column and propose *excluded*.

## Proposal table (Phase-1 summary, updated at Gate 2)

```
Skills found for <slug> (Node 20, Express, TypeScript, vitest — package.json:1, vitest.config.ts:1)

| Skill / agent | Category | Why it fits | Proposed use |
|---|---|---|---|
| <name> | knowledge | TypeScript strict, tsconfig.json:5; every task | implementation — all tasks |
| <name> | tester | vitest + supertest in test/; every task | implementation — all tasks |
| <name> | documentation | AC-4 adds a public export; README §API exists | implementation — tasks with public API |
| <name> | reviewer | TypeScript reviewer; explicit invocation | review (Phase 5) |
| <agent type> | review agent | general code reviewer | review (Phase 5) — fallback if no stack reviewer |
| <name> | workflow | full implementation pipeline for this stack | excluded — nested workflow (warning) |
| <name> | knowledge | Angular UI rules; scope has no UI files | excluded — no matching files |
```

Excluded-unrelated skills are not in the table. Excluded-with-reason skills are, so the user can
override the reason.

## Gate-2 multi-select flow

The structured question tool takes at most four options per question and up to four questions per
call. Use that shape, all in the Gate-2 call (a second call if more than four questions are needed):

1. **Keep / drop.** One multi-select question per group of up to four *proposed-for-implementation*
   skills, grouped by category. Option label = skill name; description = the one-line *why*.
   Introduce the group as "Keep the skills you want loaded during implementation". Whatever is left
   unselected is dropped and recorded.
2. **Excluded overrides.** One multi-select question over the *excluded — reason* skills (workflow
   skills included, with their warning in the description): "Include any of these anyway?" Default:
   none selected.
3. **Review set.** Reviewer skills and review agents as one question: "Use these for the Phase 5
   review (Recommended)" versus "Change the review set — I'll describe". They are not loaded now.
   If the set is empty, say so here; Phase 5 will search for general review skills and ask again.
4. **Additions.** The free-form escape of the call: "Skills the proposal missed?" Each name given
   is checked against the runtime list. Present → added with `origin: user's own`. Absent →
   reported as *not in this runtime's skill list, cannot be loaded*, not added, and noted in the
   report.

Record the outcome as `D-n`: found n, proposed n, kept n (names), dropped n (names), added n
(names), review set (names).

## Mapping

Per task, derive the skills from the task's own fields; the rules, in order:

| Rule | Applies to |
|---|---|
| Stack baseline knowledge skill(s) — the ones whose descriptions say "baseline", "fundamentals", or that every other knowledge skill of the family builds on them | every task whose *Files* include production code |
| Tester skill(s) for the test framework found in Phase 1 | every task (every task has tests) |
| Layer or framework knowledge skill | tasks whose *Files* or *Goal* touch that layer (an HTTP skill for the task that adds the route; a data-access skill for the repository task) |
| Documentation skill | tasks with a documentation item on public API, or whose *Files* include documentation files |
| Tooling skill | tasks whose items add, remove, or upgrade a dependency, or scaffold |
| Test-type-specific skill (BDD, contract testing) | tasks whose planned tests have that type |

A task with only the baseline and tester rows is normal. A task with five skills is a sign that the
task is too broad or that the rules were applied loosely — check before presenting.

The checklist printed under each task at Gate 3 is this mapping. It is what the implementer brief,
the verifier brief (same list), and the Skill-Invocation Log in Phase 6 use; the report also lists,
per task, the skills the implementer *actually* loaded, from the sub-agent reports or your own log.
