# ai-store

A curated collection of [Agent Skills](https://code.claude.com/docs/en/skills) for Claude Code and compatible AI coding agents, organized by technology stack.

Each skill is a self-contained `SKILL.md` file that teaches the agent a specific workflow or set of best practices — from implementing .NET features and reviewing Angular code to writing Gherkin scenarios and refactoring safely. Skills are loaded automatically when relevant, or can be invoked explicitly by name.

The repository currently contains **39 skills** in six categories:

| Category | Skills | Focus |
|---|---|---|
| [Angular](skills/angular) | 11 | Angular development, testing, reviews, libraries |
| [.NET](skills/dotnet) | 11 | .NET/C# development, ASP.NET Core, EF Core, NuGet |
| [General](skills/general) | 7 | Language-agnostic workflows: reviews, BDD, docs, prompts |
| [Development](skills/development) | 5 | Requirement engineering, diagnosis, and code quality: interview-driven specifications, traceable development plans, plan-driven implementation, root-cause bug diagnosis, and evidence-driven refactoring |
| [Java](skills/java) | 4 | Spring Boot, JUnit 5, Javadoc |
| [TypeScript](skills/typescript) | 2 | Jest, RxJS |

## Plugins

The skills are also distributed as **plugins** through a marketplace in this repository. A plugin
bundles a whole category of skills, installs with a single command, and updates in place. Plugins
work in both **Claude Code** and the **GitHub Copilot CLI** — the two read the same
`.claude-plugin/` manifests, so there is only one set of files to maintain.

| Plugin | Skills | Contents |
|---|---|---|
| `cc-ai-dev` | 5 | The complete [Development](skills/development) category: `create-dev-spec`, `create-dev-plan`, `implement-dev-plan`, `diagnose-bug`, `refactor` |

### Claude Code

```bash
/plugin marketplace add CreativeCodersTeam/ai-store
/plugin install cc-ai-dev@creativecoders-ai-store
```

Claude Code namespaces plugin skills with the plugin name, so they are invoked as
`/cc-ai-dev:create-dev-spec`.

### GitHub Copilot CLI

```bash
copilot plugin marketplace add CreativeCodersTeam/ai-store
copilot plugin install cc-ai-dev@creativecoders-ai-store
```

Copilot does **not** namespace plugin skills — they appear under their plain name
(`create-dev-spec`). Copilot resolves skills in the order `.github/skills/` → `.agents/skills/` →
`.claude/skills/` → plugins, and the first one loaded wins. If you already installed these skills
with `npx skills add` (see [Installation](#installation)), that copy shadows the plugin's and the
plugin version is ignored without any error. **Pick one installation method, not both.**

### Updating and removing

Plugins are not version-pinned; each update pulls the current state of `main`.

```bash
claude plugin update cc-ai-dev
claude plugin uninstall cc-ai-dev@creativecoders-ai-store
claude plugin marketplace remove creativecoders-ai-store

copilot plugin update cc-ai-dev
copilot plugin uninstall cc-ai-dev
copilot plugin marketplace remove creativecoders-ai-store
```

### Installing declaratively for a team

Instead of installing interactively, commit the plugin into a repository's settings so everyone on
the project gets it automatically.

```jsonc
// .claude/settings.json — Claude Code
{
  "extraKnownMarketplaces": {
    "creativecoders-ai-store": {
      "source": { "source": "github", "repo": "CreativeCodersTeam/ai-store" }
    }
  },
  "enabledPlugins": { "cc-ai-dev@creativecoders-ai-store": true }
}
```

```jsonc
// .github/copilot/settings.json — GitHub Copilot CLI
{
  "enabledPlugins": ["cc-ai-dev@creativecoders-ai-store"]
}
```

## Installation

Individual skills — including those not yet bundled into a plugin — are installed with the
[Skills CLI](https://github.com/vercel-labs/skills) (`npx skills`). It requires Node.js and works
with Claude Code, Codex, Cursor, OpenCode, and many other agents.

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
ln -s "$(pwd)/ai-store/skills/development/refactor" ~/.claude/skills/refactor

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
| `create-readme` | Generates professional README files following OSS conventions |
| `convert-plaintext-to-md` | Converts plain text or legacy documentation to Markdown |
| `gherkin-bdd` | Writing Gherkin feature files and step definitions (Reqnroll, Cucumber) |
| `gherkin-bdd-reviewer` | Reviews existing Gherkin/BDD files against best practices |

### Development

| Skill | Description |
|---|---|
| `create-dev-spec` | Turns a rough requirement into an approved specification through a structured interview, a reviewable draft in `docs/draft/`, and a final spec in `docs/specs/` |
| `create-dev-plan` | Turns an approved spec (or a requirement) into a reviewed development plan in `docs/plans/`: tasks with dependencies, interfaces, and a traceability matrix linking every requirement to the test that proves it |
| `implement-dev-plan` | Implements an approved plan from `docs/plans/` task by task: consistency check against the spec, runtime skill discovery, sub-agent or direct implementation with per-task verification, independent review with rework loop, report in `docs/implementation/`. Never commits |
| `diagnose-bug` | Finds and proves the root cause of a bug instead of its symptom: reproduction test first, every claim verified against experiments, repository history, and the installed library version, refuted causes recorded, then a self-contained report in `docs/bugs/` with a causal chain and ranked fix proposals. Never implements the fix, never commits |
| `refactor` | Improves the structure of existing code in a defined scope without changing behaviour: smell analysis with `file:line` evidence, a prioritised report in `docs/refactoring/`, user-selected candidates, a coverage gate per candidate, then one named refactoring per step with build, test, and lint verification and rollback on red. Never fixes bugs along the way, never commits |

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
.claude-plugin/
└── marketplace.json              # the plugin catalog; read by Claude Code and Copilot CLI
scripts/
└── validate-skills.sh            # checks every SKILL.md and plugin manifest
skills/
├── angular/
│   ├── angular/
│   │   └── SKILL.md
│   ├── angular-dev/
│   │   └── SKILL.md
│   └── ...
├── development/                  # also the root of the `cc-ai-dev` plugin
│   ├── .claude-plugin/
│   │   └── plugin.json           # lists the skills the plugin ships
│   ├── create-dev-spec/
│   └── ...
├── dotnet/
├── general/
├── java/
├── typescript/
└── tests/                        # test artifacts, mirroring the tree above
    ├── dotnet/
    │   ├── dotnet-reviewer/      # tests for that one skill
    │   └── _shared/              # tests covering the whole .NET family
    └── ...
```

Every skill lives in `skills/<category>/<skill-name>/SKILL.md`. Some skills ship additional reference files or scripts alongside their `SKILL.md`.

Tests are not skill siblings. They live under `skills/tests/<category>/<skill-name>/`, mirroring the skill tree from a separate root — so a category folder contains only skills and installing one with `npx skills add …/skills/dotnet -s '*'` never pulls in test material.

A category that is also published as a plugin carries a `.claude-plugin/plugin.json` at its root. The plugin root is the category directory itself, so nothing is duplicated — the plugin ships exactly the skill directories it lists.

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
   Tests are the exception: they go to `skills/tests/<category>/<skill-name>/`, never next to the
   `SKILL.md`.
4. Keep `description` **at or below 1024 characters**. This is a hard limit in the
   [Agent Skills specification](https://agentskills.io/specification): GitHub Copilot drops a skill
   whose description exceeds it, without printing any error, while Claude Code loads it anyway — so
   the defect is invisible unless you check for it.
5. If the category is published as a plugin, add the new skill to its
   `skills/<category>/.claude-plugin/plugin.json`, otherwise it will not ship with the plugin.
6. Run the validator and make sure it passes:

   ```bash
   bash scripts/validate-skills.sh
   ```

   It verifies frontmatter, the 1024-character limit, that `name` matches the directory name, and
   that every plugin manifest lists exactly the skills present on disk. Exit codes: `0` all checks
   passed, `1` validation failures, `2` usage error or missing dependency.
7. Update the category counts table and the "Available Skills" table above, and the family router
   `SKILL.md` if the category has one.
8. Open a pull request.
