# Cross-Cutting Concerns

The client-side counterparts to a web API's cross-cutting concerns (OpenAPI, health, CORS, rate limiting).

## Title & Meta (SEO)

Set the document title and meta tags per route — the discoverability analogue of OpenAPI documentation.

```typescript
// Per-route static title
{ path: 'orders', title: 'Orders', loadComponent: () => import('./order-list.component') }

// Or dynamically
inject(Title).setTitle(`Order #${order.id}`);
inject(Meta).updateTag({ name: 'description', content: order.summary });
```

For real SEO on public pages, render server-side with **Angular SSR** (`@angular/ssr`).

## Internationalization (i18n)

Use Angular's built-in `i18n` attributes (`ng extract-i18n`, per-locale builds) or a runtime library (`@ngx-translate/core`) when locales must switch without a rebuild.

## Accessibility

Accessibility is a first-class cross-cutting concern: semantic elements, labels for every control, `aria-*` on dynamic regions (`role="alert"` for errors), visible focus, and keyboard operability. Use the Angular CDK a11y utilities (`FocusTrap`, `LiveAnnouncer`).

## Route Preloading

Balance small initial bundles with fast navigation by preloading lazy routes after load.

```typescript
provideRouter(routes, withPreloading(PreloadAllModules));
// or a custom strategy that preloads only routes flagged data: { preload: true }
```

## HTTP Caching

The client analogue of output caching: cache GET responses in a `cacheInterceptor` (see interceptors.md), keyed by URL, with a short TTL or explicit invalidation on mutations.

## Throttling User Actions

The client analogue of rate limiting is protecting *your own* UX: `debounceTime` on search inputs, `exhaustMap` to ignore double-submits, and disabling buttons during in-flight requests.

```typescript
readonly results = toSignal(
  toObservable(this.term).pipe(
    debounceTime(300),
    distinctUntilChanged(),
    switchMap((t) => this.api.search(t)),
  ),
  { initialValue: [] },
);
```

## SSR Hydration & Event Replay

With Angular SSR, enable hydration to reuse server-rendered DOM instead of re-rendering on the client. Prefer **incremental hydration** and **event replay**:

```typescript
provideClientHydration(withIncrementalHydration(), withEventReplay());
```

- **Incremental hydration** hydrates parts of the page on demand (e.g. on viewport/interaction via `@defer` triggers) rather than all at once — smaller, faster initial work.
- **Event replay** captures user events fired before hydration completes and replays them afterward, so early clicks aren't lost.

## Related Skills

- **[angular-fundamentals](../../angular-fundamentals/SKILL.md)** — Cross-cutting services registered via DI
- **[angular-components](../SKILL.md)** — Core Angular UI skill
