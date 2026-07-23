---
name: angular-library-builder
description: Generates complete Angular libraries / client SDKs with DI support, a provideXxx() entry point, typed HttpClient services, typed configuration, and typed errors. Use when asked to create an Angular library, build an Angular client SDK, wrap a REST API in a typed Angular service, or generate a publishable ng-packagr library. Invokes angular-tsdoc for documentation and angular-tester for tests.
---

# Angular Library / Client SDK Builder

Generate complete, production-ready Angular libraries from existing TypeScript services or API documentation. The output follows Angular library conventions (ng-packagr, secondary entry points, `provideXxx()` APIs) with full DI support, testability via injectable services, and idiomatic Angular patterns.

## When to Use

- Building a new Angular library or client SDK from existing TypeScript code, OpenAPI/Swagger specs, or REST API docs
- Wrapping a REST API in a typed Angular service with a DI entry point (`provideXxx(...)`)
- Generating typed `HttpClient` services with typed configuration and typed errors
- Producing libraries that follow Angular packaging conventions (buildable library, correct peer dependencies)

## Workflow Overview

Follow these steps in order. See the reference files for detailed guidance on each phase.

### Step 1: Analyze Input

Determine what the input is:

- **Existing TypeScript code**: Read and understand the public API surface, method signatures, and responsibilities.
- **Documentation** (OpenAPI, Swagger JSON/YAML, Markdown): Parse endpoints, request/response models, authentication, and error responses.

### Step 2: Determine Angular & Workspace Version

1. Read the workspace `package.json` and `angular.json`.
2. Note the Angular major version (drives standalone/`provideXxx` APIs, signals, control flow).
3. Confirm `strict` mode in `tsconfig.json`; if off, enable strict null checks for the library's own `tsconfig`.
4. Confirm the workspace is set up for libraries (an Angular CLI workspace with `projects`). If not, create one (`ng new <ws> --create-application=false`).

### Step 3: Determine Target Library Project

1. If the user specified a library project → use it.
2. If none specified → scan `angular.json` for existing `projectType: "library"` projects.
3. If a candidate is found → **ask the user** before adding files to it.
4. If no suitable library exists → create one with `ng generate library <name>`. See [project-setup.md](references/project-setup.md) for conventions.

### Step 4: Derive Names

Derive the service/client name from the input:

| Input | Derived Name Example |
|---|---|
| `GitHubService` class | `GitHub` → `GitHubClient`, `provideGitHub(...)`, `GITHUB_CONFIG` |
| `PaymentsApi` class | `Payments` → `PaymentsClient`, `providePayments(...)`, `PAYMENTS_CONFIG` |
| OpenAPI `title: Stripe API` | `Stripe` → `StripeClient`, `provideStripe(...)`, `STRIPE_CONFIG` |

If the name cannot be derived with confidence → ask the user. Provide an `abstract class XxxClient` token when the implementation should be substitutable (testing/mocking); otherwise the concrete class is the token.

### Step 5: Ask About Resilience

Before generating HTTP code, ask:

> "Should resilience (retry with backoff, timeout) be added — via RxJS (`retry`, `timeout`) in the service, or as a provided HTTP interceptor consumers can opt into?"

If yes → add a retry/timeout pipeline. See [http-client-patterns.md](references/http-client-patterns.md#resilience).

### Step 6: Ask About Existing Types Used as Arguments or Return Values

When wrapping existing TypeScript code, identify all types used directly as method parameters or return values.

For each such type, ask the user **once** (grouped into a single question):

> "The following types from the source are used directly as parameters or return values:
> - `OrderRequest` (argument of `placeOrder`)
> - `ProductDto` (return value of `getProduct`)
> - ...
>
> Should these be re-exported as-is (reused from the source), or should new equivalents be generated in the library?"

**Options and consequences:**

| Choice | When to recommend | What to generate |
|---|---|---|
| **Re-export** | Source types live in a shared package consumers already depend on | No new model code; re-export source types from the public API |
| **Generate new types** | Source types are app-internal or consumers should not depend on the source project | New model interfaces/types in `models/`; add mapping functions between source and library types |

If generating new types, apply the same conventions as for response DTOs (see [http-client-patterns.md](references/http-client-patterns.md)). Add private mapper functions to convert between the source type and the library type.

### Step 7: Generate Library Code

Generate all components. See [di-patterns.md](references/di-patterns.md) and [http-client-patterns.md](references/http-client-patterns.md) for full patterns.

**Required components:**

| Component | Description |
|---|---|
| `XxxClient` service | Injectable typed `HttpClient` wrapper (the public contract) |
| `provideXxx(config)` | `EnvironmentProviders` entry point (DI registration) |
| `XxxConfig` + `XXX_CONFIG` token | Configuration via the typed-config/InjectionToken pattern |
| `XxxError` (+ subtypes) | Typed errors with status code, message, and response body |
| Model types | Request/response DTO interfaces/types |
| Public API (`public-api.ts`) | Barrel exporting only the intended public surface |

**Peer dependencies (not direct deps):** `@angular/core`, `@angular/common` (for `HttpClient`), and `rxjs`. Use the `angular-package-manager` skill to add any extra dependencies; do not hand-edit `package.json`.

### Step 8: Document the Code

After generating all source files, invoke the `angular-tsdoc` skill to add TSDoc comments to all public types and members.

### Step 9: Write Tests

After documentation is complete, invoke the `angular-tester` skill to generate unit tests for the library (using `provideHttpClient()` + `provideHttpClientTesting()` and `HttpTestingController`; the `HttpClientTestingModule` is deprecated).

## Key Design Principles

- **Injectable services**: The public client is an `@Injectable` service; provide an `abstract class` token when substitution is required.
- **Typed config**: Configuration always via the `XXX_CONFIG` `InjectionToken` and `provideXxx()`, never magic strings scattered through the code.
- **`HttpClient` only**: Never use `fetch`/`XMLHttpRequest` directly; use Angular's `HttpClient` so interceptors, testing, and SSR work.
- **Typed errors**: HTTP errors become typed errors with status code, reason, and response body.
- **Strict null safety**: The library compiles under `strict`.
- **No global/static state**: All state via DI; no module-level singletons.
- **Tree-shakable**: Side-effect-free; `provideXxx()` is the only entry point.

## Additional Resources

- **[di-patterns.md](references/di-patterns.md)** — `provideXxx()` entry point, typed-config token, injectable service registration
- **[http-client-patterns.md](references/http-client-patterns.md)** — `HttpClient` typed services, resilience (retry/timeout), typed errors, DTO models
- **[project-setup.md](references/project-setup.md)** — `ng generate library`, folder layout, `public-api.ts`, ng-packagr & peer-dependency conventions

## Related Skills

- **[angular-fundamentals](../angular-fundamentals/SKILL.md)** — Provides the DI and typed-config patterns this skill emits in generated libraries
- **[angular-tsdoc](../angular-tsdoc/SKILL.md)** — Invoked in Step 8 to document generated libraries with TSDoc
- **[angular-tester](../angular-tester/SKILL.md)** — Invoked in Step 9 to generate unit tests
- **[angular-package-manager](../angular-package-manager/SKILL.md)** — Invoked in Step 7 to add library dependencies
- **[angular-components](../angular-components/SKILL.md)** — Consumes the generated typed clients from components and interceptors
