# Transactions & Unit of Work

## `SaveChanges()` is already a transaction

On a relational provider, a single `SaveChanges()` / `SaveChangesAsync()` call is atomic: EF opens a
transaction for the duration of the save (default `AutoTransactionBehavior.WhenNeeded` — skipped only
when the save is one command, which is trivially atomic anyway) and rolls back on failure. Wrapping
one save in `BeginTransaction` is not just redundant — under a retrying execution strategy it throws:

```csharp
// Redundant, and throws outright if EnableRetryOnFailure is configured
await using var tx = await context.Database.BeginTransactionAsync();
context.Orders.Add(order);
context.OrderLines.AddRange(lines);
await context.SaveChangesAsync();
await tx.CommitAsync();
```

**Where the guarantee does not hold:** Cosmos (no transactions at all — a failure part-way leaves
earlier writes committed), the InMemory provider, MySQL/MariaDB MyISAM tables, an ambient
`TransactionScope` or externally supplied transaction (atomicity belongs to whoever owns it), and
`AutoTransactionBehavior.Never`.

## When you need an explicit transaction

1. **Multiple `SaveChanges()` calls that must succeed or fail together** — typically because a
   generated key from the first save is needed to build the second batch.
2. **EF writes mixed with raw SQL.** `ExecuteUpdate`/`ExecuteDelete` bypass the change tracker and
   execute immediately, so a later `SaveChanges()` does not cover them — but they *do* enlist in an
   open `Database.CurrentTransaction`, which is what makes this work. They also leave the tracker
   stale: entities already loaded still hold pre-update values. For Dapper on the same connection you
   must pass both `context.Database.GetDbConnection()` and `GetDbTransaction()` explicitly; nothing
   is picked up ambiently.
3. **Sharing one transaction across two `DbContext` instances** (see below).
4. **Enlisting in an externally supplied ADO.NET transaction** via `UseTransaction` — the standard
   integration-test pattern: begin, run the test, roll back.
5. **A non-default isolation level**, for any reason.
6. **Savepoints** — `CreateSavepointAsync`/`RollbackToSavepointAsync` require a user transaction.

For "this row must not change between my read and my write", an explicit transaction is usually the
wrong tool. Raising the isolation level does not by itself take the lock you want (SQL Server needs
`UPDLOCK`/`HOLDLOCK`, PostgreSQL needs `SELECT … FOR UPDATE`, and PostgreSQL `Serializable` raises
40001 serialization failures you must catch and retry). Prefer **optimistic concurrency** — see
[concurrency-control.md](./concurrency-control.md).

```csharp
await using var tx = await context.Database.BeginTransactionAsync();

context.Orders.Add(order);
await context.SaveChangesAsync();           // order.Id generated here

foreach (var line in lines) line.OrderId = order.Id;
context.OrderLines.AddRange(lines);
await context.SaveChangesAsync();

await context.Database.ExecuteSqlInterpolatedAsync(
    $"UPDATE Inventory SET Reserved = Reserved + {order.Quantity} WHERE Sku = {order.Sku}");

await tx.CommitAsync();
```

Disposing an uncommitted transaction rolls it back, so no explicit rollback call is needed.

**After a rollback, discard the `DbContext`.** The change tracker still believes the first save
succeeded — those entities are `Unchanged` and hold store-generated keys for rows that no longer
exist. Reusing that context produces inserts with explicit identity values or duplicated rows.
(EF Core 6+ takes a savepoint before each `SaveChanges` inside a user transaction and rolls back to
it on failure, which limits but does not eliminate this.)

Keep transactions short. `BeginTransaction` pins a pooled connection and holds locks for the whole
block — no HTTP calls, no user prompts, no `Task.Delay` inside one. Nested `BeginTransaction` throws;
check `Database.CurrentTransaction` if an interceptor or decorator may have started one.

## The retrying-execution-strategy trap

With `EnableRetryOnFailure()` configured (standard for cloud SQL — Azure SQL and managed instances;
optional on-prem, where it can mask genuine failures), EF **throws** on `BeginTransaction`:

> `InvalidOperationException`: The configured execution strategy 'SqlServerRetryingExecutionStrategy'
> does not support user-initiated transactions. Use the execution strategy returned by
> `DbContext.Database.CreateExecutionStrategy()` to execute all the operations in the transaction as
> a retriable unit.

It throws eagerly, whether or not a transient error ever occurs, and also on `UseTransaction` and on
ambient `TransactionScope` enlistment. Hand the whole unit to the strategy:

```csharp
var strategy = context.Database.CreateExecutionStrategy();

await strategy.ExecuteAsync(async () =>
{
    // A fresh context per attempt. The previous attempt's rollback left the old one
    // with Unchanged entities holding keys for rows that were never committed —
    // retrying on it inserts explicit identity values or duplicates.
    await using var ctx = await contextFactory.CreateDbContextAsync();
    await using var tx = await ctx.Database.BeginTransactionAsync();

    var order = BuildOrder(request);          // rebuild the graph from source data
    ctx.Orders.Add(order);
    await ctx.SaveChangesAsync();

    ctx.OrderLines.AddRange(BuildLines(request, order.Id));
    await ctx.SaveChangesAsync();

    await tx.CommitAsync();
});
```

Reusing the outer `context` here — the obvious-looking version — is the most common way this pattern
is written wrong. If a factory is not available, `ChangeTracker.Clear()` at the top of the delegate
and rebuild the graph from source data; never carry entity instances in from outside.

The delegate must be **idempotent**: it can run more than once. Non-transactional side effects
(sending mail, publishing an event, writing a file) go after a successful commit — or, if losing them
on a crash is unacceptable, into an outbox table written inside the same transaction.

**Commit ambiguity.** If the connection drops after `CommitAsync` is sent but before the
acknowledgement arrives, the strategy retries a unit that already committed. Where a double-apply
matters, use `ExecuteInTransactionAsync(operation, verifySucceeded)` and have `verifySucceeded` look
for a marker row written inside the transaction.

Do not assume deadlocks (SQL Server 1205) or PostgreSQL 40001 are treated as transient — the built-in
detector lists differ by provider and version. Verify before relying on it.

## Sharing a transaction across contexts

Both contexts must be on the **same `DbConnection`** — construct the second one over the first one's
connection, then pass the transaction:

```csharp
using Microsoft.EntityFrameworkCore.Storage;   // for GetDbTransaction()

var options = new DbContextOptionsBuilder<OtherDbContext>()
    .UseSqlServer(context.Database.GetDbConnection())
    .Options;

await using var other = new OtherDbContext(options);
await using var tx = await context.Database.BeginTransactionAsync();
other.Database.UseTransaction(tx.GetDbTransaction());
```

Passing a transaction from a *different* connection does not escalate to a distributed transaction —
`UseTransaction` simply throws `InvalidOperationException`.

## `TransactionScope` — prefer not to

- **Defaults to `IsolationLevel.Serializable`**, which is the single most common source of accidental
  deadlocks in .NET apps. If you use a scope, set the level explicitly.
- Requires `TransactionScopeAsyncFlowOption.Enabled` for any `await` inside it. Without it the usual
  symptom is `InvalidOperationException: A TransactionScope must be disposed on the same thread that
  it was created` at dispose; in some shapes the work commits outside the scope instead.
- **Escalation** to a distributed transaction — two enlisted connections — needs .NET 7+, Windows,
  `Microsoft.Data.SqlClient` 5.0+, and a running MSDTC. On Linux or macOS it throws
  `PlatformNotSupportedException` at runtime. A scope over a **single** connection stays local and
  works fine cross-platform; only escalation is affected.
- Does not compose with the retrying execution strategy above.
- EF enlists only if the connection is opened inside the scope and `Enlist=true` (the default).

Use `Database.BeginTransaction` unless an existing ambient-transaction API forces the scope.

## Abstractions over `DbContext`

`DbContext` is already a unit of work and `DbSet<T>` already a repository, so an `IUnitOfWork` whose
only member forwards `SaveChangesAsync()` adds a layer without adding a guarantee. Abstractions that
*do* earn their place: enforcing aggregate boundaries, coordinating a write across two stores, or
providing a seam for non-EF persistence. Whatever you build, it inherits the constraint — a
`DbContext` is not thread-safe and is a short-lived, scoped unit of work.
