# Middleware Pipeline

This file holds the single canonical middleware ordering for the skill — `SKILL.md` deliberately carries no sequence of its own. It covers *ordering only*; configuration of the individual components lives in the other references: [openapi-and-cross-cutting.md](openapi-and-cross-cutting.md) (OpenAPI, health checks, CORS policy, rate limiting, output caching, compression), [error-handling.md](error-handling.md) (ProblemDetails, `IExceptionHandler`), [auth.md](auth.md) (JWT, policies).

## Canonical Order

```csharp
// 1. Error surface — outermost, so it wraps everything registered below
app.UseExceptionHandler();
app.UseStatusCodePages();

// 2. Transport security
if (!app.Environment.IsDevelopment())
    app.UseHsts();
app.UseHttpsRedirection();

// 3. Optional: compression — before anything that writes responses
//    you want compressed (including static files)
app.UseResponseCompression();

// 4. Static content — cheap short-circuit before routing and auth run
app.UseStaticFiles();

// 5. Routing — implicit in minimal hosting; call it explicitly when the
//    order relative to the middleware below must be provable
app.UseRouting();

// 6. Cross-origin policy — after routing, before authentication
app.UseCors();

// 7. Identity — authentication resolves *who*, authorization decides *may*
app.UseAuthentication();
app.UseAuthorization();

// 8. Endpoint-aware throttling and caching
app.UseRateLimiter();      // default position — see "Rate limiter vs. auth"
app.UseOutputCache();

// 9. Custom middleware that needs endpoint metadata + identity goes here

// 10. Endpoints
app.MapControllers();                  // or MapGroup()/MapGet() for minimal APIs
app.MapOpenApi();                      // if OpenAPI is enabled
app.MapHealthChecks("/health/live");   // config: openapi-and-cross-cutting.md
```

## Why this order

- **Exception handler outermost** — only middleware registered *after* it is covered by it. Anything placed before it fails unhandled.
- **`UseStatusCodePages` right after** — turns bare status codes (404, 405) produced further down into consistent responses; thrown exceptions still belong to the exception handler.
- **HSTS / HTTPS redirection before any content** — no response body should ever be served over plain HTTP; `UseHsts` is skipped in Development so local HTTP keeps working.
- **Static files before routing** — file requests short-circuit without paying for routing, auth, or rate limiting. Caveat: this makes everything under `wwwroot` public; files that need protection must be served by an endpoint behind authorization instead.
- **Routing before CORS, auth, rate limiting, output caching** — these all read endpoint metadata (`RequireCors`, `[Authorize]`, `RequireRateLimiting`, cache policies). Registered before routing, they cannot see which endpoint was matched.
- **CORS before authentication** — the CORS middleware must intercept and answer browser preflight (`OPTIONS`) requests itself. Registered later, a preflight — which carries no credentials — falls through to a response without CORS headers (commonly a 405 or 404, or an auth challenge), and the browser blocks the actual request.
- **Authentication before authorization** — authorization evaluates the principal that authentication established; reversed, every policy sees an anonymous user.
- **Output cache after CORS** — cached responses must include the negotiated CORS headers. Authenticated requests are not output-cached by default.
- **Endpoints last** — `Map…` calls are terminal; everything that should run per request must be registered above them.

## Rate limiter vs. auth — an explicit decision

The canonical position is **after** authentication/authorization:

- Partitions can key on identity (`RateLimitPartition` per user/claim), and authenticated APIs usually want per-client rather than per-IP limits.

Move it **before** `UseAuthentication` (directly after `UseRouting`) when the auth stack itself is the asset to protect — e.g. throttling credential-stuffing floods before token validation burns CPU. Either way it must stay after `UseRouting` whenever endpoint-specific limits (`RequireRateLimiting`) are used. Deviating from the default is fine; deviating *silently* is not — state the reason.

## Placing your own middleware

Rule of thumb: register custom middleware **after the last middleware whose output it needs, and before the first middleware that must observe its effect.**

- `RequestTimingMiddleware` (below) wants to measure the whole request → register it early, directly after `UseExceptionHandler()`.
- Middleware reading `context.User` → after `UseAuthentication()`.
- Middleware branching on the matched endpoint (`context.GetEndpoint()`) → after `UseRouting()`.

## Custom Middleware

```csharp
public class RequestTimingMiddleware(RequestDelegate next)
{
    public async Task InvokeAsync(HttpContext context)
    {
        var sw = Stopwatch.StartNew();
        context.Response.OnStarting(() =>
        {
            context.Response.Headers["X-Response-Time-Ms"] = sw.ElapsedMilliseconds.ToString();
            return Task.CompletedTask;
        });
        await next(context);
    }
}
```

- Use primary constructors for middleware
- Inject scoped services via `InvokeAsync` parameters, not the constructor — middleware instances are effectively singletons
- Keep middleware focused — one concern per middleware
