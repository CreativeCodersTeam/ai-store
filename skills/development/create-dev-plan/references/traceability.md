# Traceability — From Requirement ID to Test

Depth material for Phases 1 and 4 of `create-dev-plan`. The plan connects every requirement to
the test that will later prove it. The connection is made when the plan is written, not during
implementation, so that approval of the plan can check *whether* every requirement will be
verified, and the end of implementation can check *that* it was.

Contents:

- [Classification](#classification) — the four kinds and how to tell them apart
- [Kind → test type](#kind--test-type) — the fixed mapping
- [ID assignment](#id-assignment) — when the spec has no IDs
- [Verifies block](#verifies-block) — format per task
- [Completeness rules](#completeness-rules) — exactly once, at least once, never blank
- [Happy-path rule](#happy-path-rule) — one error or edge case per functional requirement
- [Untestable criteria and orphan tests](#untestable-criteria-and-orphan-tests)
- [Mock boundaries](#mock-boundaries)
- [Traceability matrix](#traceability-matrix) — format
- [Todo derivation](#todo-derivation) — test, implementation, docs
- [Self-check](#self-check) — run before every draft
- [Change Log](#change-log) — stability after approval

## Classification

Every requirement ID gets a *kind*. The kind decides the test type; the prefix does not. A
functional requirement that reads "the system exposes `GET /orders/export`" is a contract, not a
rule, and a unit test for it would test nothing.

| Kind | What it is | Typical source |
|---|---|---|
| **behaviour** | Observable from outside the system boundary: a user or client does X and sees Y. Given/When/Then. | `AC-n` |
| **rule** | Business rule, calculation, validation, permission decision, precedence between rules. Decidable inside the code without the boundary. | most `FR-n` |
| **contract** | Shape of an interface or data: endpoint, payload, status code per error case, schema, event, migration. | `IF-n` (Design / Data / API section), some `FR-n` |
| **quality** | Non-functional: performance, scale, security, privacy, accessibility, observability, compatibility. | `NFR-n` |

When one requirement is two kinds ("validates the date range *and* returns 400 with
ProblemDetails"), it is one ID with two rows in the matrix — a rule row and a contract row — and
two tests. Do not split the ID; the spec owns IDs.

## Kind → test type

Fixed. It is not re-decided per task; a task that wants a different type has misclassified the
requirement.

| Kind | Test type | Notes |
|---|---|---|
| behaviour | **acceptance / integration** test at the system boundary | One test per criterion. The ID appears in the test name or as a marker the project uses. |
| rule | **unit** test of the affected logic | Rule tables become parameterised tests — one case per row. |
| contract | **contract** test | Schema; status code per documented error case; a migration is tested against an empty database. |
| quality | **automated** *or* **manual**, always explicit | Automated: analyser, budget, load-test threshold, lint rule. Otherwise a named manual check step with an owner. Never a blank. |

Concrete frameworks and tools are not chosen here; they come from the Codebase Findings (Phase 3)
or, for greenfield projects, from the user (Phase 2). The same goes for test naming: the plan
follows the project's convention. Where none exists, the user picks one before test names are
written — names are frozen at approval, and a frozen name in an invented convention is a problem
for every later test.

## ID assignment

Existing IDs are used unchanged. Where the input has none, or only some, assign them:

- `FR-n`, `NFR-n`, `AC-n` continue the existing numbering (a spec with `FR-1`–`FR-4` and an
  unnumbered rule gets `FR-5`, not `FR-4b`).
- `IF-n` for each interface or data contract in the spec's Design / Data / API section, in
  document order. The spec template does not number this section, so most specs need `IF-` IDs.
- Every assigned ID is listed in **Spec Feedback** with the text it was attached to, so the spec
  can be updated to match.

Assigning an ID to a sentence that is in the input is bookkeeping. Writing a new acceptance
criterion because the input has none is spec work: propose it, have the user confirm it
(`C-ac-n`), and mark it `origin: derived`.

## Verifies block

Every task has one:

```
Task #N: <subject>
  Verifies:
    AC-3  → acceptance   <TestName>
    FR-2  → unit         <TestName>
    IF-1  → contract     <TestName>
    NFR-1 → manual       <check step> — <owner>
```

- The test is the task's *first* work result, not its last (see [Todo derivation](#todo-derivation)).
- Test names follow the project's convention verbatim and carry the ID where the convention
  allows it (`Export_AC3_UnknownCustomer_Returns403`, `it('AC-3: returns 403 for another
  customer')`).
- Manual entries name a concrete step ("open the export in Excel on Windows, confirm no import
  wizard") and a person or role.

## Completeness rules

| ID kind | In Verifies blocks | Why |
|---|---|---|
| `AC-n` | **exactly one**, across the whole plan set | An acceptance test that two tasks both claim is either duplicated or owned by nobody. |
| `FR-n`, `IF-n`, `NFR-n` | **at least one** | A rule can be exercised from several tasks; a contract can have a producer and a consumer task. The matrix lists all of them. |
| any | **never blank** in the matrix | A blank cell reads as "not verified". Untestable → `open — G-n`; quality without target → `manual` + step. |

A plan set (several plans from one spec) applies these rules to the union. Each plan's matrix
holds its own IDs; the *Plan Set* table in every part shows which IDs each part covers, so the
"exactly once" rule can be checked across parts.

## Happy-path rule

For every functional requirement, among the acceptance criteria that name it there must be at
least one that describes an error or edge case — empty input, invalid input, missing permission,
concurrent change, partial failure, boundary value. A functional requirement whose criteria show
only the success path is reported as a gap (`G-n`, category *happy-path-only*), never planned
silently.

The rule is per *requirement*, not per criterion: an acceptance criterion in Given/When/Then form
is one scenario, and a spec is expected to have separate success and failure scenarios. Asking
every single criterion to contain an error case would flag well-written specs.

A criterion that describes the *failure* of an action verifies both the requirement that states
the action and the one that states the rule refusing it — name both. Otherwise the action's
requirement looks happy-path-only while its error cases sit under a neighbouring ID, and the gap
you report is a bookkeeping artefact rather than a missing scenario.

## Untestable criteria and orphan tests

- A criterion that cannot be translated into a test as written ("the export should look right in
  Excel") is not concrete enough. Write no vague test. Report it as `G-n` (category
  *untestable*), put it under Open Questions, and give its matrix row `open — G-n` in the test
  column. If the user answers in Phase 2, the answer becomes a `C-n`, the criterion gets its test,
  and the Spec Feedback entry tells the spec what wording to adopt.
- A test you want to plan that no requirement ID reaches is either an implementation detail —
  then it is listed under the task's Todos as "(implementation detail)" and stays out of the
  Verifies block — or a sign of a missing requirement, which is reported as `G-n` (category
  *missing requirement*). Do not invent an ID to make an orphan test look traced.

## Mock boundaries

Where a test uses the real dependency and where it substitutes it is decided by the target
project — the boundaries it already draws (repository interfaces, HTTP clients, clocks, message
buses) are in the Codebase Findings. The spec's wording ("the system stores…") says nothing about
what to mock. Greenfield projects have no boundaries yet: ask (Phase 2) rather than decide.

## Traceability matrix

One row per ID and task; an ID verified in two tasks has two rows.

```
| ID    | Kind      | Task | Test type   | Test name / manual step               | Automated |
|-------|-----------|------|-------------|---------------------------------------|-----------|
| AC-1  | behaviour | #3   | acceptance  | Export_AC1_ThreeOrders_ReturnsCsv     | yes       |
| FR-2  | rule      | #2   | unit        | CsvFormatter_FR2_FormatsIsoDate       | yes       |
| IF-1  | contract  | #3   | contract    | ExportEndpoint_IF1_StatusCodes        | yes       |
| NFR-2 | quality   | #4   | manual      | open in Excel (Windows), no wizard — QA | no      |
| AC-6  | behaviour | —    | —           | open — G-3                            | —         |
```

Sort by ID. The matrix is the artefact reviewers check against the test suite at the end of
implementation; it must be readable without the rest of the plan.

## Todo derivation

The Todos of a task are derived from its Verifies block, in this order:

1. one checkbox per verified ID: "Test `<name>` for `<ID>`" — written and failing first;
2. the implementation, as many checkboxes as there are separately checkable steps;
3. documentation (XML docs, TSDoc, README, ADR) for what the task produced;
4. anything the task must leave behind for its dependants (a fixture, a registered service).

The order is part of the plan. Implementation workflows work the list top to bottom.

## Self-check

Run before writing every draft and again in Phase 6 after re-reading an edited draft. Any
failure means the decomposition is wrong — fix it, do not annotate it.

- [ ] Every `AC-n` from the inventory appears in exactly one Verifies block (across the plan set).
- [ ] Every `FR-n`, `IF-n`, `NFR-n` appears in at least one Verifies block.
- [ ] Every matrix row has a test name, a manual step, or `open — G-n`. No blank cells.
- [ ] Every Verifies entry has a test type from the mapping table, consistent with the ID's kind.
- [ ] Every test name follows the convention recorded in Codebase Findings (or decided in `C-n`).
- [ ] No planned test lacks an ID (orphans are marked implementation detail or reported as `G-n`).
- [ ] Every functional requirement passes the happy-path rule or has a `G-n`.
- [ ] Every task's Todos start with its tests, one per verified ID.
- [ ] Every task's *Consumes* names a task that *Provides* it, with identical names and signatures.
- [ ] Tasks are numbered in dependency order; no task depends on a higher number.
- [ ] Every file in the file structure is touched by at least one task, and every task's files are in the structure.
- [ ] Every `G-n` is either answered by a `C-n` or listed under Open Questions / Spec Feedback.

## Change Log

After approval, test names and interfaces are frozen. The Change Log is the only place an
approved plan changes, apart from ticked checkboxes:

```
| Date | Task | Change | Reason | Origin |
|---|---|---|---|---|
| 2026-09-10 | #3 | Test renamed Export_AC1_ThreeOrders_ReturnsCsv → Export_AC1_ReturnsCsvWithHeaderAndRows | Project convention requires outcome in name | implementer |
```

An implementation workflow that renames a test, changes a signature in *Provides*, or re-cuts a
task adds a row. A reviewer comparing the matrix with the test suite reads the Change Log first.
