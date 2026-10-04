#!/usr/bin/env bash
# apply-pins.sh — rewrite the selected `uses:` lines to a commit SHA plus version comment.
#
# Takes the output of check-updates.sh and the row ids the user picked, and turns
# every occurrence of each selected row into
#
#     uses: owner/repo[/path]@<40-hex-sha> # vX.Y.Z
#
# keeping indentation, the `- ` list marker and any quoting. A trailing comment that
# held a version (`# v4`, `# tag=v4.1.1`) is replaced; any other comment text is kept
# after the new version (`# v4.2.2 keep in sync with deploy.yml`). Dependabot and
# Renovate both read the leading `# vX.Y.Z` to keep such pins up to date.
#
# All-or-nothing: every target line is checked first (it must still contain the
# `uses:` value the scan saw). If one has drifted, nothing is written.
#
# Output JSON: {root, applied[], files[]}
#   applied[] = {id, file, line, target_sha, target_version, before, after}
#   files[]   = files that were rewritten, relative to root
# On a failed check (exit 4) the JSON carries failed[] = {id, file, line, expected, actual}
# instead, and applied[] is empty.
#
# Exit codes: 0 all applied, 1 usage, 3 malformed input or unknown row id,
#             4 a target line no longer matches — nothing written,
#             5 two selected rows target the same lines (e.g. major and same-major
#               row of one action) — nothing written.

set -u

UPDATES="" SELECT="" ROOT=""

usage() {
  cat <<EOF
apply-pins.sh — pin selected GitHub Actions to commit SHAs

Usage:
  apply-pins.sh --updates <file> --select <id[,id...]> --root <dir>
  apply-pins.sh --help

Options:
  --updates <file>   output of check-updates.sh
  --select <ids>     comma-separated row ids to apply (e.g. 1,3,4)
  --root <dir>       repository root the scan ran against (file paths are relative to it)
EOF
}

while (( $# > 0 )); do
  case "$1" in
    --updates) [[ $# -ge 2 ]] || { usage >&2; exit 1; }; UPDATES="$2"; shift 2 ;;
    --select)  [[ $# -ge 2 ]] || { usage >&2; exit 1; }; SELECT="$2"; shift 2 ;;
    --root)    [[ $# -ge 2 ]] || { usage >&2; exit 1; }; ROOT="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *)         echo "unknown argument: $1" >&2; usage >&2; exit 1 ;;
  esac
done

[[ -n "$UPDATES" && -n "$SELECT" && -n "$ROOT" ]] || { usage >&2; exit 1; }
[[ "$SELECT" =~ ^[0-9]+(,[0-9]+)*$ ]] || { echo "--select must be a comma-separated list of row ids" >&2; exit 1; }
[[ -f "$UPDATES" ]] || { echo "updates file not found: $UPDATES" >&2; exit 1; }
[[ -d "$ROOT" ]] || { echo "root is not a directory: $ROOT" >&2; exit 1; }
command -v jq >/dev/null 2>&1 || { echo "jq is required" >&2; exit 1; }
ROOT="$(cd "$ROOT" && pwd)"

jq -e '.groups | type == "array"' "$UPDATES" >/dev/null 2>&1 || { echo "malformed updates input" >&2; exit 3; }

IDS_JSON=$(printf '%s' "$SELECT" | jq -Rc 'split(",") | map(tonumber) | unique')

# Selected rows, flattened to one entry per occurrence.
PLAN=$(jq -c --argjson ids "$IDS_JSON" '
  [.groups[] as $g | $g.rows[] | select(.id as $i | $ids | index($i))
   | . as $r | $g.occurrences[]
   | {id: $r.id, file, line, uses, sha: $r.target_sha, version: $r.target_version,
      action: (.uses | sub("@[^@]*$"; ""))}]' "$UPDATES") || { echo "malformed updates input" >&2; exit 3; }

UNKNOWN=$(jq -rn --argjson ids "$IDS_JSON" --slurpfile u "$UPDATES" \
  '[$u[0].groups[].rows[].id] as $known | [$ids[] | select(. as $i | $known | index($i) | not)] | join(",")')
[[ -z "$UNKNOWN" ]] || { echo "unknown row id(s): $UNKNOWN" >&2; exit 3; }

if ! printf '%s' "$PLAN" | jq -e 'all(.[]; (.sha | test("^[0-9a-f]{40}$")) and (.version | type == "string"))' >/dev/null; then
  echo "malformed updates input: a selected row has no valid target_sha" >&2; exit 3
fi

CONFLICT=$(printf '%s' "$PLAN" | jq -c '
  group_by([.file, .line]) | map(select((map(.id) | unique | length) > 1))
  | map({file: .[0].file, line: .[0].line, ids: (map(.id) | unique)})')
if [[ "$CONFLICT" != "[]" ]]; then
  jq -n --arg root "$ROOT" --argjson c "$CONFLICT" '{root:$root, applied:[], files:[], conflicts:$c}'
  echo "selected rows overlap — pick one row per action" >&2
  exit 5
fi

USES_RE="^([[:space:]]*(-[[:space:]]+)?uses:[[:space:]]*)(['\"]?)([^'\"[:space:]#]+)(['\"]?)([[:space:]]*)(#(.*))?$"
VERSION_LEAD_RE='^(tag=|pin@)?v?[0-9]+(\.[0-9]+){0,2}[[:space:]]*(.*)$'

WORK=$(mktemp -d "${TMPDIR:-/tmp}/apply-pins.XXXXXX")
trap 'rm -rf "$WORK"' EXIT

APPLIED="" FAILED=""
COUNT=$(printf '%s' "$PLAN" | jq 'length')
for (( k=0; k<COUNT; k++ )); do
  entry=$(printf '%s' "$PLAN" | jq -c ".[$k]")
  id=$(jq -r .id <<<"$entry"); file=$(jq -r .file <<<"$entry"); line=$(jq -r .line <<<"$entry")
  uses=$(jq -r .uses <<<"$entry"); sha=$(jq -r .sha <<<"$entry")
  version=$(jq -r .version <<<"$entry"); action=$(jq -r .action <<<"$entry")

  path="$ROOT/$file"
  actual=""
  [[ -f "$path" ]] && actual=$(sed -n "${line}p" "$path")
  cr=""
  [[ "$actual" == *$'\r' ]] && cr=$'\r'
  text="${actual%$'\r'}"

  if [[ "$text" =~ $USES_RE && "${BASH_REMATCH[4]}" == "$uses" ]]; then
    lead="${BASH_REMATCH[1]}" q1="${BASH_REMATCH[3]}" q2="${BASH_REMATCH[5]}" old_comment="${BASH_REMATCH[8]}"
    old_comment="${old_comment#"${old_comment%%[![:space:]]*}"}"
    old_comment="${old_comment%"${old_comment##*[![:space:]]}"}"
    rest="$old_comment"
    [[ "$old_comment" =~ $VERSION_LEAD_RE ]] && rest="${BASH_REMATCH[3]}"
    new="${lead}${q1}${action}@${sha}${q2} # ${version}"
    [[ -n "$rest" ]] && new+=" $rest"
    printf '%s\n%s\n' "$line" "$new$cr" >> "$WORK/$(printf '%s' "$file" | cksum | tr -c '0-9\n' _).edits"
    printf '%s\n' "$file" >> "$WORK/files"
    APPLIED+=$(jq -nc --argjson id "$id" --arg file "$file" --argjson line "$line" \
      --arg sha "$sha" --arg version "$version" --arg before "$text" --arg after "$new" \
      '{id:$id, file:$file, line:$line, target_sha:$sha, target_version:$version, before:$before, after:$after}')$'\n'
  else
    FAILED+=$(jq -nc --argjson id "$id" --arg file "$file" --argjson line "$line" \
      --arg expected "$uses" --arg actual "$text" '{id:$id, file:$file, line:$line, expected:$expected, actual:$actual}')$'\n'
  fi
done

if [[ -n "$FAILED" ]]; then
  jq -n --arg root "$ROOT" --argjson f "$(printf '%s' "$FAILED" | jq -sc .)" \
    '{root:$root, applied:[], files:[], failed:$f}'
  echo "target lines changed since the scan — nothing written; re-run the scan" >&2
  exit 4
fi

FILES=$(LC_ALL=C sort -u "$WORK/files")
while IFS= read -r file; do
  [[ -n "$file" ]] || continue
  edits="$WORK/$(printf '%s' "$file" | cksum | tr -c '0-9\n' _).edits"
  awk 'NR == FNR { if (FNR % 2 == 1) n = $0; else r[n] = $0; next }
       FNR in r { print r[FNR]; next }
       { print }' "$edits" "$ROOT/$file" > "$WORK/out" || { echo "rewrite failed: $file" >&2; exit 1; }
  # Write in place (cat >) so the file keeps its mode and inode.
  cat "$WORK/out" > "$ROOT/$file"
done <<<"$FILES"

jq -n --arg root "$ROOT" \
  --argjson a "$(printf '%s' "$APPLIED" | jq -sc .)" \
  --argjson files "$(printf '%s\n' "$FILES" | jq -R . | jq -sc 'map(select(. != ""))')" \
  '{root:$root, applied:$a, files:$files}'
