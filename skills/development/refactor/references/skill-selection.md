# Skill Discovery (Phases 1, 4, 5)

Refactoring is language-agnostic in principle and stack-specific in practice: what counts as an
idiomatic extraction, which test framework the new tests use, which linter decides the step is
clean. That knowledge is in the skills installed in *this* runtime — so take the names from the
runtime, not from memory.

Nothing in this file names a skill. Names come from the runtime at the moment of the run.

## Discovery

Use the skill list your runtime exposes right now — in Claude Code, the available-skills listing in
your context. That is the complete candidate set. Do not:

- scan `.claude/skills/`, `~/.claude/skills/`, or a skills repository on disk — a directory the
  runtime did not register cannot be invoked;
- take names from a README, another project, or your own recollection;
- assume a family exists because one member does.

If the runtime exposes no skill list, say so once and continue with this skill's own catalogues as
the only guidance. Record it as a decision.

## What to look for

Match against what Phase 0 established about the scope — languages, frameworks, test framework,
build tool — and classify each candidate by what its description says:

| Category | Description says… | Used in |
|---|---|---|
| **knowledge** | idioms, patterns, best practices for a language or framework | Phase 1 (what is idiomatic here) and Phase 5 (how the extracted shape should look) |
| **tester** | writing or extending tests for this stack | Phase 4, when tests or characterization tests have to be written |
| **tooling** | linters, formatters, build or package tooling for this stack | Phase 5 verification, when the project's linter has to be found and run |
| **reviewer** | structured code review, explicit invocation, report to `docs/reviews/` | **not used** — this workflow produces its own report and its own verification |
| **workflow** | multi-phase pipeline with its own planning, review, and gates | **not used** — running one inside this one nests two sets of gates and two reports |
| **router** | "entry point", "routes to", "directs you to the right skill" | not used — load what it routes to instead |
| **unrelated** | nothing matches the scope's stack | ignored silently |

A skill can match on one line of its description and be wrong on another ("for framework X 21+"
while the project is on 15). Read the whole description before adopting it.

## Confirming with the user

Present what you found as a short table — skill, category, why it fits, where it would be used — and
ask whether to load it. With the structured question tool, one multi-select question of at most four
options per category group; unselected means not loaded. Record the outcome as a decision, and list
in the report which skills were proposed, kept, dropped, and actually loaded.

Non-interactively, load the knowledge and tester skills that match the stack unambiguously, skip
everything ambiguous, and record each choice with its origin (`default`).

## Keeping the scope of borrowed guidance

A stack skill informs *how* a refactoring is written — naming, idiom, test shape. It does not change
*what* this workflow does: the behaviour rule, the step size, the gates, and the report stay as
defined here. If a loaded skill wants to commit, run its own review phase, or expand the change,
that part does not apply inside this run.
