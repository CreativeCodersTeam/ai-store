#!/usr/bin/env bash
# check-updates.sh — find newer, old-enough versions for the actions scan-actions.sh found.
#
# For every repository referenced in the scan it asks the GitHub GraphQL API (via
# `gh`) for the 100 most recent releases and the 100 most recently committed tags,
# then decides per (repository, ref) group:
#
#   current   the version in use — from the ref itself (v4.1.1), from the exact tag a
#             floating ref points at (v4 -> v4.2.2), from the version comment of a
#             SHA pin (verified against the tag), or from a tag pointing at the SHA.
#   rows      what can be offered: the newest eligible version overall (flagged
#             major when it crosses a major version), the newest eligible version
#             within the current major when that differs, and — when the ref is a
#             tag and no row stays within the current major — a pin row for the
#             newest eligible version within the ref's range (v4 -> v4.x.y,
#             v4.1 -> v4.1.y, v4.1.1 -> v4.1.1), so staying on the major is always
#             an option next to a major upgrade.
#   too_young newer versions that exist but are younger than the minimum age.
#
# Release notes are scanned, not interpreted: a row's notes_flags lists the lines of
# every release in (current, target] that mention breaking changes, removals,
# deprecations, or new runner requirements; a group's current_warnings lists the
# lines of every release newer than the current one that announce a deprecation,
# sunset, or shutdown — the hint that the version in use may itself stop working.
# Both are keyword matches; the caller judges what they mean. runtimes[] reports
# runs.using of each action at the ref in use (node16, node20, composite, docker).
#
# Eligible = a full X.Y.Z version (optional leading v) that is at least
# --min-age-days old. In a repository that publishes releases, only non-draft,
# non-prerelease releases count and the age is the release's publishedAt, which
# GitHub sets server-side. In a repository without any release the age falls back
# to the tagger date (annotated tag) or the committer date (lightweight tag); both
# are set by whoever created them, so such rows carry age_source "tag" and
# age_reliable false.
#
# Output JSON: {min_age_days, now, groups[], errors[], scan_skipped[]}
#   groups[] = {repo, ref, ref_type, actions[], occurrences[], current_version,
#               current_source, current_sha, status, rows[], too_young[], notes[],
#               current_warnings[], runtimes[]}
#     current_warnings[] = {version, url, lines[]}
#     runtimes[] = {action, using} — using is null when action.yml could not be read
#     current_source ∈ ref | floating-resolved | floating-unresolved | comment
#                      | comment-unverified | sha-lookup | branch | unknown
#     status ∈ upgradeable | pin-only | blocked-by-age | up-to-date
#              | unknown-current | no-versions | error
#     rows[] = {id, kind (upgrade|pin), major, downgrade, target_version, target_sha,
#               published, age_days, age_source (release|tag), age_reliable,
#               immutable, release_url, compare_url, notes_flags[]}
#     notes_flags[] = {version, url, lines[]} — empty for pin rows and when the
#               current version is unknown or the repository has no releases
#     id is a 1-based number unique across all groups — apply-pins.sh selects by it.
#   errors[] = {repo, message} — a repository that could not be queried; its
#              group is still listed with status "error".
#
# Exit codes: 0 ok (per-repository failures are reported inside the JSON),
#             1 usage, 2 gh missing or not authenticated, 3 malformed scan input.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCAN="" MIN_AGE_DAYS=7 NOW=""

usage() {
  cat <<EOF
check-updates.sh — find upgradeable GitHub Actions that are old enough to adopt

Usage:
  check-updates.sh --scan <file|-> [--min-age-days <n>] [--now <ISO-8601>]
  check-updates.sh --help

Options:
  --scan <file|->      output of scan-actions.sh ('-' reads stdin)
  --min-age-days <n>   minimum age of an offered version in days (default: 7)
  --now <ISO-8601>     reference time for the age calculation (default: current time)
EOF
}

while (( $# > 0 )); do
  case "$1" in
    --scan)         [[ $# -ge 2 ]] || { usage >&2; exit 1; }; SCAN="$2"; shift 2 ;;
    --min-age-days) [[ $# -ge 2 ]] || { usage >&2; exit 1; }; MIN_AGE_DAYS="$2"; shift 2 ;;
    --now)          [[ $# -ge 2 ]] || { usage >&2; exit 1; }; NOW="$2"; shift 2 ;;
    -h|--help)      usage; exit 0 ;;
    *)              echo "unknown argument: $1" >&2; usage >&2; exit 1 ;;
  esac
done

[[ -n "$SCAN" ]] || { echo "--scan is required" >&2; usage >&2; exit 1; }
[[ "$MIN_AGE_DAYS" =~ ^[0-9]+$ ]] || { echo "--min-age-days must be a non-negative integer" >&2; exit 1; }
command -v jq >/dev/null 2>&1 || { echo "jq is required" >&2; exit 1; }

if [[ -n "$NOW" ]]; then
  NOW_EPOCH=$(jq -rn --arg s "$NOW" '$s | sub("\\.[0-9]+Z$"; "Z") | fromdateiso8601' 2>/dev/null) \
    || { echo "--now must be an ISO-8601 UTC timestamp like 2026-10-04T12:00:00Z" >&2; exit 1; }
else
  NOW_EPOCH=$(date -u +%s)
fi

command -v gh >/dev/null 2>&1 || { echo "gh (GitHub CLI) is required" >&2; exit 2; }
gh auth status >/dev/null 2>&1 || { echo "gh is not authenticated — run 'gh auth login'" >&2; exit 2; }

WORK=$(mktemp -d "${TMPDIR:-/tmp}/check-updates.XXXXXX")
trap 'rm -rf "$WORK"' EXIT

if [[ "$SCAN" == "-" ]]; then
  cat > "$WORK/scan.json"
else
  [[ -f "$SCAN" ]] || { echo "scan file not found: $SCAN" >&2; exit 1; }
  cp "$SCAN" "$WORK/scan.json"
fi
jq -e '(.occurrences | type == "array") and all(.occurrences[]; (.repo|type=="string") and (.ref|type=="string"))' \
  "$WORK/scan.json" >/dev/null 2>&1 || { echo "malformed scan input" >&2; exit 3; }

# runs.using of <repo>/<subpath>/action.y(a)ml at <ref>, or empty when unreadable.
runtime_of() {
  local repo=$1 subpath=$2 ref=$3 meta using=""
  for meta in action.yml action.yaml; do
    using=$(gh api "repos/$repo/contents/${subpath:+$subpath/}$meta?ref=$ref" 2>/dev/null \
      | jq -r '.content // empty | gsub("\n"; "") | @base64d' 2>/dev/null \
      | sed -n -E "s/^[[:space:]]+using:[[:space:]]*['\"]?([A-Za-z0-9_-]+).*/\1/p" | head -n 1)
    [[ -n "$using" ]] && break
  done
  printf '%s' "$using"
}

QUERY='query($owner:String!,$name:String!){
  repository(owner:$owner,name:$name){
    releases(first:100,orderBy:{field:CREATED_AT,direction:DESC}){
      nodes{ tagName publishedAt isPrerelease isDraft immutable url description }
    }
    refs(refPrefix:"refs/tags/",first:100,orderBy:{field:TAG_COMMIT_DATE,direction:DESC}){
      nodes{ name target{ __typename oid
        ... on Commit{ committedDate }
        ... on Tag{ tagger{ date } target{ __typename oid ... on Commit{ committedDate } } } } }
    }
  }
}'

i=0
while IFS= read -r repo; do
  [[ -n "$repo" ]] || continue
  i=$((i+1))
  owner="${repo%%/*}" name="${repo#*/}"
  resp=$(gh api graphql -f query="$QUERY" -f owner="$owner" -f name="$name" 2>"$WORK/err")
  rc=$?
  if (( rc != 0 )) || ! printf '%s' "$resp" | jq -e '.data.repository != null' >/dev/null 2>&1; then
    msg=$(printf '%s' "$resp" | jq -r '[.errors[]?.message] | join("; ")' 2>/dev/null)
    [[ -n "$msg" ]] || msg=$(tr '\n' ' ' < "$WORK/err")
    [[ -n "$msg" ]] || msg="gh api graphql failed (exit $rc)"
    jq -n --arg repo "$repo" --arg msg "$msg" '{repo:$repo, error:$msg}' > "$WORK/repo-$i.json"
    continue
  fi
  printf '%s' "$resp" > "$WORK/resp-$i.json"

  # Tags the groups depend on but that fell outside the 100 newest: resolve them
  # one by one, so an old pin can still be identified.
  extra="{}"
  while IFS= read -r tag; do
    [[ -n "$tag" ]] || continue
    sha=$(gh api "repos/$repo/commits/refs/tags/$tag" --jq .sha 2>/dev/null) || sha=""
    if [[ "$sha" =~ ^[0-9a-f]{40}$ ]]; then
      extra=$(printf '%s' "$extra" | jq -c --arg t "$tag" --arg s "$sha" '. + {($t): $s}')
    fi
  done < <(jq -r --arg repo "$repo" --slurpfile resp "$WORK/resp-$i.json" '
      ($resp[0].data.repository.refs.nodes | map(.name)) as $known
      | [.occurrences[] | select(.repo == $repo)
         | (if .ref_type == "semver" then .ref else empty end), (.comment_version // empty)]
      | unique | .[] | select(. as $t | $known | index($t) | not)' "$WORK/scan.json")

  # runs.using of each action at the ref in use — one contents call per action and
  # ref. Reusable workflows have no action.yml and are skipped.
  runtimes="[]"
  # \x1f, not a tab: read collapses consecutive whitespace separators, which
  # would shift the fields when subpath is empty.
  while IFS=$'\x1f' read -r action subpath ref; do
    [[ -n "$action" ]] || continue
    using=$(runtime_of "$repo" "$subpath" "$ref")
    runtimes=$(printf '%s' "$runtimes" | jq -c --arg a "$action" --arg r "$ref" --arg u "$using" \
      '. + [{action:$a, ref:$r, using:(if $u == "" then null else $u end)}]')
  done < <(jq -r --arg repo "$repo" '[.occurrences[] | select(.repo == $repo and .kind == "action")
            | [.action, .subpath, .ref]] | unique | .[] | join("\u001f")' "$WORK/scan.json")

  jq -n --arg repo "$repo" --argjson extra "$extra" --argjson runtimes "$runtimes" \
    --slurpfile resp "$WORK/resp-$i.json" \
    '{repo:$repo, data:$resp[0].data.repository, extra:$extra, runtimes:$runtimes}' > "$WORK/repo-$i.json"
done < <(jq -r '.occurrences[].repo' "$WORK/scan.json" | LC_ALL=C sort -u)

if (( i > 0 )); then
  jq -s 'map({key:.repo, value:.}) | from_entries' "$WORK"/repo-*.json > "$WORK/repos.json"
else
  echo '{}' > "$WORK/repos.json"
fi

jq -n -L "$SCRIPT_DIR" --slurpfile scan "$WORK/scan.json" --slurpfile repos "$WORK/repos.json" \
  --argjson now "$NOW_EPOCH" --argjson min_days "$MIN_AGE_DAYS" > "$WORK/out.json" '
include "lib";

# Release-note lines worth a look before upgrading, and lines announcing that an
# older version is going away. Keyword matches only — the caller judges them.
def flag_re: "breaking|deprecat|removed|no longer|end[- ]of[- ]life|\\beol\\b|must (upgrade|update|migrate)|requires? .*(runner|node)|minimum .*(runner|version)|will stop working|shut ?down|sunset|retire";
def warn_re: "deprecat|sunset|shut ?down|will stop working|no longer (work|function|be supported|supported)|end[- ]of[- ]life|\\beol\\b|retire|brownout|must (upgrade|update|migrate)";

($min_days * 86400) as $min_seconds
| $scan[0] as $scan
| $repos[0] as $repos

# --- per repository: tag list and the candidate versions ---------------------
| ($repos | with_entries(.value |= (
    if .error then . else
      .data as $r
      | ([$r.refs.nodes[]
          | {name,
             sha: (if .target.__typename == "Tag"
                   then (if .target.target.__typename == "Commit" then .target.target.oid else null end)
                   else .target.oid end),
             tag_date: (if .target.__typename == "Tag" then .target.tagger.date else .target.committedDate end)}]
         + [.extra | to_entries[] | {name: .key, sha: .value, tag_date: null}]) as $tags
      | ([$r.releases.nodes[] | select(.isDraft | not)]) as $pub
      | ($pub | map({key: .tagName, value: .}) | from_entries) as $rel
      | (($pub | length) > 0) as $has_rel
      | {tags: $tags,
         runtimes: (.runtimes // []),
         candidates: (
           [$tags[]
            | (.name | semver) as $sv
            | select($sv != null and $sv.full and .sha != null)
            | $rel[.name] as $r1
            | select(if $has_rel then ($r1 != null and ($r1.isPrerelease | not)) else true end)
            | (if $has_rel then $r1.publishedAt else .tag_date end) as $date
            | ($date | ts) as $t
            | {tag: .name, v: $sv.parts, sha, published: $date,
               age_source: (if $has_rel then "release" else "tag" end),
               immutable: (if $has_rel then ($r1.immutable // false) else null end),
               url: (if $has_rel then $r1.url else null end),
               body: (if $has_rel then $r1.description else null end),
               age_seconds: (if $t == null then null else ($now - $t) end)}
            | .age_days = (if .age_seconds == null then null else ((.age_seconds / 86400) | floor) end)
            | .eligible = (.age_seconds != null and .age_seconds >= $min_seconds)]
           | sort_by([.v, (.tag | startswith("v") | not)]) | unique_by(.v))}
    end)))
  as $info

# --- per (repo, ref) group ----------------------------------------------------
| [$scan.occurrences | group_by([.repo, .ref])[]
   | .[0] as $o
   | {repo: $o.repo, ref: $o.ref, ref_type: $o.ref_type,
      actions: (map(.action) | unique),
      comment_version: ([.[].comment_version | select(. != null)] | first),
      occurrences: map({file, line, uses})}
   | . as $g
   | $info[$g.repo] as $ri
   | if $ri.error then
       . + {current_version: null, current_source: "unknown", current_sha: null,
            status: "error", rows: [], too_young: [], notes: [$ri.error],
            current_warnings: [], runtimes: []}
     else
       ($ri.tags) as $tags
       | ($ri.candidates) as $cands
       | ($tags | map({key: .name, value: .sha}) | from_entries) as $tagsha
       # highest full version whose tag points at $sha, optionally within a prefix
       | def exact_for($sha; $prefix):
           [$tags[] | select(.sha == $sha and $sha != null)
            | (.name | semver) as $sv | select($sv != null and $sv.full)
            | select($sv.parts[0:($prefix | length)] == $prefix)
            | {v: $sv.parts, tag: .name}] | max_by(.v);
       # --- current version
       ( if $g.ref_type == "semver" then
           ($g.ref | semver) as $rv
           | if $rv.full then
               {cur: {v: $rv.parts, tag: $g.ref}, src: "ref", sha: $tagsha[$g.ref], notes: []}
             else
               exact_for($tagsha[$g.ref]; $rv.parts) as $ex
               | if $ex then {cur: $ex, src: "floating-resolved", sha: $tagsha[$g.ref], notes: []}
                 else {cur: {v: ($rv.parts | pad3), tag: $g.ref}, src: "floating-unresolved",
                       sha: $tagsha[$g.ref],
                       notes: ["\($g.ref) could not be matched to an exact version"]} end
             end
         elif $g.ref_type == "sha" then
           ($g.comment_version | if . then semver else null end) as $cv
           | exact_for($g.ref; []) as $bysha
           | ([$tags[] | select(($cv != null) and ((.name | semver) as $s | $s != null and $s.parts == $cv.parts)) | .sha]
              | first) as $cvsha
           | if $cv != null and $cv.full and $cvsha == $g.ref then
               {cur: {v: $cv.parts, tag: $g.comment_version}, src: "comment", sha: $g.ref, notes: []}
             elif $bysha then
               {cur: $bysha, src: "sha-lookup", sha: $g.ref,
                notes: (if $cv != null and $cvsha != null and $cvsha != $g.ref
                        then ["comment says \($g.comment_version), but that tag points at \($cvsha[0:12]) — the comment is stale"]
                        else [] end)}
             elif $cv != null and $cv.full and $cvsha == null then
               {cur: {v: $cv.parts, tag: $g.comment_version}, src: "comment-unverified", sha: $g.ref,
                notes: ["tag \($g.comment_version) not found — version taken from the comment unverified"]}
             else
               {cur: null, src: "unknown", sha: $g.ref,
                notes: (["no tag points at \($g.ref[0:12])"]
                        + (if $cv != null and $cvsha != null and $cvsha != $g.ref
                           then ["comment says \($g.comment_version), but that tag points at \($cvsha[0:12])"]
                           else [] end))}
             end
         else
           {cur: null, src: "branch", sha: null, notes: ["ref \($g.ref) is a branch or non-version tag"]}
         end ) as $c
       # {version, url, lines[]} for every release passing $cond whose notes match $re
       | def notes_in(cond; $re):
           [$cands[] | select(.body != null) | select(cond)
            | {version: .tag, url, lines: (.body | matching_lines($re) | .[0:3])}
            | select(.lines | length > 0)];
       ($cands | map(select(.eligible))) as $el
       | ($el | max_by(.v)) as $latest
       | (if $c.cur == null then null else ($el | map(select(.v[0] == $c.cur.v[0])) | max_by(.v)) end) as $same
       | def row($kind; $major; $t):
           {kind: $kind, major: $major,
            downgrade: ($c.cur != null and $t.v < $c.cur.v),
            target_version: $t.tag, target_sha: $t.sha, published: $t.published,
            age_days: $t.age_days, age_source: $t.age_source,
            age_reliable: ($t.age_source == "release"), immutable: $t.immutable,
            release_url: ($t.url // "https://github.com/\($g.repo)/tree/\($t.tag)"),
            compare_url: (if $c.cur != null and $c.src != "floating-unresolved" and $c.cur.tag != $t.tag
                          then "https://github.com/\($g.repo)/compare/\($c.cur.tag)...\($t.tag)" else null end),
            notes_flags: (if $kind == "upgrade" and $c.cur != null
                          then notes_in(.v > $c.cur.v and .v <= $t.v; flag_re) else [] end)};
       ( if $c.cur == null then
           (if $latest then [row("upgrade"; null; $latest)] else [] end)
         else
           ( (if $latest and $latest.v > $c.cur.v then [row("upgrade"; ($latest.v[0] > $c.cur.v[0]); $latest)] else [] end)
           + (if $same and $same.v > $c.cur.v and $same.v != $latest.v then [row("upgrade"; false; $same)] else [] end) )
           # Without an upgrade inside the current major, a tag ref still gets a
           # pin row — the way to stay on this major and leave the mutable tag.
           | if (any(.[]; .major == false) | not) and $g.ref_type == "semver" then
               ($g.ref | semver | .parts) as $range
               | ($el | map(select(.v[0:($range | length)] == $range)) | max_by(.v)) as $pin
               | if $pin then . + [row("pin"; false; $pin)] else . end
             else . end
         end ) as $rows
       | ([$cands[] | select((.eligible | not) and ($c.cur == null or .v > $c.cur.v))
           | select(. as $y | all($rows[]; $y.v > (.target_version | semver | .parts)))]
          | sort_by(.v) | reverse | .[0:3]
          | map({version: .tag, published, age_days, age_source,
                 eligible_in_days: (if .age_seconds == null then null
                                    else ((($min_seconds - .age_seconds) / 86400) | ceil) end)})) as $young
       | . + {current_version: ($c.cur.tag // null), current_source: $c.src, current_sha: $c.sha,
              rows: $rows, too_young: $young, notes: $c.notes,
              current_warnings: (if $c.cur == null then []
                                 else notes_in(.v > $c.cur.v; warn_re) | sort_by(.version | semver | .parts) | reverse | .[0:5] end),
              runtimes: [$ri.runtimes[]? | select(.ref == $g.ref and (.action as $a | $g.actions | index($a))) | {action, using}],
              status: (if ($cands | length) == 0 then "no-versions"
                       elif any($rows[]; .kind == "upgrade") then "upgradeable"
                       elif ($rows | length) > 0 then "pin-only"
                       elif ($young | length) > 0 then "blocked-by-age"
                       elif $c.cur == null then "unknown-current"
                       else "up-to-date" end)}
     end
   | del(.comment_version)]

# --- number the rows across all groups ------------------------------------------
| reduce .[] as $g ({n: 0, out: []};
    .n as $n
    | .out += [$g | .rows = [.rows | to_entries[] | .value + {id: ($n + .key + 1)}]]
    | .n += ($g.rows | length))
| .out as $groups
| {min_age_days: $min_days,
   now: ($now | todateiso8601),
   groups: $groups,
   errors: [$repos | to_entries[] | select(.value.error) | {repo: .key, message: .value.error}],
   scan_skipped: ($scan.skipped // [])}
'

# Runtime of every offered target, so a pin or same-major upgrade that still declares
# an old runtime is visible before the user picks it.
echo '[]' > "$WORK/target-runtimes.json"
while IFS=$'\x1f' read -r repo action subpath sha; do
  [[ -n "$repo" ]] || continue
  using=$(runtime_of "$repo" "$subpath" "$sha")
  jq -c --arg a "$action" --arg s "$sha" --arg u "$using" \
    '. + [{action:$a, sha:$s, using:(if $u == "" then null else $u end)}]' \
    "$WORK/target-runtimes.json" > "$WORK/tr.tmp" && mv "$WORK/tr.tmp" "$WORK/target-runtimes.json"
done < <(jq -r --slurpfile scan "$WORK/scan.json" '
    ([$scan[0].occurrences[] | select(.kind == "action") | .action] | unique) as $js
    | [.groups[] as $g | $g.rows[] as $r | $g.actions[] | select(. as $a | $js | index($a))
       | [$g.repo, ., (ltrimstr($g.repo) | ltrimstr("/")), $r.target_sha]]
    | unique | .[] | join("\u001f")' "$WORK/out.json")

jq --slurpfile tr "$WORK/target-runtimes.json" '
  .groups |= map(.actions as $acts | .rows |= map(.target_sha as $s
    | .target_runtimes = [$tr[0][] | select(.sha == $s and (.action as $a | $acts | index($a))) | {action, using}]))' \
  "$WORK/out.json"
