# Authentication & Authorization

## JWT Bearer Authentication

Requires the `Microsoft.AspNetCore.Authentication.JwtBearer` NuGet package (use the `dotnet-nuget-manager` skill).

```csharp
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.Authority = builder.Configuration["Auth:Authority"];
        options.Audience = builder.Configuration["Auth:Audience"];
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ClockSkew = TimeSpan.FromMinutes(1), // default is 5 minutes
        };
    });

// ...
app.UseAuthentication();
app.UseAuthorization();
```

- Authority/Audience come from configuration — never hard-code them.
- Issuer signing keys are resolved automatically from the Authority's OIDC metadata endpoint.

## Authorization Policies

```csharp
builder.Services.AddAuthorizationBuilder()
    .AddPolicy("AdminOnly", policy => policy.RequireRole("Admin"))
    .AddPolicy("CanEditOrder", policy =>
        policy.Requirements.Add(new OrderOwnerRequirement()));
```

- Use policy-based authorization over role checks in attributes
- Apply `[Authorize]` at controller level, `[AllowAnonymous]` for exceptions
- For minimal APIs use `.RequireAuthorization("PolicyName")`

## Resource-Based Authorization (IAuthorizationHandler)

Role checks cannot answer "may THIS user edit THIS order". Implement a requirement + handler pair for the `CanEditOrder` policy above:

```csharp
public class OrderOwnerRequirement : IAuthorizationRequirement { }

public class OrderOwnerHandler : AuthorizationHandler<OrderOwnerRequirement, Order>
{
    protected override Task HandleRequirementAsync(
        AuthorizationHandlerContext context,
        OrderOwnerRequirement requirement,
        Order order)
    {
        var userId = context.User.FindFirstValue(ClaimTypes.NameIdentifier);
        if (userId is not null && order.OwnerId == userId)
            context.Succeed(requirement);

        return Task.CompletedTask;
    }
}

builder.Services.AddSingleton<IAuthorizationHandler, OrderOwnerHandler>();
```

Evaluate against the loaded resource via `IAuthorizationService`:

```csharp
[ApiController]
[Route("api/orders")]
[Authorize]
public class OrdersController(
    IOrderService orders,
    IAuthorizationService authorization) : ControllerBase
{
    [HttpPut("{id:guid}")]
    public async Task<IActionResult> Update(Guid id, UpdateOrderRequest request, CancellationToken ct)
    {
        var order = await orders.GetByIdAsync(id, ct);
        if (order is null)
            return NotFound();

        var result = await authorization.AuthorizeAsync(User, order, "CanEditOrder");
        if (!result.Succeeded)
            return Forbid();

        // proceed with the update
        return NoContent();
    }
}
```

- **Do NOT put `[Authorize(Policy = "CanEditOrder")]` on the action** — the attribute runs before the order is loaded, so the handler never receives a resource and the policy silently cannot succeed. Resource-based policies are evaluated imperatively via `IAuthorizationService.AuthorizeAsync(user, resource, policyName)`.
- Register handlers as singletons; use `AddScoped` only when the handler depends on scoped services (e.g. a `DbContext`).
- A handler that does not call `context.Succeed` simply leaves the requirement unmet — call `context.Fail()` only to veto other handlers of the same requirement.
