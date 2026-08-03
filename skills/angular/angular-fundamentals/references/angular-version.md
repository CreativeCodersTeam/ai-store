# Angular Version Resolution

The single rule for deciding which Angular version a skill targets — when scaffolding a workspace or
library, declaring peer dependencies, choosing a checklist, or naming a version in output. Every
Angular skill resolves the version the same way. This mirrors the .NET family's
`dotnet-fundamentals/references/target-framework.md`.

## The Cascade

Walk the steps in order and stop at the first one that yields a version.

### 1. Explicit user directive

A version named in the request (`"Angular 19"`, `"target 17"`). This always wins — over the
workspace, over the default, over what looks more modern, and over the "installed major wins" rule
in step 2. Do not talk the user out of an older target; if it conflicts with something in the
workspace, say so once and proceed with their choice.

A directive that names no concrete version (`"use the latest"`, `"whatever the workspace has"`) is a
*pointer* to a later step, not a version. Resolve it there, but record the origin as `user`.

### 2. Repo directive

Read the workspace, in this precedence order — the first source that yields a major decides:

| Order | Source | What to read |
|---|---|---|
| 1 | lockfile (`package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`) or `node_modules/@angular/core/package.json` | the **installed** `@angular/core` version — this is what the code actually builds against |
| 2 | `package.json` → `dependencies` / `devDependencies` | the declared `@angular/core` range; use its **lower bound** when nothing is installed |
| 3 | `package.json` → `peerDependencies` | for a **library** repo, whose own peers are the only declaration; a wide range (`>=17 <22`) states compatibility, not a target — pick the installed devDependency major, else the range's upper bound minus one, and say which |

`angular.json` is not a version source. Its presence confirms a CLI workspace and it enumerates
projects; it carries no Angular version.

A declared **range is not an installed version**. `^19.2.0` cannot cross a major so reading it is
safe; `>=19`, `*`, `latest`, `next`, `workspace:*`, and git/tarball specs are not, which is why the
lockfile outranks the manifest.

**Granularity** is the major, unless a `(since X.Y)` marker forces the minor — then resolve the
minor from the lockfile, never from a caret range.

**Monorepos** (Nx, npm workspaces) can hold several `package.json` files at different majors. Use
the one owning the code being written; if that is ambiguous, name the candidates rather than
guessing.

When adding to an **existing** library or application, the workspace's installed major wins over the
step 3 default — new code must build against what is actually there. An explicit user directive
still outranks it.

### 3. Latest stable

The fallback when the request names no version and there is no workspace to read (empty directory,
no `package.json`). Resolve it with `npm view @angular/core dist-tags.latest` — that command, not a
number written down here, is the authority.

If the registry is unreachable and no user is reachable either, use the family baseline these skills
are written against (**Angular 21**), record the origin as `default-latest (offline; baseline 21)`,
and say that the number was not verified. Never stall waiting for the network.

## Recording the Origin

Whatever resolves the version, name where it came from:

- `user` — explicit directive (including a directive that pointed at a later step)
- `repo:<file>` — e.g. `repo:package-lock.json`, `repo:package.json`
- `default-latest` — no directive found; fell through to the latest stable

When an explicit directive contradicted the workspace, record the origin **and** the conflict in one
clause — e.g. `user (repo:package.json declares ^21.0.0)`. A resolved version that silently
discarded a competing signal is a defect.

`angular-library-builder` already applies this cascade for peer dependency ranges
(`references/project-setup.md` → "Peer version resolution"); `angular-reviewer` records it in its
report metadata.

## `(since X)` Is Not a Target

Documentation marks feature availability as `(since Angular 19)`. That records **when an API
appeared** — a fact about the framework, never a target selection. Use these markers to decide
whether a pattern is available on the resolved version:

- Resolved version ≥ the `since` version → the pattern is available, use it.
- Resolved version < the `since` version → use the documented alternative, and say why.
- Resolved version < the `since` version and **no** alternative is documented → do not silently emit
  the unavailable API and do not raise the version on your own. State the gap and let the user
  decide.

An Angular major also carries Node and TypeScript floors. If the resolved version cannot run on the
toolchain that is actually installed, say so before generating — an explicit user directive is
honoured, but an unbuildable result is reported, not shipped silently.

## Non-Interactive Invocation

When running as a sub-agent, or in any context where no user is reachable: **never stall and never
guess.** Walk the cascade, take the first hit, record the origin, and continue. A missing answer
falls through to the next step — it does not become a question.

## Maintenance

Step 3 resolves the latest stable at runtime, so it does not go stale. What does go stale is the
**family baseline** — the version these skills' examples are written against, used only as the
offline fallback. It lives in exactly two places: the offline clause in **step 3** above and the
**Version baseline** note in the `angular` router `SKILL.md`. Every other mention in the family is a
hook that links here and names no version of its own.
