#!/usr/bin/env bash
# detect-dotnet-version.sh — Detect .NET SDK and target frameworks in a repo.
# Outputs JSON: {sdk, target_frameworks[], project_files[], resolved_from}
#
# resolved_from names where target_frameworks came from — "csproj",
# "Directory.Build.props", or "global.json" (SDK pinned but no TFM found).
# The script never invents a version: when the repo declares none it exits 4 and
# the calling skill applies the latest-LTS fallback, recording origin "default-lts".
# See dotnet-fundamentals/references/target-framework.md for the full cascade.
#
# Exit codes: 0 ok, 1 usage, 4 no .NET project found, 5 malformed project file.

set -u

usage() {
  cat <<EOF
detect-dotnet-version.sh — detect .NET SDK and target frameworks

Usage: detect-dotnet-version.sh --repo-root <path>
       detect-dotnet-version.sh --help

Exit codes:
  0  success
  1  usage error
  4  no .NET project found (no *.csproj and no global.json)
  5  malformed global.json or *.csproj
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
[[ -d "$REPO_ROOT" ]] || { echo "not a directory: $REPO_ROOT" >&2; exit 1; }

# extract the first <TargetFramework(s)> value from a file; empty if absent
extract_tfm() {
  local f=$1 line
  line=$(grep -oE '<TargetFramework[s]?>[^<]+</TargetFramework[s]?>' "$f" | head -n1 || true)
  [[ -n "$line" ]] || return 0
  printf '%s' "$line" | sed -E 's|<TargetFrameworks?>([^<]+)</TargetFrameworks?>|\1|'
}

# --- parse global.json (optional) — pins the SDK, never a TFM ---
SDK="unknown"
HAS_GLOBAL_JSON=0
if [[ -f "$REPO_ROOT/global.json" ]]; then
  HAS_GLOBAL_JSON=1
  SDK=$(grep -oE '"version"[[:space:]]*:[[:space:]]*"[^"]+"' "$REPO_ROOT/global.json" \
        | head -n1 | sed -E 's/.*"version"[[:space:]]*:[[:space:]]*"([^"]+)".*/\1/')
  if [[ -z "$SDK" ]]; then
    echo "malformed global.json: $REPO_ROOT/global.json" >&2
    exit 5
  fi
fi

# --- parse Directory.Build.props (optional) — repo-wide TFM default ---
PROPS_TFM=""
if [[ -f "$REPO_ROOT/Directory.Build.props" ]]; then
  PROPS_TFM=$(extract_tfm "$REPO_ROOT/Directory.Build.props")
fi

# --- find all *.csproj and extract <TargetFramework(s)> ---
# bash 3.2 compatible: read into array via while loop
projects=()
while IFS= read -r line; do
  projects+=("$line")
done < <(find "$REPO_ROOT" -type f -name '*.csproj' -not -path '*/bin/*' -not -path '*/obj/*' 2>/dev/null | sort)

all_tfms=()
rel_paths=()
RESOLVED_FROM=""

for p in "${projects[@]:-}"; do
  [[ -n "$p" ]] || continue
  rel=${p#"$REPO_ROOT/"}
  rel_paths+=("$rel")
  # crude check for malformed XML: must contain </Project>
  if ! grep -q '</Project>' "$p"; then
    echo "malformed csproj: $p" >&2
    exit 5
  fi
  tfm_value=$(extract_tfm "$p")
  if [[ -z "$tfm_value" ]]; then
    # a project may inherit its TFM from Directory.Build.props
    if [[ -n "$PROPS_TFM" ]]; then
      tfm_value=$PROPS_TFM
      [[ -n "$RESOLVED_FROM" ]] || RESOLVED_FROM="Directory.Build.props"
    else
      echo "no TargetFramework in: $p" >&2
      exit 5
    fi
  else
    RESOLVED_FROM="csproj"
  fi
  IFS=';' read -r -a parts <<<"$tfm_value"
  for t in "${parts[@]}"; do
    [[ -n "$t" ]] && all_tfms+=("$t")
  done
done

# --- nothing to go on: the repo declares no .NET version anywhere ---
if [[ ${#all_tfms[@]} -eq 0 ]]; then
  if [[ $HAS_GLOBAL_JSON -eq 1 ]]; then
    RESOLVED_FROM="global.json"
  else
    echo "no .NET project found under $REPO_ROOT (no *.csproj, no global.json)" >&2
    exit 4
  fi
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

if [[ ${#all_tfms[@]} -gt 0 ]]; then
  tfms_json=$(json_array "${all_tfms[@]}")
else
  tfms_json="[]"
fi

if [[ ${#rel_paths[@]} -gt 0 ]]; then
  project_files_json=$(json_array "${rel_paths[@]}")
else
  project_files_json="[]"
fi

printf '{"sdk":"%s","target_frameworks":%s,"project_files":%s,"resolved_from":"%s"}\n' \
  "$SDK" "$tfms_json" "$project_files_json" "$RESOLVED_FROM"
