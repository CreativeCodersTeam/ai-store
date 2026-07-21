---
name: rxjs
description: RxJS reactive programming patterns and best practices for TypeScript and Angular projects. Use when working with Observables, Subjects, operators (switchMap, combineLatest, etc.), subscription management, error handling with catchError/retry, or performance optimization (shareReplay, debounce). Includes Angular-specific patterns like async pipe and takeUntil.
---

# RxJS Skill

## Best Practices

### 1. Observable Creation
- Use appropriate creation operators (of, from, interval, etc.)
- Prefer cold observables for most use cases
- Use subjects sparingly and with clear intent
- Document whether an observable is hot or cold

### 2. Subscription Management
- Always unsubscribe to prevent memory leaks
- Use takeUntil pattern with destroy$ subject
- Prefer async pipe in templates (auto-unsubscribes)
- Use takeWhile or first for self-completing observables

### 3. Operator Usage
- Chain operators efficiently
- Use appropriate operators for the task (map, filter, switchMap, etc.)
- Avoid nested subscriptions - use higher-order operators instead
- Keep operator chains readable with proper formatting

### 4. Error Handling
- Use retry/retryWhen for transient failures
- Use catchError operator for error handling
- Decide whether to recover or propagate errors
- Always handle errors to prevent stream termination

### 5. Performance
- Use shareReplay for expensive operations
- Debounce user inputs
- Use distinctUntilChanged to avoid unnecessary emissions
- Consider using schedulers for CPU-intensive operations

## Common Patterns

### Unsubscribe Pattern
```typescript
private destroy$ = new Subject<void>();

ngOnInit() {
  this.service.getData()
    .pipe(takeUntil(this.destroy$))
    .subscribe(data => this.data = data);
}

ngOnDestroy() {
  this.destroy$.next();
  this.destroy$.complete();
}
```

### Combining Observables
```typescript
// Sequential
source$.pipe(
  switchMap(data => this.service.getRelated(data.id))
).subscribe();

// Parallel
combineLatest([obs1$, obs2$]).subscribe(([data1, data2]) => {});

// Race
race([obs1$, obs2$]).subscribe();
```

### Error Handling
```typescript
this.service.getData().pipe(
  retry(3),
  catchError(error => {
    console.error('Error:', error);
    return of(defaultValue);
  })
).subscribe();
```
