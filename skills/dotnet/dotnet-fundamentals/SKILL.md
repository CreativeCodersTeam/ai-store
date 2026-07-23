---
name: dotnet-fundamentals
description: Use when registering services in any .NET host (ASP.NET Core, Worker Service, Console, MAUI), choosing DI lifetimes, binding configuration to IOptions<T>, setting up appsettings.json / User Secrets / environment variables, or applying modern C# idioms such as primary constructors, required properties, nullable reference types, and CancellationToken propagation.
---

# Modern .NET Fundamentals

## When to Use

- Writing or modifying any C# production code — this is the baseline skill; `dotnet-aspnet`, `dotnet-ef-core`, and `dotnet-sdk-builder` build on top of it, so load this skill alongside them, not instead of them
- Registering services in any `IServiceCollection` (ASP.NET Core, Worker Service, Console app, MAUI, library DI extension methods)
- Choosing a DI lifetime (Transient, Scoped, Singleton) or registering keyed services (.NET 8+)
- Binding configuration sections to a strongly-typed Options class
- Setting up `appsettings.json`, environment-specific overrides, User Secrets, or environment variables
- Adopting primary constructors, `required` properties, nullable reference types, or `CancellationToken` propagation in new code

## Core Principles

- This skill is **technology-agnostic across .NET hosts**. ASP.NET Core, EF Core, and SDK builders all sit on top of these fundamentals.
- **Interface-first registration** — register services via their abstraction (`AddScoped<IFoo, Foo>()`), not the concrete type. Enables substitution and testing.
- **No service locator** — never inject `IServiceProvider` into business logic. Constructor-inject the dependencies you actually need.
- **Options over constructor parameters for configuration** — bind config sections to `IOptions<T>`, do not pass raw `IConfiguration` values around.
- **Fail fast** — use `ValidateDataAnnotations().ValidateOnStart()` so misconfiguration surfaces at startup, not at first use.
- **Immutable configuration** — Options classes use `required` properties and `init`-only setters.
- **Cancellation flows everywhere** — every async method takes a `CancellationToken` as its last parameter (`= default` on public API surfaces) and forwards the received token to every async call — never re-default it mid-chain.

## Reference Index

- **[dependency-injection.md](references/dependency-injection.md)** — `IServiceCollection` registration, lifetimes, keyed services, interface-based registration, anti-service-locator
- **[options-pattern.md](references/options-pattern.md)** — `IOptions<T>` vs `IOptionsMonitor<T>` vs `IOptionsSnapshot<T>`, `BindConfiguration`, `ValidateDataAnnotations`, `ValidateOnStart`
- **[configuration.md](references/configuration.md)** — `appsettings.json` and environment overrides, User Secrets, environment variables, production secret stores
- **[modern-patterns.md](references/modern-patterns.md)** — primary constructors, `required` / `init`-only properties, nullable reference types, `CancellationToken` propagation

## Related Skills

- **dotnet-aspnet / dotnet-ef-core / dotnet-sdk-builder** — build on these fundamentals for their HTTP, data-access, and SDK layers
- **dotnet-nuget-manager** — use when adding the `Microsoft.Extensions.*` packages for DI, Options, and Configuration

The full skill overview lives in the `dotnet` router skill.
