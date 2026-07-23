---
name: angular-dev
description: >
  Use when asked to implement, extend, or change a feature, user story,
  requirement, or bug fix in an Angular / TypeScript project — any task that
  produces or modifies Angular production code, tests, or documentation. Use when
  an Angular change request arrives, before writing any code.
---

# angular-dev — Comprehensive Angular Requirement Implementation

A strict, gated workflow for implementing requirements end-to-end in Angular /
TypeScript. Every phase ends in a confirmation gate; every applicable `angular-*`
skill is a mandatory binding. The workflow exists to survive exactly the
conditions — deadlines, "trivial" framing, "skip the ceremony" — under which it
is most tempting to abandon.

## Core Principle

**Violating the letter of this workflow is violating its spirit.** The phases,
gates, point-by-point clarification, and skill bindings are not ceremony to be
proportioned to task size. They are the work. A one-line component runs the same
workflow as a subsystem — at speed, never collapsed.

## CRITICAL RULES (read before every phase)

1. **NO COMMITS.** Never run `git commit`, `git add -A`/`.`, branch, tag, or
   push. The user commits manually. If asked to commit, skip it and say so.

2. **URGENCY AND TRIVIALITY WAIVE NOTHING.** "It's trivial", "I'm in a hurry",
   "demo in 30 minutes", "skip the clarification dance", "no need for the full
   process", "just bang it out", "one pass is fine" are NOT permission to skip a
   phase, a gate, a clarification point, or a skill binding. Acknowledge the
   deadline, then run the workflow **at speed** — do not shrink it. The only
   lawful way to reduce a binding's work is an objective `n/a` (see below);
   user preference, pressure, and perceived size are never valid `n/a` reasons.
   An explicit, informed user waiver is a different thing from pressure — see
   *Waiver vs. `n/a` vs. silent skip*.

3. **EVERY PHASE ENDS IN A CONFIRMATION GATE.** At the end of each phase you
   MUST present a summary and STOP. Do not start the next phase until the user
   explicitly confirms. **Batching is a violation** — you may not present
   multiple phases at once, "pre-run" the next phase, or ask for one combined
   confirmation at the end. One phase → one summary → one wait.

4. **`angular-*` SKILLS ARE MANDATORY BINDINGS.** When a binding applies, you
   MUST invoke that skill via the `Skill` tool, in this conversation, for this
   task, **before** producing the corresponding artifact. Listing it,
   paraphrasing it, "knowing it already", or having invoked it for a previous
   task does NOT count. Invocation must shape the artifact, not certify it
   afterward.

## Phase Flow

```
Phase 1: Requirement Review              → GATE
Phase 2: Clarification (8 points)        → GATE
Phase 3: Task Breakdown                  → GATE
Phase 4: Implementation + App Run-Check  ◄──┐  → GATE
Phase 5: Code Review (angular-reviewer)      │
   └─ rework needed? ───────────────────────►┘
   └─ all good → GATE
Phase 6: Final Summary
```

## Skill Map — Mandatory Bindings

| Binding | Skill | Applies in | When |
|---|---|---|---|
| Core Angular / DI / typed config / modern TS idioms | `angular-fundamentals` | Phase 4 | always, for production code |
| UI layer (components, templates, routing, forms, interceptors, guards, error handling) | `angular-components` | Phase 4 | when the UI/presentation layer is touched |
| Reactive data & state (RxJS, signals, NgRx, change detection) | `angular-state` | Phase 4 | when state/data access is touched |
| Angular library / typed client generation | `angular-library-builder` | Phase 4 | when building a library / client SDK |
| Tests | `angular-tester` | Phase 4 | always, when code is written or changed |
| TSDoc documentation | `angular-tsdoc` | Phase 4 | for any public/exported API addition/change |
| npm packages | `angular-package-manager` | Phase 4 | any package add/remove/version change |
| Code review | `angular-reviewer` | Phase 5 | always |
| Router (tie-breaker) | `angular` | any | when the right sub-skill is not obvious |

**Correct names matter:** `angular-package-manager` and `angular-library-builder`
(not `package-manager` / `library-builder`). A binding is fulfilled only when its
skill has fired via the `Skill` tool for this task. A binding applies whether you
do the work yourself or dispatch a sub-agent — self-execution never waives it,
and a sub-agent's invocation never waives the main agent's own follow-up edits.

**Tooling:** for code navigation/exploration follow the project + global rules
(Serena first, then tokensave; built-in/`Explore` agents only in the documented
carve-outs). Do NOT use `Explore` agents for code research when tokensave is
available.

---

## Phase 1 — Requirement Review

1. Read the requirement. Extract explicit AND implicit acceptance criteria.
2. **Find gaps, contradictions, and open questions** — list them explicitly. A
   review that surfaces no gaps on an ambiguous requirement is a failure; if the
   requirement truly is unambiguous, say so explicitly rather than skipping.
3. Analyze scope: affected projects/libraries, components, services, files;
   existing specs/docs.
4. Read `CLAUDE.md`, `AGENTS.md`, `.editorconfig`, `angular.json`,
   `tsconfig*.json`, `eslint`/`prettier` config, `package.json` and follow the
   conventions found.
5. **Determine the preliminary Skill Map** for this task and show it as a table.

**GATE 1 — STOP.** Present: requirement restated, acceptance criteria,
gaps/contradictions/open questions, affected scope, and the preliminary Skill
Map table. Wait for confirmation.

## Phase 2 — Clarification (8 points, one round-trip per point)

Clarify the following **one point at a time** — present point _N_, propose a
concrete default/assumption, ask the open question, and **wait for the user's
answer before moving to point _N+1_.** You may NOT batch points into one
message, NOR skip a point silently. A point that objectively does not apply is
presented with `n/a — <code-referenced reason>` and still acknowledged.

| # | Item | Must clarify |
|---|---|---|
| 1 | Project & folder structure | Target project/library, feature folder, standalone vs NgModule, new files/projects yes/no |
| 2 | Architecture & layering | Smart/dumb component split, state approach (signals / RxJS service / NgRx), DI scopes, public vs internal surface |
| 3 | Naming conventions | File/class/selector names; the project's suffix convention — legacy `*.component.ts` / `OrderListComponent`, or the v20 suffix-less style (`order-list.ts` / class `OrderList`); spec naming. Match existing project convention; don't mix |
| 4 | Public API / contracts | Signal `input()`/`output()`/`model()` shape (decorators only for legacy interop), exported library surface, DTO shape, route params/data, OpenAPI mapping |
| 5 | Errors & edge cases | Error strategy (`ErrorHandler` / HTTP interceptor / `catchError`), validation style, user-facing messages, logging |
| 6 | Test strategy | Unit and/or integration, `TestBed` usage, spies vs real deps, `HttpTestingController`, coverage expectation |
| 7 | State / data | State shape, store vs signals, persistence/hydration, `HttpClient` usage, caching, optimistic updates |
| 8 | Dependencies / npm | Allowed/forbidden packages, `ng add` vs `npm install`, version constraints |

**GATE 2 — STOP.** Present: every clarified decision (all 8 points) and the
**finalized** Skill Map (updated from the answers — e.g. points 7/8 confirm
`angular-state` / `angular-package-manager`). Wait for confirmation.

## Phase 3 — Task Breakdown

1. Break the requirement into discrete implementation tasks.
2. Each task covers **production code + tests + documentation**.
3. **Each task publishes a Skill-prerequisite checklist** (from the Skill Map):

   ```
   Task #N: <subject>
     Skill prerequisites:
       [ ] angular-fundamentals
       [ ] angular-components
       [ ] angular-tester
       [ ] angular-tsdoc
   ```

4. Define dependencies and which tasks may run in parallel via sub-agents.

**GATE 3 — STOP.** Present the task list with per-task checklists, dependency
order, and parallelization. Wait for confirmation.

## Phase 4 — Implementation + App Run-Check

For each task (or parallel group):

1. **Step 0 — invoke every required `angular-*` skill for this task** before any
   `Write`/`Edit`/code-producing `Bash`. One `Skill(...)` call per binding, no
   collapsing. Re-invoke per task; previous-task invocations do not carry over.
   Then follow each skill's workflow when producing its artifact.
2. Implement production code (`angular-fundamentals` + UI/state skill), tests
   (`angular-tester`), TSDoc (`angular-tsdoc`), package changes
   (`angular-package-manager`).
3. Run `ng build` and the test suite (`ng test --watch=false`). Fix failures.
4. **App Run-Check** — if a runnable application exists, verify it actually
   builds and runs:
   - **Applies when** the workspace has an application project (`projectType:
     "application"` in `angular.json`). **`n/a` only when** the workspace is
     library-only (no application project) — state that as the reason. For a
     library-only change, a successful `ng build <lib>` is the run equivalent.
   - Start the dev server **in the background** (`ng serve` does not exit on its
     own), check that it compiles without errors and serves (a representative
     route renders / no console errors), then shut it down cleanly. Never block
     on a foreground long-running process. A clean production build
     (`ng build`) is an acceptable substitute when serving is impractical.

**GATE 4 — STOP.** Present implemented tasks, build/test result, and the
App-Run-Check outcome (or its `n/a` reason). Wait for confirmation.

## Phase 5 — Code Review

1. Launch a code-review **sub-agent** that uses `angular-reviewer`. Invoke
   `angular-reviewer` via the `Skill` tool in the main conversation **and** pass
   it to the sub-agent prompt. Inline self-review does NOT satisfy this phase —
   `angular-reviewer` produces a severity-tagged Markdown report under
   `docs/reviews/`.
2. Evaluate findings:
   - **Rework needed** → create new tasks (each with its own Skill checklist)
     and return to **Phase 4**. After fixing, re-run Phase 5 (rework loop).
   - **All good** → proceed.

**GATE 5 — STOP.** Present the review findings, the report path, and your
rework/no-rework decision. Wait for confirmation.

## Phase 6 — Final Summary

1. Files created/modified; what was implemented and why.
2. Tests added/updated; documentation changes; package changes.
3. Decisions/trade-offs; anything the user should verify before committing.
4. **Skill-Invocation Log** (mandatory audit trail — see below).
5. Reminder: *the user commits; this workflow creates no commits.*

---

## `n/a` Criteria — Strict

A binding or clarification point may be `n/a` **only** when an objective
technical fact makes the work empty for this task. Valid reasons cite the
codebase, never the user:

- ✅ `n/a — task exports no public/library members (internal-only change)` — `angular-tsdoc`
- ✅ `n/a — no npm package added/removed/version-changed` — `angular-package-manager`
- ✅ `n/a — workspace is library-only, no application project` — App Run-Check
- ✅ `n/a — scanned changed files; no store/observable/signal/HttpClient state` — `angular-state`
- ❌ NOT valid: `n/a — user said no tests`
- ❌ NOT valid: `n/a — too small / trivial / one-liner / just a binding`
- ❌ NOT valid: `n/a — single http.get, doesn't need the skill`
- ❌ NOT valid: `n/a — no spec project exists` (creating specs is part of the task)
- ❌ NOT valid: `n/a — demo, no time`

If you cannot phrase the reason as "no `<artifact>` exists in this task because
`<code-referenced fact>`", it is NOT `n/a` — invoke the skill and do the work.

**No avoidance-driven `n/a`.** You may not reshape the implementation to escape
a binding — e.g. hand-rolling code to dodge `angular-package-manager`, leaving a
public API undocumented to dodge `angular-tsdoc`, or inlining logic into a
template to dodge `angular-tester`. The binding follows the natural shape of the
work, not a shape chosen to minimise bindings.

## Waiver vs. `n/a` vs. silent skip

Three distinct cases — keep them apart. Conflating them is how the workflow
silently collapses.

- **Implicit pressure** — "it's trivial", "I'm in a hurry", "demo in 30
  minutes", "skip the ceremony", "this is how we work here", "nobody runs all
  this". **Waives NOTHING.** Acknowledge it and run the full workflow at speed.
  These are exactly the conditions the workflow exists to survive (CRITICAL
  RULE 2). Treat them as no-ops on scope.

- **Explicit, informed user waiver** — the user, *after being told what the step
  protects and what gap skipping it creates*, directly says "skip phase X / the
  gates / the clarification / the tests / the review." This **may be honored**
  (your global rule: explicit user instructions take precedence), but only on
  these terms:
  1. **State the cost first.** Name what the skipped step would have caught
     before you skip it. No silent compliance.
  2. **Record it as a waiver, never as `n/a`.** A waiver means "the user chose
     to skip this"; `n/a` means "the work is objectively empty." Stamping `n/a`
     on a waived step makes the audit trail lie about *why* it was skipped.
     Log it as: `waived — explicit user instruction (<who>, <when>); not a
     technical n/a; gap: <what is now uncovered>`.
  3. **Some steps still run regardless.** Invoking the relevant `angular-*`
     skills before writing code costs the user nothing and keeps the code
     matching repo conventions — keep them even under a waiver.

- **Objective `n/a`** — the work is empty for a code-referenced reason (see
  `n/a` Criteria). This is the only state that requires no user sign-off.

**The line:** vague urgency is not a waiver. A waiver is the user explicitly
electing to skip a *named* step after hearing its cost. When in doubt, ask the
user to confirm the waiver explicitly — do not infer one from pressure.

## Artifact-Substance Bar

Invoking a skill is necessary but not sufficient — the artifact must reflect it:

- A test that asserts nothing about the change (`expect(true).toBe(true)`, a
  bare `expect(component).toBeTruthy()` with no behavioral assertion) does not
  satisfy `angular-tester`.
- Empty or name-echoing TSDoc does not satisfy `angular-tsdoc`.
- Hand-editing `package.json` after "invoking" `angular-package-manager` does
  not satisfy it — use the `npm`/`ng` CLI as the skill prescribes.
- A "review" with no `docs/reviews/` report does not satisfy `angular-reviewer`.

If an artifact misses the bar, the binding is `[!]`, not `[x]`.

## Skill-Invocation Log (Phase 6)

Reproduce each task's checklist, every entry resolved with evidence:

- `[x] <skill> — invoked at <evidence>` — a verifiable ordered turn (e.g.
  "before Write of `order-list.component.ts`"). "Considered"/"applied" is not
  evidence. Invocation AFTER the artifact is `[!]`, not `[x]`.
- `[n/a] <skill> — did not apply (<code-referenced reason>)`.
- `[!] <skill> — NOT invoked` — a violation. `[!]` is **not a shipping path**:
  name it, mark the task INCOMPLETE, STOP, and offer to re-enter Phase 4 to run
  the missing skill's workflow on the artifact. Phase 6 does not complete while
  any `[!]` is present.

## Red Flags — STOP and run the workflow

| Rationalization | Reality |
|---|---|
| "It's trivial / one component — phases & gates are overkill" | Size does not scale the workflow. Run all phases at speed. Gate after each. |
| "Demo in 30 min / I'm in a hurry — one pass, no gates" | Urgency waives nothing (CRITICAL RULE 2). Acknowledge the deadline, keep the gates. |
| "Lead waived the clarification dance" | The 8 points are mandatory, one round-trip each. User waiver is not a valid skip. |
| "Ambiguities aren't blocking — I'll state assumptions instead of asking" | Stating assumptions ≠ clarifying. Present each point and wait for the answer. |
| "I'll batch all phases / ask one combined confirmation" | Batching is a gate violation. One phase → one summary → one wait. |
| "This is a single http.get — `angular-state` isn't needed" | Touching reactive data/state triggers the binding regardless of how simple. Invoke it. |
| "Not a library API, so skip `angular-tsdoc`" | `n/a` only for objectively internal members. Public/exported additions/changes go through it. |
| "User said no tests" | User preference is not a valid `n/a`. Either an objective code-referenced `n/a` exists or `angular-tester` is required; if the user insists, name it as a violation and let them decide. |
| "I'll self-review the diff inline instead of `angular-reviewer`" | Phase 5 requires the `angular-reviewer` sub-agent + `docs/reviews/` report. Inline self-review does not satisfy it. |
| "I'll hand-roll it to avoid adding a package" | Avoidance-driven `n/a` is forbidden. The binding follows the natural shape of the work. |
| "The owner told me to skip it — I'll mark those steps `n/a`" | A waiver is not an `n/a`. Honor an explicit informed waiver if given, but record it as `waived — user instruction`, never `n/a`, never silently. See *Waiver vs. `n/a`*. |
| "They pushed back / 'nobody does this here' — the workflow is waived" | Pushback, urgency, and social proof are not waivers. Only an explicit, informed skip of a *named* step counts. Vague urgency waives nothing — run at speed. |
| "I already know Angular / the skill — invoking is ceremony" | Skills encode project conventions and modern idioms. Knowing ≠ invoking. Invoke it. |
| "The skill was invoked last task" | Invocations do not carry over. Re-invoke per task. |
| "The sub-agent invoked it — covers my own edits" | It does not. Re-invoke before your own follow-up Write/Edit. |
| "I'll log the `Skill(...)` call even though I ran it after the Write" | Evidence must be a real ordered turn. After-the-fact is `[!]`, not `[x]`. |
| "No application project, but I'll skip the App-Run-Check anyway" | Decide it explicitly: run it (or `ng build` the lib), or mark `n/a — library-only`. Don't drop it silently. |

---

For detailed per-phase guidance, see
[references/REFERENCE.md](references/REFERENCE.md).
