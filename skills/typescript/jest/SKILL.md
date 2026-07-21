---
name: jest
description: Best practices for writing JavaScript and TypeScript tests with Jest. Use when asked to write unit tests, improve test coverage, set up mocking, test async code, or test React components with Testing Library. Covers test structure, mock strategies, snapshot testing, and common Jest matchers.
---

# Jest Testing Best Practices

## Test Structure
- Name test files with `.test.ts` or `.test.js` suffix
- Place test files next to the code they test or in a dedicated `__tests__` directory
- Use descriptive test names that explain the expected behavior
- Use nested describe blocks to organize related tests
- Follow the pattern: `describe('Component/Function/Class', () => { it('should do something', () => {}) })`

## Effective Mocking
- Mock external dependencies (APIs, databases, etc.) to isolate your tests
- Use `jest.mock()` for module-level mocks
- Use `jest.spyOn()` for specific function mocks
- Use `mockImplementation()` or `mockReturnValue()` to define mock behavior
- Reset mocks between tests with `jest.resetAllMocks()` in `afterEach`

## Testing Async Code
- Always return promises or use async/await syntax in tests
- Use `resolves`/`rejects` matchers for promises
- Set appropriate timeouts for slow tests with `jest.setTimeout()`

## Snapshot Testing
- Use snapshot tests for UI components or complex objects that change infrequently
- Keep snapshots small and focused
- Review snapshot changes carefully before committing

## Testing React Components
- Use React Testing Library over Enzyme for testing components
- Test user behavior and component accessibility
- Query elements by accessibility roles, labels, or text content
- Use `userEvent` over `fireEvent` for more realistic user interactions

