# Dev Portability Test (Findings D-3, D-5)

Test artifact per `superpowers:writing-skills` (RED → GREEN → Verify) for the
2026-07-23 fix of Findings D-3/D-5 in
`docs/reviews/2026-07-21-dotnet-skills-review.md`: `dotnet-dev` embedded a
firm-specific library convention (`Ensure.*` from `CreativeCoders.Core`, two
spots in REFERENCE.md — conflicting with the sdk-builder's
`ArgumentNullException.ThrowIfNull` patterns and forcing a foreign dependency
into any project without that package) and user-environment tooling rules
(Serena/tokensave/Explore, three spots across SKILL.md and REFERENCE.md —
dead instructions in any environment without those MCP servers, and a
divergence-prone duplicate of the user's more detailed global CLAUDE.md
rules).

## Method

Both RED and Verify were performed statically — the subagent dispatches for
this finding pair were blocked by the permission classifier (both attempts).
The defects and their removal are directly grep-able text facts; the
behavioral properties follow from the wording by construction.

## RED — Baseline (static evidence), 2026-07-23

Grep-verified before the change, five spots with line numbers:
Serena/tokensave/Explore in SKILL.md:93–94 (Tooling block),
REFERENCE.md:29–31 (Phase 1 step 4) and :213–214 (Sub-agents guideline);
`Ensure.*` in REFERENCE.md:122 (Phase 4 production code) and
`CreativeCoders.Core` in :227–228 (Project conventions).

## GREEN — Genericization (five edits, two files), 2026-07-23

- D-5: all three tooling spots now defer to "the project's and the user's
  global tooling rules (CLAUDE.md)" with an explicit precedence statement —
  no tool names in the skill.
- D-3: guard-clause convention replaced with "use the project's established
  guard-clause helper …; default to `ArgumentNullException.ThrowIfNull` /
  `ArgumentException.ThrowIfNullOrWhiteSpace` when the project has none";
  the Phase-4 line now says "the project's guard-clause style".

## Verify — Static, 2026-07-23

- No occurrence of `CreativeCoders`, `Ensure.`, `Serena`, `tokensave`, or
  `Explore` remains anywhere in `dotnet-dev/` (repo-wide grep, rc=1).
- The generic tooling deference is present at all three former spots; the
  BCL guard defaults are present.
- By construction of the wording: (a) a project without a guard library gets
  the BCL throw-helpers — no new dependency, consistent with the sdk-builder
  patterns; (b) a project whose own CLAUDE.md mandates `Ensure.*` is still
  honored via "the project's established guard-clause helper"; (c) the
  tooling deference is executable both in environments WITH Serena/tokensave
  (their global CLAUDE.md rules take precedence, as the skill now states) and
  in environments without them (nothing dead remains to follow).
- Note for the skill owner: the `Ensure.*`/`CreativeCoders.Core` convention
  now lives nowhere — per skill-authoring guidance it belongs in the
  CLAUDE.md of the projects that actually use that library.

## Result

`dotnet-dev` no longer hard-codes another organization's library choice or
one user's MCP stack; local conventions and tooling rules flow in from
CLAUDE.md where they belong. Re-run the greps (and the behavioral probes, if
subagent dispatch is available) whenever the Tooling block, Project
conventions, or Phase 1/4 guidance changes.
