# SDK-Builder References Test (Findings S-2, S-3, S-4)

Test artifact per `superpowers:writing-skills` (RED → GREEN → Verify) for the
2026-07-22 fix of Findings S-2/S-3/S-4 in
`docs/reviews/2026-07-21-dotnet-skills-review.md`, all in
`dotnet-sdk-builder/references/`:

- S-2: the `project-setup.md` csproj template embedded three
  `<PackageReference … Version="*" />` entries (same pattern in
  `http-client-patterns.md`'s resilience section) — contradicting SKILL.md
  Step 7 and the `dotnet-nuget-manager` rules, defeating version pinning, and
  a restore error (NU1008) under Central Package Management.
- S-3: prose said `AddHttpClient<TClient, TInterface>()` — reversed naming vs.
  the real `<TClient, TImplementation>` API and the file's own example.
- S-4: `GitHubRateLimitException.ResetAt` was documented but never assigned
  anywhere in the canonical pattern.

## Method

One combined probe: a fresh general-purpose subagent audits the excerpts
(template + Step 7 + nuget-manager rules; prose vs. real API; exception
mapping) for consistency, correctness, and consumer impact.

## RED — Baseline (old texts), 2026-07-22

- S-2: "internally contradictory … An agent that copies the template has
  therefore *already* added all three packages by direct `.csproj` editing …
  The template as written fails `dotnet restore` outright in a CPM solution
  [NU1008] … The template ships in a state EXCERPT 3 forbids." Resilience
  snippet: "Same double violation."
- S-3: "there is no parameter named `TInterface` in the API … The example is
  right; the prose naming is wrong; the document is internally inconsistent."
- S-4: "`ResetAt` … is never assigned anywhere … A consumer … gets **`null` —
  always** … The XML doc … is actively misleading … a silent correctness
  trap."

## GREEN — Fixes (two files), 2026-07-22

1. Template `<ItemGroup>` removed; replacement note routes the three packages
   through `dotnet-nuget-manager` (Step 7) and names both hazards (floating
   versions, NU1008 under CPM). Resilience XML block replaced with prose
   routing through Step 5/Step 7.
2. Prose corrected to `AddHttpClient<TClient, TImplementation>()` with the
   order spelled out and the file's own example inlined.
3. `TooManyRequests` arm now populates `ResetAt` from `Retry-After` (absolute
   `Date` preferred, `Delta` converted via `UtcNow + delay`), using an object
   initializer valid for the `init` property.

## Verify — 2026-07-22

- (1) "No contradiction remains among Excerpts 1, 2, 3, 4 … CPM/NU1008 and
  floating versions: resolved."
- (2) Naming "Correct on both counts" and consistent with the example.
- (3) `ResetAt` always assigned in the arm; code compiles (init-in-initializer,
  target-typed conditional under net9.0); mapping "technically correct for
  both RFC forms"; a 429 with `Retry-After: 120` yields a non-null absolute
  reset timestamp.

Residual notes accepted as non-defects: where the pin lands under CPM belongs
to the `dotnet-nuget-manager` skill (Finding N-3); `TClient` need not be an
interface (prescriptive convention); GitHub's `x-ratelimit-reset` is a
domain-specific header beyond the generic `Retry-After` pattern.

## Result

Template, workflow, and delegated skill agree; the prose matches the API; the
documented diagnostic property is populated in the canonical path. No REFACTOR
round needed. Re-run this probe whenever the template, the typed-client
opening prose, or the exception-mapping example changes.
