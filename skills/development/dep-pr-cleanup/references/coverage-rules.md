# Coverage rules

How `analyze_prs.py` (`scripts/deplib/versions.py`, `scripts/deplib/coverage.py`) decides that a
pull request is obsolete.

## Who may cover whom

Only pull requests of the **same bot** (normalised login: `app/renovate`, `renovate[bot]`, and
`renovate` are one bot) against the **same base branch** are compared. Unevaluable pull requests
take no part. Overlaps across those boundaries are still listed, with `not_counted_reason`.

## Relation of two targets

For two updates with the same identity, the target of A relative to B is:

| Relation | When |
| --- | --- |
| `equal` | the normalised target values are identical (quotes and surrounding whitespace removed) |
| `newer` | A's release is higher within the same major version |
| `newer-major` | A's release is higher and its major version differs |
| `older` | B is newer |
| `incomparable` | anything else — see below |

Ordering uses the numeric release (`4.17.21`, `v5`, `>=2.31.0,<3` → `2.31.0`; leading operators
and `v` are stripped, missing components count as 0, so `v4` < `v4.1.0`). The major version is
the first component, also for `0.x`. At an equal release, pre-release words order as
dev/snapshot < alpha/a/preview < beta/b < milestone/m < rc/cr < (none)/final/ga/release <
post/sp; an unknown word makes the pair incomparable. npm and NuGet build metadata (`+…`) is
ignored for ordering.

**Incomparable** — never a cover, unless the values are equal:

- a value with no number (`latest`, `stable`, `npm:other@1.0.0`, a bare SHA or digest);
- the same release written differently (`^1.2.3` vs `1.2.3`, `1.2` vs `1.2.0`);
- Docker tags with a different variant (`22` vs `20-alpine`, `20-alpine3.20` vs
  `20-alpine3.19`) or the same tag with a different digest;
- an action pinned to a SHA without a version comment, or two SHAs with the same comment.

## Modes

| Mode | A covers B's update when the relation is |
| --- | --- |
| `exact` | `equal` |
| `newer` | `equal` or `newer` |
| `any` | `equal`, `newer`, or `newer-major` |

The global default follows the options: newer counts = no → `exact`; yes and across majors = no →
`newer`; yes and yes → `any`. A per-pair exception (`--pair-mode COVERER:COVERED=mode`) replaces
the mode for that one direction only.

## Obsolete

A pull request P is **covered** by a set S of other pull requests when every update of P has, in
some member of S, an update with the same identity whose relation is allowed by that member's
mode towards P. Several pull requests may share the work (union).

Within each (bot, base branch) group, starting with every evaluable pull request kept:

1. Take the kept pull requests ordered by number of updates, then by number (oldest first).
2. The first one that is covered by the other kept pull requests **and** whose removal leaves every
   pull request already marked obsolete still covered by the remaining kept ones is marked
   obsolete.
3. Repeat until no pull request can be marked.

Consequences:

- A pull request that covers an obsolete one is always kept, so any subset of the proposals can be
  closed safely.
- The smaller pull request goes first; among identical ones the oldest goes and the newest stays.
- The second check in step 2 matters because per-pair modes make coverage non-transitive:
  with 1 → `1.0.0`, 2 → `1.1.0`, 3 → `1.2.0` and the exception `3:1=exact`, pull request 1 is
  obsolete through 2, and 2 must stay open even though 3 covers it.

For each obsolete pull request, `details[]` names one covering pull request per update — an
`equal` cover before a newer one, then the one with more updates, then the newer number — and
`covered_by` is the set of those choices; `also_covered_by` lists the alternatives.
