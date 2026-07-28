# HTTP Interceptors

Functional HTTP interceptors are the client analogue of a server middleware pipeline: each request passes through the chain, each response passes back.

## Pipeline Order

Order is critical and follows registration order in `withInterceptors([...])`. A sensible default:

```typescript
provideHttpClient(
  withInterceptors([
    baseUrlInterceptor,  // prefix relative URLs with the API base — must run before auth
    authInterceptor,     // attach bearer token (matches on the now-absolute URL)
    cacheInterceptor,    // serve/refresh cached GETs
    errorInterceptor,    // map errors to user-facing messages — outside retry: fires once, after retries are exhausted
    retryInterceptor,    // retry transient failures
    loggingInterceptor,  // log each attempt and its outcome
  ]),
)
```

Two ordering constraints matter. Position N wraps position N+1 — requests flow top-down, responses and errors bubble bottom-up. (1) `baseUrlInterceptor` must run before `authInterceptor`: the auth interceptor decides by URL whether to attach the token, which only matches once relative URLs carry the API base. (2) `errorInterceptor` must sit outside `retryInterceptor`: placed inside, its `catchError` (and user notification) would fire on every retry attempt; outside, the user sees one message after retries are exhausted.

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
