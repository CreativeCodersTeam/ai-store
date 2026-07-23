# HTTP Client Patterns

## Typed Service with `HttpClient`

Never use `fetch`/`XMLHttpRequest` directly. Use Angular's `HttpClient` so interceptors, `HttpTestingController`, and SSR all work. Provide the base URL via config.

```typescript
@Injectable()
export class GitHubClient {
  private readonly http = inject(HttpClient);
  private readonly cfg = inject(GITHUB_CONFIG);

  getUser(login: string): Observable<User> {
    return this.http.get<User>(`${this.cfg.baseUrl}/users/${login}`, {
      headers: { Authorization: `Bearer ${this.cfg.token}` },
    });
  }
}
```

Prefer relative URLs + a `baseUrlInterceptor` when the consuming app already centralizes its API base; use absolute `baseUrl` from config when the library targets a fixed external API.

## Resilience

Add retry-with-backoff and a timeout via RxJS. Only retry idempotent calls / transient statuses.

```typescript
getUser(login: string): Observable<User> {
  return this.http.get<User>(`${this.cfg.baseUrl}/users/${login}`).pipe(
    timeout(this.cfg.timeoutMs),
    retry({ count: 3, delay: (_, n) => timer(Math.min(1000 * 2 ** n, 8000)) }),
    catchError((e) => throwError(() => GitHubError.from(e))),
  );
}
```

Alternatively ship an opt-in `HttpInterceptorFn` consumers add to their `withInterceptors([...])`.

## Typed Errors

```typescript
export class GitHubError extends Error {
  constructor(
    message: string,
    readonly status?: number,
    readonly responseBody?: unknown,
    options?: { cause?: unknown },
  ) {
    super(message, options);
    this.name = 'GitHubError';
  }

  static from(e: unknown): GitHubError {
    if (e instanceof HttpErrorResponse) {
      return new GitHubError(e.message, e.status, e.error, { cause: e });
    }
    return new GitHubError('Unexpected error', undefined, undefined, { cause: e });
  }
}
```

## Request/Response Models

Use `interface`/`type` for DTOs. Map snake_case API fields to camelCase in a mapper rather than leaking wire names into the public API.

```typescript
export interface Repository {
  readonly id: number;
  readonly fullName: string;
}

export function toRepository(dto: { id: number; full_name: string }): Repository {
  return { id: dto.id, fullName: dto.full_name };
}
```

## Related Skills

- **[angular-fundamentals](../../angular-fundamentals/SKILL.md)** — Typed config and DI used by typed services
- **[angular-tester](../../angular-tester/SKILL.md)** — Tests generated clients with `HttpTestingController`
