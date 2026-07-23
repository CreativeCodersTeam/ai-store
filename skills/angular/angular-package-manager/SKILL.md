---
name: angular-package-manager
description: Manages npm packages in Angular projects and workspaces. Use when adding, removing, or updating npm dependencies or versions. Enforces the npm/ng CLI for package operations, prefers `ng add` for Angular-aware packages and `ng update` for framework upgrades, and provides version verification workflows. Handles npm install/uninstall, npm outdated, ng add, ng update, and lockfile-consistent installs.
---

# Angular Package Manager

## When to Use

- Adding, removing, or updating npm packages in an Angular project or workspace
- Listing outdated packages and planning version bumps
- Verifying a specific package version exists before bumping it
- Upgrading Angular itself or Angular ecosystem libraries (which ship migration schematics)
- Working in an Angular monorepo / npm workspace

## Prerequisites

- Node.js and npm installed (a version compatible with the target Angular version; see the project's `engines` field and `package.json`).
- `npm` available on your `PATH`. If the repo uses `pnpm` or `yarn`, match the existing package manager and lockfile instead.
- Angular CLI (`ng`) available (via `npx ng` or a local devDependency) for `ng add` / `ng update`.

## Core Rules

1.  **Prefer `ng add <pkg>`** for packages that ship an Angular schematic (e.g. `@angular/material`, `@angular/pwa`, `@ngrx/store`). It installs the package **and** wires up the necessary config, providers, and imports. Use plain `npm install` only for libraries with no schematic.
2.  **NEVER** hand-edit `package.json` to **add** or **remove** a dependency. Always use `npm install <pkg>` / `npm uninstall <pkg>` (or `ng add`) so the lockfile stays consistent.
3.  **DIRECT EDITING** of a version range in `package.json` is permitted only for **changing the version of an existing dependency** — and must be followed immediately by `npm install` to update the lockfile.
4.  **NEVER hand-bump `@angular/*` versions.** Angular core/CLI/Material upgrades MUST go through `ng update`, which runs the version-specific migration schematics. Manually editing Angular versions skips migrations and breaks the workspace.
5.  **VERSION UPDATES** must follow the mandatory workflow below.

## Workflows

### Adding a Package

- Angular-aware package: `ng add <pkg>` (e.g. `ng add @angular/material`).
- Plain library: `npm install <pkg>` (runtime dep) or `npm install -D <pkg>` (dev/build-only dep).
- Pin a version: `npm install <pkg>@<version>`.

In a workspace, target a specific package with `npm install <pkg> -w <workspace>`.

### Removing a Package

Use `npm uninstall <pkg>` (add `-w <workspace>` in a monorepo). This updates `package.json` and the lockfile together.

### Updating Package Versions

When updating a version, follow these steps:

1.  **Verify version existence**:
    - All published versions: `npm view <pkg> versions --json`
    - Exact version exists: `npm view <pkg>@<version> version` (prints the version if it exists, empty otherwise)
    - Latest: `npm view <pkg> version`

2.  **Choose the right mechanism**:
    - **`@angular/*`, `@angular/cli`, `@angular/material`, `@ngrx/*`** → use `ng update <pkg>@<version>` (runs migrations). Never hand-edit.
    - **Other libraries** → `npm install <pkg>@<version>`, or edit the version range in `package.json` then run `npm install`.

3.  **Apply changes**: install via CLI, or modify the version string in the appropriate `package.json` (root or workspace member).

4.  **Verify stability**: run `npm install` (reconciles the lockfile), then `npm run build` (and `ng test --watch=false` if practical). If errors occur, revert the change and investigate.

### Listing Outdated Packages

Use `npm outdated` to find packages with newer versions available. The output shows `Current`, `Wanted` (max satisfying the range), and `Latest` for each package. Use this as the basis for deciding what to update, then follow the **Updating Package Versions** workflow for each.

For Angular specifically, run `ng update` with **no arguments** — it inspects the workspace and lists which Angular packages can be updated and the recommended order, without changing anything.

### Auditing Vulnerabilities

`npm audit` reports known vulnerabilities. Prefer `npm audit fix` (safe, semver-compatible) over `npm audit fix --force` (may install breaking major versions — only with explicit confirmation).

## Important Notes

- **Lockfile is source of truth for CI.** Use `npm ci` (not `npm install`) for clean, reproducible installs from `package-lock.json`; use `npm install` when intentionally changing dependencies.
- Commit `package.json` **and** the lockfile together.
- npm has **no central package-version manifest**. In a monorepo, dependency versions are deduplicated by the lockfile and can be aligned via workspace root dependencies — there is no separate central-version file to edit.

## Related Skills

- **[angular-fundamentals](../angular-fundamentals/SKILL.md)** — Used when adding DI/config-related libraries and provider packages
- **[angular-components](../angular-components/SKILL.md)** — Invokes this skill for UI, router, forms, and HTTP-related packages (often via `ng add`)
- **[angular-state](../angular-state/SKILL.md)** — Adds RxJS, NgRx, or component-store packages (`ng add @ngrx/store`)
- **[angular-library-builder](../angular-library-builder/SKILL.md)** — Invokes this skill to add library runtime/peer dependencies
- **[angular-reviewer](../angular-reviewer/SKILL.md)** — Used when a review surfaces outdated or vulnerable packages
