# EF Core Concurrency Provider Test (Finding E-4)

Test artifact per `superpowers:writing-skills` (RED → GREEN → REFACTOR → Verify)
for the 2026-07-23 fix of Finding E-4 in
`docs/reviews/2026-07-21-dotnet-skills-review.md`:
`dotnet-ef-core/references/concurrency-control.md` claimed "[Timestamp] for
automatic row-version concurrency (SQL Server / PostgreSQL with `rowversion`
or `xmin`)" over a `byte[] RowVersion` example — implying the SQL-Server-only
pattern works on PostgreSQL.

## Method

Adversarial fact-check probes (same subagent for RED and follow-up verify),
no tools — provider-behavior knowledge checks.

## RED — Baseline fact-check (old text), 2026-07-23

- (a) SQL Server example: correct (canonical `byte[]`/`rowversion` pattern).
- (b) On Npgsql, `[Timestamp] byte[]` "does not work as written … a broken
  model: inserts/updates expect a database-generated value that never arrives
  … It is not a functioning row-version mechanism on PostgreSQL under any
  Npgsql version." Correct pattern confirmed: `uint` mapped to the `xmin`
  system column — `[Timestamp] public uint Version` / `IsRowVersion()` since
  provider 7.0, `UseXminAsConcurrencyToken()` before.
- (c) The parenthetical rated "**Wrong (not merely misleading)** … correct
  for exactly one of the two named scenarios" — `xmin` is a 32-bit xid whose
  CLR mapping is `uint`, and PostgreSQL has no `rowversion` type at all.

## GREEN — Rewritten section, 2026-07-23

Provider-split intro ("the CLR type of the version property differs"); the
`byte[]` example scoped to **SQL Server** (initializer made version-proof:
`Array.Empty<byte>()`); new **PostgreSQL** snippet with `[Timestamp] uint`
(system column, no migration output); pre-7.0 `UseXminAsConcurrencyToken()`
fallback; explicit warning that `[Timestamp] byte[]` yields no working
concurrency on PostgreSQL. Remainder of the file unchanged.

## Verify + REFACTOR — 2026-07-23

Follow-up fact-check: "The new section is technically correct … all accurate
— confidence high." Two precision nits adopted via REFACTOR: the version gate
named precisely ("Npgsql.EntityFrameworkCore.PostgreSQL 7.0+" — the EF
provider, not the ADO.NET package, gates the feature), and the unchanged
fluent snippet clarified to apply equally to the `uint` property on Npgsql.
`[ConcurrencyCheck]` and `DbUpdateConcurrencyException` sections confirmed
provider-neutral and consistent.

## Result

The reference no longer implies the SQL Server pattern works on PostgreSQL;
both providers have a correct, version-annotated pattern. Re-run the
fact-check whenever this section or the provider versions it names change.
