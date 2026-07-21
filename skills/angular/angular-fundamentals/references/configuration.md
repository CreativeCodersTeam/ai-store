# Configuration

Build-time environments and runtime configuration for Angular apps.

## Build-Time Environments

Angular's classic mechanism is `environment.ts` files swapped at build time via `fileReplacements` in `angular.json`.

```typescript
// src/environments/environment.ts (development default)
export const environment = { production: false, apiBaseUrl: '/api' };

// src/environments/environment.prod.ts
export const environment = { production: true, apiBaseUrl: 'https://api.example.com' };
```

```jsonc
// angular.json → configurations.production
"fileReplacements": [
  { "replace": "src/environments/environment.ts",
    "with": "src/environments/environment.prod.ts" }
]
```

Values are **baked into the bundle at build time**. Use this for non-secret, per-build constants (API base URL, flags). Build with `ng build --configuration production`.

## Runtime Configuration

When the same artifact must run in multiple environments (one Docker image, many stages), load config at runtime instead of baking it in. Fetch a JSON file before the app starts using an app initializer.

```typescript
// assets/config.json (served, not bundled — overridable per deployment)
{ "apiBaseUrl": "https://api.staging.example.com" }
```

```typescript
export const APP_CONFIG = new InjectionToken<AppConfig>('APP_CONFIG');

export function provideRuntimeConfig(): EnvironmentProviders {
  return makeEnvironmentProviders([
    { provide: APP_CONFIG, useFactory: () => structuredClone(loadedConfig) },
    provideAppInitializer(async () => {
      loadedConfig = await firstValueFrom(inject(HttpClient).get<AppConfig>('/assets/config.json'));
    }),
  ]);
}
```

Precedence pattern: bundled `environment` defaults, overridden by the runtime `config.json` when present.

## Secrets — Important

**A front-end app has no real secrets.** Everything shipped to the browser — every environment value, every `config.json` field — is fully visible to any user via dev tools. Never put API keys, client secrets, connection strings, or tokens in `environment.ts`, `config.json`, or any bundled code.

- Keep secrets on a backend; the Angular app calls the backend, which holds the credentials.
- Use OAuth/OIDC (PKCE) for auth — the browser holds short-lived, user-scoped tokens, not application secrets.
- "Public" keys meant for client use (e.g. a publishable Stripe key, a Maps API key restricted by referrer) are fine; restrict them at the provider.

## Related Skills

- **[angular-components](../../angular-components/SKILL.md)** — Reads base-URL / feature config for routing, interceptors, and HTTP setup
- **[angular-fundamentals](../SKILL.md)** — Core fundamentals that build on this configuration foundation
