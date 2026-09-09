# Coverage Assessment (Phase 4)

The question is never "what is the project's coverage percentage". It is narrower and much more
useful: **will a test go red if this particular code stops behaving the way it does today?** A file
at 90% can leave exactly the branch you are about to touch untested, and a file at 40% can have the
one function you care about fully pinned down.

So assess per candidate, immediately before its first step, and state in the report which of the
three levels of evidence below you have. Never state a level you did not produce.

## Level 1 — Measurement (preferred)

If the project has a coverage tool configured, run it and read the numbers for the *lines the
planned step will touch*.

| Stack | Typical command |
|---|---|
| .NET | `dotnet test /p:CollectCoverage=true` (coverlet), or `dotnet-coverage collect` |
| Node / TypeScript | `npm test -- --coverage` (jest), `vitest run --coverage`, `nyc <cmd>` |
| Python | `pytest --cov=<package> --cov-report=term-missing` |
| Java | `mvn test jacoco:report`, `gradle test jacocoTestReport` |
| Go | `go test -cover ./...`, `-coverprofile` for per-line detail |

Prefer a report format that shows uncovered *lines* (`term-missing`, the HTML/XML detail report) —
a per-file percentage does not answer the question. Scope the run to the relevant project or test
selection if the full suite is slow; say in the report what you scoped it to.

Record: command, the lines or branches at the site that are covered, and the ones that are not.

## Level 2 — Mapping (when no tool is configured)

Find the tests that exercise the symbol and read them:

1. Search for direct uses of the symbol in test files.
2. If none, follow callers one or two hops and search for those — a function is often covered
   through its caller, and that still counts.
3. Open the tests you found. A test that *calls* the code but asserts nothing about its result does
   not protect it; note that distinction rather than counting the hit.

Record the test `file:line` list, and state explicitly: *mapping, not measurement — the tests reach
this code, the exact branches are not measured.* That sentence is the difference between honest
evidence and a number nobody can trust.

## Level 3 — The break probe (optional, strongest)

When it matters — a high-risk candidate, or a mapping that looks thin — prove the net exists:
temporarily break the behaviour at the site (invert a condition, return a wrong constant), run the
tests, and see whether anything goes red.

- A red test names the exact safety net you are relying on.
- **All green means the site is effectively untested**, whatever the percentage said.

Take a snapshot first (`step-protocol.md`) and restore it immediately afterwards — this deliberate
break must never survive into the diff. Record the probe and its outcome in the report.

## What counts as "covered enough"

All three must hold for the site the step will touch:

1. At least one test executes it, and that test is green against the *unchanged* code.
2. The test asserts observable behaviour of that code, not merely that it ran without throwing.
3. The specific branches the step will restructure are among the executed ones — a guard-clause
   rewrite of an untested error path is unverified even if the happy path is covered.

If any of the three fails, the candidate goes to the gate with the four options in `SKILL.md`
Phase 4.

## When tests have to be written first

Writing them is its own unit of work, before any refactoring of that candidate:

- Use the runtime's tester skill for the stack if there is one (`skill-selection.md`).
- The new tests must be **green against the unchanged code**. A test that only passes after the
  refactoring is describing the new code, not protecting the old behaviour — and it will not detect
  the regression it was written to prevent.
- **Characterization tests pin down what the code does, not what it should do.** If one exposes
  behaviour that looks wrong, the test asserts the wrong behaviour and the finding goes into *Found,
  not fixed*. "Correcting" it while writing removes the very baseline you are building.
- Run the new tests, record the result, and only then start Phase 5.
