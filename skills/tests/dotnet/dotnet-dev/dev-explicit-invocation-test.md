# dotnet-dev — explicit invocation only: the workflow loads only when the user names it

Covers the `description` frontmatter of `skills/dotnet/dotnet-dev/SKILL.md`, the **Explicit
invocation.** paragraph after its Core Principle, the two new rows at the top of the Red Flags
table, the `dotnet-dev` note in the `dotnet` router, and the README `.NET` table row.

Until 2026-09-15 the description was an auto-trigger description: "Use when asked to implement,
extend, or change a feature, user story, requirement, or bug fix in a .NET / C# project — any task
that produces or modifies C# production code, tests, or documentation. Use when a .NET change
request arrives, before writing any code." That is every .NET change request. The workflow it
starts has six confirmation gates and eight one-at-a-time clarification questions and
deliberately has no non-interactive mode (`dev-noninteractive-test.md`), so a request that merely
*resembled* the trigger list turned a two-line fix into an interview the user never asked for.
The decision was to make `dotnet-dev` load only when **the user themselves** names it — `/dotnet-dev`,
"dotnet-dev", "dotnet dev" in the prompt, or the user picking it by name when another skill asks
which skills to use. This is one step stricter than the `development` category
(`skills/tests/development/_shared/explicit-invocation-test.md`), which also accepts a hand-off
from another skill: for `dotnet-dev` a skill, workflow, or orchestrating agent selecting it on the
user's behalf is explicitly *not* an invocation, because the gate and clarification answers are
the user's decisions and nobody else can supply them.

## Why this is not a fixture test

Triggering is decided from the skill list alone, before any file is read. So the test is the
skill list: a fresh sub-agent, no file access, no tools, sees the eleven `skills/dotnet/`
descriptions in the form Claude Code shows them and classifies requests. The pass criterion for
the negatives is "`dotnet-dev` not loaded", not "no skill loaded" — the knowledge skills
(`dotnet-aspnet`, `dotnet-fundamentals`, `dotnet-tester`) are *supposed* to fire on those.

## The probe

Twelve requests, all arriving in a .NET / C# repository. Four must load `dotnet-dev`; eight must
not. The negatives carry the weight: 4–8 are the request shapes the old description listed
verbatim (feature, user story, bug fix, change + tests, one in German), 9 and 11 are orchestrator
dispatches — 11 even names the skill, but the orchestrator is not the user — and 10 is the control
that a neighbouring skill still wins its own case. 12 is the one indirect form that *does* count:
the user picking the skill by name when another skill asked.

| | Request | dotnet-dev? |
|---|---|---|
| 1 | `/dotnet-dev Add a GET /orders/{id} endpoint …` | yes |
| 2 | "run dotnet-dev for this user story: As a customer I want to cancel an order …" | yes |
| 3 | "Please use the dotnet dev workflow to implement the retry policy in PaymentClient." | yes |
| 4 | "Implement a feature: users can export their invoices as PDF. It's a .NET 10 Web API with EF Core and xUnit." | no |
| 5 | "Here's a user story from Jira: '…' Add the endpoint and tests please." | no |
| 6 | "Fix this bug: NullReferenceException in OrderService.GetTotal() …" + stack trace | no |
| 7 | "Ich brauche ein neues Feature in meinem C#-Projekt: Kunden sollen … stornieren können, inklusive Tests." | no |
| 8 | "Change DiscountCalculator so that discounts stack multiplicatively …, and update the existing tests." | no |
| 9 | Sub-agent dispatched by an orchestrator: "Implement task 3 of docs/plans/checkout.md … Use whatever installed skills fit the stack." | no |
| 10 | "Write unit tests for OrderService." | no (`dotnet-tester`) |
| 11 | Sub-agent dispatched by an orchestrator: "Use dotnet-dev to implement the cancel-order feature …" | no |
| 12 | Another skill asked "Which installed skills should I use for the .NET tasks?"; the user replied "dotnet-dev for the implementation tasks, dotnet-tester for the test tasks." | yes |

Harness: one `general-purpose` sub-agent per round, prompt = "do NOT read files, do NOT use
tools" + the eleven descriptions as a `- name: description` list (folded YAML flattened to one
line each) + the requests + "would you load dotnet-dev yes/no; confidence; other skills instead or
alongside; one reason citing the description text; table only". The agent is told to answer from
what the descriptions actually say, not from what it thinks the policy should be. The RED round
ran requests 1–10 only; 11 and 12 were added for GREEN to probe the orchestrator and
user-picks-by-name edges the new description introduces.

## Rounds

**RED — 2026-09-15, old description** (`feature/refine-dotnet-skills` at `1d43319`): 4/10.

| | Loaded | Conf. | Agent's reason (abridged) |
|---|---|---|---|
| 1–3 | yes | high | named directly; and the task is "implement … a feature / user story / change" anyway |
| 4 | **yes** | high | "Use when asked to implement … a feature … Use when a .NET change request arrives" — "no explicit name is required by the text" |
| 5 | **yes** | high | a Jira "user story" asking for "the endpoint and tests" matches "implement … a user story … production code, tests" |
| 6 | **yes** | high | "or bug fix in a .NET / C# project" — a concrete NRE fix |
| 7 | **yes** | high | "language is irrelevant to the description" — a new feature in a C# project with tests |
| 8 | **yes** | high | "extend, or change a feature … modifies C# production code, tests" |
| 9 | **yes** | medium | "implement task 3" is a requirement producing C# code; medium only because the orchestrator "already owns planning/review" |
| 10 | no | medium | `dotnet-tester` matches directly; medium because dotnet-dev's "produces or modifies … tests" overlaps |

All six negatives fired, five at high confidence, each citing a phrase the description listed.
The baseline is not a judgement failure of the agent — the description told it to load. Even the
control (10) was only a medium "no": the old wording's "tests, or documentation" reached into
`dotnet-tester`'s territory.

**Fix.** Description rewritten to the `development` shape with the stricter actor clause: `Use
only when the user themselves explicitly requests it by name — "dotnet-dev", "dotnet dev",
"/dotnet-dev", "run dotnet-dev", "use the dotnet-dev workflow" — for <purpose>.` then `Never
commits.` then `Must NOT activate on its own for "implement this feature", "add an endpoint",
"fix this bug", a pasted user story, or any other .NET change request that does not name the
skill — those are ordinary requests handled with the knowledge skills (dotnet-fundamentals,
dotnet-aspnet, …) as usual.` and, new for this skill, `Must NOT be started by another skill,
workflow, or orchestrating agent on the user's behalf.` The purpose clause names the six phases so
the `/` listing stays informative once the skill *is* named. 844 characters. The body gained an
**Explicit invocation.** paragraph after the Core Principle (with the *why*: gates and
clarification answers are the user's decisions) and two Red-Flags rows ("clearly a .NET feature —
I'll run it anyway", "the orchestrator told me to use it"). The `dotnet` router gained a note
parallel to its `dotnet-reviewer` note; the README row says "(explicit invocation only)". No
`/cc-ai-dev:`-style alias: the `.NET` category is not published as a plugin.

**GREEN — 2026-09-15, new description, requests 1–12:** 12/12, eleven at high confidence.

| | Loaded | Conf. | Agent's reason (abridged) |
|---|---|---|---|
| 1–3 | yes | high | a listed form (`/dotnet-dev`, "run dotnet-dev", "dotnet dev" / "use the dotnet-dev workflow") |
| 4–8 | no | high | each cited the matching *Must NOT activate on its own* entry ("implement this feature", "a pasted user story" + "add an endpoint", "fix this bug", "any other .NET change request that does not name the skill" for the German and the DiscountCalculator requests); loaded `dotnet-fundamentals` + `dotnet-aspnet` / `dotnet-ef-core` / `dotnet-tester` instead |
| 9 | no | high | skill not named, and "Must NOT be started by another skill, workflow, or orchestrating agent" |
| 10 | no | high | `dotnet-tester` is the exact match; dotnet-dev "requires the user to name it" — the RED overlap is gone |
| 11 | no | high | "although 'dotnet-dev' is named, … an orchestrator's prompt is not the user" |
| 12 | yes | **low** | the user named it, but "the launcher would be the other skill, which brushes against 'Must NOT be started by another skill … on the user's behalf' … worth clarifying in the description" |

All eight negatives held, including the orchestrator that names the skill (11). The one soft spot
was the user-picks-by-name form (12): correct answer, low confidence, and the agent pointed at the
exact clause that made it hesitate.

**Follow-up fix, same day.** The actor clause gained its exception: `Must NOT be started by
another skill, workflow, or orchestrating agent on the user's behalf; the user picking it by name
when another skill asks which skills to use does count as the user requesting it.` Request 13
added: an orchestrator dispatch that *claims* "the user asked for dotnet-dev" with no user message
in the sub-agent's context — the relayed-claim edge. Expected `no`: the dispatcher is speaking,
not the user, and such a run has no user channel (`dev-noninteractive-test.md`).

**GREEN 2 — 2026-09-15, requests 1, 4, 9, 11, 12, 13:** 6/6.

| | Loaded | Conf. | Agent's reason (abridged) |
|---|---|---|---|
| 1 | yes | high | `/dotnet-dev` is a listed form |
| 4, 9 | no | high | not named; 9 also cited "Must NOT be started by … orchestrating agent" |
| 11 | no | medium | the name appears, "but it is the orchestrating agent naming it, not 'the user themselves'"; medium because "the orchestrator might be relaying a user choice the prompt does not show" |
| 12 | yes | **high** | "the description explicitly covers this case" — the new exception clause |
| 13 | no | **low** | correct on the literal text; low because the agent believed the carve-out "plainly intends this relay to succeed" |

12 moved from low to high on the exception clause. 11 and 13 are the two orchestrator forms and
both held; their lower confidence is the agent second-guessing whether a relay *should* count,
not a reading of the text that lets it count. The relay case therefore got its own sentence in
the body's **Explicit invocation.** paragraph — "a dispatch prompt that *says* 'the user asked
for dotnet-dev' is still the dispatcher speaking, not the user" — with a pointer to the
Precondition section, which is the second line of defence: even a sub-agent that loads the skill
stops at Gate 1 with the `Blocked — interactive user required` handoff. The description itself
stayed as it was; adding the relay sentence there would have pushed it over the validator's
900-character warning.

**Trim, same day.** The description was at 954 characters (validator warning at 900). The
purpose clause lost its phase adjectives ("eight-point", "mandatory … skill bindings", "code
review", "final") and the knowledge-skill parenthetical went: 876 characters, no warning. Trigger
wording untouched.

**GREEN 3 — 2026-09-15, final description (876 chars), all 13 requests:** 13/13, twelve at high
confidence.

| | Loaded | Conf. | Agent's reason (abridged) |
|---|---|---|---|
| 1–3 | yes | high | a listed form, cited verbatim each time |
| 4–8 | no | high | the matching *Must NOT activate on its own* entry; 7 (German) and 8 fell to "any other .NET change request that does not name the skill" |
| 9, 11 | no | high | "Must NOT be started by another skill, workflow, or orchestrating agent"; 11: "although the prompt names the skill, it comes from an orchestrating agent" |
| 10 | no | high | `dotnet-tester` fits, "nothing names dotnet-dev" |
| 12 | yes | high | "the user picking it by name when another skill asks … does count" — "exactly this exchange" |
| 13 | no | medium | "a relayed claim is that case, though the description does not spell out relayed requests" |

The trimmed purpose clause cost nothing: every answer that was high in GREEN 2 stayed high, and
11 rose from medium to high. 13 remains the only non-high answer and is correct on the text; the
body paragraph now spells out the relay case for the run that does load the skill, and the
Precondition section blocks it at Gate 1 regardless. Requests 9, 11, 12, and 13 are load-bearing
for the actor clause and its exception — remove or reword either sentence and re-run before
merging.

## Re-run when

- the `dotnet-dev` description changes, including adding an alias;
- the **Explicit invocation.** paragraph or the two Red-Flags rows are removed or reworded;
- the `.NET` category is published as a plugin (the plugin-namespaced alias must be added to the
  description, the body paragraph, and the router note, and the probe needs a request using it);
- `angular-dev` is switched to the same rule — its probe should reuse these twelve shapes
  (family parity, see `CLAUDE.md`);
- another `skills/dotnet/` description is changed to overlap with implementation requests — the
  probe only shows that `dotnet-dev` does not fire, not that something else does (see
  `_shared/description-selection-test.md` for the family-wide selection probe).
