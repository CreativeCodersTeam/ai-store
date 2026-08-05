# Testing EF Core Code

- Avoid the EF Core In-Memory provider for tests. The decisive reason is that it is not a relational store: queries execute as LINQ-to-Objects, so an expression the real provider cannot translate succeeds in the test and throws in production, and string comparison, collation, and case semantics differ. It also leaves foreign keys, unique indexes, check constraints, and max-length unenforced, and ignores transactions (primary-key uniqueness is the one thing it does check) — so a test can pass against data the real database would have rejected
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
- For integration tests that exercise the database **through the HTTP surface** (endpoint + pipeline + DI + auth), swap the provider inside a `WebApplicationFactory` — the factory/auth/service-override patterns are owned by the `dotnet-aspnet` skill, `references/testing.md`; the provider choice above stays authoritative here
