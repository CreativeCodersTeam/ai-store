#!/usr/bin/env bash
# locate-artifacts.sh — find Gherkin .feature files and step-definition dirs in a repo.
# Outputs JSON: {feature_files[], step_def_dirs[], feature_count}
# Exit codes: 0 ok (empty is ok), 1 usage, 2 not a directory.

set -u

usage() {
  cat <<EOF
locate-artifacts.sh — locate .feature files and step-definition directories

Usage: locate-artifacts.sh --repo-root <path>
       locate-artifacts.sh --help

Excludes: bin/ obj/ node_modules/ target/ .git/ (anywhere in the tree).

Step-definition directories are inferred from files carrying binding markers:
  - .cs            : [Binding] or [Given]/[When]/[Then]
  - .java / .kt    : @Given/@When/@Then/@Step
  - .js/.ts/.mjs/.cjs : @cucumber/cucumber import or Given(/When(/Then( step calls

Exit codes:
  0  success (no artifacts is still success)
  1  usage error
  2  --repo-root is not a directory
EOF
}

REPO_ROOT=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-root) REPO_ROOT=${2:-}; shift 2 ;;
    --help|-h)   usage; exit 0 ;;
    *) echo "unknown arg: $1" >&2; usage >&2; exit 1 ;;
  esac
done

[[ -n "$REPO_ROOT" ]] || { echo "missing --repo-root" >&2; usage >&2; exit 1; }
[[ -d "$REPO_ROOT" ]] || { echo "not a directory: $REPO_ROOT" >&2; exit 2; }

REPO_ROOT=$(cd "$REPO_ROOT" && pwd)

PRUNE=( -type d \( -name bin -o -name obj -o -name node_modules -o -name target -o -name .git \) -prune )

# --- feature files (relative, sorted) ---
feature_files=()
while IFS= read -r f; do
  [[ -z "$f" ]] && continue
  feature_files+=("${f#"$REPO_ROOT"/}")
done < <(find "$REPO_ROOT" "${PRUNE[@]}" -o -type f -name '*.feature' -print 2>/dev/null | sort)

# --- step-definition directories (relative, unique, sorted) ---
# Candidate source files, then grep for binding markers; collect parent dirs.
step_dirs=()
while IFS= read -r f; do
  [[ -z "$f" ]] && continue
  case "$f" in
    *.cs)
      grep -Eq '\[Binding\]|\[(Given|When|Then|StepDefinition)\b' "$f" || continue ;;
    *.java|*.kt)
      grep -Eq '@(Given|When|Then|And|But|Step)\b' "$f" || continue ;;
    *.js|*.ts|*.mjs|*.cjs)
      grep -Eq '@cucumber/cucumber|\b(Given|When|Then)\s*\(' "$f" || continue ;;
    *) continue ;;
  esac
  d=$(dirname "$f")
  step_dirs+=("${d#"$REPO_ROOT"/}")
done < <(find "$REPO_ROOT" "${PRUNE[@]}" -o -type f \
           \( -name '*.cs' -o -name '*.java' -o -name '*.kt' \
              -o -name '*.js' -o -name '*.ts' -o -name '*.mjs' -o -name '*.cjs' \) -print 2>/dev/null)

# unique + sort the step dirs
uniq_dirs=()
if [[ ${#step_dirs[@]} -gt 0 ]]; then
  while IFS= read -r d; do
    [[ -z "$d" ]] && continue
    uniq_dirs+=("$d")
  done < <(printf '%s\n' "${step_dirs[@]}" | sort -u)
fi

# --- emit JSON (manual, jq-free) ---
json_array() {
  local first=1
  printf '['
  for v in "$@"; do
    [[ $first -eq 0 ]] && printf ','
    first=0
    printf '"%s"' "${v//\"/\\\"}"
  done
  printf ']'
}

ff_json=$(json_array ${feature_files[@]+"${feature_files[@]}"})
sd_json=$(json_array ${uniq_dirs[@]+"${uniq_dirs[@]}"})

printf '{"feature_files":%s,"step_def_dirs":%s,"feature_count":%d}\n' \
  "$ff_json" "$sd_json" "${#feature_files[@]}"
