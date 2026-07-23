# OpenAPI, Health Checks & Cross-Cutting Concerns

## OpenAPI / Swagger

- Use the built-in OpenAPI support (.NET 9+) or Swashbuckle/NSwag for earlier versions:

```csharp
builder.Services.AddOpenApi();
// ...
app.MapOpenApi();
```

- Enable XML comments in `.csproj` for automatic documentation:
  ```xml
  <PropertyGroup>
    <GenerateDocumentationFile>true</GenerateDocumentationFile>
    <NoWarn>$(NoWarn);1591</NoWarn>
  </PropertyGroup>
  ```
- Use `[Tags]`, `[EndpointSummary]`, `[EndpointDescription]` for metadata
- Use `WithName()` and `WithTags()` on minimal API endpoints
- Use the `dotnet-xmldocs` skill for writing XML documentation comments

## Health Checks

```csharp
builder.Services.AddHealthChecks()
    .AddNpgSql(connectionString, name: "database", tags: new[] { "ready" })
    .AddRedis(redisConnectionString, name: "cache", tags: new[] { "ready" });

// Liveness: is the process responsive? Runs NO checks — restarting the app
// does not fix a downed database.
app.MapHealthChecks("/health/live", new HealthCheckOptions
{
    Predicate = _ => false
});

// Readiness: are the dependencies available? Runs only "ready"-tagged checks.
app.MapHealthChecks("/health/ready", new HealthCheckOptions
{
    Predicate = check => check.Tags.Contains("ready")
});
```

- Liveness (`/health/live`) must run no dependency checks; readiness (`/health/ready`) covers the dependencies
- Tag every dependency check `ready` — a readiness endpoint whose predicate matches zero checks evaluates nothing and always reports Healthy
- `Degraded` maps to HTTP 200 by default — a degraded dependency still counts as ready
- `HealthCheckOptions` requires `using Microsoft.AspNetCore.Diagnostics.HealthChecks;` (not part of the implicit usings)
- Pass a `timeout:` to dependency checks — without one, a hung (not refused) connection stalls the probe until the orchestrator's own timeout kills it
- Use NuGet packages `AspNetCore.HealthChecks.*` for common dependencies (add them via the `dotnet-nuget-manager` skill)
- For a rich JSON payload (e.g. for HealthChecks UI dashboards) add `ResponseWriter = UIResponseWriter.WriteHealthCheckUIResponse` on the readiness or a dedicated UI endpoint (pointless on liveness — its report is empty) — requires the `AspNetCore.HealthChecks.UI.Client` package and `using HealthChecks.UI.Client;`

## CORS

```csharp
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowFrontend", policy =>
        policy.WithOrigins("https://app.example.com")
              .AllowAnyHeader()
              .AllowAnyMethod()
              .AllowCredentials());
});

app.UseCors("AllowFrontend");
```

## Rate Limiting (.NET 7+)

```csharp
builder.Services.AddRateLimiter(options =>
{
    options.AddFixedWindowLimiter("api", limiter =>
    {
        limiter.PermitLimit = 100;
        limiter.Window = TimeSpan.FromMinutes(1);
    });
    options.RejectionStatusCode = StatusCodes.Status429TooManyRequests;
});

app.UseRateLimiter();
```

- Apply per-endpoint with `[EnableRateLimiting("api")]` or `.RequireRateLimiting("api")`

## Output Caching (.NET 7+)

```csharp
builder.Services.AddOutputCache(options =>
{
    options.AddBasePolicy(builder => builder.Expire(TimeSpan.FromMinutes(5)));
    options.AddPolicy("NoCache", builder => builder.NoCache());
});
```

## Response Compression

```csharp
builder.Services.AddResponseCompression(options =>
{
    options.EnableForHttps = true;
    options.Providers.Add<BrotliCompressionProvider>();
    options.Providers.Add<GzipCompressionProvider>();
});
```
