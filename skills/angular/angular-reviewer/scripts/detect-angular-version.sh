#!/usr/bin/env bash
# detect-angular-version.sh — Detect the Angular version and workspace projects in a repo.
# Outputs JSON: {version, projects[], project_files[]}
# Exit codes: 0 ok, 1 usage, 2 not a directory, 4 Angular<17 or none, 5 malformed package.json/angular.json.

set -u

usage() {
  cat <<EOF
detect-angular-version.sh — detect the Angular version and workspace projects

Usage: detect-angular-version.sh --repo-root <path>
       detect-angular-version.sh --help

Exit codes:
  0  success
  1  usage error
  2  not a directory
  4  Angular below 17 or no Angular detected
  5  malformed package.json or angular.json
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

PKG="$REPO_ROOT/package.json"
NG="$REPO_ROOT/angular.json"

[[ -f "$PKG" ]] || { echo "no package.json under $REPO_ROOT" >&2; exit 4; }

py() { python3 "$@"; }

# --- extract @angular/core version from dependencies or devDependencies ---
VERSION=$(py - "$PKG" <<'PY' 2>/dev/null
import json, sys, re
try:
    with open(sys.argv[1]) as f:
        pkg = json.load(f)
except Exception:
    sys.exit(5)
dep = {}
for k in ("dependencies", "devDependencies", "peerDependencies"):
    dep.update(pkg.get(k, {}) or {})
v = dep.get("@angular/core")
if not v:
    print("")
    sys.exit(0)
# strip range operators (^ ~ >= etc.) and any prerelease suffix; keep major
m = re.search(r"(\d+)\.\d+", v)
print(m.group(1) if m else "")
PY
)
rc=$?
if [[ $rc -eq 5 ]]; then
  echo "malformed package.json: $PKG" >&2
  exit 5
fi

if [[ -z "$VERSION" ]]; then
  echo "no @angular/core dependency found in $PKG" >&2
  exit 4
fi

if ! [[ "$VERSION" =~ ^[0-9]+$ ]]; then
  echo "could not parse @angular/core version from $PKG" >&2
  exit 5
fi

if [[ "$VERSION" -lt 17 ]]; then
  echo "Angular major $VERSION detected; this skill targets Angular 17+" >&2
  exit 4
fi

# --- collect workspace project names + their root paths from angular.json (optional) ---
PROJECTS_JSON="[]"
FILES_JSON="[]"
if [[ -f "$NG" ]]; then
  ng_out=$(py - "$NG" <<'PY' 2>/dev/null
import json, sys
try:
    with open(sys.argv[1]) as f:
        ng = json.load(f)
except Exception:
    sys.exit(5)
projects = ng.get("projects", {}) or {}
names = list(projects.keys())
roots = [ (p.get("root") or p.get("sourceRoot") or "") for p in projects.values() ]
# one compact JSON array per line so the shell can read each safely
print(json.dumps(names, separators=(",", ":")))
print(json.dumps(roots, separators=(",", ":")))
PY
)
  if [[ $? -eq 5 || -z "$ng_out" ]]; then
    echo "malformed angular.json: $NG" >&2
    exit 5
  fi
  PROJECTS_JSON=$(printf '%s\n' "$ng_out" | sed -n '1p')
  FILES_JSON=$(printf '%s\n' "$ng_out" | sed -n '2p')
fi

printf '{"version":"%s","projects":%s,"project_files":%s}\n' \
  "$VERSION" "$PROJECTS_JSON" "$FILES_JSON"
