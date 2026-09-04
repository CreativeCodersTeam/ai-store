# Codebase Survey — Phase 3

Depth material for Phase 3 of `create-dev-plan`. The survey exists because the plan is read by
someone who has not read the codebase — a fresh agent per task, or a developer new to the area.
Everything the plan assumes about the project must be written down with a file reference.

Contents:

- [What to look for](#what-to-look-for)
- [Where constraints come from](#where-constraints-come-from)
- [Output: Global Constraints](#output-global-constraints)
- [Output: Codebase Findings](#output-codebase-findings)
- [Greenfield](#greenfield)
- [Depth](#depth)

## What to look for

Walk the list in order; each row answers a question the decomposition will ask.

| Question | Where to look | Feeds |
|---|---|---|
| What is the project, and what commands build and test it? | manifest (`package.json`, `*.csproj`, `pom.xml`, `pyproject.toml`), README, CI config | Global Constraints, Task #1 |
| Which language / framework / runtime version floors apply? | manifest target fields, `engines`, `global.json`, lock files, `.tool-versions` | Global Constraints |
| Which dependencies are allowed or forbidden? | manifest, central package files, lint rules, ADRs, CONTRIBUTING | Global Constraints |
| How is the code layered and where are the entry points? | top-level folders, composition root (`Program.cs`, `app.ts`, `main.py`), routers / controllers | file structure |
| Which existing feature is closest to what the spec asks for? | search for the nouns in the spec (`order`, `export`, `customer`) | the template every new file copies |
| How are things named and organised? | file and folder names, class/function naming, one-type-per-file or not, feature folders vs. layers | file structure |
| Which test framework, runner, and naming convention are in use? | test folders, test files, test config (`vitest.config`, `xunit.runner.json`), CI test step | Verifies blocks — test names |
| Where do tests live and how are they grouped? | test directory layout, fixture folders, shared helpers | file structure |
| Where are the existing mock boundaries? | interfaces injected at construction, HTTP client abstractions, clock / id providers, in-memory implementations used in tests | Verifies blocks — what is real, what is substituted |
| Which cross-cutting patterns must new code follow? | error handling (problem details, result types), logging, validation, auth middleware, transaction handling | task Todos |
| Is there documentation that new code must extend? | API docs, changelog, ADR folder, doc comments convention | task Todos — documentation step |

Record what you find *and* what you looked for and did not find ("no ADR folder", "no
integration tests present"). Absence is a finding too: the plan then knows the first integration
test also sets up the harness.

## Where constraints come from

Two sources, and they can disagree:

- **The spec** — Context, Non-Functional Requirements, Decisions Log, and anything phrased as
  "must use", "must not", "at least version".
- **The code** — manifest target versions, lint and analyser configuration, existing conventions
  that the spec does not mention.

Quote each constraint verbatim with its source. When the spec and the code disagree (spec:
".NET 8 or later"; `global.json`: SDK 10, `TargetFramework` net10.0 with features the spec's floor
would not allow), do not pick a side: it is a blocking gap (*constraint conflict*), back to Phase 2
for that one item.

## Output: Global Constraints

A table at the top of the plan. They apply to every task implicitly, which is why they are stated
once, first, and verbatim.

```
| # | Constraint | Source |
|---|---|---|
| 1 | Node.js >= 20 ("engines": { "node": ">=20" }) | package.json:8 |
| 2 | No new runtime dependencies without ADR | CONTRIBUTING.md:14 |
| 3 | All HTTP errors as RFC 9457 problem details | spec §5 NFR-3; src/common/problem.ts |
| 4 | Test files: test/<area>.<unit>.test.ts, vitest, describe/it | test/orders.service.test.ts |
```

## Output: Codebase Findings

Prose or bullets, each with a file reference, grouped by the questions above. The reader must be
able to open every reference and see what the finding means. Minimum content:

- build and test commands;
- entry points and layering, one line each;
- the closest existing feature and which of its files a new task copies the shape of;
- test framework, naming convention (quote one real test name), directory layout, existing
  fixtures and helpers;
- mock boundaries: what tests substitute today and how (interface + in-memory implementation,
  library, handler stub);
- cross-cutting patterns new code must follow, one line each with the file that defines them;
- what was looked for and not found.

## Greenfield

No code means nothing to lean on and nothing to copy. Then:

- record `greenfield — no existing code` as the first finding;
- the test framework, the test naming convention, the directory layout, and the mock boundaries
  are **questions for the user** (Phase 2), each with a recommendation and its consequence. The
  skill never chooses a framework; it records the project's choice, and here the project has not
  chosen yet;
- Task #1 is the scaffold: project skeleton, build, one passing placeholder test, CI if the spec
  asks for it. Every other task depends on it;
- Global Constraints come from the spec alone and say so.

## Depth

Enough to name files, patterns, and test conventions with references — no more. Signs you have
gone too far: reading whole implementations to judge their quality, noting bugs, proposing
refactorings. Note a bug or a convention violation you stumble over in one line under Findings
("existing `orders.router.ts` does not validate `customerId`; not in scope") so the reader is not
surprised; do not plan its fix unless a requirement needs it.
