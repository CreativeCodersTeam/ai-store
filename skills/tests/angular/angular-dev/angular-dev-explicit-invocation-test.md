# angular-dev — explicit invocation only: the workflow loads only when the user names it

Covers the `description` frontmatter of `skills/angular/angular-dev/SKILL.md`, the **Explicit
invocation.** paragraph after its Core Principle, the two new rows at the top of the Red Flags
table, the `angular-dev` note in the `angular` router (and the two router sections it replaced),
and the README `Angular` table row.

Until 2026-09-15 `angular-dev` still carried the auto-trigger description its .NET mirror had
already shed: "Use when asked to implement, extend, or change a feature, user story, requirement,
or bug fix in an Angular / TypeScript project — any task that produces or modifies Angular
production code, tests, or documentation. Use when an Angular change request arrives, before
writing any code." That is every Angular change request. The workflow it starts has six
confirmation gates and eight one-at-a-time clarification questions and deliberately has no
non-interactive mode, so a request that merely *resembled* the trigger list turned a two-line fix
into an interview the user never asked for.

This is the family-parity follow-up to
`skills/tests/dotnet/dotnet-dev/dev-explicit-invocation-test.md`, whose *Re-run when* section named
it. The rule adopted is identical: `angular-dev` loads only when **the user themselves** names it —
`/angular-dev`, `/cc-ai-angular:angular-dev`, "angular-dev", "angular dev" in the prompt, or the
user picking it by name when another skill asks which skills to use. A skill, workflow, or
orchestrating agent selecting it on the user's behalf is explicitly *not* an invocation, because
the gate and clarification answers are the user's decisions and nobody else can supply them.

Angular carries one extra burden .NET did not: its router actively routed *into* the workflow. A
`### Orchestration skill` table listed `angular-dev` as a routing target, and an **Arbitration with
`angular-dev`** note said requirement-shaped requests "belong to the `angular-dev` workflow". Both
were removed so the router matches `skills/dotnet/dotnet/SKILL.md`, which never had them
(`git log -S` over that file finds neither string). The interactive-only warning they carried is
not lost: it is canonical in the skill's own *Precondition — Interactive User Required*, and the
replacement note says neither the router nor any other skill or agent starts the workflow.

A third Angular-only passage said the same thing from inside the skill: the **Arbitration with the
other `angular-*` skills** paragraph in *Skill Map — Mandatory Bindings* opened with "this workflow
owns every requirement-shaped request". `dotnet-dev` has no such paragraph. It was reworded rather
than deleted — the binding precedence it describes is still correct *inside* a run — so it now
scopes that ownership to a started run and sends every implementation request that did not name the
workflow to the specialized skills.

## Why this is not a fixture test

Triggering is decided from the skill list alone, before any file is read. So the test is the skill
list: a fresh sub-agent, no file access, no tools, sees the eleven `skills/angular/` descriptions in
the form Claude Code shows them and classifies requests. The pass criterion for the negatives is
"`angular-dev` not loaded", not "no skill loaded" — the knowledge skills (`angular-components`,
`angular-fundamentals`, `angular-tester`) are *supposed* to fire on those.

## The probe

Fourteen requests, all arriving in an Angular / TypeScript repository. Five must load
`angular-dev`; nine must not. They are the thirteen shapes of the .NET probe translated to Angular
(endpoint → route/component, EF Core/xUnit → signals/Vitest), plus 14 for the plugin-namespaced
alias, which the .NET artifact's *Re-run when* demanded once the category ships as a plugin
(`cc-ai-angular`). The negatives carry the weight: 4–8 are the request shapes the old description
listed verbatim (feature, user story, bug fix, change + tests, one in German), 9, 11 and 13 are
orchestrator dispatches — 11 names the skill and 13 *claims* the user asked for it — and 10 is the
control that a neighbouring skill still wins its own case. 12 is the one indirect form that *does*
count: the user picking the skill by name when another skill asked.

| | Request | angular-dev? |
|---|---|---|
| 1 | `/angular-dev Add a lazy-loaded /orders/:id detail route with a resolver.` | yes |
| 2 | "run angular-dev for this user story: As a customer I want to cancel an order from the order list." | yes |
| 3 | "Please use the angular dev workflow to implement the retry policy in PaymentApiService." | yes |
| 4 | "Implement a feature: users can export their invoices as PDF. It's an Angular 21 app with signals and Vitest." | no |
| 5 | "Here's a user story from Jira: '…' Add the component and tests please." | no |
| 6 | "Fix this bug: TypeError: Cannot read properties of undefined (reading 'total') in OrderService.getTotal() …" + stack trace | no |
| 7 | "Ich brauche ein neues Feature in meinem Angular-Projekt: Kunden sollen ihre Bestellung stornieren können, inklusive Tests." | no |
| 8 | "Change DiscountCalculator so that discounts stack multiplicatively …, and update the existing tests." | no |
| 9 | Sub-agent dispatched by an orchestrator: "Implement task 3 of docs/plans/checkout.md … Use whatever installed skills fit the stack." | no |
| 10 | "Write unit tests for OrderService." | no (`angular-tester`) |
| 11 | Sub-agent dispatched by an orchestrator: "Use angular-dev to implement the cancel-order feature …" | no |
| 12 | Another skill asked "Which installed skills should I use for the Angular tasks?"; the user replied "angular-dev for the implementation tasks, angular-tester for the test tasks." | yes |
| 13 | Sub-agent dispatched by an orchestrator: "The user asked for angular-dev to be used for this work. Implement the cancel-order feature." No user message anywhere in context. | no |
| 14 | `/cc-ai-angular:angular-dev implement the invoice export dialog.` | yes |

Harness: one `general-purpose` sub-agent per round, prompt = "do NOT read files, do NOT use tools" +
the eleven descriptions as a `- name: description` list (folded YAML flattened to one line each) +
the requests + "would you load angular-dev yes/no; confidence; other skills instead or alongside;
one reason citing the description text; table only". The agent is told to answer from what the
descriptions actually say, not from what it thinks the policy should be. Both rounds ran all
fourteen requests.

## Rounds

**RED — 2026-09-15, old description** (`feature/refine-dotnet-skills`, working tree before the
change): **6/14**. Of nine negatives, exactly one held.

| | Loaded | Conf. | Agent's reason (abridged) |
|---|---|---|---|
| 1–3 | yes | high | named directly — but 2 and 3 also cited the auto-trigger text ("Use when an Angular change request arrives, before writing any code"), i.e. the name was not doing the work |
| 4 | **yes** | high | "Use when asked to implement, extend, or change a feature… in an Angular / TypeScript project" |
| 5 | **yes** | high | "implement, extend, or change a feature, user story…"; also `angular-components`, `angular-tester` |
| 6 | **yes** | high | "…or bug fix in an Angular / TypeScript project — any task that produces or modifies Angular production code" |
| 7 | **yes** | high | same clause; the German wording changed nothing |
| 8 | **yes** | medium | "implement, extend, or change a feature, user story, requirement, or bug fix" |
| 9 | **yes** | high | "any task that produces or modifies Angular production code" — the orchestrator dispatch read as an ordinary requirement |
| 10 | no | high | `angular-tester`: "Use when asked to create or extend unit tests…"; the only negative that held |
| 11 | **yes** | high | "Explicit instruction 'Use angular-dev to implement the cancel-order feature'" — the orchestrator's words taken as the user's |
| 12 | yes | high | the user's own words |
| 13 | **yes** | high | "Relayed instruction: 'The user asked for angular-dev to be used for this work.'" — the claim believed at face value |
| 14 | yes | high | treated `/cc-ai-angular:angular-dev` as an explicit invocation although the old description listed no alias — right answer, no textual basis |

Eight of nine negatives fired, seven at high confidence, each citing a phrase the description
listed. This is not a judgement failure of the agent — the description told it to load. The two
relay forms (11, 13) are the sharpest: the old text gave the agent no reason to distinguish an
orchestrator from the user, so a dispatched sub-agent would have opened a six-gate interview with
nobody there to answer it.

**Fix.** Description rewritten to the `dotnet-dev` shape: `Use only when the user themselves
explicitly requests it by name — "angular-dev", "angular dev", "/angular-dev",
"/cc-ai-angular:angular-dev" — for <purpose>.` then `Never commits.` then `Must NOT activate on its
own for "implement this feature", "add a component", "fix this bug", a pasted user story, or any
other Angular change request that does not name the skill — those are ordinary requests handled
with the knowledge skills.` then the actor clause with its exception: `Must NOT be started by
another skill, workflow, or orchestrating agent on the user's behalf; the user picking it by name
when another skill asks which skills to use does count as the user requesting it.` 877 characters
(validator warns at 900). Unlike .NET the list carries the plugin alias from the start and drops
"run …"/"use the … workflow", both of which the bare-name forms already cover — GREEN request 2 and
3 test exactly that. The body gained the **Explicit invocation.** paragraph after the Core
Principle, including the relay sentence and the pointer to *Precondition — Interactive User
Required*, and two Red-Flags rows. The router lost `### Orchestration skill` and the **Arbitration**
note and gained the `angular-dev` note; the README row says "(explicit invocation only)".

**GREEN — 2026-09-15, new description, all fourteen requests: 14/14**, thirteen at high confidence.

| | Loaded | Conf. | Agent's reason (abridged) |
|---|---|---|---|
| 1, 2 | yes | high | quoted the trigger list verbatim |
| 3 | yes | high | "the phrase 'angular dev workflow' matches the accepted name form 'angular dev'" — the dropped "use the … workflow" entry is not missed |
| 4–8 | no | high | each cited the matching *Must NOT activate on its own* entry (4: "implement this feature"; 5: "a pasted user story"; 6: "fix this bug"; 7 and 8: "any other Angular change request that does not name the skill"); loaded `angular-components` / `angular-fundamentals` / `angular-tester` instead |
| 9 | no | high | "Dispatched by an orchestrating agent, not the user: 'Must NOT be started by another skill, workflow, or orchestrating agent on the user's behalf'" |
| 10 | no | high | `angular-tester` is the exact match; "angular-dev's gate is not met since the skill is not named" — the RED overlap is gone |
| 11 | no | high | "Even though 'angular-dev' is named, it is the orchestrating agent instructing on the user's behalf" |
| 12 | yes | high | "This is exactly the carve-out: 'the user picking it by name … does count as the user requesting it.'" |
| 13 | no | **medium** | "No actual user message appears in context — only the orchestrating agent's claim — so it cannot be verified as 'the user themselves explicitly request[ing] it by name'" |
| 14 | yes | high | "Exact match to the listed accepted form: '/cc-ai-angular:angular-dev'" |

All nine negatives held, including both relay forms that RED got wrong. 13 is the only non-high
answer and mirrors .NET exactly: correct on the text, hesitant because the description does not
spell out relayed *claims*. That case is covered twice over in the body — the **Explicit
invocation.** paragraph names it, and the *Precondition* section stops such a run at Gate 1 with
the `Blocked — interactive user required` handoff — so the description was left at 877 characters
rather than spending the remaining budget on it.

Requests 9, 11, 12, and 13 are load-bearing for the actor clause and its exception; 2, 3 and 14
are load-bearing for the trimmed trigger list. Remove or reword either and re-run before merging.

## Re-run when

- the `angular-dev` description changes, including adding or dropping a trigger form or alias;
- the **Explicit invocation.** paragraph or the two Red-Flags rows are removed or reworded;
- the `angular` router's `angular-dev` note changes, or a routing table lists `angular-dev` again;
- the `cc-ai-angular` plugin is renamed — request 14 and the alias in the description, the body
  paragraph, and the router note all carry the plugin name;
- `dotnet-dev`'s rule changes — the two are a deliberate mirror (`CLAUDE.md`, *Family parity*), so
  its probe (`skills/tests/dotnet/dotnet-dev/dev-explicit-invocation-test.md`) and this one move
  together;
- another `skills/angular/` description is changed to overlap with implementation requests — the
  probe only shows that `angular-dev` does not fire, not that something else does.
