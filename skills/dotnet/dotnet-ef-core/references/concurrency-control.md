# Concurrency Control

Row-version concurrency is provider-specific — the CLR type of the version property differs:

**SQL Server** — `byte[]` mapped to a `rowversion` column:

```csharp
public class Order
{
    public int Id { get; set; }
    public string Status { get; set; } = string.Empty;

    [Timestamp]
    public byte[] RowVersion { get; set; } = Array.Empty<byte>();
}
```

**PostgreSQL (Npgsql.EntityFrameworkCore.PostgreSQL 7.0+)** — `uint` mapped to the `xmin` system column (no table column is added; migrations emit nothing for it):

```csharp
public class Order
{
    public int Id { get; set; }

    [Timestamp]
    public uint Version { get; set; }
}
```

On older Npgsql versions use `modelBuilder.Entity<Order>().UseXminAsConcurrencyToken();` instead. A `[Timestamp]` `byte[]` property does NOT give working concurrency on PostgreSQL — nothing ever populates the `byte[]` column.

Use `[ConcurrencyCheck]` to protect individual properties without a row version column:

```csharp
public class Product
{
    public int Id { get; set; }

    [ConcurrencyCheck]
    public decimal Price { get; set; }
}
```

Or configure via fluent API — `IsRowVersion()` applies equally to the `uint` property on Npgsql:

```csharp
modelBuilder.Entity<Order>()
    .Property(o => o.RowVersion)
    .IsRowVersion();

modelBuilder.Entity<Product>()
    .Property(p => p.Price)
    .IsConcurrencyToken();
```

Catch `DbUpdateConcurrencyException` at the call site and implement a retry or conflict-resolution strategy:

```csharp
try
{
    await context.SaveChangesAsync();
}
catch (DbUpdateConcurrencyException ex)
{
    // Reload the entity and resolve the conflict, or inform the user
    await ex.Entries.Single().ReloadAsync();
}
```
