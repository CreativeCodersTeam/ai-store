# Typed Configuration (the `provide` pattern)

Bind configuration to a strongly-typed object and expose it through a `provideXxx()` function with validation.

## Basic Typed Config

```typescript
export interface SmtpConfig {
  readonly host: string;
  readonly port: number;     // default 587
  readonly useSsl: boolean;  // default true
}

export const SMTP_CONFIG = new InjectionToken<Required<SmtpConfig>>('SMTP_CONFIG');

export function provideSmtp(config: SmtpConfig): EnvironmentProviders {
  const merged: Required<SmtpConfig> = { port: 587, useSsl: true, ...config };
  validateSmtp(merged);
  return makeEnvironmentProviders([{ provide: SMTP_CONFIG, useValue: merged }]);
}
```

```typescript
// app.config.ts
bootstrapApplication(App, {
  providers: [provideSmtp({ host: 'smtp.example.com' })],
});
```

Consumers inject the token:

```typescript
export class EmailService {
  private readonly cfg = inject(SMTP_CONFIG);
}
```

## Static vs Reactive Config

Distinguish config read once at startup from config that can change at runtime:

| Need | Approach |
|------|----------|
| Config read once at startup (the common case) | `InjectionToken` + `useValue` (immutable) |
| Config that can change at runtime (feature flags, theme) | A service exposing a `signal<T>()` or `Observable<T>` consumers read reactively |
| Per-route/feature variation | Provide a different config object in that route's `providers` |

```typescript
@Injectable({ providedIn: 'root' })
export class FeatureFlags {
  private readonly flags = signal<Readonly<Record<string, boolean>>>({});
  readonly value = this.flags.asReadonly();
  set(next: Record<string, boolean>) { this.flags.set(next); }
}
```

## Validate at Bootstrap (fail fast)

Run validation when the config is provided, or as an app initializer so misconfiguration aborts startup rather than failing at first use.

```typescript
export function provideApiConfig(cfg: ApiConfig): EnvironmentProviders {
  return makeEnvironmentProviders([
    { provide: API_CONFIG, useValue: cfg },
    provideAppInitializer(() => {
      const c = inject(API_CONFIG);
      if (!/^https?:\/\//.test(c.baseUrl)) {
        throw new Error(`API_CONFIG.baseUrl must be an absolute URL, got "${c.baseUrl}"`);
      }
    }),
  ]);
}
```

## Named / Multiple Configs

Use distinct tokens for multiple named instances:

```typescript
export const SMTP_PRIMARY = new InjectionToken<SmtpConfig>('SMTP_PRIMARY');
export const SMTP_BACKUP  = new InjectionToken<SmtpConfig>('SMTP_BACKUP');
```

## Related Skills

- **[angular-components](../../angular-components/SKILL.md)** — Binds HTTP/base-URL and feature config consumed by components and interceptors
- **[angular-library-builder](../../angular-library-builder/SKILL.md)** — Generates typed `XxxConfig` + `provideXxx()` following this pattern
