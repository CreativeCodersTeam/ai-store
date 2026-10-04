#!/usr/bin/env bash
set -u
TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TESTS_DIR="${TESTS_DIR:-$(cd "$TEST_DIR/.." && pwd)}"
SKILL_DIR="${SKILL_DIR:-$(cd "$TESTS_DIR/../../../../development/upgrade-gh-wf-actions" && pwd)}"
FIX="$TESTS_DIR/fixtures"
SCRIPT="$SKILL_DIR/scripts/release-notes.sh"
# shellcheck source=../helpers.sh
source "$TESTS_DIR/helpers.sh"

export PATH="$TESTS_DIR/mock-gh:$PATH"
export MOCK_GH_DATA="$FIX/gh-data"

# 1. usage
bash "$SCRIPT" --repo acme/checkout --from v4 --to v5.0.0 >/dev/null 2>&1; assert_exit $? 1 "floating --from rejected"
bash "$SCRIPT" --repo acme --from v4.0.0 --to v5.0.0 >/dev/null 2>&1; assert_exit $? 1 "repo without owner rejected"
MOCK_GH_AUTH=fail bash "$SCRIPT" --repo acme/checkout --from v4.0.0 --to v5.0.0 >/dev/null 2>&1
assert_exit $? 2 "gh not authenticated"
bash "$SCRIPT" --repo missing/repo --from v1.0.0 --to v2.0.0 >/dev/null 2>&1; assert_exit $? 4 "unknown repository"

# 2. range: exclusive from, inclusive to, ordered by version, drafts and prereleases out
out=$(bash "$SCRIPT" --repo acme/checkout --from v4.0.0 --to v5.0.0); rc=$?
assert_exit "$rc" 0 "range"
assert_json_eq "$out" '[.releases[].version] | join(",")' "v4.2.2,v4.3.0,v5.0.0" "versions in range"
assert_json_eq "$out" '.releases[2].body | test("Requires runner")' "true" "body included"
assert_json_eq "$out" '.releases[0].url' "https://github.com/acme/checkout/releases/tag/v4.2.2" "release url"
assert_json_eq "$out" '.truncated' "false" "not truncated"

out=$(bash "$SCRIPT" --repo acme/checkout --from v5.0.0 --to v7.0.0)
assert_json_eq "$out" '[.releases[].version] | join(",")' "v5.1.0" "prerelease v6 and draft v7 skipped"

out=$(bash "$SCRIPT" --repo acme/checkout --from v5.1.0 --to v5.1.0)
assert_json_eq "$out" '.releases | length' "0" "empty range"

summary
