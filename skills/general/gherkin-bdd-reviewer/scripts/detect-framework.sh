#!/usr/bin/env bash
# detect-framework.sh — detect the BDD framework in use.
# Outputs JSON: {framework, config_files[], signals[]}
#   framework ∈ reqnroll | cucumber-jvm | cucumber-js | unknown
# Exit codes: 0 ok (unknown is ok), 1 usage, 2 not a directory.

set -u

usage() {
  cat <<EOF
detect-framework.sh — detect the BDD framework (Reqnroll / Cucumber-JVM / Cucumber.js)

Usage: detect-framework.sh --repo-root <path>
       detect-framework.sh --help

Signals (first match wins):
  - *.csproj referencing Reqnroll            -> reqnroll
  - pom.xml / build.gradle* with io.cucumber -> cucumber-jvm
  - package.json with @cucumber/cucumber     -> cucumber-js
  - none of the above                        -> unknown

Exit codes:
  0  success (unknown is still success)
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

config_files=()
signals=()
framework="unknown"

# find files of a given name, return relative paths
find_named() {
  find "$REPO_ROOT" "${PRUNE[@]}" -o -type f -name "$1" -print 2>/dev/null | sort
}

# 1. Reqnroll — any .csproj referencing Reqnroll
while IFS= read -r f; do
  [[ -z "$f" ]] && continue
  if grep -qi 'Reqnroll' "$f"; then
    framework="reqnroll"
    config_files+=("${f#"$REPO_ROOT"/}")
    signals+=("Reqnroll PackageReference in ${f#"$REPO_ROOT"/}")
  fi
done < <(find_named '*.csproj')

# 2. Cucumber-JVM — pom.xml or build.gradle* with io.cucumber
if [[ "$framework" == "unknown" ]]; then
  while IFS= read -r f; do
    [[ -z "$f" ]] && continue
    if grep -q 'io\.cucumber' "$f"; then
      framework="cucumber-jvm"
      config_files+=("${f#"$REPO_ROOT"/}")
      signals+=("io.cucumber dependency in ${f#"$REPO_ROOT"/}")
    fi
  done < <( { find_named 'pom.xml'; find_named 'build.gradle'; find_named 'build.gradle.kts'; } )
fi

# 3. Cucumber.js — package.json with @cucumber/cucumber
if [[ "$framework" == "unknown" ]]; then
  while IFS= read -r f; do
    [[ -z "$f" ]] && continue
    if grep -q '@cucumber/cucumber' "$f"; then
      framework="cucumber-js"
      config_files+=("${f#"$REPO_ROOT"/}")
      signals+=("@cucumber/cucumber dependency in ${f#"$REPO_ROOT"/}")
    fi
  done < <(find_named 'package.json')
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

cf_json=$(json_array ${config_files[@]+"${config_files[@]}"})
sg_json=$(json_array ${signals[@]+"${signals[@]}"})

printf '{"framework":"%s","config_files":%s,"signals":%s}\n' \
  "$framework" "$cf_json" "$sg_json"
