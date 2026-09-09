# Refactoring Catalogue (Phase 5)

A step is one entry from this list, applied at one site. Naming the refactoring is not ceremony: the
name fixes the intended shape of the change *before* it is made, which is what lets the user approve
it and what makes "the diff is bigger than the plan" a detectable mistake.

Each entry says what has to be true before, and what verification actually proves afterwards. The
**class** column decides the gate: `local` runs through the normal step approval, `structural` is an
architecture decision and needs the user's explicit yes (see Principle 3 in `SKILL.md`).

## Composing methods

| Refactoring | Precondition | Watch out for | Class |
|---|---|---|---|
| **Extract Function** | the extracted block has one clear responsibility and few inputs | variables written in the block and read after it — they must become return values, not shared state | local |
| **Inline Function** | the body says as much as the name | callers relying on the name for readability; recursion | local |
| **Extract Variable** | a subexpression needs a name | evaluation order and side effects in the expression | local |
| **Replace Temp with Query** | a temp is computed once from stable inputs | cost of recomputation; inputs that change between uses | local |
| **Split Phase** | one function first prepares data, then acts on it | the intermediate structure becomes a real contract | local |
| **Remove Flag Argument** | a boolean parameter selects between two behaviours | every call site must be updated; a public signature makes it structural | local / structural |

## Simplifying conditionals

| Refactoring | Precondition | Watch out for | Class |
|---|---|---|---|
| **Decompose Conditional** | the condition or branches are hard to read | short-circuit evaluation must be preserved | local |
| **Replace Nested Conditional with Guard Clauses** | one path is the normal one, the rest are exits | changing the order of exits can change which one wins | local |
| **Consolidate Conditional Expression** | several conditions lead to the same action | only valid when the conditions are truly independent of order | local |
| **Introduce Special Case / Null Object** | callers repeatedly check for the same special value | every caller must be found, or a check quietly disappears | structural |
| **Replace Conditional with Polymorphism** | the same type-based switch appears repeatedly | this creates types and a hierarchy — a design decision | structural |

## Moving things

| Refactoring | Precondition | Watch out for | Class |
|---|---|---|---|
| **Rename (variable, function, field, class)** | the current name misleads | internal rename is local; a public or serialized name is a contract change | local / structural |
| **Move Function / Field** | it is used more by the other unit than by its own | dependency direction between layers; DI registration and configuration | structural |
| **Extract Class** | one class carries two responsibilities | shared mutable state between the two halves | structural |
| **Inline Class** | a class no longer earns its existence | external references, serialization, DI registration | structural |
| **Hide Delegate** | callers navigate a chain to reach a delegate | the wrapper must not grow into a Middle Man | local |
| **Remove Middle Man** | a class only forwards | callers now depend on the delegate — that is a coupling decision | structural |

## Data and parameters

| Refactoring | Precondition | Watch out for | Class |
|---|---|---|---|
| **Introduce Parameter Object** | the same values travel together | the new type becomes part of the signature — structural if public | local / structural |
| **Preserve Whole Object** | a caller unpacks an object only to pass its parts | it widens what the callee can reach | local |
| **Replace Primitive with Object** | a primitive carries domain rules | serialization, equality, persistence mapping | structural |
| **Encapsulate Field / Collection** | callers mutate internal state directly | a returned mutable collection is still a leak | local / structural |
| **Extract Interface** | several implementations or a seam for tests is needed | one implementation and no second caller is Speculative Generality | structural |

## Removing

| Refactoring | Precondition | Watch out for | Class |
|---|---|---|---|
| **Remove Dead Code** | the reference search found nothing | reflection, DI, configuration, string lookup, public API, tests, other repositories | local / structural |
| **Remove Unused Parameter** | no caller supplies a meaningful value | overrides, interface implementations, public signatures | local / structural |
| **Collapse Hierarchy** | a subclass adds nothing | external references to the removed type | structural |

## What verification actually proves

Green tests after a step do not prove the refactoring was correct — they prove that *the behaviour
the tests describe* did not change. Two blind spots follow, and both belong in the report rather
than in silence:

- **Uncovered branches stay uncovered.** A refactoring of a path no test enters is unverified, no
  matter how green the suite is. That is why Phase 4 asks per candidate, not per scope.
- **Compilation is not equivalence.** For renames and moves, a green build proves the references
  were updated. It says nothing about reflective or string-based access, which no compiler sees.
  When such access is plausible in this stack, search for the old name as a *string* too, and
  record that you did.

## Step sizing

If a planned step cannot be described in one sentence naming one refactoring and one site, it is
not one step. Split it and present the sequence — the user approves the sequence, then each step
runs and is verified on its own.
