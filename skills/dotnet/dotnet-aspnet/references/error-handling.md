# Error Handling

## ProblemDetails (RFC 9457)

```csharp
builder.Services.AddProblemDetails(options =>
{
    options.CustomizeProblemDetails = ctx =>
    {
        ctx.ProblemDetails.Extensions["traceId"] = ctx.HttpContext.TraceIdentifier;
    };
});
```

## Global Exception Handling (since .NET 8)

```csharp
public class GlobalExceptionHandler(
    IProblemDetailsService problemDetailsService,
    ILogger<GlobalExceptionHandler> logger) : IExceptionHandler
{
    public async ValueTask<bool> TryHandleAsync(
        HttpContext context, Exception exception, CancellationToken ct)
    {
        logger.LogError(exception, "Unhandled exception");

        context.Response.StatusCode = StatusCodes.Status500InternalServerError;

        return await problemDetailsService.TryWriteAsync(new ProblemDetailsContext
        {
            HttpContext = context,
            Exception = exception, // ProblemDetailsContext.Exception requires .NET 9+; omit this line on .NET 8
            ProblemDetails = new()
            {
                Status = StatusCodes.Status500InternalServerError,
                Title = "An error occurred"
            }
        });
    }
}

builder.Services.AddExceptionHandler<GlobalExceptionHandler>();
```

- Use `IExceptionHandler` (since .NET 8) instead of custom exception middleware
- Write the response through `IProblemDetailsService.TryWriteAsync`, never manually via
  `WriteAsJsonAsync` — only the service runs the `CustomizeProblemDetails` callback registered
  with `AddProblemDetails` above, so a manual write silently drops extensions like `traceId`
  on exactly the path they exist for
- Return the result of `TryWriteAsync` from `TryHandleAsync`: it is `false` when no registered
  writer can produce a response (the default writer handles only `application/json` /
  `application/problem+json` — an Accept header excluding both means no body), and returning
  `false` lets the exception flow to the next handler instead of swallowing it with an empty body
- `TryWriteAsync` takes no `CancellationToken` — it uses `HttpContext.RequestAborted`; the `ct`
  parameter stays in the signature because `IExceptionHandler` requires it
- Leave `Type` unset unless you have a real, documented problem-type URI: RFC 9457 defines the
  default as `about:blank`, and ASP.NET Core substitutes the matching RFC 9110 status-section
  reference for well-known status codes. Never link third-party status-code sites
- `ExceptionHandlerMiddleware` already logs every unhandled exception at Error level — keep
  logging in the handler only if it adds context beyond the middleware's own entry
- Map domain exceptions to appropriate HTTP status codes
- Never expose internal exception details in production responses
- Use `app.UseStatusCodePages()` for consistent responses on empty status codes (404, 405, etc.)
- The handler only runs when `app.UseExceptionHandler()` is in the pipeline — placement is
  covered in [middleware.md](middleware.md)
