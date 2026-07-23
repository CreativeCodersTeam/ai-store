#!/usr/bin/env bash
# collect-diff.sh — collect a unified diff restricted to BDD artifacts.
# Output JSON: {loc, files, file_list, diff}
# Exit codes: 0 ok (incl. empty diff), 1 usage, 2 not git, 3 baseline missing.

set -u

usage() {
  cat <<EOF
collect-diff.sh — collect a unified diff of .feature / step-definition changes

Usage:
  collect-diff.sh --repo-root <path> --mode uncommitted|branch [--baseline main] \\
                  [--include-glob '<glob>' ...]
  collect-diff.sh --help

Modes:
  uncommitted  working tree vs HEAD (staged + unstaged + untracked)
  branch       <baseline>...HEAD (default baseline: main)

Includes (BDD artifacts only). Default globs, overridable via --include-glob:
  *.feature  *Steps.*  *StepDefinitions*  *step_definitions*  */steps/*

Exit codes:
  0  success (empty diff is success)
  1  usage error
  2  not a git repository
  3  baseline branch not found (branch mode) or no commits yet (uncommitted mode)
EOF
}

REPO_ROOT="" MODE="" BASELINE="main"
INCLUDES=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-root)    REPO_ROOT=${2:-}; shift 2 ;;
    --mode)         MODE=${2:-};      shift 2 ;;
    --baseline)     BASELINE=${2:-};  shift 2 ;;
    --include-glob) INCLUDES+=("${2:-}"); shift 2 ;;
    --help|-h)      usage; exit 0 ;;
    *) echo "unknown arg: $1" >&2; usage >&2; exit 1 ;;
  esac
done

[[ -n "$REPO_ROOT" && -n "$MODE" ]] || { usage >&2; exit 1; }
case "$MODE" in uncommitted|branch) ;; *) echo "invalid --mode: $MODE" >&2; exit 1 ;; esac
[[ -d "$REPO_ROOT/.git" ]] || { echo "not a git repository: $REPO_ROOT" >&2; exit 2; }

# Default include set restricts the diff to BDD artifacts.
if [[ ${#INCLUDES[@]} -eq 0 ]]; then
  INCLUDES=( '*.feature' '*Steps.*' '*StepDefinitions*' '*step_definitions*' '*/steps/*' )
fi

cd "$REPO_ROOT"

if [[ "$MODE" == "branch" ]]; then
  if ! git rev-parse --verify --quiet "$BASELINE" -- >/dev/null; then
    echo "baseline branch not found: $BASELINE" >&2
    exit 3
  fi
fi

if [[ "$MODE" == "uncommitted" ]] && ! git rev-parse --verify --quiet HEAD -- >/dev/null; then
  echo "repository has no commits yet (HEAD missing)" >&2
  exit 3
fi

if [[ "$MODE" == "uncommitted" ]]; then
  diff_payload=$(git diff HEAD --no-renames -- "${INCLUDES[@]}")
  # Append untracked artifacts as added-from-empty diffs
  while IFS= read -r f; do
    [[ -z "$f" ]] && continue
    diff_payload+=$'\n'$(git diff --no-index --no-renames /dev/null "$f" 2>/dev/null || true)
  done < <(git ls-files --others --exclude-standard -- "${INCLUDES[@]}")
else
  diff_payload=$(git diff "$BASELINE"...HEAD --no-renames -- "${INCLUDES[@]}")
fi

# Count files & LOC from the diff
files=0
loc=0
file_list=()
while IFS= read -r line; do
  case "$line" in
    "+++ b/"*) f=${line#+++ b/}; [[ "$f" != "/dev/null" ]] && { file_list+=("$f"); files=$((files+1)); } ;;
    "+"*|"-"*)
      [[ "$line" == "+++ "* || "$line" == "--- "* ]] || loc=$((loc+1))
      ;;
  esac
done <<< "$diff_payload"

# emit JSON (escape diff payload for JSON string)
json_escape() {
  printf '%s' "$1" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()), end="")'
}

list_json() {
  local first=1
  printf '['
  for v in "$@"; do
    [[ $first -eq 0 ]] && printf ','
    first=0
    printf '"%s"' "${v//\"/\\\"}"
  done
  printf ']'
}

diff_json=$(json_escape "$diff_payload")
fl_json=$(list_json ${file_list[@]+"${file_list[@]}"})

printf '{"loc":%d,"files":%d,"file_list":%s,"diff":%s}\n' \
  "$loc" "$files" "$fl_json" "$diff_json"
