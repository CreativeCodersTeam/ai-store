# angular-dev — Detailed Reference

In-depth guidance per phase. Assumes an Angular / TypeScript project. The Skill
Map and the CRITICAL RULES in `SKILL.md` are authoritative; this document
expands the *how*.

---

## Phase 1 — Requirement Review (Detail)

### Goal
Understand the requirement fully before any code is written, and surface every
gap before it becomes rework.

### Steps
1. **Read the requirement** (issue, story, ticket, message). Identify the core
   objective and expected outcome.
2. **Acceptance criteria** — explicit (stated) and implicit (existing specs must
   still pass, component/API contracts honored, public/exported additions need
   TSDoc, existing conventions respected).
3. **Gaps / contradictions / open questions** — write them down. Watch for:
   - Scope boundaries (what is in / out).
   - Error-handling behavior (`ErrorHandler`? HTTP interceptor? `catchError`?).
   - Backward compatibility (component `@Input`/`@Output` surface, exported
     library API, route contracts).
   - Angular-version / bundle-size / performance constraints.
   - Contradictions between the request and existing code/conventions.
4. **Codebase analysis** — affected projects/libraries, app vs library, state
   approach (signals / RxJS / NgRx), cross-cutting (DI, interceptors, guards).
   Locate existing specs (`*.spec.ts`) and docs. Read `angular.json`,
   `tsconfig*.json`, `.editorconfig`, eslint/prettier config, `package.json`.
   Use Serena / tokensave per project + global tooling rules — not `Explore`
   agents when tokensave is available.
5. **Preliminary Skill Map** — from the requirement, list which bindings the
   work will touch. It is *preliminary*: state (point 7) and dependencies
   (point 8) are confirmed in Phase 2 and may add `angular-state` /
   `angular-package-manager`.

### GATE 1 output
Requirement restated in your words · acceptance criteria · gaps/contradictions/
open questions · affected scope · preliminary Skill Map table. **Wait.**

---

## Phase 2 — Clarification (Detail)

### Goal
Resolve the 8 standard implementation dimensions, one at a time, so nothing is
silently assumed.

### Protocol
- **One point per message.** Present point _N_: a concrete proposed default,
  then the open question. Wait for the answer before point _N+1_.
- **No batching, no skipping.** A point that objectively does not apply is shown
  with `n/a — <code-referenced reason>` and still acknowledged before moving on.
- Pre-filling a sensible default is encouraged — it lets the user reply "ok"
  fast — but the default never replaces the round-trip.

### The 8 points (expanded prompts)
1. **Project & folder structure** — which project/library, feature folder,
   standalone vs NgModule; new files/projects yes/no.
2. **Architecture & layering** — smart/dumb component split; state approach
   (signals / RxJS service / NgRx); DI scopes (root/route/component); public vs
   internal surface.
3. **Naming conventions** — file/class/selector names; the project's suffix
   convention — legacy `*.component.ts` / `OrderListComponent`, or the v20
   suffix-less style (`order-list.ts` / class `OrderList`); spec naming. Match the
   existing project convention; don't mix.
4. **Public API / contracts** — signal `input()`/`output()`/`model()` shape
   (decorators only for legacy interop), exported library surface, DTO shape,
   route params/data, OpenAPI mapping for clients.
5. **Errors & edge cases** — error strategy (`ErrorHandler` / interceptor /
   `catchError`), validation style, user-facing messages, logging granularity.
6. **Test strategy** — unit and/or integration, `TestBed` usage, spies vs real
   deps, `HttpTestingController`, naming, coverage expectation.
7. **State / data** — state shape, store vs signals, persistence/hydration,
   `HttpClient` usage, caching, optimistic updates. Confirms `angular-state`.
8. **Dependencies / npm** — allowed/forbidden packages, `ng add` vs
   `npm install`, version constraints. Confirms `angular-package-manager`.

### GATE 2 output
All 8 clarified decisions · the **finalized** Skill Map. **Wait.**

---

## Phase 3 — Task Breakdown (Detail)

### Goal
A trackable plan of discrete tasks, each self-contained.

### Steps
- Break into the smallest reasonable tasks; descriptive IDs; enough detail to
  execute without re-reading the plan.
- Each task addresses **production code + tests + documentation**.
- Each task publishes its **Skill-prerequisite checklist** from the Skill Map.
- Dependencies — common Angular order: models/DTOs → services/state →
  components/templates → routes/guards → interceptors; package changes before
  code using them.
- Parallelization — group independent tasks for sub-agents; do not parallelize
  shared-state/store changes with components that consume them.

### GATE 3 output
Task list with per-task checklists · dependency order · parallel groups. **Wait.**

---

## Phase 4 — Implementation + App Run-Check (Detail)

### Step 0 — Skill invocation (per task)
Before any `Write`/`Edit`/code-producing `Bash` for the task, invoke each
required binding once via the `Skill` tool. A task touching code + tests + docs
is at least three calls (`angular-fundamentals` + `angular-tester` +
`angular-tsdoc`) plus stack skills (`angular-components` / `angular-state`) and
`angular-package-manager` if packages change. Wait for each skill's content;
follow its workflow when producing the artifact. Sub-agent dispatch is in
addition to Step 0, not a substitute — pass the skills explicitly to the
sub-agent (sub-agents are stateless).

### Production code
`angular-fundamentals` always; plus `angular-components` (UI layer),
`angular-state` (reactive data/state), `angular-library-builder` (typed
client/library). Apply project conventions: standalone components, `inject()`,
signals, `OnPush` change detection, strict null checks, `takeUntilDestroyed()`
for teardown, `track` in `@for`. Never leave subscriptions un-torn-down; prefer
`async` pipe / `toSignal()` over manual `subscribe`.

### Tests
`angular-tester` always when code is written/changed — match the project's runner
(Vitest for new projects from v21; Jasmine/Karma and Jest also supported) +
`TestBed` + `provideHttpClient()`/`provideHttpClientTesting()` with
`HttpTestingController`, plus its second-agent missing-case pass.
Cover new/changed behavior and the edge cases from Phase 1.

### Documentation
`angular-tsdoc` for every public/exported API addition/change (component
inputs/outputs, exported library members).

### Build & dependencies
`angular-package-manager` for any package add/remove/version change (enforces the
`npm`/`ng` CLI, `ng add`/`ng update`). Then `ng build` + `ng test --watch=false`;
fix failures before the gate.

### App Run-Check
- **Applies** when an application project exists (`projectType: "application"` in
  `angular.json`). **`n/a`** only when library-only — a clean `ng build <lib>`
  is the run equivalent there.
- Start `ng serve` in the **background** (it does not self-exit). Verify it
  compiles without errors and serves (a representative route renders / no console
  errors). Shut down cleanly. A clean `ng build` is an acceptable substitute when
  serving is impractical. Never block on a foreground long-running process.

### GATE 4 output
Implemented tasks · build/test result · App-Run-Check outcome (or `n/a` reason).
**Wait.**

---

## Phase 5 — Code Review (Detail)

### Steps
- Launch a code-review **sub-agent** instructed to invoke `angular-reviewer`;
  also invoke `angular-reviewer` in the main conversation. The skill reviews
  working-tree or branch-vs-`main` changes and writes a severity-tagged Markdown
  report under `docs/reviews/`.
- Review covers: correctness/completeness vs requirement, test coverage, doc
  accuracy, code quality/bugs/security, Angular idioms, accessibility, bundle/
  change-detection performance, convention consistency.

### Evaluate findings
- **No / minor issues** → fix directly (still invoking the required skills
  before edits), then gate.
- **Significant issues** → new tasks (each with its Skill checklist) → return to
  Phase 4 → re-run Phase 5. If the same issue recurs after 2 cycles, consult the
  user.

### GATE 5 output
Findings · report path · rework/no-rework decision. **Wait.**

---

## Phase 6 — Final Summary (Detail)

1. **Requirement** restated briefly.
2. **Files** created/modified.
3. **Implementation details** and key design decisions.
4. **Tests** added/updated and what they cover.
5. **Documentation** changes (TSDoc, READMEs).
6. **Package changes** (cross-reference `package.json` / lockfile).
7. **Decisions / trade-offs.**
8. **Review notes** — key `angular-reviewer` points + report link.
9. **Things to check** before committing.
10. **Skill-Invocation Log** — every task's checklist resolved to `[x]`/`[n/a]`/
    `[!]` with evidence (see `SKILL.md`). Mandatory even when all bindings were
    correct — it is the audit trail.

End with: *All changes are ready for your review. Commit them yourself when
satisfied — this workflow creates no commits.*

---

## General Guidelines

### Sub-agents
- Provide complete context (stateless). Pass the relevant `angular-*` skills in
  the prompt. Use a build/test runner for `ng build`/`ng test`. Prefer small
  focused tasks; launch independent tasks in parallel.
- For code research, follow the project + global tooling rules (Serena →
  tokensave → built-in; no `Explore` agents when tokensave is available).

### Git
- NEVER `git commit`, `git add -A`/`.`, branch, tag, or push. Read-only git
  (`diff`/`status`/`log`) is fine. Stage by name only when explicitly asked;
  refuse secret-like files (`.env`, `*.pem`, credentials).
- If a commit is requested, skip it: *"Committing is your responsibility."*

### Project conventions
- Honor `CLAUDE.md`, `AGENTS.md`, `.github/copilot-instructions.md`,
  `.editorconfig`, eslint/prettier config, `angular.json`, `tsconfig*.json`.
- Match the project's existing state-management choice and component style
  rather than introducing a new one.
