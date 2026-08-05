# Change Tracking & Saving

- Track entities only on write paths; use `AsNoTracking()` for read paths and `AsNoTrackingWithIdentityResolution()` when the same entity may appear multiple times in the result graph
- Accumulate related changes and call `SaveChanges()` once per unit of work — not once per entity, and never concurrently on the same `DbContext` (it is not thread-safe). Deliberate exception: very large bulk operations may save in chunks of N entities (with `ChangeTracker.Clear()` between chunks), wrapped in an explicit transaction if atomicity matters
- Add a concurrency token to any entity where two users can edit the same row between load and save — without one the second save silently overwrites the first on every column it changed, with no exception and no audit trail. Append-only and single-writer tables do not need one
- In a disconnected flow (load in one request, save in the next) the token on the entity is not enough: it must be round-tripped to the client and restored as the **original** value before saving (`entry.Property(e => e.RowVersion).OriginalValue = posted.RowVersion`), and the resulting `DbUpdateConcurrencyException` must be handled. Details in [concurrency-control.md](./concurrency-control.md)
- Do not wrap a single `SaveChanges()` in an explicit transaction — it is already atomic across every entity in the batch. Reach for `BeginTransaction` only to span **multiple** `SaveChanges()` calls, to mix EF writes with raw SQL (`ExecuteUpdate`/`ExecuteDelete` run immediately and are not covered by a later save), or to hold a read stable until the write. Under a retrying execution strategy this must go through `CreateExecutionStrategy().ExecuteAsync(…)` or EF throws — see [transactions.md](./transactions.md)

## Related references

- **[concurrency-control.md](./concurrency-control.md)** — `[Timestamp]`, `[ConcurrencyCheck]`, provider-specific row-version types, `DbUpdateConcurrencyException` handling
- **[transactions.md](./transactions.md)** — when an explicit transaction is actually required, the retrying-execution-strategy rule, sharing a transaction across contexts, and why `TransactionScope` is not the default
