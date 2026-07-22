# dotnet-inspect — Command Reference

Detailed reference for `dotnet-inspect`. For the decision tree and key syntax, see the skill's `SKILL.md`. All commands run as `dnx dotnet-inspect -y -- <command>`.

## Command Reference

| Command | Purpose |
| ------- | ------- |
| `type` | **Discover types** — terse output, no docs, use `--shape` for hierarchy |
| `member` | **Inspect members** — docs on by default, supports dotted syntax (`-m Type.Member`) |
| `find` | Search for types by glob or fuzzy match across any scope |
| `diff` | Compare API surfaces between versions — breaking/additive classification |
| `extensions` | Find extension methods/properties for a type (`--reachable` for transitive) |
| `implements` | Find types implementing an interface or extending a base class |
| `depends` | Walk dependency graphs upward — type hierarchy, package deps, or library refs |
| `package` | Package metadata, files, versions, dependencies, `search` for NuGet discovery |
| `library` | Library metadata, symbols, references, SourceLink audit |
| `source` | **SourceLink URLs** — type-level or member-level (with line numbers), `--cat` to fetch content, `--verify` to check URLs |
| `demo` | Run curated showcase queries — list, invoke, or feeling-lucky |

## Version Resolution (Docker-style)

Version queries use Docker-like semantics: cached packages are served in under 15ms, network calls cost 1–4 seconds. Three flags, three behaviors:

| Flag | Behavior | Network | Like Docker... |
| ---- | -------- | ------- | -------------- |
| `--version` (bare) | **Local** — returns the version from local cache | Only on cache miss | `docker run nginx` |
| `--latest-version` | **Remote** — queries nuget.org for the absolute latest | Always | `docker pull nginx` |
| `--versions` | **Remote** — returns every published version | Always | `docker image ls --all` |

`--version` and bare-name inspection share the same cache. If `Foo --version` returns `2.0.3`, then `Foo` (or `package Foo`) will inspect that same `2.0.3` — no surprises, no extra network call. This is the fast path for most tasks.

`--latest-version` and `--versions` always query nuget.org, so they reflect the latest published state. Use `--latest-version` when you need to confirm the newest version, e.g., before a dependency upgrade.

```bash
dnx dotnet-inspect -y -- Foo --version            # what's in the cache? (fast, local)
dnx dotnet-inspect -y -- Foo --latest-version     # what's on nuget.org? (always network)
dnx dotnet-inspect -y -- Foo --versions           # list all published versions
dnx dotnet-inspect -y -- Foo --versions 5         # list latest 5 versions
dnx dotnet-inspect -y -- Foo --versions --preview # include prerelease versions
```

The same flags work on the `package` subcommand (`package Foo --version`, etc.).

Version pinning with `@version` syntax:

```bash
dnx dotnet-inspect -y -- Foo@2.0.3                # pinned — no network if cached
dnx dotnet-inspect -y -- Foo@latest               # always checks nuget.org
dnx dotnet-inspect -y -- Foo                      # prefer cache, refresh on TTL expiry
```

**Use `--version` (not `--latest-version`) as the default.** It's fast and returns the same version that bare-name commands will use. Only reach for `--latest-version` when you need the absolute latest from nuget.org.

## Platform Diffs & Release Notes

For framework libraries (System.*, Microsoft.AspNetCore.*), use `--platform` instead of `--package`. This is the primary workflow for .NET release notes — diff each framework library between preview versions:

```bash
dnx dotnet-inspect -y -- diff --platform System.Runtime@P2..P3 --additive        # what's new?
dnx dotnet-inspect -y -- diff --platform System.Net.Http@P2..P3 --additive       # per-library
dnx dotnet-inspect -y -- diff --platform System.Text.Json@9.0.0..10.0.0          # across major versions
```

**Multi-library packages:** `diff --package` works across all libraries in a package (e.g., `Microsoft.Azure.SignalR` with multiple DLLs). For framework ref packages like `Microsoft.NETCore.App.Ref`, prefer `--platform` per-library since it resolves from installed packs.

**Nightly/preview packages from custom feeds:** The `--source` flag works for version listing but not package downloads. Pre-populate the NuGet cache instead:

```bash
# Pre-populate cache (fails with NU1213 but downloads the package)
dotnet add package Microsoft.NETCore.App.Ref --version <version> --source <feed-url>
# Then use normally — resolves from NuGet cache
dnx dotnet-inspect -y -- diff --platform System.Runtime@P2..P3 --additive
```

## Structured Queries (like Go templates, without a DSL)

Discover the schema, then select and project — no template language needed:

```bash
dnx dotnet-inspect -y -- System.Text.Json -D                          # list sections
dnx dotnet-inspect -y -- System.Text.Json -D --effective              # sections with data (dry run)
dnx dotnet-inspect -y -- library System.Text.Json -D --tree           # full schema tree
dnx dotnet-inspect -y -- System.Text.Json -S Symbols                  # render one section
dnx dotnet-inspect -y -- System.Text.Json -S Symbols --fields "PDB*"  # project specific fields
dnx dotnet-inspect -y -- type System.Text.Json --columns Kind,Type    # project specific columns
```

## Mermaid Diagrams

The `depends` command supports `--mermaid` for Mermaid diagram output. Two modes:

| Flags | Output | Use case |
| ----- | ------ | -------- |
| `--mermaid` | Standalone mermaid (`graph TD`) | Pipe to `mmdc`, embed in tooling |
| `--markdown --mermaid` | Mermaid fenced blocks inside markdown | Render in GitHub, VS Code, docs |

```bash
dnx dotnet-inspect -y -- depends Stream --mermaid                               # type hierarchy as mermaid
dnx dotnet-inspect -y -- depends Stream --markdown --mermaid                    # embedded in markdown
dnx dotnet-inspect -y -- depends --library System.Text.Json --mermaid           # assembly reference graph
dnx dotnet-inspect -y -- depends --package Markout --mermaid                    # package dependency graph
```

## Search Scope

Search commands (`find`, `extensions`, `implements`, `depends`) use scope flags:

- **(no flags)** — all platform frameworks (runtime, aspnetcore, netstandard)
- **`--platform`** — all platform frameworks
- **`--extensions`** — curated Microsoft.Extensions.* packages
- **`--aspnetcore`** — curated Microsoft.AspNetCore.* packages
- **`--package Foo`** — specific NuGet package (combinable with scope flags)

`type`, `member`, `library`, `diff` accept `--platform <name>` as a string for a specific platform library.

## Filtering and Limiting

```bash
dnx dotnet-inspect -y -- type System.Text.Json -k enum                  # filter by kind (type and member commands)
dnx dotnet-inspect -y -- type System.Text.Json -t "*Converter*"         # glob filter on type names
dnx dotnet-inspect -y -- member System.Text.Json JsonDocument -m Parse  # filter by member name
dnx dotnet-inspect -y -- type System.Text.Json --head 5                 # first 5 lines
dnx dotnet-inspect -y -- type System.Text.Json --tail 10                # last 10 lines
```

**Do not pipe output through `head`, `tail`, or `Select-Object`.** Use the built-in flags:

- **`--head N`** — first N lines (like `head`). Keeps headers, truncates cleanly. Aliases: `-n N`, `-N` (e.g. `-5`) — prefer the long form in scripts and examples.
- **`--tail N`** — last N lines (like `tail`). Buffers output, emits only the final N lines.
- **`-k Kind`** — filter by kind: `class/struct/interface/enum/delegate` (type) or `method/property/field/event/constructor` (type single-type view, member).
- **`-S Section`** — show only a specific section (glob-capable).
- **`-m`** — **name argument = member filter** (`-m Parse`, `-m .ctor`); **numeric argument = item limit** per kind section (`-m 5`). The overload is easy to misread — use `-m` only for member filtering and `--head N` for output limiting.
