# Error Handling

Catch errors centrally and surface a friendly message — never render raw exception text or stack traces to users (the client analogue of mapping exceptions to ProblemDetails).

## Global ErrorHandler

Replace Angular's default `ErrorHandler` to log and notify on uncaught errors.

```typescript
@Injectable()
export class GlobalErrorHandler implements ErrorHandler {
  private readonly logger = inject(LoggerService);
  private readonly notify = inject(NotificationService);

  handleError(error: unknown): void {
    this.logger.error('Unhandled error', error);
    this.notify.show('Something went wrong. Please try again.');
  }
}

// app.config.ts
providers: [{ provide: ErrorHandler, useClass: GlobalErrorHandler }];
```

## HTTP Error Interceptor

Map HTTP failures to typed, user-facing outcomes in one place. Re-throw so callers can still react.

```typescript
export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const notify = inject(NotificationService);
  return next(req).pipe(
    catchError((err: HttpErrorResponse) => {
      const message =
        err.status === 0 ? 'Network unavailable.' :
        err.status === 401 ? 'Your session expired.' :
        err.status === 403 ? 'You are not allowed to do that.' :
        err.status === 404 ? 'Not found.' :
        'Unexpected server error.';
      notify.show(message);
      return throwError(() => new ApiError(err.status, message, err));
    }),
  );
};
```

## Component-Level `catchError`

When a component needs a local fallback (e.g. show empty state instead of a toast), handle it at the stream:

```typescript
readonly orders = toSignal(
  this.service.list().pipe(catchError(() => of([] as Order[]))),
  { initialValue: [] as Order[] },
);
```

## Related Skills

- **[angular-fundamentals](../../angular-fundamentals/SKILL.md)** — Error handler and interceptors resolve logging/notification via DI
- **[angular-components](../SKILL.md)** — Core Angular UI skill
