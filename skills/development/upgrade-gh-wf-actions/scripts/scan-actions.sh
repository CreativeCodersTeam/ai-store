#!/usr/bin/env bash
# scan-actions.sh — list every remote action a repository's workflows reference.
#
# Scans the top-level workflow directory (<root>/.github/workflows/*.yml|*.yaml —
# GitHub reads no subdirectories there) and every composite action metadata file
# (**/action.yml|action.yaml) below the root, and reports each `uses:` line that
# points at a remote action or reusable workflow.
#
# Local references (./ or ../) and container references (docker://) carry no
# version that this skill can upgrade; they are listed under `skipped` with a
# reason instead of being dropped silently.
#
# Output JSON: {root, files[], occurrences[], skipped[]}
#   occurrences[] = {file, line, uses, action, repo, subpath, ref, ref_type,
#                    comment, comment_version, kind}
#     file             path relative to root
#     uses             the value exactly as written, without quotes
#     action           uses without the @ref part (owner/repo[/subpath])
#     repo             owner/repo — the repository whose tags and releases count
#     ref_type         sha (40 hex chars) | semver (v1, v1.2, v1.2.3) | other
#     comment          trailing comment text after '#', trimmed, or null
#     comment_version  first version-looking token in the comment, or null
#     kind             action | reusable-workflow
#   skipped[] = {file, line, uses, reason}  reason ∈ local | docker | no-ref | malformed
#
# Exit codes: 0 ok (also when nothing was found), 1 usage, 2 root is not a directory.

set -u

ROOT="$PWD"
EXCLUDES=()

usage() {
  cat <<EOF
scan-actions.sh — list remote GitHub Actions referenced by workflows and composite actions

Usage:
  scan-actions.sh [--root <dir>] [--exclude <relative-path-prefix>]...
  scan-actions.sh --help

Options:
  --root <dir>       repository root to scan (default: current directory)
  --exclude <path>   skip files whose path relative to root starts with <path>;
                     repeatable (use it for test fixtures that are not real workflows)
EOF
}

while (( $# > 0 )); do
  case "$1" in
    --root)    [[ $# -ge 2 ]] || { usage >&2; exit 1; }; ROOT="$2"; shift 2 ;;
    --exclude) [[ $# -ge 2 ]] || { usage >&2; exit 1; }; EXCLUDES+=("${2%/}"); shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *)         echo "unknown argument: $1" >&2; usage >&2; exit 1 ;;
  esac
done

command -v jq >/dev/null 2>&1 || { echo "jq is required" >&2; exit 1; }
[[ -d "$ROOT" ]] || { echo "root is not a directory: $ROOT" >&2; exit 2; }
ROOT="$(cd "$ROOT" && pwd)"

is_excluded() {
  local rel=$1 ex
  for ex in ${EXCLUDES[@]+"${EXCLUDES[@]}"}; do
    [[ "$rel" == "$ex" || "$rel" == "$ex"/* ]] && return 0
  done
  return 1
}

# Workflows: top level only. Composite actions: anywhere, minus vendored trees.
FILES=()
while IFS= read -r f; do
  rel="${f#"$ROOT"/}"
  is_excluded "$rel" || FILES+=("$rel")
done < <(
  {
    if [[ -d "$ROOT/.github/workflows" ]]; then
      find "$ROOT/.github/workflows" -maxdepth 1 -type f \( -name '*.yml' -o -name '*.yaml' \)
    fi
    find "$ROOT" \( -name .git -o -name node_modules \) -prune -o \
      -type f \( -name action.yml -o -name action.yaml \) -print
  } | LC_ALL=C sort -u
)

# `uses:` as a step key (`- uses:`) or a job key (reusable workflow), optionally
# quoted, optionally followed by a comment.
USES_RE="^[[:space:]]*(-[[:space:]]+)?uses:[[:space:]]*(['\"]?)([^'\"[:space:]#]+)(['\"]?)[[:space:]]*(#(.*))?$"
VERSION_RE='(^|[^0-9A-Za-z.])(v?[0-9]+(\.[0-9]+){0,2})([^0-9A-Za-z.]|$)'

OCC=""
SKIP=""

emit_skip() {
  SKIP+=$(jq -nc --arg file "$1" --argjson line "$2" --arg uses "$3" --arg reason "$4" \
    '{file:$file, line:$line, uses:$uses, reason:$reason}')$'\n'
}

for rel in ${FILES[@]+"${FILES[@]}"}; do
  n=0
  while IFS= read -r raw || [[ -n "$raw" ]]; do
    n=$((n+1))
    line="${raw%$'\r'}"
    [[ "$line" == *uses:* ]] || continue
    if ! [[ "$line" =~ $USES_RE ]]; then
      # A `uses:` key we cannot parse (flow mapping, odd quoting) — report it.
      if [[ "$line" =~ ^[[:space:]]*(-[[:space:]]+)?uses: ]]; then
        emit_skip "$rel" "$n" "$line" malformed
      fi
      continue
    fi
    value="${BASH_REMATCH[3]}"
    comment="${BASH_REMATCH[6]}"
    # trim the comment
    comment="${comment#"${comment%%[![:space:]]*}"}"
    comment="${comment%"${comment##*[![:space:]]}"}"

    case "$value" in
      ./*|../*)   emit_skip "$rel" "$n" "$value" local;  continue ;;
      docker://*) emit_skip "$rel" "$n" "$value" docker; continue ;;
    esac
    if [[ "$value" != *@* ]]; then
      emit_skip "$rel" "$n" "$value" no-ref; continue
    fi

    action="${value%@*}"
    ref="${value##*@}"
    owner="${action%%/*}"
    rest="${action#*/}"
    if [[ "$owner" == "$action" || -z "$owner" || -z "$rest" || -z "$ref" ]]; then
      emit_skip "$rel" "$n" "$value" malformed; continue
    fi
    name="${rest%%/*}"
    subpath=""
    [[ "$rest" == */* ]] && subpath="${rest#*/}"

    if [[ "$ref" =~ ^[0-9a-f]{40}$ ]]; then
      ref_type=sha
    elif [[ "$ref" =~ ^v?[0-9]+(\.[0-9]+){0,2}$ ]]; then
      ref_type=semver
    else
      ref_type=other
    fi

    kind=action
    [[ "$subpath" =~ ^\.github/workflows/[^/]+\.ya?ml$ ]] && kind=reusable-workflow

    comment_version=""
    if [[ -n "$comment" && "$comment" =~ $VERSION_RE ]]; then
      comment_version="${BASH_REMATCH[2]}"
    fi

    OCC+=$(jq -nc \
      --arg file "$rel" --argjson line "$n" --arg uses "$value" --arg action "$action" \
      --arg repo "$owner/$name" --arg subpath "$subpath" --arg ref "$ref" \
      --arg ref_type "$ref_type" --arg comment "$comment" --arg cv "$comment_version" \
      --arg kind "$kind" \
      '{file:$file, line:$line, uses:$uses, action:$action, repo:$repo, subpath:$subpath,
        ref:$ref, ref_type:$ref_type,
        comment:(if $comment == "" then null else $comment end),
        comment_version:(if $cv == "" then null else $cv end),
        kind:$kind}')$'\n'
  done < "$ROOT/$rel"
done

FILES_JSON=$(printf '%s\n' ${FILES[@]+"${FILES[@]}"} | jq -R . | jq -sc 'map(select(. != ""))')
OCC_JSON=$(printf '%s' "$OCC" | jq -sc .)
SKIP_JSON=$(printf '%s' "$SKIP" | jq -sc .)

jq -n --arg root "$ROOT" --argjson files "$FILES_JSON" \
  --argjson occ "$OCC_JSON" --argjson skip "$SKIP_JSON" \
  '{root:$root, files:$files, occurrences:$occ, skipped:$skip}'
