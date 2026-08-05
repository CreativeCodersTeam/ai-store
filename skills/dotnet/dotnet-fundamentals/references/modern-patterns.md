# Modern C# / .NET Patterns

Conventions for code written against current .NET. Use these consistently in new code; match existing project style if it predates these features.

## Primary Constructors (classes and structs since C# 12; record classes since C# 9, record structs since C# 10)

Declare constructor parameters directly on the type; they are in scope in instance members, initializers, and the base clause (not in static members). The standard use is DI in services and controllers:

```csharp
public class OrderService(IOrderRepository repository, ILogger<OrderService> logger)
{
    public async Task<Order?> GetAsync(Guid id, CancellationToken ct = default)
    {
        logger.LogDebug("Loading order {Id}", id);
        return await repository.FindAsync(id, ct);
    }
}
```

### Capturing semantics

- A parameter used in a member body is **captured**: the compiler synthesizes an unspeakable private field holding it. You never declare that field.
- Captured parameters are **not `readonly`** — an accidental reassignment inside a member body compiles (at most a nullability warning when assigning `null`). This is the main semantic difference from the classic `private readonly` field pattern.
- **Double-capture trap:** initializing your own field from a parameter *and* also using the parameter elsewhere in member bodies stores two copies that can drift apart. The compiler warns (CS9124) only for the field-initializer case; the same drift caused by an assignment inside a member body goes un-warned. Either way, treat it as a defect: if you put the parameter into a field, use only the field afterwards.

### `class` vs. `record` primary constructors

- On a plain `class`, primary-constructor parameters produce **nothing public** — no properties, no equality members; a parameter used in member bodies becomes a private capture, nothing more.
- On a `record class`, the same parameter list generates public `init`-only properties and deconstruction; value-based equality comes from being a `record`, primary constructor or not. (A positional `record struct` generates mutable `get`/`set` properties unless declared `readonly record struct`.) Use record primary constructors for DTO shapes (see the `required` + `init` section below); use `class` primary constructors for behavior-bearing services.

### Decision rules

- Parameters are only stored and used (typical DI service or controller) → **primary constructor**, use the parameters directly. Do not add mirror fields.
- You need a `readonly` guarantee or a guard clause → primary constructor plus assignment to a `private readonly` field (`private readonly IOrderRepository _repository = repository ?? throw new ArgumentNullException(nameof(repository));`), then use only the field. A classic constructor is equally valid here — follow the project's existing style.
- Multiple constructors/overloads, or construction logic beyond guard clauses → **classic constructor**. Extra constructors next to a primary one must chain to it via `: this(...)` — workable for simple defaults, awkward once the overloads stop sharing one initialization path.
- Middleware: inject scoped services via `InvokeAsync` parameters, not the primary constructor — see the `dotnet-aspnet` skill, `references/middleware.md`, for why.

## `required` Properties + `init`-Only Setters

Force callers to supply mandatory values at object initialization; prevent mutation afterward.

```csharp
public record CreateOrderRequest
{
    public required string CustomerId { get; init; }
    public required IReadOnlyList<OrderItem> Items { get; init; }
    public string? Notes { get; init; }
}

var req = new CreateOrderRequest
{
    CustomerId = "C-123",
    Items = items,
};
```

- Combine with `record` for value-semantics DTOs.
- `required` runs at compile time — the compiler refuses initialization expressions that omit a required member.
- Use `init` (not `set`) for immutable-after-construction shape.

## Nullable Reference Types

Enable project-wide in the `.csproj`:

```xml
<Nullable>enable</Nullable>
```

- Declare a reference type as nullable explicitly: `string?` means "may be null", `string` means "guaranteed non-null".
- Treat nullable warnings as errors (`<TreatWarningsAsErrors>true</TreatWarningsAsErrors>`) in new projects.
- For legacy code being migrated, use `<Nullable>annotations</Nullable>` first (annotations only, no warnings) to add types incrementally, then flip to `enable`.
- Use the null-forgiving `!` operator only at provable-non-null boundaries (post-validation, after `ArgumentNullException.ThrowIfNull`). Do not sprinkle it to silence warnings.

## `CancellationToken` Propagation

Every async method takes a `CancellationToken` as its **last** parameter and forwards it to every async call it makes.

```csharp
public async Task<Order?> GetByIdAsync(Guid id, CancellationToken ct = default)
{
    var dto = await _db.Orders
        .AsNoTracking()
        .FirstOrDefaultAsync(o => o.Id == id, ct);
    return dto is null ? null : await _mapper.MapAsync(dto, ct);
}
```

- Parameter is named `ct` or `cancellationToken` consistently within a codebase.
- Use `= default` on public API surfaces (library and service methods) so callers without a token can still call cleanly; **forward** the received token to every downstream async call — never re-default mid-chain and never substitute `CancellationToken.None`.
- In ASP.NET Core, `HttpContext.RequestAborted` is automatically bound to action parameters of type `CancellationToken`.
- Never swallow `OperationCanceledException` — let it bubble. The host treats it as expected cancellation.

## `ConfigureAwait(false)`

**Rule:** in library code (NuGet packages, SDKs, reusable class libraries), call `.ConfigureAwait(false)` on every `await`. In server and headless application code (ASP.NET Core endpoints and services, Worker Services, console apps, tests), do not. In GUI application code (WPF, WinForms, MAUI, Avalonia), it depends on what follows the `await` — see below.

```csharp
// Library method — every await opts out of context capture
public async Task<Repository> GetRepositoryAsync(string owner, CancellationToken ct = default)
{
    var response = await _httpClient.GetAsync($"repos/{owner}", ct).ConfigureAwait(false);
    return await ParseAsync(response, ct).ConfigureAwait(false);
}
```

- **Why libraries opt out:** a library can be consumed from contexts that install a `SynchronizationContext` (UI frameworks, legacy ASP.NET). Continuing on that captured context costs scheduling and can deadlock consumers that block on the returned task (sync-over-async). The library itself never needs the caller's context.
- **Why server/headless apps don't bother:** ASP.NET Core, the Generic Host, and plain console apps have no `SynchronizationContext` — there is nothing to capture, so `.ConfigureAwait(false)` is inert noise there. Test code counts as application code.
- **GUI apps sit in between:** WPF, WinForms, MAUI, and Avalonia install a `SynchronizationContext` on the UI thread, so `ConfigureAwait(false)` genuinely matters there. Use it on every `await` whose continuation does not touch the UI (services, helpers, I/O paths); omit it where the code after the `await` updates controls or view state — that continuation must resume on the UI thread. The same captured context is why blocking with `.Result`/`.Wait()` on the UI thread deadlocks.
- Apply it consistently within a library: one context-capturing `await` in a call chain is enough to reintroduce the risk.

## File-Scoped Namespaces (since C# 10)

```csharp
namespace MyCompany.MyProduct.Orders;

public class OrderService { /* ... */ }
```

Default for all new files. Removes one level of indentation across the file.

## `global using` Directives

Centralize common imports in `GlobalUsings.cs`:

```csharp
global using System;
global using System.Collections.Generic;
global using System.Threading;
global using System.Threading.Tasks;
global using Microsoft.Extensions.DependencyInjection;
global using Microsoft.Extensions.Options;
```

Use the SDK-provided `<ImplicitUsings>enable</ImplicitUsings>` for the default set; add project-specific globals via explicit `global using` declarations.
