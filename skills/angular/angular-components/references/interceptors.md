# HTTP Interceptors

Functional HTTP interceptors are the client analogue of a server middleware pipeline: each request passes through the chain, each response passes back.

## Pipeline Order

Order is critical and follows registration order in `withInterceptors([...])`. A sensible default:

```typescript
provideHttpClient(
  withInterceptors([
    authInterceptor,     // attach bearer token
    baseUrlInterceptor,  // prefix relative URLs with the API base
    cacheInterceptor,    // serve/refresh cached GETs
    retryInterceptor,    // retry transient failures
    errorInterceptor,    // map errors to user-facing messages (outermost on the way back)
    loggingInterceptor,  // observe final outcome
  ]),
)
```

## Functional Interceptor

Prefer functional interceptors (`HttpInterceptorFn`) over class-based ones. Use `inject()` for dependencies.

```typescript
export const baseUrlInterceptor: HttpInterceptorFn = (req, next) => {
  const base = inject(API_BASE_URL);
  const url = req.url.startsWith('http') ? req.url : `${base}${req.url}`;
  return next(req.clone({ url }));
};
```

## Logging Interceptor

```typescript
export const loggingInterceptor: HttpInterceptorFn = (req, next) => {
  const logger = inject(LoggerService);
  const started = Date.now();
  return next(req).pipe(
    tap({
      next: (event) => {
        if (event.type === HttpEventType.Response) {
          logger.info(`${req.method} ${req.urlWithParams} → ${event.status} (${Date.now() - started}ms)`);
        }
      },
    }),
  );
};
```

## Caching & Retry

- **Cache**: short-circuit GETs by returning a cached `HttpResponse` via `of(...)`; otherwise pass through and `tap` the response into the cache.
- **Retry**: wrap with `retry({ count, delay })` and only retry idempotent methods / transient status codes (`429`, `503`).

## Reactive Reads (`httpResource`)

`httpResource()` (signal-driven GETs, see [angular-state](../../angular-state/SKILL.md)) is built on `HttpClient`, so it flows through **this same interceptor chain** — auth, base URL, caching, retry, and error mapping all apply. Use `httpResource` for reactive reads; keep `HttpClient` for mutations and streaming.

## Related Skills

- **[angular-fundamentals](../../angular-fundamentals/SKILL.md)** — Interceptors resolve config/services via `inject()`
- **[angular-components](../SKILL.md)** — Core Angular UI skill
