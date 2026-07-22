---
name: dotnet-aspnet
description: Use when building or changing ASP.NET Core Web/REST APIs — controllers, minimal APIs, middleware pipeline, routing, model binding, validation, authentication, authorization, error handling with ProblemDetails, OpenAPI/Swagger, health checks, CORS, or rate limiting. For DI, Options pattern, and configuration common to all .NET hosts, use dotnet-fundamentals instead.
---

# ASP.NET Core Web API Best Practices

## When to Use

- Creating new controllers, minimal API endpoints, or feature folders in an ASP.NET Core project
- Configuring the middleware pipeline, routing, or model binding
- Adding authentication, authorization policies, or `[Authorize]`-based access control
- Implementing error handling with `ProblemDetails` (RFC 9457) or `IExceptionHandler`
- Wiring up OpenAPI/Swagger, health checks, CORS, rate limiting, output caching, or response compression
- Reviewing or restructuring an existing ASP.NET Core project to align with best practices

This skill covers the **HTTP / web layer only**. For dependency injection, Options pattern, and configuration that apply to any .NET host, see [`dotnet-fundamentals`](../dotnet-fundamentals/SKILL.md).

## Core Principles

- Use feature folders, not layer folders. Keep `Program.cs` lean — extract registrations into extension methods.
- Always use `[ApiController]` on MVC controllers; prefer `TypedResults` in minimal APIs.
- Accept `CancellationToken` on every async endpoint.
- Map domain exceptions to ProblemDetails — never leak internal exception messages.
- Middleware order matters: exception handler → status code pages → HSTS/HTTPS → CORS → auth → rate limiter → endpoints.

## Reference Index

Detailed patterns and code samples live in `references/`:

- **[project-and-endpoints.md](references/project-and-endpoints.md)** — Project structure, Controllers vs Minimal APIs, routing, API conventions, response types (`TypedResults`, `[ProducesResponseType]`)
- **[model-binding-validation.md](references/model-binding-validation.md)** — Binding sources (`[FromBody]`, `[FromRoute]`, etc.), Data Annotations, FluentValidation, `ValidationProblemDetails`
- **[middleware.md](references/middleware.md)** — Pipeline order, custom middleware with primary constructors
- **[auth.md](references/auth.md)** — JWT Bearer, authorization policies, `IAuthorizationHandler`, `RequireAuthorization`
- **[error-handling.md](references/error-handling.md)** — ProblemDetails, `IExceptionHandler` (.NET 8+), `UseStatusCodePages`
- **[openapi-and-cross-cutting.md](references/openapi-and-cross-cutting.md)** — OpenAPI/Swagger, XML doc generation, health checks (liveness/readiness), CORS, rate limiting, output caching, response compression

## Related Skills

- **[dotnet-fundamentals](../dotnet-fundamentals/SKILL.md)** — Foundation: DI, Options pattern, configuration, modern C# idioms used by every endpoint and service in this skill
- **[dotnet-ef-core](../dotnet-ef-core/SKILL.md)** — Data access with Entity Framework Core, wired in via DI
- **[dotnet-xmldocs](../dotnet-xmldocs/SKILL.md)** — XML documentation comments (feed OpenAPI output)
- **[dotnet-nuget-manager](../dotnet-nuget-manager/SKILL.md)** — Use when adding the health-check, resilience, or middleware packages shown in these references

The full skill overview lives in the `dotnet` router skill.
