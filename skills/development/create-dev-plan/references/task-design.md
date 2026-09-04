# Task Design — Phase 4

Depth material for Phase 2 (`C-scope`) and Phase 4 of `create-dev-plan`. The decomposition is
where the plan's value is decided: a fresh implementer of Task #4 succeeds or fails on what Tasks
#1–3 were said to provide and on how big #4 is.

Contents:

- [Scope](#scope) — one plan or several
- [File structure](#file-structure)
- [Task sizing](#task-sizing)
- [Dependencies and order](#dependencies-and-order)
- [Shared setup](#shared-setup)
- [Interfaces between tasks](#interfaces-between-tasks)
- [Task format](#task-format)
- [Plan sets](#plan-sets)

## Scope

A spec belongs in **several plans** when it covers parts that are independently deliverable:
each part can be built, tested, and shipped without the others, and a user of the system would
notice value from one part alone. Signs: separate subsystems or services, separate deployables,
separate teams, a "phase 2" the spec itself names, or a matrix where two disjoint sets of IDs
share no task.

A spec stays in **one plan** when its parts only make sense together (an endpoint and the rule
it exposes), when splitting would leave a part with no acceptance criterion of its own, or when
the whole thing is under roughly ten tasks anyway.

`C-scope` is always asked, with the recommended cut first and its consequence stated ("one plan
of 7 tasks; the admin UI ships with the API" / "two plans; the API ships first, the admin UI
plan consumes `IF-1` and `IF-2` from it"). The user sees the cut before any task is written.

## File structure

Fixed before the task list, because task boundaries follow file boundaries, not the other way
round.

```
| Path | Status | Responsibility | Tasks |
|---|---|---|---|
| src/orders/export/csv-formatter.ts | new | turns Order[] into CSV lines (FR-2) | #2 |
| src/orders/orders.router.ts | changed | adds GET …/export route (IF-1) | #3 |
| test/orders/csv-formatter.test.ts | new | unit tests for FR-2 | #2 |
```

Rules:

- one responsibility per file, stated in a few words — if you need "and", it is two files;
- things that change together live together: the formatter and its options type, the route
  and its request schema; follow the project's grouping (feature folders or layers) as found in
  Codebase Findings, never a layout the project does not use;
- test files are in the table too, in the project's test layout;
- `deleted` and `moved` are statuses; a moved file lists both paths;
- every file is touched by at least one task and every task's files are in the table — the
  self-check verifies both directions.

## Task sizing

A task is the smallest unit with its own test cycle that a reviewer could accept or reject on its
own. Working definition: it has at least one test of its own, it leaves the code base building
and all tests green, and its result is meaningful to a reviewer without the following tasks.

| Too big | Too small |
|---|---|
| verifies more than ~5 IDs | verifies no ID and provides nothing another task consumes |
| touches files in more than two areas of the layout | is "add a field" or "rename" — fold it into the task whose result needs it |
| its Todos have more than ~10 checkboxes | its only test is one another task must write anyway |
| a reviewer would want to reject part of it and accept the rest | |

Setup, configuration, migration, and documentation are not tasks of their own: they belong to the
first task whose result needs them (see [Shared setup](#shared-setup)). A "documentation task" at
the end is where documentation goes to be forgotten. The same goes for a manual check: a manual
NFR step belongs to the task that produces what is being checked; a task whose only content is a
manual step has nothing a reviewer can accept or reject on its own.

Prefer the first task to be a thin vertical slice when the layout allows it — one request in, one
response out, one acceptance test green — so that every later task extends something that
already works end to end.

## Dependencies and order

- Every task lists `Depends on:` — the tasks whose *Provides* it *Consumes* — or `none`.
- Number tasks so that every dependency has a lower number (topological order). A cycle means two
  tasks are one task, or an interface is in the wrong task.
- `Parallel with:` lists tasks that share no dependency edge in either direction and touch no
  common file; implementation workflows with sub-agents use it. Leave it empty rather than guess.
- A task that is blocked on an unresolved gap (headless runs, or a user-deferred question) is
  marked `Status: blocked — G-n` and keeps its place in the order.

## Shared setup

When several tasks need the same setup (a test harness, a fixture, a registered service, a
migration), it goes into the **first task in order that needs it**, that task's *Provides* lists
it, and every later task *Consumes* it. Nobody has to hunt for where the harness came from, and
the setup is tested by the first task that depends on it.

## Interfaces between tasks

Whoever works on one task learns the names of its neighbours only from the plan. Therefore, per
task:

- **Consumes** — what it uses from earlier tasks: exact identifier, signature or shape, and the
  task that provides it (`OrdersRepository.listByCustomer(customerId: string, range?: DateRange):
  Promise<Order[]> — from #1`).
- **Provides** — what later tasks may rely on, in the same precision, with the tasks that will
  consume it (`CsvFormatter.format(orders: Order[]): string — for #3`).

Contracts the spec fixes in its Design / Data / API section are cited by `IF-n` and quoted, not
re-designed. Where the plan has to invent a name or signature, it is a decision: it is frozen at
approval like a test name, and a change during implementation goes to the Change Log.

## Task format

```
### Task #3 — Export endpoint

Goal: GET /api/customers/{id}/orders/export returns the customer's orders as CSV (IF-1, AC-1, AC-2, AC-3).
Depends on: #1, #2
Parallel with: —
Status: ready

Consumes:
- OrdersRepository.listByCustomer(customerId, range?) — from #1
- CsvFormatter.format(orders) — from #2
- requireCustomer middleware (existing, src/auth/auth.middleware.ts)

Provides:
- route GET /api/customers/:id/orders/export — for #4 (manual NFR check)

Files: src/orders/orders.router.ts (changed), test/orders/orders.export.test.ts (new)

Verifies:
  AC-1 → acceptance   it('AC-1: returns header and one row per order')
  AC-2 → acceptance   it('AC-2: returns header only for a customer without orders')
  AC-3 → acceptance   it('AC-3: returns 403 for another customer')
  IF-1 → contract     it('IF-1: responds text/csv 200, problem+json 400/403')

Todos:
- [ ] Test it('AC-1: …') in test/orders/orders.export.test.ts — failing
- [ ] Test it('AC-2: …') — failing
- [ ] Test it('AC-3: …') — failing
- [ ] Test it('IF-1: …') — failing
- [ ] Add route in orders.router.ts using requireCustomer and CsvFormatter
- [ ] Map repository errors to problem details (src/common/problem.ts)
- [ ] Document the route in README §API
- [ ] All four tests green; existing tests untouched

Done when: all Verifies tests pass, build and full test run green, README updated.
```

Every task has every field; `—` or `none` where empty. The Verifies block and the first Todos
mirror each other exactly — the self-check compares them.

## Plan sets

When `C-scope` cuts the spec into several plans:

- files: `docs/plans/<slug>-1-<part>.md`, `docs/plans/<slug>-2-<part>.md`, …; drafts likewise
  under `docs/draft/plan_<slug>-<n>-<part>.md`;
- every part has the same **Plan Set** table: part, file, one-line scope, IDs covered, depends on
  part(s). The union of the *IDs covered* columns must be the whole inventory, with every `AC-n`
  in exactly one part;
- a part that consumes another part's result lists it under *Consumes* with the part number
  instead of a task number (`IF-1 — from plan 1`);
- the gate is per part; the user may approve parts separately. Test names freeze per part at its
  approval.
