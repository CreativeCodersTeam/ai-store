# ai-store

A curated collection of [Agent Skills](https://code.claude.com/docs/en/skills) for Claude Code and compatible AI coding agents, organized by technology stack.

Each skill is a self-contained `SKILL.md` file that teaches the agent a specific workflow or set of best practices — from implementing .NET features and reviewing Angular code to writing Gherkin scenarios and refactoring safely. Skills are loaded automatically when relevant, or can be invoked explicitly by name.

The repository currently contains **39 skills** in six categories:

| Category | Skills | Focus |
|---|---|---|
| [Angular](skills/angular) | 11 | Angular development, testing, reviews, libraries |
| [.NET](skills/dotnet) | 11 | .NET/C# development, ASP.NET Core, EF Core, NuGet |
| [General](skills/general) | 8 | Language-agnostic workflows: reviews, refactoring, BDD, docs |
| [Development](skills/development) | 3 | Requirement engineering: interview-driven specifications, traceable development plans, and plan-driven implementation |
| [Java](skills/java) | 4 | Spring Boot, JUnit 5, Javadoc |
| [TypeScript](skills/typescript) | 2 | Jest, RxJS |

## Installation

Skills are installed with the [Skills CLI](https://github.com/vercel-labs/skills) (`npx skills`). It requires Node.js and works with Claude Code, Codex, Cursor, OpenCode, and many other agents.

Use `-g` to install **user-scoped** (e.g. `~/.claude/skills/` for Claude Code, available in all projects). Without `-g`, skills are installed **project-scoped** into the current repository (e.g. `.claude/skills/`).

### Install all skills

```bash
# User-scoped, for Claude Code, no prompts
npx skills add CreativeCodersTeam/ai-store -g -a claude-code -s '*' -y

# Interactive: pick skills and target agents from a list
npx skills add CreativeCodersTeam/ai-store
```

### Install a single skill

```bash
npx skills add CreativeCodersTeam/ai-store -g -a claude-code -s dotnet-dev
```

### Install a whole category

Point the CLI at a subfolder to install everything in it with one command:

```bash
# All 11 .NET skills
npx skills add CreativeCodersTeam/ai-store/skills/dotnet -g -a claude-code -s '*' -y

# All 11 Angular skills
npx skills add CreativeCodersTeam/ai-store/skills/angular -g -a claude-code -s '*' -y
```

The shorthand always resolves to the repository's default branch (`main`). To install from another branch, use the full URL form instead:

```bash
npx skills add https://github.com/CreativeCodersTeam/ai-store/tree/<branch>/skills/dotnet -g -a claude-code -s '*' -y
```

### Useful flags

| Flag | Description |
|---|---|
| `-g, --global` | Install user-scoped instead of into the current project |
| `-a, --agent <agents...>` | Target specific agents (e.g. `claude-code`, `codex`) |
| `-s, --skill <names...>` | Install specific skills by name; `'*'` installs all |
| `-l, --list` | List the skills a source offers without installing |
| `--copy` | Copy files instead of symlinking |
| `-y, --yes` | Skip all confirmation prompts |

To preview what a source contains before installing:

```bash
npx skills add CreativeCodersTeam/ai-store --list
```

### Manual installation

Skills are plain directories — you can also clone the repository and copy or symlink individual skills yourself:

```bash
git clone https://github.com/CreativeCodersTeam/ai-store.git

# User-scoped (all projects)
cp -R ai-store/skills/dotnet/dotnet-dev ~/.claude/skills/

# Or symlink, so `git pull` keeps the skill up to date
ln -s "$(pwd)/ai-store/skills/general/refactoring" ~/.claude/skills/refactoring

# Project-scoped (current repository only)
cp -R ai-store/skills/typescript/jest .claude/skills/
```

Restart Claude Code afterwards and run `/skills` to confirm the skills are loaded.

## Available Skills

### Angular

| Skill | Description |
|---|---|
| `angular` | Entry point that routes to the right specialized Angular skill |
| `angular-dev` | End-to-end implementation workflow for Angular features and bug fixes |
| `angular-fundamentals` | DI and providers, typed configuration, standalone APIs, signals, modern TypeScript idioms |
| `angular-components` | Components, templates, routing, forms, HttpClient, interceptors, guards |
| `angular-state` | State design: signals vs. RxJS vs. NgRx, selectors, change detection |
| `angular-rxjs` | RxJS in modern Angular: combining HttpClient streams, `toSignal`/`toObservable`, `httpResource`/`rxResource` vs. classic RxJS, memory-leak fixes |
| `angular-library-builder` | Publishable Angular libraries and typed API client SDKs (ng-packagr) |
| `angular-tester` | Unit tests with Vitest, Jasmine/Karma, Jest, TestBed, HttpTestingController |
| `angular-reviewer` | Structured Angular code review (explicit invocation only) |
| `angular-package-manager` | npm package management, `ng add`/`ng update`, version verification |
| `angular-tsdoc` | TSDoc/JSDoc comments for public APIs, Compodoc conventions |

### .NET

| Skill | Description |
|---|---|
| `dotnet` | Entry point that routes to the right specialized .NET skill |
| `dotnet-dev` | End-to-end implementation workflow for .NET/C# features and bug fixes |
| `dotnet-fundamentals` | DI lifetimes, IOptions, configuration, modern C# idioms |
| `dotnet-aspnet` | ASP.NET Core APIs: controllers, minimal APIs, middleware, auth, ProblemDetails |
| `dotnet-ef-core` | EF Core: DbContext design, LINQ, migrations, query performance |
| `dotnet-sdk-builder` | Typed C# client SDKs with IHttpClientFactory and DI registration |
| `dotnet-tester` | Unit tests with xUnit, NUnit, MSTest, Moq, FakeItEasy, FluentAssertions |
| `dotnet-reviewer` | Structured .NET code review (explicit invocation only) |
| `dotnet-inspect` | Inspect NuGet packages and DLLs, API diffs between versions |
| `dotnet-nuget-manager` | NuGet package management, including central package management |
| `dotnet-xmldocs` | C# XML documentation comments (`///`) in Microsoft style |

### General

| Skill | Description |
|---|---|
| `implementer` | Language-agnostic 5-phase implementation workflow with review loop |
| `boost-prompt` | Interactively refines vague prompts before execution |
| `code-review` | General code review: quality, security, performance, with severity levels |
| `refactoring` | Behavior-preserving refactoring, verifies tests before and after |
| `create-readme` | Generates professional README files following OSS conventions |
| `convert-plaintext-to-md` | Converts plain text or legacy documentation to Markdown |
| `gherkin-bdd` | Writing Gherkin feature files and step definitions (Reqnroll, Cucumber) |
| `gherkin-bdd-reviewer` | Reviews existing Gherkin/BDD files against best practices |

### Development

| Skill | Description |
|---|---|
| `create-dev-spec` | Turns a rough requirement into an approved specification through a structured interview, a reviewable draft in `docs/draft/`, and a final spec in `docs/specs/` |
| `create-dev-plan` | Turns an approved spec (or a requirement) into a reviewed development plan in `docs/plans/`: tasks with dependencies, interfaces, and a traceability matrix linking every requirement to the test that proves it |
| `implement-feature` | Implements an approved plan from `docs/plans/` task by task: consistency check against the spec, runtime skill discovery, sub-agent or direct implementation with per-task verification, independent review with rework loop, report in `docs/implementation/`. Never commits |

### Java

| Skill | Description |
|---|---|
| `java-springboot` | Spring Boot best practices: REST, JPA, security, testing |
| `create-spring-boot-java-project` | Project scaffolding via Spring Initializr with Docker Compose support |
| `java-junit` | JUnit 5 tests, including parameterized tests and Mockito |
| `java-docs` | Javadoc comments following Java best practices |

### TypeScript

| Skill | Description |
|---|---|
| `jest` | Jest best practices: mocking, async tests, Testing Library |
| `rxjs` | RxJS patterns: operators, subscription management, error handling |

## Repository Structure

```
skills/
├── angular/
│   ├── angular/
│   │   └── SKILL.md
│   ├── angular-dev/
│   │   └── SKILL.md
│   └── ...
├── development/
├── dotnet/
├── general/
├── java/
└── typescript/
```

Every skill lives in `skills/<category>/<skill-name>/SKILL.md`. Some skills ship additional reference files or scripts alongside their `SKILL.md`.

## Contributing

To add a new skill:

1. Create `skills/<category>/<skill-name>/SKILL.md` (add a new category folder if none fits).
2. Start the file with YAML frontmatter containing `name` and `description`:

   ```yaml
   ---
   name: my-skill
   description: Use when ... — a precise trigger description so agents load the skill at the right moment.
   ---
   ```

3. Keep the skill self-contained; put larger reference material in files next to the `SKILL.md`.
4. Open a pull request.
