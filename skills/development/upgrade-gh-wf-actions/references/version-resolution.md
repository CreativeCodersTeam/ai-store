# Version resolution

How `check-updates.sh` decides what an action currently uses, which versions are eligible, and
which rows it offers. The script is the authority; this file explains its behaviour so results
can be interpreted and questioned.

## Data source

One GraphQL query per action repository, via `gh api graphql`:

- the **100 most recently created releases** (`tagName`, `publishedAt`, `isPrerelease`,
  `isDraft`, `immutable`, `url`), and
- the **100 tags with the most recent commit dates** (`name` and the commit each points at —
  annotated tags are dereferenced to their commit; the tagger date for annotated tags, the
  committer date for lightweight ones).

A tag the scan needs (the ref itself, or the version in a SHA pin's comment) that is not among
those 100 is looked up individually via `GET /repos/{owner}/{repo}/commits/refs/tags/{tag}`.

Release bodies (`description`) come with the same query and feed `notes_flags` and
`current_warnings`. `runs.using` is read from `action.yml` (falling back to `action.yaml`) via
`GET /repos/{owner}/{repo}/contents/{subpath/}action.yml?ref=…` — once per action at the ref in
use and once per action at every offered target SHA. Reusable workflows have no `action.yml` and
get no runtime.

Limit: a version older than the 100 newest tags can still be the *current* version (via that
individual lookup), but it is never offered as a *target*. That is irrelevant in practice — the
targets are by definition the newest versions.

## Versions

A version is a tag of the form `X.Y.Z` with an optional leading `v`. Tags such as `v4` or `v4.1`
are **floating** refs, never targets. Suffixes (`-rc.1`, `-beta`) are not versions, so
pre-releases published only as tags are ignored.

Ordering is numeric per component (`v4.10.0 > v4.9.3`), never by publication date — release
lists are ordered by creation, and backports (a `v5.1.0` released after `v7.0.1`) would
otherwise look newer.

## Eligibility and age

| Repository publishes releases? | Candidates                                             | Age measured from                         | `age_reliable` |
| ------------------------------ | ------------------------------------------------------ | ----------------------------------------- | -------------- |
| yes (≥ 1 non-draft release)    | versions with a non-draft, non-prerelease release      | release `publishedAt` (set by GitHub)     | `true`         |
| no                             | every version tag                                      | tagger date, else committer date          | `false`        |

A candidate is **eligible** when `now − age_timestamp ≥ min_age_days × 86400 s`. `age_days` is
the floor of the elapsed days.

## Current version (`current_source`)

| Ref in the workflow             | Resolution                                                                                         | `current_source`      |
| ------------------------------- | -------------------------------------------------------------------------------------------------- | --------------------- |
| `v4.1.1`                        | the ref itself                                                                                      | `ref`                 |
| `v4`, `v4.1`                    | highest `X.Y.Z` tag pointing at the same commit as the floating tag, within its prefix             | `floating-resolved`   |
|                                 | no such tag: treated as `v4.0.0` / `v4.1.0` for comparison                                          | `floating-unresolved` |
| SHA with `# vX.Y.Z` comment     | the comment, if that tag points at exactly this SHA                                                 | `comment`             |
| SHA, comment missing or stale   | highest `X.Y.Z` tag pointing at the SHA (a stale comment is reported in `notes`)                   | `sha-lookup`          |
| SHA, no tag points at it        | the comment, if its tag no longer exists at all                                                     | `comment-unverified`  |
|                                 | otherwise unknown                                                                                   | `unknown`             |
| anything else (`main`, `latest`)| unknown                                                                                             | `branch`              |

## Rows

With `eligible` = eligible candidates, `latest` = the highest of them, and `same` = the highest
within the current major:

1. `latest > current` → `upgrade` row, `major: true` when the major differs.
2. `same > current` and `same ≠ latest` → `upgrade` row, `major: false`.
3. No row with `major: false` yet, and the ref is a tag → `pin` row for the highest eligible
   version within the ref's range: `v4` → any `4.y.z`, `v4.1` → any `4.1.z`, `v4.1.1` → exactly
   `4.1.1`. `downgrade: true` when that is lower than the current version (the current one is too
   young). This keeps "stay on this major" selectable next to a major upgrade.
4. Current unknown → one `upgrade` row for `latest`, `major: null`.

A SHA pin without a newer version gets no row — it is already pinned.

`too_young` lists up to three versions newer than both the current version and every offered
row that are not yet eligible, with `eligible_in_days`.

## Release-note hints

Both lists are case-insensitive keyword matches over release bodies; each entry is
`{version, url, lines[]}` with at most 3 matching lines per release, trimmed of Markdown list and
heading markers and cut to 200 characters.

| Field              | Releases scanned                                   | Keywords (regex alternatives)                                                                 |
| ------------------ | -------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| `rows[].notes_flags` | `current < v ≤ target`, `upgrade` rows with a known current version | breaking, deprecat, removed, no longer, end of life, EOL, must upgrade/update/migrate, requires … runner/node, minimum … runner/version, will stop working, shut down, sunset, retire |
| `current_warnings` | every `v > current` (the 5 highest with a match)   | deprecat, sunset, shut down, will stop working, no longer work/supported, end of life, EOL, retire, brownout, must upgrade/update/migrate |

Repositories without releases have no bodies, so both lists stay empty there.

## Status

`no-versions` (repository has no version tags) · `upgradeable` (an `upgrade` row exists) ·
`pin-only` · `blocked-by-age` (no rows, but `too_young` is not empty) · `unknown-current` ·
`up-to-date` · `error` (query failed; message in `notes` and `errors[]`).
