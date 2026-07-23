# Reqnroll (.NET) Implementation

Reqnroll is the BDD framework for .NET; binding attributes live in the `Reqnroll`
namespace.

## Setup

Add packages to the test project (`.csproj`):
```xml
<ItemGroup>
  <PackageReference Include="Reqnroll.xUnit" Version="2.*" />
  <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.*" />
  <PackageReference Include="xunit" Version="2.*" />
  <PackageReference Include="xunit.runner.visualstudio" Version="2.*" />
</ItemGroup>
```
Place `.feature` files in the test project; their build action is `Reqnroll feature`
(set automatically by the package).

## Step Definitions

A `[Binding]` class holds the steps. Attributes use regex or cucumber expressions.
```csharp
using Reqnroll;

[Binding]
public class CheckoutSteps
{
    private readonly Cart _cart = new();

    [Given(@"the cart contains a ""(.*)""")]
    public void GivenTheCartContainsA(string item) => _cart.Add(item);

    [When(@"the user checks out")]
    public void WhenTheUserChecksOut() => _cart.Checkout();

    [Then(@"the order total is (\d+)")]
    public void ThenTheOrderTotalIs(int total) =>
        Assert.Equal(total, _cart.Total);
}
```

## Sharing State

Use constructor injection (Reqnroll's context injection) to share state between
binding classes — one instance per scenario:
```csharp
public class CheckoutSteps
{
    private readonly Cart _cart;
    public CheckoutSteps(Cart cart) => _cart = cart; // Cart resolved per scenario
}
```

## Hooks

```csharp
[Binding]
public class Hooks
{
    [BeforeScenario]
    public void BeforeScenario() { /* arrange */ }

    [AfterScenario]
    public void AfterScenario() { /* cleanup */ }
}
```

## Run

```bash
dotnet test
# Filter by tag:
dotnet test --filter "Category=smoke"   # @smoke tag maps to xUnit trait "Category"
```
Expected: test output lists each scenario as a passing test.
