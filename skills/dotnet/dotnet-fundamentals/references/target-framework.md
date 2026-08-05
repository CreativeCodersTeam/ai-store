# Target Framework Resolution

The single rule for deciding which .NET version a skill targets — when scaffolding a project,
generating a `.csproj`, creating a test project, choosing a checklist, or naming a version in
output. Every .NET skill resolves the target the same way.

## The Cascade

Walk the steps in order and stop at the first one that yields a version.

### 1. Explicit user directive

A version named in the request (`"target net8.0"`, `".NET 9 please"`). This always wins — over the
repo, over the default, over what looks more modern, and over the "existing project wins" rule in
step 2. Do not talk the user out of an older target; if it conflicts with something in the repo, say
so once and proceed with their choice.

A directive that names no concrete version (`"use the LTS"`, `"whatever the repo uses"`) is a
*pointer* to a later step, not a version. Resolve it there, but record the origin as `user` — the
user chose the rule.

### 2. Repo directive

Only two things declare a target framework. Read them in this order — the first that yields a TFM
decides:

| Order | Source | What to read |
|---|---|---|
| 1 | the project's own `*.csproj` | `<TargetFramework>` / `<TargetFrameworks>` |
| 2 | `Directory.Build.props` | `<TargetFramework>` / `<TargetFrameworks>` — the repo-wide default a project inherits when its own `.csproj` declares none |

**`global.json` is not a TFM source.** Its `sdk.version` pins the *SDK that builds* the repo, which
is a different thing: SDK 10 builds `net8.0` fine, SDK 8 cannot build `net10.0`. Treat it as a
feasibility constraint, not a version to target:

- A pinned SDK **older** than the resolved target → the target cannot be built. Say so and stop
  before generating anything.
- A `global.json` with no TFM anywhere else in the repo → the only signal available; derive the
  major from `sdk.version` and record the origin as `repo:global.json`.

Same for the installed SDK: if `dotnet --list-sdks` has nothing that can build the resolved target,
say so rather than generating a project that will not compile.

**Multi-targeting.** `<TargetFrameworks>net8.0;net10.0</TargetFrameworks>` means the project targets
*all* of them — new code in it must compile under every one, so write to the **lowest**. When a
single value must be named (a new project, a report header), take the **highest** and list the rest.

**Comparing versions.** "Highest" compares the major of `net<N>.0` monikers only. Keep any platform
suffix (`net10.0-windows` stays `net10.0-windows`). `netstandard2.0` and `net4xx` are separate
families and are never "lower" than a `net<N>.0` — carry them through unchanged and, if one must be
mixed with a modern target, say so instead of ranking them.

When projects disagree and one target must be picked for new code, take the **highest** and state
which projects were surveyed and what each targets. Ask only when the choice is material *and* a
user is reachable (see Non-Interactive below); otherwise take the highest and report it.

When adding to an **existing** project, that project's own TFM wins over the repo-wide default —
a new file must compile in the project it lands in. A **test** project matches the TFM of the
project under test, not the repo maximum.

If a TFM is an MSBuild property reference (`<TargetFramework>$(DefaultTfm)</TargetFramework>`) or
comes from a chained `Directory.Build.props`, resolve it as MSBuild would — nearest file wins,
imports chain upward. If it cannot be resolved to a literal, treat the repo as declaring nothing and
fall through to step 3, recording why.

### 3. Latest LTS — currently **.NET 10** (`net10.0`)

The fallback when the request names no version and the repo has none to read (new solution, empty
directory, no `.csproj` anywhere).

## Recording the Origin

Whatever resolves the target, name where it came from. Skills that emit a report or metadata block
record it as one of:

- `user` — explicit directive (including a directive that pointed at a later step)
- `repo:<file>` — e.g. `repo:src/Api/Api.csproj`, `repo:Directory.Build.props`, `repo:global.json`
- `default-lts` — no directive found; fell through to .NET 10

When an explicit directive contradicted the repo, or projects disagreed and the highest was taken,
record the origin **and** the conflict in one clause — e.g.
`user (repo:src/Api/Api.csproj targets net10.0)`. A resolved target that silently discarded a
competing signal is a defect.

This mirrors how `dotnet-reviewer` already records the origin of its mode/tools/language parameters.

## `(since X)` Is Not a Target

Documentation marks feature availability as `(since .NET 8)`, `(since C# 12)`. That records **when
an API appeared** — it is a fact about the platform, never a target selection. A page describing
keyed services as `(since .NET 8)` does not make .NET 8 the target; the cascade above does that.

Use these markers to decide whether a pattern is *available* on the resolved target:

- Resolved target ≥ the `since` version → the pattern is available, use it.
- Resolved target < the `since` version → use the documented alternative, and say why.
- Resolved target < the `since` version and **no** alternative is documented → do not silently emit
  the unavailable API and do not raise the target on your own. State the gap and let the user decide
  between raising the target and dropping the feature.

## Non-Interactive Invocation

When running as a sub-agent, or in any context where no user is reachable: **never stall and never
guess.** Walk the cascade, take the first hit, record the origin, and continue. A missing answer
falls through to the next step — it does not become a question.

Where a user *is* reachable and the cascade produced an ambiguous result (projects disagree, and the
choice changes the generated code), a single grouped question is appropriate. One question, not a
sequence.

## Maintenance

When the latest LTS moves past .NET 10, exactly two places change: the version in **step 3** above,
and the **Version baseline** note in the `dotnet` router `SKILL.md`. Every other mention in the
family is a hook that links here and names no version of its own.
