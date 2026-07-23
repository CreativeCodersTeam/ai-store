# DI Patterns for .NET SDK Libraries

## Service Registration Extension Method

The entry point for consumers is a single `AddXxx(...)` extension method on `IServiceCollection`.

### Basic Pattern (no options)

```csharp
public static class GitHubServiceCollectionExtensions
{
    public static IHttpClientBuilder AddGitHub(
        this IServiceCollection services,
        Action<GitHubOptions> configureOptions)
    {
        services.Configure(configureOptions);
        services.AddSingleton<IValidateOptions<GitHubOptions>, GitHubOptionsValidator>();
        services.AddOptions<GitHubOptions>().ValidateOnStart();

        return services
            .AddHttpClient<IGitHubClient, GitHubClient>()
            .ConfigureHttpClient((sp, client) =>
            {
                var options = sp.GetRequiredService<IOptions<GitHubOptions>>().Value;
                client.BaseAddress = new Uri(options.BaseUrl);
                client.DefaultRequestHeaders.Add("User-Agent", options.UserAgent);
            });
    }
}
```

### Pattern with IConfiguration Section

```csharp
public static IHttpClientBuilder AddGitHub(
    this IServiceCollection services,
    IConfiguration configuration,
    string sectionName = "GitHub")
{
    services.Configure<GitHubOptions>(configuration.GetSection(sectionName));

    return services
        .AddHttpClient<IGitHubClient, GitHubClient>()
        .ConfigureHttpClient((sp, client) =>
        {
            var options = sp.GetRequiredService<IOptions<GitHubOptions>>().Value;
            client.BaseAddress = new Uri(options.BaseUrl);
        });
}
```

### Pattern Supporting Both Overloads

Expose both so consumers can use either approach:

```csharp
public static class GitHubServiceCollectionExtensions
{
    public static IHttpClientBuilder AddGitHub(
        this IServiceCollection services,
        Action<GitHubOptions> configureOptions)
    {
        ArgumentNullException.ThrowIfNull(services);
        ArgumentNullException.ThrowIfNull(configureOptions);

        services.Configure(configureOptions);
        return services.AddGitHubCore();
    }

    public static IHttpClientBuilder AddGitHub(
        this IServiceCollection services,
        IConfiguration configuration,
        string sectionName = "GitHub")
    {
        ArgumentNullException.ThrowIfNull(services);
        ArgumentNullException.ThrowIfNull(configuration);

        services.Configure<GitHubOptions>(configuration.GetSection(sectionName));
        return services.AddGitHubCore();
    }

    private static IHttpClientBuilder AddGitHubCore(this IServiceCollection services)
    {
        services.AddSingleton<IValidateOptions<GitHubOptions>, GitHubOptionsValidator>();
        services.AddOptions<GitHubOptions>().ValidateOnStart();

        return services
            .AddHttpClient<IGitHubClient, GitHubClient>()
            .ConfigureHttpClient((sp, client) =>
            {
                var options = sp.GetRequiredService<IOptions<GitHubOptions>>().Value;
                client.BaseAddress = new Uri(options.BaseUrl);
            });
    }
}
```

`services.Configure(...)` in the public overloads composes with `AddOptions<GitHubOptions>()` here — both act on the same default-named options instance, so configuration from either overload is validated at host startup.

## Options Class

```csharp
/// <summary>Options for configuring the GitHub client.</summary>
public sealed class GitHubOptions
{
    /// <summary>The base URL of the GitHub API. Defaults to https://api.github.com/.</summary>
    public string BaseUrl { get; set; } = "https://api.github.com/";

    /// <summary>The personal access token used for authentication.</summary>
    public string? AccessToken { get; set; }

    /// <summary>The User-Agent header value sent with every request.</summary>
    public string UserAgent { get; set; } = "GitHubSdk/1.0";

    /// <summary>Request timeout. Defaults to 30 seconds.</summary>
    public TimeSpan Timeout { get; set; } = TimeSpan.FromSeconds(30);
}
```

**Rules:**
- Use `sealed` — options classes are never subclassed.
- Provide sensible defaults for all non-secret properties.
- Nullable (`string?`) for optional secrets/tokens.
- No validation logic in the class itself; validation lives in the `IValidateOptions<T>` validator (see below).

> **Deviation from `dotnet-fundamentals`** (which mandates `required` properties and `init`-only setters for options): SDK options use mutable `get; set;` properties **because consumers configure them via the `Action<TOptions>` lambda** in `AddXxx(...)` — `required` members cannot be satisfied by a configure delegate, and `init` setters reject assignment inside it. The fail-fast guarantee that `required` would provide comes from the standard `IValidateOptions<T>` validator plus `ValidateOnStart()` instead.

## Options Validation (Standard)

```csharp
internal sealed class GitHubOptionsValidator : IValidateOptions<GitHubOptions>
{
    public ValidateOptionsResult Validate(string? name, GitHubOptions options)
    {
        if (string.IsNullOrWhiteSpace(options.BaseUrl))
            return ValidateOptionsResult.Fail($"{nameof(GitHubOptions.BaseUrl)} must not be empty.");

        if (!Uri.TryCreate(options.BaseUrl, UriKind.Absolute, out _))
            return ValidateOptionsResult.Fail($"{nameof(GitHubOptions.BaseUrl)} must be a valid absolute URI.");

        return ValidateOptionsResult.Success;
    }
}
```

Every generated SDK library ships this validator (at minimum the BaseUrl checks above). Its registration — together with `ValidateOnStart()` — is already part of the canonical `AddXxxCore()` pattern shown earlier; do not treat it as an add-on.

## Interface Pattern

```csharp
/// <summary>Provides access to the GitHub REST API.</summary>
public interface IGitHubClient
{
    /// <summary>Gets a repository by owner and name.</summary>
    Task<Repository> GetRepositoryAsync(string owner, string repo, CancellationToken cancellationToken = default);

    /// <summary>Lists public repositories for a user.</summary>
    Task<IReadOnlyList<Repository>> ListRepositoriesAsync(string username, CancellationToken cancellationToken = default);
}
```

**Rules:**
- Every method returns `Task<T>` or `Task`.
- Always include `CancellationToken cancellationToken = default` as the last parameter.
- Interface lives in the same namespace as the implementation; no separate `Abstractions` sub-namespace unless the library is large.

## Namespace Conventions

```
MyCompany.GitHub          ← root namespace
MyCompany.GitHub.Models   ← DTOs, request/response models
MyCompany.GitHub.Http     ← internal HTTP helpers (if needed)
```

Keep namespaces shallow. Avoid deep hierarchies for small/medium libraries.

## Consumer Registration Example

What the consumer writes in `Program.cs` or `Startup.cs`:

```csharp
// Action-based
builder.Services.AddGitHub(options =>
{
    options.AccessToken = builder.Configuration["GitHub:AccessToken"];
    options.UserAgent = "MyApp/1.0";
});

// Configuration-section-based
builder.Services.AddGitHub(builder.Configuration);
```
