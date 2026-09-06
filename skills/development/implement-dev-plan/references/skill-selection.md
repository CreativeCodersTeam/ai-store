# Skill Discovery and Mapping (Phases 2–3)

The skills that shape the code have to be the ones installed in *this* runtime, chosen for *this*
plan. Two things go wrong otherwise: a skill named from memory turns out not to exist here, and
the task runs with no guidance at all; or a skill is loaded because it sounds related, and the
implementer follows rules for the wrong layer. This file keeps the selection tied to evidence.

Nothing in this file names a skill. The names come from the runtime at the moment of the run.

## Runtime discovery

Take the list of skills your runtime exposes right now — in Claude Code, the available-skills
listing in your context, the same list the skill tool accepts names from. That is the complete set
of candidates. Do not:

- scan `.claude/skills/`, `~/.claude/skills/`, or a repository of skills on disk — a directory the
  runtime did not register is not invocable;
- take names from the plan, the spec, a README, or another project — they describe what someone
  else had installed;
- assume a family exists because one member does (a `foo-tester` in the list does not imply a
  `foo-reviewer`).

If the runtime exposes no skill list at all, say so, and proceed with the plan's *Codebase
Findings* as the only guidance, recorded as `D-n`.

## Match criteria — from the plan

Build the criteria before looking at the list, so the list does not suggest them:

| Source in the plan | Criteria |
|---|---|
| *Codebase Findings* | language, framework(s), test framework, build tool, package manager, documentation tooling |
| *Global Constraints* | version floors, mandated or forbidden libraries, coding conventions |
| *File Structure* | file types and directories (`.cs`, `.ts`, `.feature`, `.md`, `migrations/`, `docs/`) |
| Task *Goals* and *Verifies* | concerns: HTTP API, data access, UI, messaging, CLI, packaging, documentation; test types: unit, integration, acceptance, contract, manual |

## Classification

Read each candidate's description — the same text the runtime uses to decide triggering — and
place it in one category:

| Category | Description says… | Use |
|---|---|---|
| **knowledge** | rules, patterns, best practices for a language, framework, or layer | implementation — loaded by the task implementer |
| **tester** | writing or extending tests for a stack | implementation — every task with a Verifies block |
| **documentation** | doc comments, API documentation conventions | implementation — tasks with documentation Todos on public API |
| **reviewer** | structured code review, explicit invocation, report to `docs/reviews/` | **Phase 6 only** — the review set |
| **refactoring / quality** | improving structure without changing behaviour | Phase 6 — the review set |
| **workflow** | multi-phase pipeline: requirement review, planning, implementation, own review, gates | proposed as **excluded** with a warning; user may override |
| **tooling** | adding/updating packages, inspecting libraries, scaffolding projects | implementation — only tasks whose Todos add or change dependencies or scaffold |
| **router** | "entry point", "routes to", "directs you to the right skill" | not used — load the skills it routes to instead |
| **unrelated** | none of the criteria match | excluded silently (not shown in the proposal unless the user asks) |

The workflow warning, in the proposal text: *loading this inside a task means running its phases —
requirement review, its own planning, its own code review and gates — inside a task that already
has a plan and a review. Recommended: exclude. The user may include it if they want its
implementation phase specifically.*

A skill can match on one line of its description and be wrong for the stack on another ("for
framework X 21+"; the project is on X 15). Read the whole description; put the conflict in the *why*
column and propose *excluded*.

## Proposal table

```
Skills found for docs/plans/order-history-export.md (Node 20, Express, TypeScript, vitest)

| Skill | Category | Why it fits | Proposed use |
|---|---|---|---|
| <name> | knowledge | Codebase Findings: TypeScript, strict null checks; every task | implementation — all tasks |
| <name> | tester | vitest + supertest in test/; all Verifies blocks | implementation — all tasks |
| <name> | documentation | Task #3 Todo "Document the route in README §API" | implementation — #3 |
| <name> | reviewer | TypeScript reviewer; explicit invocation | review (Phase 6) |
| <name> | refactoring | language-agnostic | review (Phase 6) |
| <name> | workflow | full implementation pipeline for this stack | excluded — nested workflow (warning) |
| <name> | knowledge | Angular UI rules; plan has no UI files | excluded — no matching files |
```

Excluded-unrelated skills are not in the table. Excluded-with-reason skills are, so the user can
override the reason.

## Multi-select flow

The structured question tool takes at most four options per question and several questions per
call. Use that shape:

1. **Keep / drop.** One multi-select question per group of up to four *proposed-for-implementation*
   skills, grouped by category (knowledge together, testers together). Option label = skill name;
   description = the one-line *why*. Introduce the group as "Keep the skills you want loaded during
   implementation". Whatever is left unselected is dropped and recorded.
2. **Excluded overrides.** One multi-select question over the *excluded — reason* skills (workflow
   skills included, with their warning in the description): "Include any of these anyway?" Default:
   none selected.
3. **Review set.** Reviewer and refactoring skills are shown as one question with the option
   "Use these for the Phase 6 review (Recommended)" versus "Change the review set — I'll describe".
   They are not loaded now.
4. **Additions.** One free-text question: "Skills the proposal missed?" Each name given is checked
   against the runtime list. Present → added with `origin: user's own`. Absent → reported as *not in
   this runtime's skill list, cannot be loaded*, not added, and noted in the report.

Record the outcome as `D-n`: found n, proposed n, kept n (names), dropped n (names), added n
(names), review set (names).

## Mapping

Per task, derive the skills from the task's own fields; the rules, in order:

| Rule | Applies to |
|---|---|
| Stack baseline knowledge skill(s) — the ones whose descriptions say "baseline", "fundamentals", or that every other knowledge skill of the family builds on them | every task whose *Files* include production code |
| Tester skill(s) for the test framework named in Codebase Findings | every task with a Verifies block (that is every task) |
| Layer or framework knowledge skill | tasks whose *Files* or *Goal* touch that layer (an HTTP skill for the task that adds the route; a data-access skill for the repository task) |
| Documentation skill | tasks with a Todo that documents public API, or whose *Files* include documentation files |
| Tooling skill | tasks whose Todos add, remove, or upgrade a dependency, or scaffold |
| Test-type-specific skill (BDD, contract testing) | tasks whose Verifies block has that test type |

A task with only the baseline and tester rows is normal. A task with five skills is a sign that the
task is too broad or that the rules were applied loosely — check before presenting.

```
| Task | Title | Skills | Why |
|---|---|---|---|
| All | — | <baseline>, <tester> | production code in every task; Verifies in every task |
| #1 | OrdersRepository.listByCustomer | <data-access skill> | Files: src/orders/orders.repository.ts |
| #2 | CsvFormatter | — (baseline + tester only) | pure module, no framework surface |
| #3 | Export endpoint | <http skill>, <documentation skill> | Files: orders.router.ts; Todo: README §API |
| #4 | NFR-1 benchmark | <tester> only | manual step + benchmark test |
```

Ask: **adopt as proposed (Recommended)** / **change — I'll describe**. On change, apply exactly what
was described, show the table again, ask again. The confirmed table is what the briefs (Phase 5)
and the report (Phase 8) use; the report also lists, per task, the skills the implementer
*actually* loaded, from the sub-agent reports or your own log.
