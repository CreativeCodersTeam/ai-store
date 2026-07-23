---
name: angular-tester
description: Writes, executes, and completes unit tests for Angular/TypeScript code using Jasmine + Karma (or Jest), TestBed, and spies. Uses a second agent to identify missing test cases. Use when asked to create Angular tests or improve test coverage.
---

# Angular Tester

Write comprehensive unit tests for the specified code. Follow a multi-step process with automatic identification of missing test cases.

## When to Use

- User asks to create unit tests, add tests, or improve test coverage for Angular/TypeScript code
- New Angular production code (components, services, pipes, directives, guards) lacks tests and needs them
- An existing test suite is missing edge cases or error-path coverage
- Working in an Angular project that uses Jasmine + Karma, Jest, or `@angular/core/testing` (`TestBed`)

Do **not** use this skill for non-Angular test code, or for end-to-end tests (Cypress, Playwright, Protractor) that primarily exercise the running application rather than units.

## Conventions

- **Test Framework / runner**: Match the project's existing setup. New Angular projects default to **Vitest** (the CLI's default runner from v21; Karma is deprecated and frozen). **Jasmine + Karma** (older CLI default) and **Jest** remain fully supported — detect which is configured and follow it (`jest.fn()`/`vi.fn()` vs Jasmine spies). Do not switch a project's runner as a side effect of writing tests.
- **Test bed**: `TestBed` for components/services that use DI; plain instantiation for pure classes/pipes with no dependencies.
- **Mocking**: `jasmine.createSpyObj` / spy objects for dependencies (`jest.fn()`/`vi.fn()` under Jest/Vitest). For `HttpClient`, register `provideHttpClient()` + `provideHttpClientTesting()` and inject `HttpTestingController` (the `HttpClientTestingModule` is deprecated).
- **Structure**: Each `it` has Arrange/Act/Assert blocks, marked with comments.
- **Language**: English for code, comments, and test names.
- **Style**: The stack above is the default. If the project already uses a different stack (Jest, Spectator, ng-mocks, …), match the existing convention instead of switching.

## Phase 1: Write Tests

1. **Analyze code**: Read the code to be tested and understand:
  - Public API (methods, inputs/outputs — `input()`/`output()`/`model()` or `@Input()`/`@Output()` — exposed signals/observables)
  - Dependencies (which injected services need to be mocked?)
  - Different code paths (if/else, switch, `catchError`, RxJS operators)
  - Edge Cases (null, empty collections, boundary values, error notifications)

2. **Identify test setup**: Angular convention is a co-located `*.spec.ts` next to each unit. Find existing `*.spec.ts` files and the test config (`karma.conf.js`, `jest.config.*`, `angular.json` `test` target) to orient yourself before adding files.

3. **Create tests**: Write tests following these patterns.

**Service with a mocked dependency (Jasmine):**

```typescript
describe('OrderService', () => {
  let service: OrderService;
  let api: jasmine.SpyObj<ApiClient>;

  beforeEach(() => {
    // Arrange
    api = jasmine.createSpyObj<ApiClient>('ApiClient', ['placeOrder']);
    TestBed.configureTestingModule({
      providers: [OrderService, { provide: ApiClient, useValue: api }],
    });
    service = TestBed.inject(OrderService);
  });

  it('should return the confirmed order on success', () => {
    // Arrange
    api.placeOrder.and.returnValue(of({ id: 1 } as Order));

    // Act
    let result: Order | undefined;
    service.place(request).subscribe((o) => (result = o));

    // Assert
    expect(result).toEqual({ id: 1 } as Order);
  });
});
```

**Component with `HttpClient` (HttpTestingController):**

```typescript
describe('UserListComponent', () => {
  let fixture: ComponentFixture<UserListComponent>;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [UserListComponent],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    fixture = TestBed.createComponent(UserListComponent);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpMock.verify());

  it('should render users returned by the API', () => {
    // Act
    fixture.detectChanges(); // triggers ngOnInit
    httpMock.expectOne('/api/users').flush([{ id: 1, name: 'Ada' }]);
    fixture.detectChanges();

    // Assert
    const rows = fixture.nativeElement.querySelectorAll('li');
    expect(rows.length).toBe(1);
  });
});
```

**Parameterized cases** (Jasmine has no `[Theory]` — loop over a data array):

```typescript
([
  ['input1', 'expected1'],
  ['input2', 'expected2'],
] as const).forEach(([input, expected]) => {
  it(`transform("${input}") returns "${expected}"`, () => {
    // Arrange
    const pipe = new SlugPipe();
    // Act
    const result = pipe.transform(input);
    // Assert
    expect(result).toBe(expected);
  });
});
```

4. **Cover test categories**:
  - Happy Path (normal success case)
  - Error handling (error notifications, thrown errors, invalid inputs)
  - Null/empty inputs
  - Boundary values (boundary conditions)
  - Dependency behavior (spies, different return values, error responses)
  - Async behavior (`fakeAsync`/`tick`, `waitForAsync`, observable completion)

## Phase 2: Execute Tests

1. Run the test command for the project: `ng test` (Vitest/Karma, depending on the configured runner), `ng test --watch=false --browsers=ChromeHeadless` (Karma explicitly headless), or `npx jest` / `npx vitest run` (Jest/Vitest). Scope to the relevant spec(s) where possible (`ng test --include='**/order.service.spec.ts'`).
2. Analyze the results:
  - On **failures**: Identify the cause and fix the test or test setup
  - On **success**: Continue to Phase 3
3. Repeat until all tests are green. Don't fakely pass tests. If a test is too complex to set up, consider if it should be refactored or if the code under test should be made more testable (e.g., extract a service, inject a dependency instead of constructing it).

## Phase 3: Identify Missing Test Cases

Start a **separate agent** that reads the production code and written tests, then returns a prioritized list of missing cases:

- **Edge Cases**: Null, empty strings/collections, boundary/maximum values
- **Error Paths**: Error notifications, thrown errors, HTTP error status codes, timeouts
- **Boundary Conditions**: Off-by-one, empty vs single-item collections
- **Interactions**: Call order, multiple/concurrent subscriptions, unsubscription/teardown
- **State Transitions**: Different initial inputs/signal values, change detection after updates

Format: `[HIGH/MEDIUM/LOW] MethodName - Scenario: Description`

## Phase 4: Add Missing Tests

1. Implement the identified missing tests (prioritized: HIGH → MEDIUM → LOW)
2. Run the test command again
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
- Do **not write tests that only assert a component was created** (`expect(component).toBeTruthy()`) as the *only* coverage — assert behavior
- Do **not mock simple value objects or DTOs** – create real instances
- Test **behavior**, not implementation details (assert rendered output / emitted values, not private fields)
- Use **descriptive test names** in the format `MethodName_Scenario_ExpectedBehavior` or a readable `should …` sentence
- Always `httpMock.verify()` in `afterEach` when using `provideHttpClientTesting()`
- Use `fakeAsync` + `tick()` for timer/async control; prefer it over real timeouts
- Verify a spy call (`expect(spy).toHaveBeenCalledWith(...)`) sparingly – only when the call itself is the expected behavior

## Related Skills

- **[angular-fundamentals](../angular-fundamentals/SKILL.md)** — Test DI-registered services by overriding providers in `TestBed`
- **[angular-state](../angular-state/SKILL.md)** — Test RxJS/signal-based state, observables, and effects
- **[angular-reviewer](../angular-reviewer/SKILL.md)** — Test-quality checks during code review
- **[angular-library-builder](../angular-library-builder/SKILL.md)** — Invoked by it to generate tests for new Angular libraries
- **[angular-components](../angular-components/SKILL.md)** — Unit and integration tests for components, forms, and routed views
