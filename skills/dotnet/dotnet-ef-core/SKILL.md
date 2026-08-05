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

## Core Principles

The non-negotiables. Each is stated in full, with the reasoning and the edge cases, in the reference
named beside it — load that file when the work touches its area.

- **A `DbContext` is scoped and not thread-safe** — one instance per request or per `IServiceScope`; never shared across concurrent operations. When the consumer outlives a scope (Blazor Server, singletons, background loops), take a context per operation from `AddDbContextFactory<T>` or `IServiceScopeFactory`. → [model-design.md](references/model-design.md)
- **Mapping lives in the fluent API**, in `IEntityTypeConfiguration<T>` classes — keys, indexes, column types, relationships. EF attributes stay off domain entities, and no property is configured by both an attribute and the fluent API. → [model-design.md](references/model-design.md)
- **Set delete behaviour explicitly** on every relationship. Convention gives required relationships `Cascade`, so one left unconfigured silently takes its children with it. → [model-design.md](references/model-design.md)
- **Never let an `IQueryable` escape the data-access layer** — no public member returns `IQueryable<T>`; materialize at the boundary and return a list or a DTO. Share filters as internal `Expression<Func<T, bool>>` constants rather than by exposing the query. → [querying-and-performance.md](references/querying-and-performance.md)
- **Do not dereference a navigation inside a loop over parents.** With lazy loading that is one query per parent (N+1). Without it, a collection navigation may be partly filled by change-tracker fixup, so the loop computes a silently wrong total instead of failing. Fix by pushing the aggregate into SQL, or `Include` when the entities themselves are needed. → [querying-and-performance.md](references/querying-and-performance.md)
- **Track only on write paths** — `AsNoTracking()` on read paths, or a `Select` projection where the entity itself is not needed. → [change-tracking.md](references/change-tracking.md), [querying-and-performance.md](references/querying-and-performance.md)
- **One `SaveChanges()` per unit of work.** On a relational provider it is already atomic, so do not wrap a single save in an explicit transaction. Atomicity is not isolation — a read-then-write still needs the concurrency token below. → [change-tracking.md](references/change-tracking.md), [transactions.md](references/transactions.md)
- **Add a concurrency token wherever two users can edit the same row**; without one the second save silently overwrites the first. → [concurrency-control.md](references/concurrency-control.md)
- **Review every migration as generated SQL before it reaches production** (`dotnet ef migrations script --idempotent`), and never edit one already applied anywhere but your own machine. → [migrations.md](references/migrations.md)
- **The application's database account has no DDL rights** — so no `Database.Migrate()` or `EnsureCreated()` at startup (apply migrations as a deployment step instead), and grants live in ops scripts, not migrations. → [security.md](references/security.md), [migrations.md](references/migrations.md)
- **Raw SQL only parameterized** — `FromSqlInterpolated`, or `FromSqlRaw` with `{0}` placeholders. `FromSqlRaw($"…{userInput}")` is SQL injection. → [security.md](references/security.md)
- **Never the In-Memory provider for tests** — it is not a relational store, so queries run as LINQ-to-Objects and expressions a real provider cannot translate pass anyway; foreign keys, unique indexes, and check constraints go unenforced. Use SQLite in-memory for speed, Testcontainers for fidelity. → [testing.md](references/testing.md)

## Reference Index

- **[model-design.md](references/model-design.md)** — `DbContext` scope and registration, `IEntityTypeConfiguration`, keys, foreign keys and delete behaviour, navigations, owned types vs. `ComplexProperty`
- **[querying-and-performance.md](references/querying-and-performance.md)** — materializing at the boundary, LINQ vs. raw SQL, `EF.Functions`, the specifications pattern, pagination, N+1, cartesian explosion and `AsSplitQuery`, projections, compiled queries
- **[change-tracking.md](references/change-tracking.md)** — tracking on write paths, unit of work and `SaveChanges`, when a concurrency token is required
- **[concurrency-control.md](references/concurrency-control.md)** — `[Timestamp]`, `[ConcurrencyCheck]`, provider-specific row-version types, `DbUpdateConcurrencyException` handling
- **[transactions.md](references/transactions.md)** — when an explicit transaction is actually required, the retrying-execution-strategy rule, sharing a transaction across contexts, `TransactionScope` caveats
- **[migrations.md](references/migrations.md)** — naming, never editing an applied migration, reviewing the SQL, concurrent index builds, deployment via bundles, seeding
- **[security.md](references/security.md)** — least-privilege database accounts, raw-SQL parameterization, column encryption and what TDE does not cover, grant management
- **[testing.md](references/testing.md)** — SQLite in-memory vs. Testcontainers, why not to mock `DbSet`, migration testing in CI, model-drift detection

## Related Skills

- **[dotnet-fundamentals](../dotnet-fundamentals/SKILL.md)** — DI lifetimes for `DbContext`, Options pattern for connection strings, modern C# idioms used in entity types
- **[dotnet-tester](../dotnet-tester/SKILL.md)** — Use for DbContext-backed unit and integration tests (SQLite in-memory, Testcontainers; see [testing.md](references/testing.md))
- **[dotnet-nuget-manager](../dotnet-nuget-manager/SKILL.md)** — Use when adding EF Core providers, Testcontainers, or SQLite packages

The full skill overview lives in the `dotnet` router skill.
