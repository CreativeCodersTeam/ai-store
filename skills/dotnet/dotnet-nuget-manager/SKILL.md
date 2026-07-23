---
name: dotnet-nuget-manager
description: Use when adding, removing, or updating NuGet package references or versions in a .NET project or solution, listing outdated packages, verifying that a package version exists, or working in a solution with Directory.Packages.props central package management — including requests phrased as dotnet add/remove package or dotnet list package --outdated.
---

# NuGet Manager

## When to Use

- Adding, removing, or updating NuGet packages in a .NET project or solution
- Listing outdated packages and planning version bumps
- Auditing packages for known vulnerabilities (CVEs) or deprecation — e.g. when a code review surfaces a vulnerable package
- Verifying a specific package version exists before bumping it
- Working in a solution that uses `Directory.Packages.props` central version management

## Prerequisites

- .NET SDK installed (typically .NET 8.0 SDK or later, or a version compatible with the target solution).
- `dotnet` CLI available on your `PATH`.
- `jq` (JSON processor) — Linux/macOS; OR
- PowerShell (`pwsh`) — Windows/cross-platform; required for version verification using `dotnet package search`.

## Core Rules

1.  **NEVER** directly edit `.csproj`, `.props`, or `Directory.Packages.props` files to **add** or **remove** packages. Always use `dotnet add package` and `dotnet remove package` commands.
2.  **VERSION UPDATES also go through the CLI:** verify the target version exists, then `dotnet add [<PROJECT>] package <PACKAGE_NAME> --version <VERSION>` — it updates the existing reference in place, and modern SDKs write the version to `Directory.Packages.props` under Central Package Management. Immediately run `dotnet restore` to verify compatibility.
3.  **HAND-EDITING a version string is the documented fallback only** — for older SDKs whose `dotnet add package` cannot write to `Directory.Packages.props`. Always try the CLI first; fall back only after it demonstrably wrote the version to the wrong place (or errored). Even then: verify the version first, change ONLY the existing `Version`/`VersionOverride` string (never add or remove attributes or elements), and run `dotnet restore` immediately; on errors, revert and investigate.

## Workflows

### Adding a Package
Use `dotnet add [<PROJECT>] package <PACKAGE_NAME> [--version <VERSION>]`.
Example: `dotnet add src/MyProject/MyProject.csproj package Newtonsoft.Json`

### Removing a Package
Use `dotnet remove [<PROJECT>] package <PACKAGE_NAME>`.
Example: `dotnet remove src/MyProject/MyProject.csproj package Newtonsoft.Json`

### Updating Package Versions
When updating a version, follow these steps:

1.  **Verify Version Existence**:
    Check if the version exists using the `dotnet package search` command with exact match and JSON formatting. 
    Using `jq`:
    `dotnet package search <PACKAGE_NAME> --exact-match --format json | jq -e '.searchResult[].packages[] | select(.version == "<VERSION>")'`
    Using PowerShell:
    `(dotnet package search <PACKAGE_NAME> --exact-match --format json | ConvertFrom-Json).searchResult.packages | Where-Object { $_.version -eq "<VERSION>" }`
    
2.  **Determine Version Management**:
    - Search for `Directory.Packages.props` in the solution root. If present, versions are normally managed there via `<PackageVersion Include="Package.Name" Version="1.2.3" />`.
    - **Even under CPM, check the target `.csproj` for a `VersionOverride`** on the `PackageReference` — an override wins over the central version, so updating `<PackageVersion>` alone silently changes nothing for that project (and `dotnet restore` still succeeds). Update or remove the override instead.
    - Build-wide packages (analyzers, source generators) may live in `Directory.Packages.props` as `<GlobalPackageReference>` — that is where their version is managed.
    - Without CPM, versions live in the individual `.csproj` files as `<PackageReference Include="Package.Name" Version="1.2.3" />`.

3.  **Apply Changes**:
    Run `dotnet add [<PROJECT>] package <PACKAGE_NAME> --version <VERSION>` (Core Rule 2). Fall back to hand-editing the identified version string only under the conditions of Core Rule 3.

4.  **Verify Stability**:
    Run `dotnet restore` on the project or solution. If errors occur, revert the change and investigate.

### Listing Outdated Packages

Use `dotnet list package --outdated` to find packages with newer versions available.

**Per project:**
```bash
dotnet list src/MyProject/MyProject.csproj package --outdated
```

**Entire solution:**
```bash
dotnet list package --outdated
```

The output shows the current version, the latest resolved version, and the latest available version for each package. Use this as the basis for deciding which packages to update, then follow the **Updating Package Versions** workflow for each.

### Auditing Packages

Outdated ≠ vulnerable — audit with the dedicated flags:

```bash
dotnet list package --vulnerable                      # direct references with known CVEs
dotnet list package --vulnerable --include-transitive # include transitive dependencies
dotnet list package --deprecated                      # deprecated packages
```

Fix findings via the **Updating Package Versions** workflow. For a vulnerability that is only in a **transitive** dependency, either update the direct parent package to a version that pulls a fixed transitive, or add a direct reference to the fixed version of the transitive package (`dotnet add package <transitive> --version <fixed>`).

## Related Skills

- **[dotnet-sdk-builder](../dotnet-sdk-builder/SKILL.md)** — Invokes this skill in Step 7 to add SDK runtime dependencies
- **[dotnet-inspect](../dotnet-inspect/SKILL.md)** — Use to inspect package APIs before upgrading or replacing them

The full skill overview lives in the `dotnet` router skill.

