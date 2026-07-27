# Dependency Injection

Modern Angular dependency injection patterns for registering and consuming providers.

## Provider Scopes

Angular has a hierarchical injector tree rather than fixed "lifetimes". Choose the narrowest scope that satisfies the dependency's state requirements.

| Scope | Created | Use for | Avoid when |
|-------|---------|---------|------------|
| **Root** (`providedIn: 'root'`) | Once per app (singleton) | Stateless or app-wide services, caches, config | Service must hold per-view or per-feature state |
| **Route / lazy** (route `providers`) | Once per lazily-loaded route injector | Feature-scoped state shared within a routed area | State must be global |
| **Component** (component `providers`) | Once per component instance (and its subtree) | Per-instance state, a fresh service per widget | Many components must share one instance |

```typescript
@Injectable({ providedIn: 'root' })
export class SystemClock implements Clock {}

// Route-scoped
export const routes: Routes = [
  { path: 'orders', providers: [OrderService], loadComponent: () => import('./orders.component') },
];

// Component-scoped (new instance per component)
@Component({ selector: 'app-editor', providers: [EditorState], /* ... */ })
export class EditorComponent {}
```

## Token-Based Registration

A TypeScript `interface` is erased at runtime and cannot be a DI token. **When the implementation must stay substitutable** (multiple implementations, decoration, a library contract), depend on an `abstract class` or an `InjectionToken<T>`.

```typescript
// ✅ Good — abstraction as token, swappable implementation
export abstract class OrderService {
  abstract get(id: number): Observable<Order>;
}

bootstrapApplication(App, {
  providers: [{ provide: OrderService, useClass: HttpOrderService }],
});
```

```typescript
// ❌ Bad when substitution is required — consumers are bound to the concrete class
@Injectable({ providedIn: 'root' })
export class HttpOrderService { /* ... */ }
```

For app-internal services with no substitution requirement, the concrete class itself is an idiomatic DI token — `TestBed` can still override it in tests (`{ provide: HttpOrderService, useValue: mock }`); an abstract token is not needed for mocking alone.

For non-class values (config, primitives, functions), use an `InjectionToken<T>`:

```typescript
export const API_BASE_URL = new InjectionToken<string>('API_BASE_URL');
providers: [{ provide: API_BASE_URL, useValue: '/api' }];
```

## Injecting Dependencies

Prefer the `inject()` function (works in field initializers, functions, and factories) over constructor parameters in modern Angular.

```typescript
@Injectable({ providedIn: 'root' })
export class OrderFacade {
  private readonly orders = inject(OrderService);
  private readonly logger = inject(LoggerService);

  get(id: number): Observable<Order> {
    this.logger.info(`Fetching order ${id}`);
    return this.orders.get(id);
  }
}
```

## Multiple Implementations

When you need several implementations of the same token, use **multi providers** and inject the array, or use distinct `InjectionToken`s.

```typescript
export const NOTIFIER = new InjectionToken<Notifier>('NOTIFIER');

providers: [
  { provide: NOTIFIER, useClass: EmailNotifier, multi: true },
  { provide: NOTIFIER, useClass: SmsNotifier, multi: true },
];

// Consumer receives Notifier[]
private readonly notifiers = inject(NOTIFIER); // Notifier[]
```

For "pick one by key", define separate tokens (`EMAIL_NOTIFIER`, `SMS_NOTIFIER`) and inject the one you need.

## Anti-Pattern: Service Locator

Never inject `Injector` to resolve dependencies manually in business logic. Inject what you need directly.

```typescript
// ❌ Bad — service locator
export class OrderProcessor {
  private readonly injector = inject(Injector);
  process() {
    const repo = this.injector.get(OrderRepository);
  }
}

// ✅ Good — direct injection
export class OrderProcessor {
  private readonly repo = inject(OrderRepository);
  process() { /* use this.repo */ }
}
```

(`Injector.get` / `runInInjectionContext` are legitimate in framework plumbing and dynamic-component factories — not in ordinary services.)
