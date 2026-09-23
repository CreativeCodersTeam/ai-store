#!/usr/bin/env bash
set -u
TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TESTS_DIR="${TESTS_DIR:-$(cd "$TEST_DIR/.." && pwd)}"
SKILL_DIR="${SKILL_DIR:-$(cd "$TESTS_DIR/../../../../development/claude-md-downstream" && pwd)}"
FIX="$TESTS_DIR/fixtures"
SCRIPT="$SKILL_DIR/scripts/fetch-upstream.sh"
# shellcheck source=../helpers.sh
source "$TESTS_DIR/helpers.sh"

# The fixtures are nested git repositories and are never kept between runs, so
# build them fresh here. make-fixtures.sh wipes and rebuilds, which also undoes
# whatever an earlier test file did to them.
bash "$TESTS_DIR/fixtures/make-fixtures.sh" >/dev/null

CACHE="$FIX/cache/upstream"
rm -rf "$FIX/cache"

# 1. first run clones
out=$(bash "$SCRIPT" --repo-url "$FIX/upstream" --cache-dir "$CACHE" 2>/dev/null); rc=$?
assert_exit "$rc" 0 "clone exit code"
assert_json_eq "$out" '.action' "cloned" "first run clones"
assert_json_eq "$out" '.stale' "false" "fresh clone is not stale"
assert_json_eq "$out" '.default_branch' "main" "default branch"
[[ -d "$CACHE/.git" ]] && assert_eq ok ok "cache directory created" || fail "cache directory created"

head_sha=$(printf '%s' "$out" | jq -r .head_sha)
expected=$(git -C "$FIX/upstream" rev-parse main)
assert_eq "$head_sha" "$expected" "head_sha matches upstream main"

# 2. second run reuses the cache and fetches
out=$(bash "$SCRIPT" --repo-url "$FIX/upstream" --cache-dir "$CACHE" 2>/dev/null); rc=$?
assert_exit "$rc" 0 "refetch exit code"
assert_json_eq "$out" '.action' "fetched" "second run fetches"

# 3. a new upstream commit is picked up by the refresh
echo "more" >> "$FIX/upstream/README.md"
git -c user.name=fixture -c user.email=fixture@example.com -C "$FIX/upstream" commit -q -am "Extend the readme"
new_head=$(git -C "$FIX/upstream" rev-parse main)
out=$(bash "$SCRIPT" --repo-url "$FIX/upstream" --cache-dir "$CACHE" 2>/dev/null)
assert_json_eq "$out" '.head_sha' "$new_head" "refresh sees the new commit"

# 4. upstream going away after the clone: the cache is reused and flagged stale.
#    Clone from a disposable copy, then delete the copy so the fetch must fail.
GONE=$(mktemp -d)/upstream
cp -R "$FIX/upstream" "$GONE"
WARM=$(mktemp -d)/cache
bash "$SCRIPT" --repo-url "$GONE" --cache-dir "$WARM" >/dev/null 2>&1
rm -rf "$GONE"
out=$(bash "$SCRIPT" --repo-url "$GONE" --cache-dir "$WARM" 2>/dev/null); rc=$?
assert_exit "$rc" 0 "unreachable-with-cache exit code"
assert_json_eq "$out" '.action' "cache-only" "unreachable upstream reuses cache"
assert_json_eq "$out" '.stale' "true" "reused cache is flagged stale"
rm -rf "$WARM"

# 4b. a cache pointing at a different upstream is discarded, not fetched into
out=$(bash "$SCRIPT" --repo-url "$FIX/upstream" --cache-dir "$CACHE" 2>/dev/null)
assert_json_eq "$out" '.action' "fetched" "matching origin is fetched"
git -C "$CACHE" remote set-url origin "$FIX/somewhere-else"
out=$(bash "$SCRIPT" --repo-url "$FIX/upstream" --cache-dir "$CACHE" 2>/dev/null); rc=$?
assert_exit "$rc" 0 "mismatched-origin exit code"
assert_json_eq "$out" '.action' "cloned" "mismatched origin forces a re-clone"

# 5. unreachable upstream with no cache fails
COLD="$FIX/cache/cold"
rm -rf "$COLD"
out=$(bash "$SCRIPT" --repo-url "$FIX/does-not-exist" --cache-dir "$COLD" 2>/dev/null); rc=$?
assert_exit "$rc" 2 "unreachable-no-cache exit code"
[[ ! -d "$COLD" ]] && assert_eq ok ok "failed clone leaves no cache behind" || fail "failed clone leaves no cache behind"

# 6. the default cache directory is derived from the repo url
HOME_TMP=$(mktemp -d)
out=$(HOME="$HOME_TMP" XDG_CACHE_HOME="$HOME_TMP/.cache" bash "$SCRIPT" --repo-url "$FIX/upstream" 2>/dev/null); rc=$?
assert_exit "$rc" 0 "default cache-dir exit code"
cdir=$(printf '%s' "$out" | jq -r .cache_dir)
case "$cdir" in
  "$HOME_TMP/.cache/claude-md-downstream/"*) assert_eq ok ok "default cache dir under XDG_CACHE_HOME" ;;
  *) fail "default cache dir under XDG_CACHE_HOME (got: $cdir)" ;;
esac
rm -rf "$HOME_TMP"

# 7. argument handling
bash "$SCRIPT" --help >/dev/null 2>&1; assert_exit "$?" 0 "--help exit code"
bash "$SCRIPT" --bogus >/dev/null 2>&1; assert_exit "$?" 1 "unknown arg exit code"
bash "$SCRIPT" --repo-url "" >/dev/null 2>&1; assert_exit "$?" 1 "empty --repo-url exit code"

summary
