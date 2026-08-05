# Testing ASP.NET Core Applications

In-memory integration tests via `WebApplicationFactory<TEntryPoint>` (`Microsoft.AspNetCore.Mvc.Testing`): the test host boots the real `Program` — routing, middleware pipeline, DI container, filters, model binding, auth — and the test talks to it through an in-process `HttpClient`. No network, no deployed environment.

Use these tests for behavior that only exists when the pieces are wired together: endpoint + pipeline + DI + auth. For isolated class-level logic, write unit tests via the `dotnet-tester` skill instead — same stack (xUnit, AwesomeAssertions), lighter and faster. Tests that only exercise a real external system (a deployed API, a shared staging database) are neither — they belong to end-to-end suites outside both skills.

## Setup

- Add `Microsoft.AspNetCore.Mvc.Testing` to the test project via the `dotnet-nuget-manager` skill. The test project targets the same framework as the web project and references it.
- Minimal API apps with top-level statements generate an **internal** `Program` class — the factory can't see it from the test project. Append to `Program.cs`:

```csharp
public partial class Program { }
```

  (Alternative: `InternalsVisibleTo`, if the project already manages internals visibility centrally.)

## Baseline: factory as class fixture

```csharp
public class OrdersEndpointTests(WebApplicationFactory<Program> factory)
    : IClassFixture<WebApplicationFactory<Program>>
{
    [Fact]
    public async Task GetOrders_ReturnsOk()
    {
        // Arrange
        var client = factory.CreateClient();

        // Act
        var response = await client.GetAsync("/api/orders");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);
    }
}
```

- `IClassFixture` shares one factory (one booted host) across all tests in the class — booting per test is the main cost driver in these suites.
- `CreateClient()` is cheap; create one per test. Pass `new WebApplicationFactoryClientOptions { AllowAutoRedirect = false }` when asserting on redirect responses.
- Assert on observable HTTP behavior (status code, headers, response body deserialized with the app's JSON options), not on internals.

## Overriding services: custom factory

Derive a factory once per test project; override registrations in `ConfigureTestServices` — it runs **after** `Program`'s own registrations, so combined with `RemoveAll` the test registration is the one that resolves:

```csharp
public class TestWebApplicationFactory : WebApplicationFactory<Program>
{
    protected override void ConfigureWebHost(IWebHostBuilder builder)
    {
        builder.UseEnvironment("Testing");
        builder.ConfigureTestServices(services =>
        {
            services.RemoveAll<IPaymentGateway>();
            services.AddSingleton<IPaymentGateway, FakePaymentGateway>();
        });
    }
}
```

- `RemoveAll<T>()` lives in `Microsoft.Extensions.DependencyInjection.Extensions`.
- Override the *seams the app already has* (interfaces, typed clients, `DbContextOptions`); if a dependency can't be replaced here, that's a production design smell, not a test problem.
- `UseEnvironment("Testing")` lets `appsettings.Testing.json` and environment checks in `Program` take effect deliberately — keep test-only branches in configuration, not in `if (env.IsTesting())` code.

## Auth: fake the scheme, not the middleware

Register a test authentication scheme that always succeeds with the claims the test needs; the real `UseAuthentication`/`UseAuthorization` pipeline and all policies still run:

```csharp
public class TestAuthHandler(
    IOptionsMonitor<AuthenticationSchemeOptions> options,
    ILoggerFactory logger,
    UrlEncoder encoder)
    : AuthenticationHandler<AuthenticationSchemeOptions>(options, logger, encoder)
{
    protected override Task<AuthenticateResult> HandleAuthenticateAsync()
    {
        var claims = new[] { new Claim(ClaimTypes.Name, "test-user"),
                             new Claim(ClaimTypes.Role, "admin") };
        var identity = new ClaimsIdentity(claims, Scheme.Name);
        var ticket = new AuthenticationTicket(new ClaimsPrincipal(identity), Scheme.Name);
        return Task.FromResult(AuthenticateResult.Success(ticket));
    }
}
```

```csharp
builder.ConfigureTestServices(services =>
{
    services.AddAuthentication(defaultScheme: "Test")
        .AddScheme<AuthenticationSchemeOptions, TestAuthHandler>("Test", _ => { });
});
```

- Setting `defaultScheme: "Test"` re-points authentication at the fake; JWT configuration in `Program` stays registered but unused. Authorization policies evaluate against the fake principal — so policy behavior (roles, claims requirements) is genuinely tested. Caveat: endpoints or policies that pin an explicit scheme (`[Authorize(AuthenticationSchemes = ...)]`) bypass the default and still hit the real handler.
- For unauthenticated-path tests (`401`/`403` assertions), prefer a handler variant returning `AuthenticateResult.NoResult()` — it stays fully offline. A client from the *base* factory also works but runs the real authentication registration.
- Vary claims per test by parameterizing the handler (e.g. read desired claims from a scoped test-context service or request header) rather than one handler class per role.

## Database: swap the provider, keep the model

Replace the app's `DbContext` registration with a test provider in `ConfigureTestServices`. Since EF Core 9, `AddDbContext` also registers a singleton `IDbContextOptionsConfiguration<TContext>` — remove **both** it and `DbContextOptions<TContext>` before re-adding, otherwise the production provider stays configured and the host fails with "multiple database providers registered". Which provider — SQLite in-memory for realistic SQL semantics, Testcontainers to match production — and the seeding/lifetime patterns are owned by the `dotnet-ef-core` skill: see `references/testing.md` there. Combine: custom factory swaps the provider, each test seeds through a scope (`factory.Services.CreateScope()`) and asserts through the HTTP surface.

## External HTTP dependencies

Integration tests never call real third-party APIs. Replace at the seam:

- App depends on a typed-client interface (`IWeatherClient`) → `RemoveAll` + register a fake implementation (simplest, preferred).
- The `HttpClient` plumbing itself is under test → re-register the typed client with a stub `HttpMessageHandler` returning canned `HttpResponseMessage`s via `ConfigurePrimaryHttpMessageHandler`.

Either way the app's own pipeline (resilience handlers, headers, serialization) stays as production-shaped as the test needs. A test that can only pass against a live external system does not belong in this suite.

## Checklist

- One custom factory per test project; test classes take it via `IClassFixture`.
- Same conventions as unit tests (`dotnet-tester`): xUnit, AwesomeAssertions, Arrange/Act/Assert, English names, `Method_Condition_Expected`.
- Assert status codes with `HttpStatusCode`, bodies via typed deserialization — no string-contains on JSON.
- Auth-protected endpoints get at least: happy path with the test scheme, `401` without, `403` with wrong role/claims when a policy exists.
