# Optimistic Updates & Concurrency

Client-side patterns for responsive updates and for resolving conflicts when the server detects a concurrent change. The server holds the real concurrency token (an ETag); the client sends it back and reacts to `409 Conflict`.

## Optimistic Update with Rollback

Apply the change to local state immediately, then reconcile or roll back based on the server response.

```typescript
@Injectable({ providedIn: 'root' })
export class ProductStore {
  private readonly api = inject(ProductApi);
  private readonly state = signal<Record<number, Product>>({});
  readonly products = this.state.asReadonly();

  rename(id: number, name: string): void {
    const previous = this.state()[id];
    // optimistic: update UI now
    this.state.update((s) => ({ ...s, [id]: { ...previous, name } }));

    this.api.rename(id, name, previous.etag).subscribe({
      next: (updated) => this.state.update((s) => ({ ...s, [id]: updated })), // reconcile (new etag)
      error: () => this.state.update((s) => ({ ...s, [id]: previous })),      // rollback
    });
  }
}
```

## Version Tokens (ETag / If-Match)

Send the last-known version with the mutation so the server can reject a stale write.

```typescript
rename(id: number, name: string, etag: string) {
  return this.http.put<Product>(`/api/products/${id}`, { name }, {
    headers: { 'If-Match': etag },
  });
}
```

## Handling 409 Conflict

When two users edit the same entity, the second write returns `409`. Resolve by refetching server values, then choose client-wins, store-wins, or merge.

```typescript
this.api.rename(id, name, etag).pipe(
  catchError((err: HttpErrorResponse) => {
    if (err.status !== 409) return throwError(() => err);
    return this.api.get(id).pipe(           // fetch current store values
      tap((current) => this.resolveConflict(current /* store-wins */, name /* client value */)),
    );
  }),
).subscribe();
```

Surface the conflict to the user when an automatic merge isn't safe (show both values and let them choose) rather than silently overwriting.

## Related Skills

- **[angular-state](../SKILL.md)** — Core Angular state skill
- **[angular-components](../../angular-components/SKILL.md)** — Surfaces conflict prompts and error messages in the UI
