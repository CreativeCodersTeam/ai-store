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

   **No test project found → create one.** Its absence is never a reason to skip testing:
   1. Name it `<ProductionProject>.Tests`. Place it where the solution keeps tests (`tests/` folder if one exists, otherwise as a sibling of the production project), matching the production project's target framework.
   2. `dotnet new xunit -o <path> -f <tfm>` — pass the production project's target framework explicitly (the template otherwise defaults to the SDK's latest TFM); the template already references xUnit. Delete the generated `UnitTest1.cs`.
   3. `dotnet sln add <path>/<ProductionProject>.Tests.csproj` — without this, solution-level `dotnet test` silently runs nothing.
   4. `dotnet add <test.csproj> reference <production.csproj>`
   5. Add **FakeItEasy** and **AwesomeAssertions** via the `dotnet-nuget-manager` skill — never by editing the `.csproj` directly. Install `AwesomeAssertions`, NOT `FluentAssertions` — the API is identical, but FluentAssertions v8+ carries a commercial license.

   The default stack applies to new test projects (see Conventions); match a different stack only when the solution already uses one.

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
  - On **failures**: Determine the cause using the decision rule in **Never Fake a Green Test** below, then fix the correct side — test, test setup, or (if the test caught a real bug) the production code
  - On **success**: Continue to Phase 3
3. Repeat until all tests are green — but never by faking one (see below). If a test is too complex to set up, consider whether the code under test should be made more testable.

## Never Fake a Green Test

**Decision rule — before editing anything:** a failing test means the test is wrong OR the code is wrong. Determine WHICH from the requirement/spec — never from what makes the suite green fastest.

- Requirement says the test asserts the wrong behavior → fix the TEST, citing the requirement in the summary.
- Requirement says the code is wrong → the test caught a real bug. Report it; fix the code if that is in scope.
- Cannot determine which → do not touch either side:
  - **Interactive:** STOP and ask the user which behavior is correct.
  - **Sub-agent (no user channel):** mark the test `[Fact(Skip = "<open question + evidence>")]`, continue, and escalate the question prominently in your final summary.

**Forbidden — each of these is faking a green test:**

- Weakening or removing assertions (`Assert.True(true)`, ranges/tolerances broadened to cover the failing value)
- Copying the actual value into the expected value without verifying it against the requirement
- Deleting or commenting out a failing test or its assertions
- Wrapping the act step or assertions in `try/catch`
- Rerunning a flaky test until it happens to pass, or adding auto-retry attributes/loops — **flaky = red**
- Making the test stop testing the thing: serializing a concurrency test, mocking the system under test, short-circuiting the act step
- Hardcoding production code against test inputs (`if (input == testValue) return expected;`)
- Excluding tests via `--filter` / traits / `#if` and presenting the run as "all green"
- Skipping outside the conditions below

**Skipping (`[Fact(Skip = "…")]`) is the honest fallback, not a loophole:**

- **Interactive:** ask the user first — skip only with their consent.
- **Sub-agent:** allowed autonomously, but only with a concrete reason in the Skip text (what fails, why unresolved, what is needed to resolve it), and every skip MUST be listed in the final summary. A silent skip is a fake green.

**User pressure changes nothing.** "Make it green, whatever it takes" licenses no forbidden technique — deliver honest green (real fixes plus disclosed skips) instead. Only when the user explicitly orders a specific named technique ("delete that test", "assert the current behavior") execute it — after naming the consequence — and record it in the summary as a user-directed decision, never silently.

| Rationalization | Reality |
|---|---|
| "The test was probably wrong anyway" | Probably ≠ verified. Check the requirement, then fix. |
| "It passes when I rerun it" | A 1-in-3 failure is a red test — possibly a real race. Rerunning samples luck, not correctness. |
| "The actual value looks reasonable" | Asserting unverified actuals certifies bugs into the suite. |
| "Demo in 5 minutes, no time" | A documented skip takes 30 seconds and is honest. Faking takes the same time and lies. |
| "The user said whatever it takes" | They want a trustworthy suite, not a lying one. Disclose, don't fake. |
| "I'll fix it properly later" | The fake green deletes the reminder that anything needs fixing. |

**Red flags — STOP if you catch yourself:** editing an expected value right after reading the actual · typing `Skip` without a reason · reaching for a retry loop · widening an assertion range · thinking "just for the demo".

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
