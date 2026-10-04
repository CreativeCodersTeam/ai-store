#!/usr/bin/env bash
# release-notes.sh — the release notes between two versions of one action repository.
#
# Returns every published, non-prerelease release with a full X.Y.Z version v where
# from < v <= to, oldest first, with its body — the material for summarising
# breaking changes, deprecations, and required migration steps of an upgrade the
# user picked. Reads the 100 most recently created releases; when the oldest of
# those is still newer than --from, older releases in the range are missing and
# `truncated` is true.
#
# Output JSON: {repo, from, to, truncated, releases[]}
#   releases[] = {version, published, url, body}
#
# Exit codes: 0 ok (also when the range holds no release), 1 usage,
#             2 gh missing or not authenticated, 4 repository query failed.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="" FROM="" TO=""

usage() {
  cat <<EOF
release-notes.sh — release notes of an action between two versions

Usage:
  release-notes.sh --repo <owner/name> --from <vX.Y.Z> --to <vX.Y.Z>
  release-notes.sh --help

The range is exclusive of --from and inclusive of --to.
EOF
}

while (( $# > 0 )); do
  case "$1" in
    --repo)    [[ $# -ge 2 ]] || { usage >&2; exit 1; }; REPO="$2"; shift 2 ;;
    --from)    [[ $# -ge 2 ]] || { usage >&2; exit 1; }; FROM="$2"; shift 2 ;;
    --to)      [[ $# -ge 2 ]] || { usage >&2; exit 1; }; TO="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *)         echo "unknown argument: $1" >&2; usage >&2; exit 1 ;;
  esac
done

[[ "$REPO" =~ ^[^/[:space:]]+/[^/[:space:]]+$ ]] || { echo "--repo must be owner/name" >&2; usage >&2; exit 1; }
command -v jq >/dev/null 2>&1 || { echo "jq is required" >&2; exit 1; }
for v in "$FROM" "$TO"; do
  jq -en -L "$SCRIPT_DIR" --arg v "$v" 'include "lib"; ($v | semver | .full) == true' >/dev/null 2>&1 \
    || { echo "--from and --to must be full versions like v4.2.1 (got '$v')" >&2; exit 1; }
done

command -v gh >/dev/null 2>&1 || { echo "gh (GitHub CLI) is required" >&2; exit 2; }
gh auth status >/dev/null 2>&1 || { echo "gh is not authenticated — run 'gh auth login'" >&2; exit 2; }

QUERY='query($owner:String!,$name:String!){
  repository(owner:$owner,name:$name){
    releases(first:100,orderBy:{field:CREATED_AT,direction:DESC}){
      nodes{ tagName publishedAt isPrerelease isDraft url description }
    }
  }
}'

resp=$(gh api graphql -f query="$QUERY" -f owner="${REPO%%/*}" -f name="${REPO#*/}" 2>/dev/null)
printf '%s' "$resp" | jq -e '.data.repository != null' >/dev/null 2>&1 \
  || { echo "could not query releases of $REPO" >&2; exit 4; }

printf '%s' "$resp" | jq -L "$SCRIPT_DIR" --arg repo "$REPO" --arg from "$FROM" --arg to "$TO" '
  include "lib";
  ($from | semver | .parts) as $f | ($to | semver | .parts) as $t
  | (.data.repository.releases.nodes | length) as $n
  | [.data.repository.releases.nodes[] | select((.isDraft or .isPrerelease) | not)
     | (.tagName | semver) as $sv | select($sv != null and $sv.full)
     | . + {v: $sv.parts}] as $all
  | {repo: $repo, from: $from, to: $to,
     truncated: ($n >= 100 and ($all | length) > 0 and (($all | min_by(.v) | .v) > $f)),
     releases: ([$all[] | select(.v > $f and .v <= $t)] | sort_by(.v)
                | map({version: .tagName, published: .publishedAt, url, body: (.description // "")}))}'
