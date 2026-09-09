# EF Core SaveChanges/Pagination Ambiguity Test (Finding E-3)

Test artifact per `superpowers:writing-skills` (RED → GREEN → REFACTOR → Verify)
for the 2026-07-22 fix of Finding E-3 in
`docs/reviews/2026-07-21-dotnet-skills-review.md`: two ambiguous bullets in
`dotnet-ef-core/SKILL.md` — "Batch your SaveChanges() calls" (multiple
incompatible readings) and "Implement pagination for large result sets with
Skip() and Take()" (no deterministic-ordering requirement).

## Method

A fresh general-purpose subagent enumerates readings of bullet 1 (including
whether `Task.WhenAll` over per-item `SaveChangesAsync` is a compatible
reading) and implements page 3/pageSize 50 exactly per bullet 2, then judges
determinism and technical correctness.

## RED — Baseline (old bullets), 2026-07-22

- Bullet 1: four plausible readings enumerated; the intended one ("call once
  per unit of work") is grammatically the *least* literal — "the bullet fails
  precisely where it matters: the one reading it most literally licenses
  [`Task.WhenAll` over per-item saves on a shared context] is the one that
  crashes" (`DbContext` is not thread-safe).
- Bullet 2: exact-wording implementation has no `OrderBy`; result
  nondeterministic; EF's `RowLimitingOperationWithoutOrderByWarning` and SQL
  Server's `ORDER BY (SELECT 1)` placeholder documented. Verdict: "50 products
  that are not reliably 'page 3' of anything."

## GREEN — Rewritten bullets, 2026-07-22

Bullet 1: "Accumulate related changes and call `SaveChanges()` once per unit
of work — not once per entity, and never concurrently on the same `DbContext`."
Bullet 2: `Skip`/`Take` always paired with deterministic `OrderBy` (unique-key
tie-breaker example) plus a keyset-pagination pointer.

## REFACTOR — triggered by verify round 1, 2026-07-22

The verifier found a technical error **introduced by the GREEN edit itself**:
the keyset example `Where(p => p.Id > lastSeenId).Take(n)` lacked `OrderBy` —
nondeterministic, violating the bullet's own rule — plus a sort-key
composability gap and a prohibition-by-omission of the legitimate chunked-save
pattern. Fixes: keyset example now `.Where(...).OrderBy(p => p.Id).Take(n)`
labeled as the Id-ordered case with "composite sorts need a composite
predicate"; bullet 1 gained the explicit carve-out (chunks of N with
`ChangeTracker.Clear()`, explicit transaction if atomicity matters).

## Verify — Final state

Verifier follow-up: "(1) Resolved … (2) Resolved adequately for bullet scope …
(3) Resolved … No remaining technical errors." Residual notes, accepted as
non-defects: no worked composite-keyset example (depth trade-off) and no
statement that concurrent saves across *separate* contexts are fine (minor
missing clarification).

## Result

Both bullets now have exactly one reading each, and the crash-prone literal
reading of the old wording is explicitly banned. One REFACTOR round — notable
because the tester caught a bug in the fix itself. Re-run this probe whenever
these bullets change.
