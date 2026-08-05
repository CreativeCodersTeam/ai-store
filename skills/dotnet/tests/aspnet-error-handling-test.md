# ASP.NET Error-Handling Integration Test (Finding M-8)

Test artifact per `superpowers:writing-skills` (RED → GREEN → Verify → REFACTOR)
for the 2026-08-05 fix of Finding M-8 in
`docs/analysis/2026-08-02-dotnet-skills-review.md`: the `IExceptionHandler`
example in `dotnet-aspnet/references/error-handling.md` set a dead
problem-type URI and wrote the response manually, bypassing the
`AddProblemDetails` customizer configured in the same file.

## RED — Baseline evidence, 2026-08-05

Grep on the pre-fix file:

```
references/error-handling.md:29:            Type = "https://httpstatuses.com/500"
references/error-handling.md:33:        await context.Response.WriteAsJsonAsync(problem, ct);
```

Two defects: (1) `httpstatuses.com` has been dead for years; RFC 9457 defines
`about:blank` as the default when no problem type is documented. (2)
`Response.WriteAsJsonAsync` is a raw serialization helper that never invokes
`CustomizeProblemDetails` — the `traceId` extension configured in the first
example of the *same file* was silently dropped on exactly the path it exists
for. The two examples looked related but were not integrated.

## GREEN — Fix applied, 2026-08-05

The handler now injects `IProblemDetailsService` and returns
`await problemDetailsService.TryWriteAsync(new ProblemDetailsContext { … })`;
`Response.StatusCode` is set explicitly before the call (the writer never sets
it — omitting this yields 200 with a 500-shaped body); `Type` is no longer set
at all. New bullets state the why: service-vs-manual write (customizer runs
only via the service), `false`-return semantics (defer to the next handler
instead of committing an empty body), no `CancellationToken` on `TryWriteAsync`
(uses `HttpContext.RequestAborted`; `ct` stays because `IExceptionHandler`
requires it), and `Type` defaults (RFC 9457 `about:blank`; ASP.NET Core
substitutes the RFC 9110 status-section URI for well-known codes). Pipeline
wiring stays single-sourced in `middleware.md` (pointer bullet only).

## Verify + REFACTOR — 2026-08-05

Fresh subagent probe, given only the rewritten passage and no file access,
answered a scenario question ("500 responses missing the configured `traceId`
— what does the passage tell you to check?") and eight accuracy checks.

Scenario: CONFIRMED sufficient — the passage points to the manual-write trap,
the `AddProblemDetails` registration, and (via the middleware.md pointer) the
pipeline wiring. Accuracy: `TryWriteAsync` signature/no-CancellationToken
CONFIRMED; customizer-only-via-service CONFIRMED (documented reason Microsoft's
own samples use the service in exception handlers); `Type`/RFC 9457/RFC 9110
substitution CONFIRMED; explicit `StatusCode` assignment CONFIRMED as required
(writer does `Status ??= Response.StatusCode`, not the reverse).

Two defects flagged and FIXED via REFACTOR:

1. `ProblemDetailsContext.Exception` is **.NET 9+**, not .NET 8 — under the
   "since .NET 8" heading the `Exception = exception` line would not compile on
   .NET 8. Fixed with an inline comment: requires .NET 9+; omit on .NET 8.
2. The `false`-return bullet's example "client accepts neither JSON nor XML"
   was wrong — ASP.NET Core ships no XML ProblemDetails writer; the default
   writer handles only `application/json` / `application/problem+json`. Bullet
   rewritten to name those content types.

Two cheap sharpenings adopted: `ExceptionHandlerMiddleware` already logs every
unhandled exception at Error level (bullet added — keep handler logging only if
it adds context), and the implicit dependency on `app.UseExceptionHandler()`
made explicit in the middleware.md pointer bullet ("the handler only runs
when…"). Residual note accepted without change: an Accept header that excludes
JSON also presents as "missing traceId" (no body at all); the rewritten
`false`-return bullet now carries enough to diagnose that.

## Result

The two examples in the file are now one integrated flow: the exception path
writes through `IProblemDetailsService`, so the `traceId` customizer applies;
no hand-set `Type`, no dead URI; version caveat for `.Exception` recorded.
Re-run the probe whenever the Global Exception Handling section changes.
