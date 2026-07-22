---
name: dotnet-tester
description: Use when creating unit tests, adding tests, or improving test coverage for C#/.NET code, when new production code lacks tests, or when an existing suite is missing edge cases or error paths — projects using xUnit, FakeItEasy, AwesomeAssertions, FluentAssertions, NUnit, MSTest, or Moq. Not for non-.NET code or integration tests that only exercise external systems.
---

# .NET Tester

Write comprehensive unit tests for the specified code. Follow a multi-step process with automatic identification of missing test cases.

## When to Use

- User asks to create unit tests, add tests, or improve test coverage for C#/.NET code
- New C#/.NET production code lacks tests and needs them
- An existing test suite is missing edge cases or error-path coverage
- Working in a C# project that uses xUnit, FakeItEasy, AwesomeAssertions/FluentAssertions, NUnit, MSTest, or Moq

Do **not** use this skill for non-.NET test code, or for integration tests that primarily exercise external systems without unit-level concerns.

## Conventions

- **Test Framework**: xUnit
- **Mocking**: FakeItEasy
- **Assertions**: AwesomeAssertions (a fork of FluentAssertions with identical API — use `Should()` as usual)
- **Structure**: Each test method has Arrange/Act/Assert blocks, marked with comments
- **Language**: English for code, comments, and test names
- **Style**: The stack above is the default. If the project already uses a different stack (NUnit, MSTest, Moq, FluentAssertions, …), match the existing convention instead of switching.

## Phase 1: Write Tests

1. **Analyze code**: Read the code to be tested and understand:
  - Public API (methods, properties)
  - Dependencies (what needs to be mocked?)
  - Different code paths (if/else, switch, exceptions)
  - Edge Cases (null, empty collections, boundary values)

2. **Identify test project**: Find the appropriate test project by looking for `*.Tests.csproj` files or `*Tests/` directories in the solution. Fall back to scanning for any project whose name ends in `.Tests` or `.Test`. Orient yourself to the existing project structure before adding files.

3. **Create tests**: Write tests following this pattern:

```csharp
public class MyClassTests
{
    [Fact]
    public void MethodName_Scenario_ExpectedBehavior()
    {
        // Arrange
        var dependency = A.Fake<IDependency>();
        A.CallTo(() => dependency.DoSomething()).Returns(expectedValue);
        var sut = new MyClass(dependency);

        // Act
        var result = sut.MethodUnderTest(input);

        // Assert
        result.Should().Be(expectedValue);
    }

    [Theory]
    [InlineData("input1", "expected1")]
    [InlineData("input2", "expected2")]
    public void MethodName_WithVariousInputs_ReturnsExpected(string input, string expected)
    {
        // Arrange
        var sut = new MyClass();

        // Act
        var result = sut.MethodUnderTest(input);

        // Assert
        result.Should().Be(expected);
    }
}
```

4. **Cover test categories**:
  - Happy Path (normal success case)
  - Error handling (exceptions, invalid inputs)
  - Null/empty inputs
  - Boundary values (boundary conditions)
  - Dependency behavior (mocks, different return values)

## Phase 2: Execute Tests

1. Run `dotnet test` in the relevant test project
2. Analyze the results:
  - On **failures**: Identify the cause and fix the test or test setup
  - On **success**: Continue to Phase 3
3. Repeat until all tests are green. Don't fakely pass tests. If a test is too complex to set up, consider if it should be refactored or if the code under test should be made more testable.

## Phase 3: Identify Missing Test Cases

Start a **separate agent** that reads the production code and the tests written in Phase 1, then returns a prioritized list of missing cases. The agent is stateless — the dispatch prompt must carry everything. Use this template (fill in the paths):

> Analyze C# test coverage. You have no prior context — everything you need is below.
>
> Production code (read in full): `<absolute paths of the files under test>`
> Tests (read in full): `<absolute paths of the test files from Phase 1>`
> You may also read fixtures, mocks, or interfaces these files reference when needed to judge coverage.
>
> For every public method, compare its behavior surface against what the tests exercise. Identify MISSING test cases in exactly these categories:
> - Edge Cases: null, empty strings/collections, boundary/maximum values
> - Error Paths: exceptions, timeouts, dependency errors
> - Boundary Conditions: off-by-one, integer overflow
> - Interactions: call order, multiple/concurrent calls
> - State Transitions: different initial states
>
> Return ONLY the prioritized list, sorted HIGH → MEDIUM → LOW, one line per case:
> `[HIGH/MEDIUM/LOW] MethodName - Scenario: Description`
> HIGH = plausible real-bug path, MEDIUM = meaningful robustness gap, LOW = completeness. Do not list already-covered cases, do not write test code, do not modify files, no preamble or commentary. Return an empty list if nothing is missing — do not invent low-value cases to fill it.

## Phase 4: Add Missing Tests

1. Implement the identified missing tests (prioritized: HIGH → MEDIUM → LOW)
2. Run `dotnet test` again
3. Fix any errors
4. Ensure all tests are green

## Output Format

At the end, provide a summary:

```
### Test Result

**Phase 1**: X tests written
**Phase 2**: All tests green ✅
**Phase 3**: Y missing cases identified (Z High, W Medium, V Low)
**Phase 4**: Y additional tests implemented, all green ✅

**Total**: X + Y tests, all passed
```

## Important Notes

- Do **not write tests for trivial getters/setters** without logic
- Do **not write tests to check if properties are initialized correctly after construction**
- Do **not mock value types** or simple DTOs – create real instances
- Test **behavior**, not implementation details
- Use **descriptive test names** in the format `MethodName_Scenario_ExpectedBehavior`
- For `[Theory]` tests: Use `[InlineData]` for simple types, `[MemberData]` for complex objects
- Use `A.CallTo(...).MustHaveHappened()` sparingly – only when the call is the expected behavior

## Related Skills

- **[dotnet-ef-core](../dotnet-ef-core/SKILL.md)** — DbContext-backed test patterns (SQLite in-memory, Testcontainers)
- **[dotnet-sdk-builder](../dotnet-sdk-builder/SKILL.md)** — Invoked by it in Step 9 to generate tests for new SDK libraries

The full skill overview lives in the `dotnet` router skill.
