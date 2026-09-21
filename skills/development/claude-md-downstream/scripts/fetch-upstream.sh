#!/usr/bin/env bash
# fetch-upstream.sh — make the upstream skill repository available locally.
#
# Keeps a blobless clone in a cache directory and refreshes it on every run, so
# the history of the CLAUDE.md template can be walked offline afterwards. Blobs
# are fetched lazily; the template is a few kilobytes, so this stays cheap even
# across a long history.
#
# Output JSON: {repo_url, cache_dir, head_sha, head_short, default_branch, action, stale}
#   action ∈ cloned | fetched | cache-only   (cache-only ⇒ refresh failed, cache reused)
#   stale  = true when the refresh failed and the cached state may lag upstream
#
# Exit codes: 0 ok, 1 usage, 2 upstream unreachable and no usable cache.

set -u

REPO_URL="https://github.com/CreativeCodersTeam/ai-store.git"
CACHE_DIR=""

usage() {
  cat <<EOF
fetch-upstream.sh — clone or refresh the cached upstream skill repository

Usage:
  fetch-upstream.sh [--repo-url <url>] [--cache-dir <path>]
  fetch-upstream.sh --help

Defaults:
  --repo-url   $REPO_URL
  --cache-dir  \${XDG_CACHE_HOME:-\$HOME/.cache}/claude-md-downstream/<repo-slug>

Exit codes:
  0  success (including a stale cache reused after a failed refresh)
  1  usage error
  2  upstream unreachable and no usable cache
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-url)  REPO_URL=${2:-};  shift 2 ;;
    --cache-dir) CACHE_DIR=${2:-}; shift 2 ;;
    --help|-h)   usage; exit 0 ;;
    *) echo "unknown arg: $1" >&2; usage >&2; exit 1 ;;
  esac
done

[[ -n "$REPO_URL" ]] || { echo "empty --repo-url" >&2; usage >&2; exit 1; }

command -v git >/dev/null 2>&1 || { echo "git not found on PATH" >&2; exit 2; }

# Derive a filesystem-safe slug so several upstreams (e.g. a fork) can coexist.
slug=$(printf '%s' "$REPO_URL" | sed -e 's|\.git$||' -e 's|^[a-z+]*://||' -e 's|^[^/]*@||' -e 's|:|/|g' | tr -c 'A-Za-z0-9._-' '-')
if [[ -z "$CACHE_DIR" ]]; then
  CACHE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/claude-md-downstream/$slug"
fi

ACTION=""
STALE=false

# A cache whose origin points somewhere else answers a different question than
# the one being asked, so it is discarded rather than fetched into.
if [[ -d "$CACHE_DIR/.git" ]]; then
  cached_origin=$(git -C "$CACHE_DIR" remote get-url origin 2>/dev/null || echo "")
  if [[ "$cached_origin" != "$REPO_URL" ]]; then
    echo "warning: cache at $CACHE_DIR points at ${cached_origin:-nothing} — re-cloning" >&2
    rm -rf "$CACHE_DIR"
  fi
fi

if [[ -d "$CACHE_DIR/.git" ]]; then
  if git -C "$CACHE_DIR" fetch --quiet --prune origin 2>/dev/null; then
    ACTION="fetched"
  else
    ACTION="cache-only"
    STALE=true
    echo "warning: could not reach $REPO_URL — reusing cached clone at $CACHE_DIR" >&2
  fi
else
  rm -rf "$CACHE_DIR"
  mkdir -p "$(dirname "$CACHE_DIR")" || { echo "cannot create cache parent for $CACHE_DIR" >&2; exit 2; }
  # Blobless + no checkout: history and trees only, blobs on demand.
  if git clone --quiet --filter=blob:none --no-checkout "$REPO_URL" "$CACHE_DIR" 2>/dev/null; then
    ACTION="cloned"
  elif git clone --quiet --no-checkout "$REPO_URL" "$CACHE_DIR" 2>/dev/null; then
    # Server or transport without partial-clone support — a full clone still works.
    ACTION="cloned"
  else
    rm -rf "$CACHE_DIR"
    echo "cannot clone $REPO_URL" >&2
    exit 2
  fi
fi

# Resolve the upstream default branch from the remote HEAD, falling back to main.
DEFAULT_BRANCH=$(git -C "$CACHE_DIR" symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null | sed 's|^origin/||')
if [[ -z "$DEFAULT_BRANCH" ]]; then
  git -C "$CACHE_DIR" remote set-head origin --auto >/dev/null 2>&1 || true
  DEFAULT_BRANCH=$(git -C "$CACHE_DIR" symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null | sed 's|^origin/||')
fi
[[ -n "$DEFAULT_BRANCH" ]] || DEFAULT_BRANCH="main"

HEAD_SHA=$(git -C "$CACHE_DIR" rev-parse "origin/$DEFAULT_BRANCH" 2>/dev/null || true)
if [[ -z "$HEAD_SHA" ]]; then
  echo "cannot resolve origin/$DEFAULT_BRANCH in $CACHE_DIR" >&2
  exit 2
fi
HEAD_SHORT=$(git -C "$CACHE_DIR" rev-parse --short "$HEAD_SHA")

printf '{"repo_url":"%s","cache_dir":"%s","head_sha":"%s","head_short":"%s","default_branch":"%s","action":"%s","stale":%s}\n' \
  "$REPO_URL" "$CACHE_DIR" "$HEAD_SHA" "$HEAD_SHORT" "$DEFAULT_BRANCH" "$ACTION" "$STALE"
