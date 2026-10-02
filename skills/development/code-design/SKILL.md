---
name: code-design
description: >
  Use only when explicitly requested by name — "code-design", "code design", "/code-design",
  "/cc-ai-dev:code-design" — or when another skill or a user-confirmed skill selection loads it by
  name, to write or change production code with a deliberate design pass instead of appending to
  the nearest existing class. Before writing, decides for every new responsibility whether it
  extends an existing unit or gets its own (Single Responsibility, Separation of Concerns); after
  the tests are green, refactors the touched code (Extract Method, Extract Class, Extract Interface
  at real seams, DRY for duplicated knowledge) and checks the result against KISS and YAGNI so it
  does not tip into over-engineering. Stack-agnostic. Reports every design decision with its
  principle and the rejected alternative. Never commits. Must NOT activate on its own for "write
  clean code", "use SOLID", "implement this feature", "clean this up", or any other request that
  does not name the skill.
---

# code-design

Write new code in a shape that a reader can follow and a maintainer can change — by deciding
*where* each piece of behaviour lives before writing it, and tightening the result after it works.

## Contract

- **Input:** a change to production code — a feature, an extension, a behaviour change — plus the
  codebase it lands in. Also works as a rule set loaded by another workflow (see
  [Inside another workflow](#inside-another-workflow)).
- **Output:** the code change with its tests, and a **Design notes** block in the final reply (or
  in the calling workflow's report).
- **Not in scope:** restructuring code the change does not touch (that is the `refactor` skill),
  bug fixes that ride along, performance tuning, style-only reformatting.
- **Never commits.** The user reviews the diff and decides what enters history.

**Explicit invocation.** This skill starts only when it was named — `/code-design`,
`/cc-ai-dev:code-design`, "code-design" in the prompt, or a load by name from another skill or a
skill selection the user confirmed. "Write clean code" or "follow SOLID" in a request is not an
invocation; such a request is handled as an ordinary request without this skill.

## Why this skill exists

An agent extending a codebase feels a strong pull toward the nearest existing class: it is already
imported, already registered, already tested, and adding a method there produces the smallest diff.
Each single step looks harmless. Repeated over twenty changes, it produces the service with 1,500
lines and twelve dependencies that nobody dares to touch.

The smallest diff is not the smallest design. The cost of "just add it here" is paid later, by
every reader of the class and by every test that has to construct all of its dependencies to check
one of its behaviours. This skill moves the decision to the moment it is cheapest: before the first
line is written.

The opposite failure is just as real. An agent told "use SOLID" tends to put an interface in front
of every class, a factory in front of every constructor, and a strategy in front of every `if`.
Indirection that does not pay for itself is also complexity. So the principles here come in pairs
that pull against each other, and the workflow ends with a check against the brakes.

## The principles, and how they pull

Operational definitions — signals, actions, counter-indications — are in
[`references/principles.md`](references/principles.md). The short version:

| Decompose when … | … but stop when |
|---|---|
| **Single Responsibility** — a unit changes for one reason | **KISS** — a split that forces the reader through more files than it saves in understanding |
| **Separation of Concerns** — domain rules, I/O, orchestration, and presentation live apart | **YAGNI** — an abstraction exists for a variation nobody has asked for |
| **DRY** — one piece of *knowledge* has one home | **Coincidental similarity** — two blocks look alike but change for different reasons |
| **Extract Interface / Dependency Inversion** — at a real seam (external system, test double for I/O, plug-in point) | **Speculative Generality** — one implementation and no second caller |
| **Extract Method / Class** — a unit does several things at several levels of abstraction | **Middle Man** — the extracted unit only forwards |

A decision cites a principle from the left column *and* has checked the right one.

## Workflow

```
Step 1  Read the neighbourhood     — the units the change would touch, their size, responsibilities, seams
Step 2  Design pass                — per new responsibility: extend, reuse, or new unit; state the sketch
Step 3  Build it                   — tests first where the project has tests; the shape from Step 2
Step 4  Refactor pass              — after green, on touched code only; one move at a time, tests after each
Step 5  Counter-check              — every abstraction pays rent, or it goes
Step 6  Design notes               — decisions, rejected alternatives, what was left alone
```

### Step 1 — Read the neighbourhood

Before designing, look at the code the change would naturally land in, and at its surroundings:

- **The candidate host(s):** the class, module, or file you would extend by default. Its size, its
  public members grouped by what they do, its dependencies (constructor parameters, imports, module
  globals). A host whose members fall into several unrelated groups already has several
  responsibilities — adding one more makes the eventual split harder, not easier.
- **The project's architecture pattern:** layering, vertical slices, handlers, services and
  repositories, feature folders. Read two or three sibling features. The pattern decides *where*
  things go; the principles decide *how finely* to cut inside it.
- **Existing units that already do part of the job:** helpers, value objects, validators,
  formatters, clients. Search by the nouns and verbs of the requirement. Re-implementing an
  existing helper is the most common DRY violation an agent produces.
- **Seams:** where external systems are called (HTTP, database, file system, clock, randomness,
  message bus) and whether they are already behind an abstraction the tests replace.
- **Test coverage of the host:** which paths of the code you will change or move have tests —
  quote the test per path, and list the paths without one. Step 2 closes those gaps before
  anything is moved.

Keep this short — enough to make the Step-2 decisions with evidence (`file:line`), no more.

### Step 2 — Design pass

**List the responsibilities the change adds**, one line each, before thinking about files. "Add
discount codes" is not one responsibility; it is *parse and validate a code*, *look up a code*,
*compute the discount*, *apply it to an order*, *record the redemption*. The list is what makes
placement decidable.

**Place each responsibility** by asking in order, and stop at the first yes:

1. **Does a unit already exist whose job this is?** Reuse it, extend it inside its responsibility,
   or generalise it if the new use is the same knowledge. (DRY)
2. **Does it share the host's reason to change?** All three must hold: the same requirement or
   stakeholder would change both; it needs no dependency the host does not already have; the host's
   name still describes the host truthfully afterwards. Then extend the host.
3. **Otherwise it gets its own unit**, named after its responsibility, in the layer its concern
   belongs to (domain rule, I/O adapter, orchestration, presentation). The host delegates to it.
   (SRP, SoC)

**A rule stays a rule when it needs data.** A check that decides whether something is allowed —
*this code may be redeemed*, *this order may be cancelled* — is domain logic, even when the facts
it decides on come from storage. The usual slip is a private method on the host that fetches those
facts and decides on them in the same breath, which leaves the new rule inside the class the
change was supposed to keep from growing. Split the two: the host (orchestration) fetches the
facts and passes them in — plain values, not the repository — and the rule unit decides. Passing
values also keeps the dependency pointing from orchestration to rules, which is what removes the
circular import that otherwise argues for keeping the check in the host.

**Heuristics that say a host is already full** — any one of them is reason enough to prefer a new
unit for new behaviour, not a verdict on the existing code:

| Signal | Rough threshold (heuristic, not law) |
|---|---|
| lines in the unit | a few hundred |
| constructor / injected dependencies | more than ~5 |
| public members falling into unrelated groups | two or more groups |
| name needs "And", "Manager", "Helper", "Util" to be truthful | — |
| the new behaviour needs a dependency the host does not have | — |

**Preparatory refactoring** — "make the change easy, then make the easy change" — applies to the
functions your change extends: when the change would land in a function that is already long or
mixes concerns, restructure that function first so the new code has a clean place to go. The
precondition is that every path you move is covered by a test:

- **Covered:** move it.
- **Not covered, but reachable through the public surface:** write **characterization tests**
  first — tests that pin what the code does *today*, including the odd parts, not what it should
  do. Run them green against the unchanged code, then move. They stay in the suite; name them for
  the behaviour, like any other test.
- **Not reachable without heavy setup** (live I/O, global state, no seam): do not move it. Put the
  new behaviour in its own unit next to it and record the gap in the design notes.

A characterization test that fails against the unchanged code has found a bug or a misreading —
stop, do not "fix" either on the side, and report it under *Left alone*.

**State the sketch** before writing code — a few lines in the conversation: the units that will be
created or changed, one sentence of responsibility each, and the dependency direction. Proceed
unless it contains a [decision that belongs to the user](#decisions-that-belong-to-the-user).

### Step 3 — Build it

Follow the project's test conventions: tests first where the project has tests, named and placed
the way sibling tests are. Test new units directly — being testable without constructing the host
is one of the payoffs of the extraction; if a new unit can only be tested through the host, the
split in Step 2 was probably wrong.

Follow the project's conventions for naming, file layout, dependency registration, and error
handling. Conventions decide style; they are not a reason to let a unit grow without bound.

### Step 4 — Refactor pass

Tests are green. Now walk **the diff** — the functions you wrote or changed and the units you
extended — and apply the moves from
[`references/design-moves.md`](references/design-moves.md) where a signal is present:

- **Every function you wrote or changed** works at one level of abstraction and reads top to
  bottom without section comments. Otherwise: Extract Method, Decompose Conditional, guard clauses.
  A function you extended counts as changed *as a whole* — adding three lines to a 50-line
  function and leaving the other 47 as they were is how it got to 50. Paths without coverage get
  characterization tests first, as in Step 2.
- **Duplication:** search the codebase — not only the diff — for the logic you just wrote. The
  same knowledge in two places: reuse or extract. Two similar blocks that change for different
  reasons: leave them.
- **Parameters:** the same group of values travelling through several signatures → parameter
  object. A primitive re-validated at several sites → value object.
- **Branching on a type or kind** at more than one site → consider polymorphism; at one site, the
  conditional is simpler.
- **Names:** every new name says what the thing is or does, in the domain's words.

One move at a time, tests after each; a red test after a move means roll that move back, not fix
forward. Stay inside the change's scope (see [Scope](#scope-what-you-may-restructure)).

### Step 5 — Counter-check

Every abstraction you introduced must pay rent. Go through them and remove or inline what does
not:

- An **interface with one implementation** and no seam behind it (no external system, no test
  double that replaces I/O, no plug-in point, no module boundary the project already enforces).
- A **class that only forwards** to another.
- A **pattern named after a pattern** (Factory, Strategy, Builder, Visitor) serving a single case.
- **Parameters, options, or generics** no caller uses.
- A **DRY merge** of two things that change for different reasons — split it back.
- **Hops:** follow one request from its entry point to its effect. If the path runs through units
  that add nothing a reader needs, collapse them.
- **Wiring:** a concrete adapter constructed inside policy or presentation code (a default
  argument, a module-level instance) — move its construction to where the application is
  assembled, or record why it stays (principles.md, *Dependency Inversion and seams*).

The counter-check removes speculative *abstractions*. It does not remove what an integration
obviously needs to run — a timeout, a failure behaviour, a plan for an I/O call that would
otherwise run once per item. Those are not YAGNI (principles.md, *YAGNI*).

Run the tests once more after this step.

### Step 6 — Design notes

End with this block — in the final reply, or in the calling workflow's report:

```markdown
## Design notes

| # | Decision | Principle | Alternative rejected — why |
|---|---|---|---|
| 1 | `DiscountCalculator` new; `OrderService` delegates | SRP — pricing rules change for marketing, orders for fulfilment | method on `OrderService` — would add its 7th dependency |
| 2 | no interface for `DiscountCalculator` | YAGNI — one implementation, pure logic, tested directly | `IDiscountCalculator` — Speculative Generality |

**Characterization tests:** <paths pinned before moving them, with the test names> | none needed
**Refactor pass:** <moves applied, one line each, with file> | none needed — <why>
**Left alone:** <smells seen in code the change did not touch, and paths that could not be pinned,
file:line — candidates for the `refactor` skill> | none
**Defaults not confirmed by the user:** <decisions taken without an answer> | none
```

A decision that cites no principle, or rejects no alternative, was not a decision — rethink it or
drop the row. "Extended the existing class" is a valid decision when Step 2 said so; it needs its
row like any other.

## Scope: what you may restructure

- **Yes:** the functions you write or change, each as a whole; the part of an existing unit your
  change touches, extracted so your change can land cleanly (preparatory refactoring, covered by
  tests or by characterization tests you write first); new units.
- **No:** units your change does not touch, even when they smell; public signatures of existing
  code without the user's decision; moving existing code across layers, modules, or packages
  without the user's decision. Write what you saw under *Left alone*.

A diff that restructures half the module to add one feature cannot be reviewed as a feature. Keep
the refactoring the feature needed, and hand the rest to the user.

## Decisions that belong to the user

These change contracts or the architecture, and are not yours to settle silently:

- a new or changed **public API** or data contract shape;
- a **pattern the codebase does not use yet** (introducing handlers into a service-based codebase,
  events where calls are used, a new layer);
- a new **project, package, or module**;
- **moving existing code** across a layer or module boundary.

**Interactive:** ask one structured question per decision, recommended option first, grounded in
what Step 1 found. **Non-interactive** (sub-agent, headless run, no one to ask): never stall and
never guess wide — take the most conservative option that still satisfies Step 2 (a new internal
unit inside the existing module, no public API change, no new pattern), and list it under
*Defaults not confirmed by the user*.

## Inside another workflow

When a workflow (an implementation pipeline, a skill selection the user confirmed) loads this
skill, the workflow owns phases, gates, test order, file-scope rules, and reporting. This skill
contributes the design pass before code is written (Steps 1–2), the refactor pass and counter-check
after the tests are green (Steps 4–5), and the design notes, which go into that workflow's task
report. A file created by extracting from a file the task owns is reported the way that workflow
reports any additional file, with the reason "extracted per code-design, decision #n".

## Red flags — stop and re-read

| Thought | Reality |
|---|---|
| "Adding a method to the existing class is the smallest change." | Smallest diff, not smallest design. Run Step 2 — it may still say "extend", but then you know why. |
| "The codebase puts everything in services, so I will too." | The pattern decides *where*; it does not say a service must absorb every new responsibility. |
| "I'll add an interface for testability." | Only if the test must replace I/O or an external system. Pure logic is tested directly. |
| "These two blocks look the same — extract them." | Same knowledge, or same shape by coincidence? Ask what would change each. |
| "While I'm here I'll clean up the whole file." | Touched code only. The rest goes under *Left alone*. |
| "Tests are green, done." | Steps 4–6 are part of done. |
| "This needs a factory and a strategy to be extensible." | Extensible for which variation that someone has asked for? None → YAGNI. |
| "This existing method is untested, but moving it is obviously safe." | Without coverage you cannot show that. Pin it with characterization tests first, then move it. |
| "This part is untested, so I'll leave the long function as it is." | Untested is a reason to write characterization tests, not to stop. Only code you cannot reach without heavy setup stays as it is. |
| "The check is a few lines — a private method on the host is simpler." | It is a new rule in the class you were keeping from growing, and the next rule will join it. The host fetches; the rule unit decides. |
| "I only added three lines to that function." | You extended it, so it is yours as a whole for the refactor pass. |

## References

- [`references/principles.md`](references/principles.md) — each principle as signal, action, and
  counter-indication; read before Step 2 on anything larger than a single function.
- [`references/design-moves.md`](references/design-moves.md) — the moves for Steps 2, 4, and 5:
  when to apply, when not, what to verify.
