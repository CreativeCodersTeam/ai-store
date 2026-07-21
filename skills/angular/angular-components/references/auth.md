# Authentication & Authorization

Client-side auth protects **navigation and UX** — the server remains the real authority. Guards gate routes; an interceptor attaches the token; the backend validates it.

## Bearer-Token Interceptor

Attach the access token to outgoing API requests (only to your own API origin).

```typescript
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const token = inject(AuthService).accessToken();
  const apiBase = inject(API_BASE_URL);
  if (token && req.url.startsWith(apiBase)) {
    req = req.clone({ setHeaders: { Authorization: `Bearer ${token}` } });
  }
  return next(req);
};
```

## OIDC / PKCE

For SPAs, use OpenID Connect Authorization Code flow **with PKCE** (no client secret — a browser app cannot keep one; see angular-fundamentals/configuration). Use a vetted library (`angular-auth-oidc-client`) rather than hand-rolling token handling. Store tokens in memory where possible; treat refresh tokens with care.

## Route Guards

Use functional guards. `CanMatch` prevents even loading a lazy chunk for unauthorized users; `CanActivate` blocks activation.

```typescript
export const authGuard: CanMatchFn = () => {
  const auth = inject(AuthService);
  const router = inject(Router);
  return auth.isAuthenticated() ? true : router.createUrlTree(['/login']);
};

export function roleGuard(role: string): CanActivateFn {
  return () => inject(AuthService).hasRole(role) || inject(Router).createUrlTree(['/forbidden']);
}
```

## Applying Guards

```typescript
export const routes: Routes = [
  {
    path: 'admin',
    canMatch: [authGuard],
    canActivate: [roleGuard('Admin')],
    loadChildren: () => import('./admin/admin.routes').then((m) => m.ADMIN_ROUTES),
  },
];
```

Mirror authorization in the template (`@if (auth.hasRole('Admin'))`) to hide controls — but never rely on it for security; the server enforces access.

## Related Skills

- **[angular-fundamentals](../../angular-fundamentals/SKILL.md)** — Auth services and tokens are provided via DI; secrets never ship to the browser
- **[angular-components](../SKILL.md)** — Core Angular UI skill
