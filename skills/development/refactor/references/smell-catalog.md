# Smell Catalogue (Phase 1)

A smell is a *signal*, not a verdict: it says "look here", not "this is wrong". That distinction is
what keeps the report useful — a list of everything that merely looks unusual trains the user to
ignore it. So every finding names its smell from this catalogue, points at `file:line`, and carries
the evidence the smell's row demands. If the evidence cannot be produced, it is not a finding.

The names are the common ones (Fowler / Beck lineage) on purpose: they are shared vocabulary, they
map onto `refactoring-catalog.md`, and they make two reports about different modules comparable.

## Bloaters — things that grew

| Smell | Signal | Evidence required | Usual refactorings |
|---|---|---|---|
| **Long Function** | one function does several things; needs comments to divide itself into sections | line count, and the sections you can name | Extract Function, Replace Temp with Query, Decompose Conditional |
| **Large Class / Module** | many fields or methods with unrelated concerns | the concern groups, each with its members listed | Extract Class, Move Function, Extract Interface |
| **Long Parameter List** | many parameters, several always passed together | the call sites that pass the same cluster | Introduce Parameter Object, Preserve Whole Object |
| **Primitive Obsession** | strings/ints carrying domain meaning, validated repeatedly | the repeated validation or parsing sites | Replace Primitive with Object, Extract Class |
| **Data Clumps** | the same group of values travels together through several signatures | at least three sites with the same group | Introduce Parameter Object, Extract Class |

## Dispensables — things that can go

| Smell | Signal | Evidence required | Usual refactorings |
|---|---|---|---|
| **Duplicated Code** | the same logic in more than one place | **both sites quoted**, plus what differs | Extract Function, Pull Up Method, Form Template Method |
| **Dead Code** | never reached or never called | the reference search you ran — including reflection, DI containers, configuration, string-based lookup, public API surface, test-only use. If the code ships as a library, add that a repository-internal search cannot rule out external consumers | Remove Dead Code |
| **Speculative Generality** | abstraction with exactly one implementation and no caller needing more | the single implementation and the absent second caller | Inline Function, Collapse Hierarchy, Remove Parameter |
| **Comments as Deodorant** | comments explaining *what* convoluted code does | the comment and the code it excuses | Extract Function, Rename, Introduce Assertion |
| **Lazy Element** | a class or function that no longer earns its indirection | its body and its callers | Inline Function, Inline Class |

## Couplers — things that know too much

| Smell | Signal | Evidence required | Usual refactorings |
|---|---|---|---|
| **Feature Envy** | a function uses another object's data more than its own | the accesses, counted per owner | Move Function, Extract Function then Move |
| **Inappropriate Intimacy** | two units reach into each other's internals | the internal accesses in both directions | Move Function/Field, Hide Delegate, Extract Class |
| **Message Chains** | `a.b().c().d()` navigating structure | the chain and its repetitions | Hide Delegate, Extract Function |
| **Middle Man** | a class that only forwards | the ratio of forwarding to real methods | Remove Middle Man, Inline Function |

## Change preventers — things that make edits expensive

| Smell | Signal | Evidence required | Usual refactorings |
|---|---|---|---|
| **Divergent Change** | one unit changes for several unrelated reasons | commits touching it for different reasons (from the hotspot data) | Extract Class, Split Phase |
| **Shotgun Surgery** | one conceptual change forces edits in many units | the set of files a past such change touched | Move Function/Field, Combine Functions into Class |
| **Parallel Inheritance** | adding a subclass here forces one there | the two hierarchies side by side | Move Function/Field, Collapse Hierarchy |

## Conditional complexity

| Smell | Signal | Evidence required | Usual refactorings |
|---|---|---|---|
| **Deep Nesting** | several levels of nested conditionals or loops | the depth and the guard conditions | Replace Nested Conditional with Guard Clauses, Extract Function |
| **Repeated Switch** | the same type-based branch in several places | every occurrence of the branch | Replace Conditional with Polymorphism, Replace Type Code with Subclasses |
| **Complex Boolean** | conditions nobody can read aloud | the expression | Decompose Conditional, Extract Variable |
| **Flag Argument** | a boolean parameter selecting behaviour | the call sites passing literals | Remove Flag Argument (split the function) |

## What is *not* a finding

These look like smells and are not; reporting them costs credibility.

- **Generated code, migrations, vendored code, build output.** Phase 0 removed them from the scope;
  if one reappears, drop it again.
- **Deliberate duplication in tests.** Test readability beats test DRYness — a test that has to be
  read in three places to be understood is worse than three similar tests.
- **Data holders with many fields.** DTOs, records, configuration objects, and API contracts are
  *supposed* to be flat and dumb.
- **Framework-mandated shapes.** Lifecycle methods, required base classes, decorator boilerplate,
  and generated partials cannot be refactored away without breaking the framework contract.
- **Style and formatting.** Naming conventions, import order, and layout belong to a linter or
  formatter, not to a refactoring step — see the "no formatter runs" rule in `SKILL.md`.
- **"I would have written it differently."** Without a named smell and evidence, that is taste, and
  taste is the user's call, not yours.

## Recording a finding

```
R-3 — Duplicated Code
  src/orders/OrderExport.cs:88-121  and  src/reports/ReportExport.cs:45-77
  Evidence: both blocks build the same CSV header and quote the same five fields; they differ only
  in the source collection (lines 92 / 49). Callers: 2 and 1.
  Suggested: Extract Function into a shared formatter — structural, crosses module boundaries.
```

Finding IDs (`R-n`) are assigned here and stay stable through the report, the selection, and the
step log.
