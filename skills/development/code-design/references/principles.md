# Design Principles — Operational

A principle is only useful if you can tell, looking at concrete code, whether it applies. So every
entry here has the same four parts: **what it means** in one sentence, **signals** you can point
at, the **action** it asks for, and the **counter-indication** that says leave it alone. A decision
in the design notes cites the principle *and* has checked its counter-indication.

The principles are stack-agnostic. "Unit" means whatever the language uses to group behaviour: a
class, a module, a file of functions, a component.

## Contents

- [Single Responsibility (SRP)](#single-responsibility-srp)
- [Separation of Concerns (SoC)](#separation-of-concerns-soc)
- [DRY — Don't Repeat Yourself](#dry--dont-repeat-yourself)
- [KISS — Keep It Simple](#kiss--keep-it-simple)
- [YAGNI — You Aren't Gonna Need It](#yagni--you-arent-gonna-need-it)
- [Dependency Inversion and seams](#dependency-inversion-and-seams)
- [Interface Segregation](#interface-segregation)
- [Open/Closed](#openclosed)
- [Composition over inheritance](#composition-over-inheritance)
- [When principles conflict](#when-principles-conflict)

## Single Responsibility (SRP)

**Means:** a unit has one reason to change — one requirement, rule set, or stakeholder whose
changes land in it.

**Signals**
- Its public members fall into groups that share no fields and no dependencies.
- Describing it truthfully takes "and": *validates orders and sends emails and computes tax*.
- Its dependencies serve disjoint subsets of its methods (the mailer is used by two methods, the
  repository by five others).
- Its tests need elaborate setup of dependencies that the behaviour under test never touches.
- Version history: it changes in commits for unrelated reasons.

**Action:** give the new responsibility its own unit; for existing mixed units, extract the group
your change touches (Extract Class) — if covered by tests.

**Counter-indication:** members that change together for the same reason belong together even when
the unit is large. Splitting cohesive logic just to hit a size target scatters one concept across
files. The test is the *reason to change*, not the line count.

## Separation of Concerns (SoC)

**Means:** different kinds of work — domain rules, input/output, orchestration, presentation,
configuration — live in different units, so each can change and be tested without the others.

**Signals**
- A function computes a business rule *and* reads a file, calls HTTP, queries a database, or
  formats output for a user.
- Domain logic reads configuration, environment variables, the clock, or randomness directly.
- Parsing or serialisation is interleaved with the decision that uses the parsed data.
- A presentation unit (controller, component, CLI command) contains business rules.
- An orchestrating unit has a private method that loads facts and decides on them — a rule hiding
  in the orchestration (rule and remedy in `SKILL.md`, Step 2, *A rule stays a rule when it needs
  data*).

**Action:** split the phases — gather input, decide, act. The decision becomes a pure function or a
unit with no I/O; the I/O sits at the edge and passes data in. Pass time, randomness, and
configuration values as parameters or collaborators.

**Counter-indication:** a script or a single thin endpoint whose whole job is I/O with a trivial
rule does not need layers. When the project has no layering at all, do not invent three layers for
one feature — separate the pure decision from the I/O inside the existing structure.

## DRY — Don't Repeat Yourself

**Means:** every piece of *knowledge* — a rule, a format, a calculation, a mapping — has one
authoritative home.

**Signals**
- The logic you are about to write already exists somewhere (search by the domain nouns and verbs
  before writing).
- The same rule is encoded at several sites, and changing the rule would require editing all of
  them.
- Copy-paste-modify: a new variant created by duplicating an existing one and changing a few lines.
- A third occurrence: two similar blocks can be coincidence; three is a pattern (rule of three).

**Action:** reuse the existing home; if none exists, extract one (function, value object,
constant, shared module) and point every site at it. For copy-paste variants, extract the common
skeleton and pass the varying part in.

**Counter-indication:** *coincidental similarity* — two blocks that look the same but encode
different knowledge and would change for different reasons. Merging them couples two concepts; the
first diverging change adds a flag parameter, the second a second flag. Wrong abstraction costs
more than duplication. Test code may repeat setup for readability.

## KISS — Keep It Simple

**Means:** the simplest structure that meets the requirement and the other principles wins.

**Signals of violation**
- A reader following one request from entry to effect passes through units that add nothing.
- Generic machinery (type parameters, reflection, configuration-driven dispatch) for a fixed set of
  cases.
- Cleverness: dense one-liners, unusual language features, where a plain loop or conditional would
  read directly.
- Nesting deeper than about three levels.

**Action:** inline pass-through units, replace generic machinery with direct code, flatten
nesting with guard clauses, prefer the language's plain constructs.

**Counter-indication:** "simple" means simple to understand and change, not fewest files. A
400-line function is not simple because it lives in one place.

## YAGNI — You Aren't Gonna Need It

**Means:** build for the variations that exist or have been asked for, not for imagined ones.

**Signals of violation**
- Options, parameters, hooks, or extension points no caller uses.
- An abstraction justified with "in case we later need to …".
- A plug-in mechanism, registry, or strategy set with exactly one entry.

**Action:** remove the unused flexibility. Write the direct version; when the second variation
arrives, the refactoring is cheap because the code is simple.

**Counter-indication:** things that are expensive to change later *and* are known to be coming —
a public API contract, a persisted data format, a module boundary the architecture defines. Those
deserve design effort now; that is not speculation.

YAGNI is about speculative *variation*, not about the operational qualities an integration
obviously needs. A call to an external system needs a timeout and a defined failure behaviour; an
I/O call that would run once per item, per row, or per request needs a plan for that frequency
(fetch once and pass the result, or cache). Leaving these out does not keep the code simple — it
ships a defect. When the right policy is a business decision (how stale may cached rates be?
show an error or fall back?), implement the simplest safe version and record the policy as a
default the user has not confirmed.

## Dependency Inversion and seams

**Means:** policy (domain rules, use cases) does not depend on detail (HTTP clients, databases,
file systems, frameworks). Where they meet, the policy side owns an abstraction the detail
implements — a *seam* where one side can be replaced.

**Signals**
- Domain logic constructs or imports an HTTP client, database driver, SDK, or file API directly.
- A test of business logic needs a network, a database, or the real clock.
- The same external system is called from several units, each with its own error handling.

**Action (Extract Interface / port):** put an abstraction, named for what the domain needs
(`ExchangeRates`, not `HttpRateClientWrapper`), between the policy and the external system. The
concrete adapter implements it; tests replace it with a fake. Put the abstraction in the policy's
module, not the adapter's.

**Wiring:** construct the concrete adapter where the application is assembled — the entry point,
`main`, the DI registration, the request handler that already creates collaborators — and pass it
in. A default argument or module-level instance of the adapter inside policy or presentation code
re-creates the dependency the seam was meant to remove: the module now imports the adapter, and a
forgotten argument silently goes to the network. Where the codebase has no assembly point and
public signatures must not change, a default is acceptable as a transition — record it in the
design notes as such.

**Counter-indication:** one implementation and no second caller is Speculative Generality. Pure
logic — calculations, validation, mapping — is tested directly and needs no interface in front of
it. If the project's convention is to put interfaces in front of every service, follow the
convention; do not add them where the convention does not ask.

## Interface Segregation

**Means:** a consumer depends only on the operations it uses.

**Signals:** an interface whose implementers throw "not supported" for some members; consumers
that each use a small, different subset of a large interface; test fakes that stub ten members to
exercise one.

**Action:** split along the consumers' needs; a unit may implement several small interfaces.

**Counter-indication:** splitting an interface that has one consumer using all of it adds names and
nothing else.

## Open/Closed

**Means:** a known kind of variation is added by adding code, not by editing a switch in several
places.

**Signals:** the same `if kind == A … elif kind == B …` (or `switch`) repeated at two or more sites;
each new kind requires hunting down every such site.

**Action:** replace the repeated conditional with polymorphism (one implementation per kind) or a
lookup table of behaviours.

**Counter-indication:** a single conditional at a single site, with a closed set of cases, is
simpler than a hierarchy. Open/Closed applies to variation that recurs, not to every branch.

## Composition over inheritance

**Means:** reuse behaviour by holding a collaborator, not by subclassing, unless the subtype is
genuinely substitutable for its base everywhere.

**Signals:** a subclass that overrides a method to do nothing or throw; a base class used only to
share helper methods; a hierarchy deeper than two levels for code reuse.

**Action:** extract the shared behaviour into a collaborator and inject or hold it.

**Counter-indication:** frameworks that require subclassing (base controllers, test base classes,
UI components) — follow the framework.

## When principles conflict

They will. Resolve in this order:

1. **Correctness and the project's architecture** first — a principle never justifies breaking the
   pattern the codebase uses for placement, or behaviour the tests pin down.
2. **Separation of concerns at I/O boundaries** — keeping side effects out of decisions pays off
   in every test you write afterwards.
3. **Single responsibility** for new behaviour.
4. **KISS / YAGNI as the veto** on any abstraction that the first three do not require.
5. **DRY last** — when in doubt between duplication and a premature merge, duplicate and wait for
   the third occurrence.

Record the conflict and its resolution as one row in the design notes.
