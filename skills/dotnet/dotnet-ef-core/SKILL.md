---
name: dotnet-ef-core
description: Use when designing a DbContext, entities, or relationships, writing LINQ queries against EF Core, creating or reviewing migrations, implementing concurrency control or repository patterns, setting up EF Core tests, or troubleshooting N+1 and other query performance issues.
---

# Entity Framework Core Best Practices

## When to Use

- Designing or restructuring a `DbContext`, entities, or relationships
- Writing LINQ queries against EF Core, or troubleshooting N+1 / performance issues
- Creating, naming, or reviewing EF Core migrations
- Implementing concurrency control, repository patterns, or change tracking strategies
- Setting up EF Core tests with SQLite in-memory or Testcontainers

## Data Context Design

- Several `DbContext` classes over one database are fine and routine (an Identity context beside a domain context) — but each one needs its own history table (`o.UseSqlServer(cs, x => x.MigrationsHistoryTable("__EFMigrationsHistory_Billing"))`) and its own `--context` argument on every `dotnet ef` command. A second context added without both is the defect to look for. Scope contexts to bounded contexts, not to features or aggregates
- Take `DbContextOptions<T>` in the constructor and pass it to `base` — never read configuration or build a connection string inside the context. Register with `AddDbContext<T>(o => o.UseX(connectionString))`; the connection string itself comes from configuration (see [`dotnet-fundamentals`](../dotnet-fundamentals/references/configuration.md))
- Put mapping in `IEntityTypeConfiguration<T>` classes, one per entity, applied with `modelBuilder.ApplyConfigurationsFromAssembly(typeof(AppDbContext).Assembly)` in `OnModelCreating`. A growing `OnModelCreating` body with inline `modelBuilder.Entity<X>(…)` calls for every entity is the thing this replaces
- A `DbContext` is not thread-safe and must not be shared across concurrent operations — EF's second-operation detection catches many cases but is best-effort, so the failure mode ranges from an exception to a corrupted change tracker
- When the consumer's lifetime does not match a scope, get a context per operation: `AddDbContextFactory<T>` for Blazor Server components (which outlive a request) and for parallel work, or `IServiceScopeFactory.CreateScope()` in an `IHostedService`/background loop. Factory-created contexts are the caller's to dispose. In a normal scoped web request, inject the context directly

## Entity Design

- Default to surrogate keys (`int`/`Guid` `Id`); use a natural key only when it is immutable and unique by domain rule (e.g. an ISO country code)
- Declare the foreign-key property explicitly (`public int CustomerId { get; set; }`) rather than letting EF create a shadow FK — a shadow FK has no CLR property, so it cannot be set in ordinary code or referenced in LINQ without `EF.Property<int>(…)` / `Entry(e).Property("CustomerId")`
- Set delete behaviour explicitly with `.OnDelete(…)` on every relationship. Convention gives **required** relationships `Cascade` and optional ones `ClientSetNull`, so a relationship that should have refused the delete silently takes its children with it. `Restrict` and `NoAction` both leave the database to refuse (on SQL Server they emit the same `ON DELETE NO ACTION` DDL and differ only in EF's in-memory fixup); `SetNull` needs an optional FK
- Configure persistence concerns (keys, indexes, column types, precision, delete behaviour, relationships) in the fluent API; keep EF attributes off domain entities so the domain does not reference infrastructure — `dotnet-reviewer` flags this (`review-checklist-architecture.md`). Data annotations that are genuinely domain statements (`[Required]` mirroring non-nullability, `[MaxLength]` mirroring a business rule) are acceptable in a persistence-model class, but never mix both styles for the same rule: the fluent API wins and the annotation becomes a lie
- Add navigation properties only for relationships the code actually traverses — every navigation invites an `Include()` and widens the change-tracking graph
- Map a value object as an owned type (`OwnsOne`/`OwnsMany`) when it has no identity of its own in the domain and is never queried independently — an `Address` on a `Customer`, not a `Product`. If you need to query it standalone, it is an entity, not a value object. Note that EF still tracks an owned type as an entity internally, so the same instance must not be assigned to two owners (see the next bullet)
- `ComplexProperty` (EF Core 8+) maps the same shape with no tracked identity at all, which removes the duplicate-tracking failure owned types have. Its limits are real: it cannot be nullable, has no collection form, and cannot map to a separate table — check the current release before assuming any of these have lifted. Use it for a non-nullable single value object stored in the owner's table; stay on owned types for everything else

## Performance

- Paginate large result sets with `Skip()`/`Take()` — always paired with a deterministic `OrderBy` (unique key as tie-breaker, e.g. `.OrderBy(p => p.Name).ThenBy(p => p.Id)`); for large offsets prefer keyset pagination over the sort key (Id-ordered list: `.Where(p => p.Id > lastSeenId).OrderBy(p => p.Id).Take(n)`; composite sorts need a composite predicate)
- Load related data the query actually touches in **one** round trip. The N+1 signature is a loop over parent entities that dereferences a navigation inside the body (`foreach (var o in orders) total += o.Lines.Sum(…)`). With lazy loading that is one query per parent. Without it the result is worse than obvious: relationship fixup populates the navigation from whatever the context already happens to track, so the total is silently **wrong** rather than zero. Best fix is to push the aggregate into SQL (`Select(o => new { o.Id, Total = o.Lines.Sum(l => l.Amount) })`); `Include` only if the entities themselves are needed
- Watch for cartesian explosion when one query `Include`s two or more **collection** navigations: the single-SQL join multiplies rows (10 lines × 10 payments = 100), multiplicatively with each further collection. `AsSplitQuery()` trades that for 1 + N round trips (the base query plus one per collection) — worth it when both collections are large, not when one has two rows or the connection is high-latency. Split queries are no longer a single atomic snapshot, and `Skip`/`Take` in one without a deterministic `OrderBy` returns **incorrect** results. `UseQuerySplittingBehavior` sets the default globally
- Project to a DTO with `Select` whenever the full entity is not needed — it moves column selection into the SQL and needs no `AsNoTracking()`, because there is no entity to track. The exception that catches people: a projection whose members are themselves entity types (`new Dto { Customer = x.Customer }`) *is* tracked, giving you the cost of both. When you genuinely need whole entities on a read path, `AsNoTracking()` is still the right tool (`AsNoTrackingWithIdentityResolution()` when the graph repeats an entity)
- Treat an `EF.CompileAsyncQuery` with no benchmark or justifying comment as unjustified, and one not stored in a field outliving the call (`static readonly` is the idiom) as a bug — recompiling per call is strictly worse than not compiling. EF already caches the plan for every query shape, so the win is limited to the cache lookup and expression-tree work: real on trivial high-frequency queries, negligible on anything substantial. The cost is permanent — a compiled query cannot be composed further, so no conditional `Where` and no paging tacked on

## Migrations

- One migration per logical schema change, named `VerbNoun` after what it does (`AddOrderShippedAt`, `RenameCustomerEmailColumn`) — not `Update1` or a timestamp restatement. The name is what a reviewer reads in the migrations folder and in the schema history table
- Never edit a migration that has been applied anywhere but your own machine — the schema history records that it ran, so the edit is invisible to every database that already has it. Add a follow-up migration instead. Re-scaffolding (`migrations remove` + `migrations add`) is only safe while the migration is still unapplied and unpushed
- Read the generated SQL before it reaches production: `dotnet ef migrations script --idempotent`. The thing to hunt for is silent data loss — a property rename or type change that EF scaffolded as `DropColumn` + `AddColumn` discards every value in that column, and it looks unremarkable in the C# migration. Also check for dropped tables and for index creation on large tables. (SQLite is the exception: since EF Core 5 its table rebuilds are create-copy-drop-rename and preserve data, though the table is locked for the duration.) Idempotent scripts break on statements that must start their own batch (`CREATE VIEW`, `CREATE PROCEDURE`)
- Building an index concurrently needs `migrationBuilder.Sql("CREATE INDEX CONCURRENTLY …", suppressTransaction: true)` — PostgreSQL refuses `CONCURRENTLY` inside a transaction and EF wraps migrations in one. SQL Server's `ONLINE = ON` is available on Azure SQL and Enterprise; `RESUMABLE = ON` needs the same `suppressTransaction` treatment
- Do not call `Database.Migrate()` at application startup. It forces the app's runtime account to hold the DDL rights the Security section says it must not have; nobody reviews the SQL before it runs; there is no rollback path; startup blocks on DDL; and in a rolling deploy the old version keeps serving traffic against the new schema. (EF Core 9 added a database-level migration lock where the provider implements one, so the concurrent-startup race is the one objection that has softened.)
- Apply migrations as a deployment step instead. `dotnet ef migrations bundle --self-contained -r <RID>` produces a single executable for targets with no SDK and no sources; it still needs a connection string at run time
- Seed only static reference data (lookup tables, enum-backed rows) via `HasData` — it requires fixed primary keys, and every change to seeded values generates a new migration. Anything environment-specific, generated (`DateTime.Now`, `Guid.NewGuid()`), or dependent on other data belongs in a seeding routine that runs after migration — `UseSeeding`/`UseAsyncSeeding` (EF Core 9+) is the named home for it

## Querying

- Materialize at the data-access boundary; return a list or a DTO, not `IQueryable<T>`. A query executes when enumerated (`ToList`/`ToArray`/`First`/`Single`/`Count`/`Any`, a `foreach`, or `await` on the async form), so an escaped `IQueryable` invites enumeration after its `DbContext` is disposed — failing with `ObjectDisposedException` at a call site that never mentioned EF — and puts query cost in the hands of callers who cannot see the SQL. Compose shared filters *inside* the layer with private `IQueryable` helpers or reusable `Expression<Func<T, bool>>` constants
- Express queries in LINQ; drop to raw SQL only for what EF cannot translate — provider hints, recursive CTEs, `MERGE`, window functions, vendor-specific operators. Set-based bulk updates and deletes are **not** on that list: use `ExecuteUpdate`/`ExecuteDelete` (EF Core 7+) — but know that they run immediately, bypass the change tracker, and skip any `SaveChanges` override or interceptor, so audit stamping and soft-delete logic do not fire. When you do write raw SQL, the parameterization rule in the Security section applies without exception
- Push filtering, ordering, and grouping into the database — apply `Where`/`OrderBy`/`GroupBy` before materialization; do not call `ToList()` and then filter in memory (if a predicate is untranslatable, restructure the query instead of materializing early)
- Use the built-in `EF.Functions.*` primitives before writing SQL — they translate and stay composable. `Like` is relational-general; `DateDiffDay`, `Contains`, and `FreeText` are SQL Server-provider methods with no equivalent elsewhere. `EF.Functions.Contains`/`FreeText` map to SQL Server's full-text `CONTAINS`/`FREETEXT` and need a full-text index — they are **not** collection containment; for that use plain `list.Contains(x)`, which translates to `IN`
- Map a database function with `HasDbFunction` only when the logic must run server-side over a set too large to materialize and cannot be expressed in LINQ. The function has to exist in the database — create it in a migration — and the C# method is a translation stub whose body conventionally throws
- Add the specifications pattern only when the same filter/include combination is genuinely reused across call sites. For a CRUD app it is a net loss: it re-implements a subset of `IQueryable` with less composability, and the "reusable" specification usually ends up used once. It is not a testing tool — evaluating a specification's predicate in memory proves nothing about whether EF can translate it (see the mocking bullet under Testing)

## Change Tracking & Saving

- Track entities only on write paths; use `AsNoTracking()` for read paths and `AsNoTrackingWithIdentityResolution()` when the same entity may appear multiple times in the result graph
- Accumulate related changes and call `SaveChanges()` once per unit of work — not once per entity, and never concurrently on the same `DbContext` (it is not thread-safe). Deliberate exception: very large bulk operations may save in chunks of N entities (with `ChangeTracker.Clear()` between chunks), wrapped in an explicit transaction if atomicity matters
- Add a concurrency token to any entity where two users can edit the same row between load and save — without one the second save silently overwrites the first on every column it changed, with no exception and no audit trail. Append-only and single-writer tables do not need one
- In a disconnected flow (load in one request, save in the next) the token on the entity is not enough: it must be round-tripped to the client and restored as the **original** value before saving (`entry.Property(e => e.RowVersion).OriginalValue = posted.RowVersion`), and the resulting `DbUpdateConcurrencyException` must be handled. Details in [concurrency-control.md](./references/concurrency-control.md)
- Do not wrap a single `SaveChanges()` in an explicit transaction — it is already atomic across every entity in the batch. Reach for `BeginTransaction` only to span **multiple** `SaveChanges()` calls, to mix EF writes with raw SQL (`ExecuteUpdate`/`ExecuteDelete` run immediately and are not covered by a later save), or to hold a read stable until the write. Under a retrying execution strategy this must go through `CreateExecutionStrategy().ExecuteAsync(…)` or EF throws — see [transactions.md](./references/transactions.md)
- `DbContext` is scoped — one instance per request or per `IServiceScope`, registered via `AddDbContext<T>`. See [`dotnet-fundamentals`](../dotnet-fundamentals/references/dependency-injection.md) for the lifetime rules and for why injecting it into a singleton is a captive dependency

### Concurrency Control

See [concurrency-control.md](./references/concurrency-control.md) for `[Timestamp]`, `[ConcurrencyCheck]`, fluent API configuration, and `DbUpdateConcurrencyException` handling patterns.

### Transactions

See [transactions.md](./references/transactions.md) for when an explicit transaction is actually required, the retrying-execution-strategy rule, sharing a transaction across contexts, and why `TransactionScope` is not the default.

## Security

- Run the application under a least-privilege database account — no DDL rights for the app user; migrations run under a separate, privileged deployment identity
- Raw SQL only via `FromSqlInterpolated` (EF Core 7+: `FromSql`) or `FromSqlRaw` with `{0}`-placeholders plus parameter arguments — never string concatenation; `FromSqlRaw($"…{userInput}")` is SQL injection
- Do not accept TDE as an answer to "this column is sensitive" — it encrypts the files at rest and defends against a stolen backup or disk, and nothing else. A compromised application or a privileged DBA reads the values unchanged. Columns that need protection *from* the database need a column-level mechanism: SQL Server Always Encrypted, whose deterministic mode still supports equality and indexing (randomized supports neither)
- An EF value converter is the fallback when the provider offers nothing, and its failure mode is silence rather than an error. Equality **does** translate (EF converts the parameter), so `Where(x => x.Ssn == value)` compiles, runs, and — with a random IV — matches nothing. `OrderBy` and range comparisons also translate, and sort or compare the **ciphertext**. `LIKE` usually fails to translate outright, and no index on that column is useful. Restrict converters to columns you only ever read back whole. Connection strings and key material are configuration secrets, not model concerns — see [`dotnet-fundamentals`](../dotnet-fundamentals/references/configuration.md)
- Grant management (`GRANT`, `CREATE USER`, role membership) belongs in ops/DDL scripts, not in EF migrations. Principal names differ per environment, so a `migrationBuilder.Sql("GRANT …")` either hardcodes one environment or grows conditionals; and separation of duties is the point — who may access the data is an operations decision with its own review path, not something that ships inside an application artifact

## Testing

- Avoid the EF Core In-Memory provider for tests — it does not enforce constraints, referential integrity, or transactions, so tests can pass while real database behavior fails
- Use **SQLite in-memory mode** for lightweight unit and integration tests that need realistic SQL semantics:
  ```csharp
  var connection = new SqliteConnection("DataSource=:memory:");
  connection.Open();
  var options = new DbContextOptionsBuilder<AppDbContext>()
      .UseSqlite(connection)
      .Options;
  ```
- Use **Testcontainers** for integration tests that must match production database behavior (e.g., PostgreSQL, SQL Server):
  ```csharp
  var container = new PostgreSqlBuilder().Build();
  await container.StartAsync();
  var options = new DbContextOptionsBuilder<AppDbContext>()
      .UseNpgsql(container.GetConnectionString())
      .Options;
  ```
- Mock `DbContext`/`DbSet` only where no query executes — a mocked `DbSet` is a LINQ-to-Objects queryable, so it happily evaluates predicates the real provider cannot translate and gives a passing test for code that throws in production (and it needs a hand-written `IAsyncQueryProvider` before `ToListAsync` works at all). If the test asserts on query results, use a real provider
- Prefer Testcontainers against the production engine for anything behavioural. SQLite in-memory is a compromise, not an equal: collation and case sensitivity, `decimal` ordering, date functions, and schema support all differ, so it has its own class of false confidence
- Apply migrations in CI against a throwaway database twice: from empty, and from a restored copy of production **with data** (anonymized or subsetted). Only the second catches the data-dependent failures — a new `NOT NULL` column without a default, a unique index over rows that already collide. A schema-only restore cannot catch either
- Fail the build on undeclared model drift: `dotnet ef migrations has-pending-model-changes` (EF Core 8+) exits non-zero when the model no longer matches the last migration. Before EF Core 8, add a throwaway migration in CI, assert its `Up`/`Down` bodies are empty, then remove it. This catches the entity change someone made without generating the migration
- Use the `dotnet-tester` skill for generating unit and integration tests after schema changes

## Related Skills

- **[dotnet-fundamentals](../dotnet-fundamentals/SKILL.md)** — DI lifetimes for `DbContext`, Options pattern for connection strings, modern C# idioms used in entity types
- **[dotnet-tester](../dotnet-tester/SKILL.md)** — Use for DbContext-backed unit and integration tests (SQLite in-memory, Testcontainers; see Testing section)
- **[dotnet-nuget-manager](../dotnet-nuget-manager/SKILL.md)** — Use when adding EF Core providers, Testcontainers, or SQLite packages

The full skill overview lives in the `dotnet` router skill.
