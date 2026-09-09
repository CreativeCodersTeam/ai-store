# EF Core Bullet Actionability Test (Finding E-1)

Test artifact per `superpowers:writing-skills` (RED → GREEN → REFACTOR → Verify)
for the 2026-07-22 fix of Finding E-1 in
`docs/reviews/2026-07-21-dotnet-skills-review.md`: `dotnet-ef-core/SKILL.md`
contained non-actionable truism bullets ("Use appropriate change tracking
strategies", "Use appropriate query operators", "Implement appropriate data
access permissions", "Be careful with raw SQL queries", "Use meaningful
primary keys", plus the same-pattern "Implement appropriate navigational
properties") that gave an agent no decision criterion.

## Method

A fresh general-purpose subagent rates each bullet: (a) what concrete,
checkable action does it prescribe, (b) could a reviewer cite it to flag a
violation, (c) is anything technically wrong or overgeneralized?

## RED — Baseline (old bullets), 2026-07-22

0 of 6 actionable, 0 of 6 flaggable. Verdict, verbatim:

> these bullets transfer essentially no EF Core knowledge. Each one names a
> topic area … and then delegates the entire decision back to the reader via
> "meaningful," "appropriate" (x4), and "careful." … They function as a table
> of contents for advice that was never written, not as guidance.

## GREEN — Rewritten bullets, 2026-07-22

All six replaced with concrete, flaggable rules: surrogate-key default with a
natural-key exception criterion; navigations only for traversed relationships;
`Where`/`OrderBy`/`GroupBy` before materialization; tracking only on write
paths (`AsNoTracking` / `AsNoTrackingWithIdentityResolution`); least-privilege
app DB account with separate migration identity; raw SQL only parameterized
with the `FromSqlRaw($"…{userInput}")` injection example.

## Verify + REFACTOR — 2026-07-22

Re-probe: 6/6 prescribe checkable actions, 6/6 flaggable with concrete
hypothetical violations, none technically wrong. Two soft caveats triggered a
REFACTOR round: bullet 3's absolute "never" lacked an escape hatch for
untranslatable predicates (now: "restructure the query instead of
materializing early"), and bullet 6 risked wrongly flagging safe
parameterized `FromSqlRaw` and omitted EF Core 7+ `FromSql` (both now named).
Verifier follow-up: "Yes, both caveats are resolved."

Out of scope (not part of E-1): "Add data seeding through migrations when
appropriate" (Migrations section) and "Use appropriate DbContext lifetimes
(scoped for web apps)" — the latter already carries a concrete criterion.

## Result

Every E-1 bullet now transfers a checkable rule instead of deferring to reader
judgment; one REFACTOR round. Re-run this probe whenever bullets in
`dotnet-ef-core/SKILL.md` are added or reworded.

---

# M-4 Round — the remaining stock (2026-08-03)

Second half of the same arc: Finding M-4 in
`docs/analysis/2026-08-02-dotnet-skills-review.md` named four vague "Consider …"
bullets plus a duplicated security bullet, and closed with "der Rest-Bestand
sollte nachgezogen werden". Scope this round: **all 8 sections**, every bullet
E-1 did not already fix.

## RED — Baseline, 2026-08-03

29 candidate bullets (`scratchpad/red-m4-bullets.txt`). The four M-4 names —
"Consider using transactions for multiple operations", "Consider database
functions for complex operations", "Consider snapshot testing for model
changes", "Consider data encryption for sensitive information" — plus:

- **Duplication**, the defect M-4 called out for security: "Use parameterized
  queries to prevent SQL injection" (line 71) restated the precise raw-SQL
  bullet two lines below it. A second instance was found during the sweep and
  is not in M-4's text: "Use AsNoTracking() for read-only queries"
  (Performance) restated the more precise tracking rule in Change Tracking.
- **A contradiction M-4 did not name:** "Use migrations to manage database user
  permissions" (line 75) against "no DDL rights for the app user; migrations
  run under a separate, privileged deployment identity" (line 72). Resolved in
  favour of 72 — grants belong in ops/DDL scripts. Separation of duties is the
  durable reason; the first draft's justification ("would encode principal
  names into the model's history") was itself wrong and was corrected in
  REFACTOR 1, since raw SQL in a migration never enters the model snapshot.
- **Advice that was questionable, not merely vague:** the specifications
  pattern and compiled queries, both stated as unconditional goods.

## GREEN — first attempt, 2026-08-03

All 29 rewritten to rule → condition → consequence in the E-1 voice; the two
duplications removed; overlapping `Include`/N+1 bullets merged. Transaction
depth moved to a new `references/transactions.md`, because the old bullet did
not merely under-specify — it contradicted the `SaveChanges`-once-per-unit-of-work
rule two lines above it, `SaveChanges` being atomic already.

## Verify — probe 1, 2026-08-03

Two fresh subagents, passage only, no file access: one auditing 27 bullets for
actionability + technical correctness, one fact-checking `transactions.md`.

**Actionability: target met.** 26/27 actionable, 25/27 flaggable — E-1 parity.

**Correctness: failed.** ~16 bullets carried something wrong, dated, or
overgeneralized. Verbatim: *"roughly a 60% defect rate on the technical claims.
The conclusions are mostly right; the justifications are where this document is
rotten, and justifications are what reviewers quote in arguments."* Worst:

1. `dotnet ef migrations add --dry-run` **does not exist**, and
   `has-pending-model-changes` is EF Core **8**, not 9 — the drift-check bullet
   would have broken any pipeline that used it.
2. The one-context-per-database rationale was fabricated: several contexts over
   one database are supported and routine, each with its own
   `MigrationsHistoryTable`.
3. `EF.Functions.Contains` is SQL Server **full-text** `CONTAINS`, not
   collection containment.
4. `ComplexProperty` recommended beyond its EF 8/9 capability (no nullable, no
   collections, no separate table).
5. SQLite table-rebuild data loss is pre-EF-Core-5; `CREATE INDEX CONCURRENTLY`
   cannot run inside EF's migration transaction without `suppressTransaction`.
6. The `Cascade`/`Restrict` sentence was incoherent — `Restrict` deletes nothing.

Plus three internal contradictions: Q "no `IQueryable` past the boundary" vs. Q
"specifications are a net loss" (leaving no sanctioned way to share a filter);
specifications-for-testability vs. the mocking bullet's own argument; and a
schema-only restore claimed to catch data-dependent migration failures.

**`transactions.md` failed on its flagship example.** The retry pattern reused
the outer `DbContext` across attempts — after a rollback the tracker still holds
`Unchanged` entities with store-generated keys for rows that were never
committed, so the retry inserts explicit identity values or duplicates. The
document taught the footgun it existed to prevent. Also: "exactly three cases"
was contradicted by its own cross-context section four headings down;
`UseTransaction` across different connections throws rather than escalating to a
distributed transaction; and `ReadCommitted` *does* take shared locks on SQL
Server's default locking mode.

## REFACTOR 1 — 2026-08-03

All of the above corrected. `transactions.md` substantially rewritten: fresh
context per attempt via `IDbContextFactory`, commit-ambiguity and
`ExecuteInTransactionAsync(operation, verifySucceeded)`, six cases instead of
three, the discard-the-context-after-rollback rule, `TransactionScope`'s
`Serializable` default, and the .NET 7+/Windows/MSDTC qualifier on
`PlatformNotSupportedException`.

## Verify — probe 2, 2026-08-03

Fresh subagent, adversarial re-check of the corrected text. **All nine version
and API claims verified CORRECT** (`has-pending-model-changes` EF 8+,
`UseSeeding` EF 9+, `ExecuteUpdate`/`ExecuteDelete` EF 7+, SQLite rebuild since
EF 5, EF 9 migration lock, `suppressTransaction` overload, `EF.Functions.Contains`
as full-text, convention delete behaviour). Both flagged contradictions
**resolved**, and the specifications/mocking pair now mutually reinforcing.

Four **new** errors introduced by the corrections — overcorrections, not
leftovers:

- `ComplexProperty` "no accidental sharing between owners" is backwards: having
  no identity is exactly why EF permits two owners to reference one CLR
  instance. Owned types are the ones that fail on sharing.
- Scoping the `ComplexProperty` limits to "EF 8/9" implied EF 10 lifted
  nullability, which it did not.
- "Data is preserved since EF Core 5" was promoted from a SQLite fact to a
  general one — blunting the exact review the bullet asks for, since on SQL
  Server a rename scaffolded as `DropColumn` + `AddColumn` does lose data.
- `Restrict` presented as uniquely causing the database to refuse; on SQL Server
  `Restrict` and `NoAction` emit the same DDL.

Four further residual imprecisions: an escaped `IQueryable` *throws* rather than
being enumerable post-dispose; shadow FKs are writable via
`Entry(e).Property(…)`; `AsSplitQuery` costs 1 + N round trips, not N; the EF 9
migration lock retires only the race objection, not the other four reasons not
to call `Database.Migrate()` at startup.

Actionability gaps: TDE exposition, the compiled-query "measured hot path"
criterion, and the one-context-per-bounded-context judgement were not things a
reviewer can cite from a diff.

## REFACTOR 2 — 2026-08-03

All eight correctness items fixed. The three unciteable bullets rewritten to
name an observable condition: TDE → "do not accept TDE as an answer to *this
column is sensitive*"; compiled queries → "no benchmark or justifying comment"
and "not stored in a field outliving the call"; contexts → "a second context
added without its own history table and `--context`". `ExecuteUpdate`/
`ExecuteDelete` gained the tracker/interceptor-bypass caveat at the point of
recommendation.

## Result

29 bullets carry checkable rules; two duplications and one security
contradiction removed; transaction depth single-sourced to
`references/transactions.md`. Two REFACTOR rounds — the first because the
rewrite was *actionable but factually wrong*, which is the more dangerous
failure: E-1's bullets deferred judgment, M-4's first draft asserted confidently
and incorrectly, and a reviewer quotes the justification.

Re-run **both** probes whenever these bullets or `transactions.md` change, and
re-check the version-gated claims (EF 8/9/10 feature availability) when the
family's target framework moves — they are the parts that go stale.

---

# Structural Split (2026-08-03) — also closes N-1

The M-4 sweep left `SKILL.md` at ~2900 words against peers at 379–508, and
Finding **N-1** already recorded the same defect from the other direction:
`dotnet-ef-core` held nearly all content in `SKILL.md` while
`dotnet-aspnet`/`dotnet-fundamentals` hold it in `references/`.

All eight sections moved into `references/` **verbatim** — the bullets had been
probe-verified twice and were not re-edited in the move. `SKILL.md` was rebuilt
to the `dotnet-fundamentals` archetype: When to Use + 12 Core Principles +
Reference Index + Related Skills, 772 words.

New: `model-design.md`, `querying-and-performance.md`, `migrations.md`,
`change-tracking.md`, `security.md`, `testing.md`, joining the existing
`concurrency-control.md` and `transactions.md`.

## Verify — probe 3, 2026-08-03

The risk this split creates is specific: compressing 49 verified bullets into 12
one-line principles is exactly how the E-1 truisms were born. A fresh subagent
was given the 12 principles, told about the historical failure mode, and asked
per principle whether it *prescribes* or *defers*.

**No regression: 0 of 12 defer, 12 of 12 flaggable** — the verifier constructed a
concrete offending line of C# for every one. On principle 6, the direct
descendant of E-1's "Use appropriate change tracking strategies": *"it now names
the API."*

Content preservation checked mechanically: all 49 distinctive bullet phrases
from the pre-split `SKILL.md` are present in `references/`.

## REFACTOR 3 — 2026-08-03

Compression damaged five principles, all repaired:

- **N+1 (worst).** The compressed line implied N+1 persists when lazy loading is
  off and that the failure is always silent. Both wrong: without lazy loading
  there is no N+1, and a `null` reference navigation throws loudly. The headline
  "in one round trip" also read as a ban on `AsSplitQuery()`, the recommended fix
  for the adjacent cartesian-explosion problem. Rewritten around the observable
  act — do not dereference a navigation inside a loop over parents — with the
  remedy named. The full bullet in `querying-and-performance.md` was already
  correct and was not touched.
- **`SaveChanges` atomicity** — qualified "on a relational provider" (not true on
  Cosmos) and linked to the concurrency-token principle, since atomicity is not
  isolation and a reader could otherwise think one covers the other.
- **In-Memory provider** — the stated reason ("enforces no constraints") was both
  too strong (it does enforce PK uniqueness) and missed the decisive one (not a
  relational store, so untranslatable queries pass). Corrected in the principle
  **and** in `testing.md`, where the imprecision predated M-4.
- **Fluent API** — "no rule is ever expressed twice" was unfalsifiable; now "no
  property configured by both an attribute and the fluent API".
- **`IQueryable`** — "compose shared filters inside the layer" had no decidable
  test; now "no public member returns `IQueryable<T>`".

Cheap additions from the same probe: the script command on the migration-review
principle, `EnsureCreated()` beside `Database.Migrate()`, and the replacement
named where a principle was purely prohibitive.

## Result

`SKILL.md` 2900 → 772 words, in line with the family. Nine references, each
loadable on its own. N-1 closed. Re-run probe 3 whenever the Core Principles are
reworded — that section is a compression of rules verified elsewhere, and
compression is where this skill has now twice introduced errors.
