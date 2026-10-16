# Report format

The comparison in the conversation (Step 3) and the report file (Step 8) share these tables.
Write both in the conversation's language; the layout below is the English one. The PR comment
used when closing is always English (SKILL.md, Step 7).

File: `docs/dep-pr-cleanup/YYYY-MM-DD-<repo-name>.md`; never overwrite — append `-2`, `-3`, …

```markdown
# Dependency PR cleanup — acme/shop — 2026-10-16

## Parameters

| Parameter | Value | Origin |
| --- | --- | --- |
| Repository | acme/shop (base branches: main, release/1.x) | working directory |
| Bots | dependabot, renovate, my-renovate | default, default, prompt |
| Newer version counts as replacement | yes | question |
| … also across major versions | no | default |
| Per-pair exceptions | #109 does not replace #102 | question |
| Collected at | 2026-10-16T09:12:00Z (re-checked 09:20:41Z before closing) | — |

## Overview

| Bot · base | Open bot PRs | Obsolete | Kept | Unevaluable |
| --- | --- | --- | --- | --- |
| renovate · main | 7 | 2 | 3 | 2 |
| dependabot · main | 5 | 1 | 4 | 0 |

## Overlaps — renovate · main

| Package | Path | Targets | Relation |
| --- | --- | --- | --- |
| lodash | package.json | #101 → ^4.17.21 · #102 → ^4.17.21 | same version |
| lodash | package.json | #102 → ^4.17.21 · #103 → ^5.0.0 | #103 newer, crosses a major version |
| express | package.json | #102 → ^4.19.2 · #104 → ^4.20.0 · #109 → ^4.20.0 | #104, #109 newer |

## Proposed as obsolete

| PR | Title | Covered by | How | Warnings |
| --- | --- | --- | --- | --- |
| #101 | Update dependency lodash to v4.17.21 | #102 | same version | commits by alice; #102 has failing checks |
| #104 | Update dependency express to v4.20.0 | #109 | same version | immortal: Renovate recreates it |

## Unevaluable

| PR | Title | Reasons |
| --- | --- | --- |
| #107 | Lock file maintenance | only lockfiles changed |
| #108 | Update Rust crate serde to v1.0.210 | Cargo.toml: unsupported file type |

## Not counted

- #101 / #105 share lodash — different bot (renovate / dependabot)
- #101 / #106 share lodash — different base branch (main / release/1.x)

## Result

| PR | Action | Detail |
| --- | --- | --- |
| #101 | closed, branch deleted | superseded by #102 |
| #104 | not closed | #109 received new commits after the analysis |
| #111 | not selected | — |

Nothing was committed.
```

Rules:

- **Targets** lists every PR of the group that updates that package at that path, in PR order;
  write `from → to` only when the from-versions differ.
- **Relation** in words: "same version", "#X newer", "#X newer, crosses a major version",
  "not comparable (different variant / digest)".
- **How** summarises `details[].relation` of the proposal: "same version", "newer version",
  "newer major version", or a mix ("lodash same version, express newer").
- **Warnings** come from `proposals[].warnings`, shortened; never drop one.
- In the report, list all `unevaluable_reasons`; in the conversation the first one is enough.
- **Result** exists only when Step 7 ran; in non-interactive runs replace it with a
  "Proposed, not closed (non-interactive run)" line listing the proposals.
- Omit a section that would be empty, except Parameters and Overview.
