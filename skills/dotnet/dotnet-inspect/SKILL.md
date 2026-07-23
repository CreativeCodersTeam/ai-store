---
name: dotnet-inspect
description: Use when answering questions about .NET library contents — which types or members a NuGet package, platform library (System.*, Microsoft.AspNetCore.*), or local .dll/.nupkg file exposes, what changed between two versions, which extension methods or interface implementors exist, or where the source of an API lives.
---

# dotnet-inspect

Query .NET library APIs — the same commands work across NuGet packages, platform libraries (System.*, Microsoft.AspNetCore.*), and local .dll/.nupkg files.

## When to Use / Decision Tree

- **Code broken after an upgrade?** → `diff --package Foo@old..new` first (classifies breaking/additive), then `member` to see the new API
- **What's new in a .NET preview?** → `diff --platform System.Runtime@P2..P3 --additive` per framework library
- **What types are in this package?** → `type --package Foo` (discover), `find` (search by pattern)
- **What members does a type have?** → `member Type --package Foo` (compact table, docs on by default)
- **What does a type look like?** → `type Type --package Foo` (tree view for single type)
- **What are the method signatures?** → `member Type --package Foo -m Method` (full signatures + docs)
- **What is the source/IL?** → `member Type --package Foo -m Method:1 -v:d` (Source, Lowered C#, IL)
- **Where is the source code?** → `source Type --package Foo` (SourceLink URLs); add `-m Member` for line numbers; `--cat` fetches and prints the file contents
- **What constructors exist?** → `member 'Type<T>' --package Foo -m .ctor` (use `<T>` not `<>`)
- **How many overloads?** → `member Type --package Foo --show-index` (shows `Name:N` indices)
- **What extends this type?** → `extensions` (extension methods/properties; `--reachable` for transitive)
- **What implements this interface?** → `implements` (concrete types)
- **What does this depend on?** → `depends` (type hierarchy, `--package` deps, or library refs); `--mermaid` for a diagram
- **What version/metadata does this have?** → `package` / `library`; `Foo --version` (cache-first), `Foo --latest-version` (always NuGet), `Foo --versions` (list all)
- **What TFMs are available?** → `package Foo --tfms`, then `type --package Foo --tfm net8.0`
- **What metadata fields exist?** → `-S Section --fields "PDB*"` (structured query, no DSL)
- **Show me something cool** → `demo` (curated showcase queries)

## Key Patterns

Default output is **markdown** — headings, tables, and field lists that render well in terminals, editors, and LLM contexts. No flags needed:

```bash
dnx dotnet-inspect -y -- member JsonSerializer --package System.Text.Json    # scan members
dnx dotnet-inspect -y -- type --package System.Text.Json                     # scan types
dnx dotnet-inspect -y -- diff --package System.CommandLine@2.0.0-beta4.22272.1..2.0.3  # triage changes
```

Optional formats: `--oneline`, `--plaintext`, `--json`, `--mermaid`. Verbosity `-v:q/m/n/d` controls which sections are included; formatter and verbosity compose freely (`--oneline` and `-v` cannot be combined).

Use `diff` first when fixing broken code — triage changes, then drill into specifics with `member`.

## Key Syntax

- **Generic types** need quotes: `'Option<T>'`, `'IEnumerable<T>'` — use `<T>` not `<>` (`"Option<>"` resolves to the abstract base)
- **`type` uses `-t`** for type filtering, **`member` uses `-m`** for member filtering (not `--filter`)
- **Dotted syntax** for `member`: `-m JsonSerializer.Deserialize` or fully qualified
- **Diff ranges** use `..`: `--package System.Text.Json@9.0.0..10.0.0`
- **Limit output** with `--head N` / `--tail N` — never pipe through `head`/`tail`/`Select-Object`
- **Derived types** only show their own members — query the base type too

## Installation

Use `dnx` (like `npx`). Always use `-y` and `--` to prevent interactive prompts:

```bash
dnx dotnet-inspect -y -- <command>
```

## Full Reference

Version resolution (cache vs. NuGet), platform diffs and release-notes workflow, structured queries, mermaid diagrams, search scopes, the command table, and all filtering/limiting flags (including aliases): see [references/command-reference.md](references/command-reference.md).

## Related Skills

- **[dotnet-sdk-builder](../dotnet-sdk-builder/SKILL.md)** — Uses this skill to query existing libraries when generating SDK wrappers
- **[dotnet-reviewer](../dotnet-reviewer/SKILL.md)** — Uses this skill to investigate API surface and version diffs during reviews
- **[dotnet-nuget-manager](../dotnet-nuget-manager/SKILL.md)** — Use this skill to inspect package APIs before upgrading or replacing them

The full skill overview lives in the `dotnet` router skill.
