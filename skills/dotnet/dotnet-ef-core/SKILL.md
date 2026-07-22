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

- Keep DbContext classes focused and cohesive
- Use constructor injection for configuration options
- Override OnModelCreating for fluent API configuration
- Separate entity configurations using IEntityTypeConfiguration
- Consider using DbContextFactory pattern for console apps or tests

## Entity Design

- Use meaningful primary keys (consider natural vs surrogate keys)
- Implement proper relationships (one-to-one, one-to-many, many-to-many)
- Use data annotations or fluent API for constraints and validations
- Implement appropriate navigational properties
- Consider using owned entity types for value objects

## Performance

- Use AsNoTracking() for read-only queries
- Implement pagination for large result sets with Skip() and Take()
- Use Include() to eager load related entities when needed
- Consider projection (Select) to retrieve only required fields
- Use compiled queries for frequently executed queries
- Avoid N+1 query problems by properly including related data

## Migrations

- Create small, focused migrations
- Name migrations descriptively
- Verify migration SQL scripts before applying to production
- Consider using migration bundles for deployment
- Add data seeding through migrations when appropriate

## Querying

- Use IQueryable judiciously and understand when queries execute
- Prefer strongly-typed LINQ queries over raw SQL
- Use appropriate query operators (Where, OrderBy, GroupBy)
- Consider database functions for complex operations
- Implement specifications pattern for reusable queries

## Change Tracking & Saving

- Use appropriate change tracking strategies
- Batch your SaveChanges() calls
- Implement concurrency control for multi-user scenarios (see below)
- Consider using transactions for multiple operations
- Use appropriate DbContext lifetimes (scoped for web apps)

### Concurrency Control

See [concurrency-control.md](./references/concurrency-control.md) for `[Timestamp]`, `[ConcurrencyCheck]`, fluent API configuration, and `DbUpdateConcurrencyException` handling patterns.

## Security

- Use parameterized queries to prevent SQL injection
- Implement appropriate data access permissions
- Be careful with raw SQL queries
- Consider data encryption for sensitive information
- Use migrations to manage database user permissions

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
- Mock DbContext and DbSet only for pure unit tests that do not execute queries
- Test migrations in isolated environments
- Consider snapshot testing for model changes
- Use the `dotnet-tester` skill for generating unit and integration tests after schema changes

## Related Skills

- **[dotnet-fundamentals](../dotnet-fundamentals/SKILL.md)** — DI lifetimes for `DbContext`, Options pattern for connection strings, modern C# idioms used in entity types
- **[dotnet-tester](../dotnet-tester/SKILL.md)** — Use for DbContext-backed unit and integration tests (SQLite in-memory, Testcontainers; see Testing section)
- **[dotnet-nuget-manager](../dotnet-nuget-manager/SKILL.md)** — Use when adding EF Core providers, Testcontainers, or SQLite packages

The full skill overview lives in the `dotnet` router skill.
