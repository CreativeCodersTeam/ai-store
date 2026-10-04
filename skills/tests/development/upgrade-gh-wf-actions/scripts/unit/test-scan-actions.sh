#!/usr/bin/env bash
set -u
TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TESTS_DIR="${TESTS_DIR:-$(cd "$TEST_DIR/.." && pwd)}"
SKILL_DIR="${SKILL_DIR:-$(cd "$TESTS_DIR/../../../../development/upgrade-gh-wf-actions" && pwd)}"
FIX="$TESTS_DIR/fixtures"
SCRIPT="$SKILL_DIR/scripts/scan-actions.sh"
# shellcheck source=../helpers.sh
source "$TESTS_DIR/helpers.sh"

OLD_V1=$(jq -r '.old["v1.0.0"]' "$FIX/shas.json")

occ() { printf '%s' "$out" | jq -c --arg f "$1" --argjson l "$2" '.occurrences[] | select(.file == $f and .line == $l)'; }

# 1. usage and root errors
bash "$SCRIPT" --bogus >/dev/null 2>&1; assert_exit $? 1 "unknown argument"
bash "$SCRIPT" --root "$FIX/does-not-exist" >/dev/null 2>&1; assert_exit $? 2 "missing root"

# 2. a repository without workflows is not an error
out=$(bash "$SCRIPT" --root "$FIX/repo-empty"); rc=$?
assert_exit "$rc" 0 "empty repo"
assert_json_eq "$out" '.occurrences | length' "0" "empty repo has no occurrences"
assert_json_eq "$out" '.files | length' "0" "empty repo scans no files"

# 3. file discovery: top-level workflows (.yml and .yaml) and composite actions, nothing else
out=$(bash "$SCRIPT" --root "$FIX/repo-basic"); rc=$?
assert_exit "$rc" 0 "basic repo"
assert_json_eq "$out" '.files | join(",")' \
  ".github/actions/composite/action.yaml,.github/actions/crlf/action.yml,.github/workflows/ci.yml,.github/workflows/release.yaml" \
  "scanned files"
assert_json_eq "$out" '.occurrences | length' "14" "remote occurrences"
assert_json_eq "$out" '[.skipped[] | .reason] | join(",")' "local,docker,no-ref" "skipped reasons"

# 4. parsing details
o=$(occ .github/workflows/ci.yml 5)
assert_json_eq "$o" '.kind' "reusable-workflow" "job-level uses is a reusable workflow"
assert_json_eq "$o" '.repo' "acme/multi" "reusable workflow repo"
assert_json_eq "$o" '.subpath' ".github/workflows/reusable.yml" "reusable workflow subpath"

o=$(occ .github/workflows/ci.yml 9)
assert_json_eq "$o" '.ref_type' "semver" "floating tag is semver"
assert_json_eq "$o" '.comment' "null" "no comment"

o=$(occ .github/workflows/ci.yml 10)
assert_json_eq "$o" '.uses' "acme/checkout@v3.6.0" "single quotes stripped"

o=$(occ .github/workflows/ci.yml 11)
assert_json_eq "$o" '.comment' "keep: needed for legacy build" "comment captured"
assert_json_eq "$o" '.comment_version' "null" "prose comment carries no version"

o=$(occ .github/workflows/ci.yml 12)
assert_json_eq "$o" '.action' "acme/multi/init" "subpath action"
assert_json_eq "$o" '.repo' "acme/multi" "subpath action repo"
assert_json_eq "$o" '.kind' "action" "subpath action kind"

o=$(occ .github/workflows/ci.yml 14)
assert_json_eq "$o" '.ref' "$OLD_V1" "sha ref"
assert_json_eq "$o" '.ref_type' "sha" "sha ref type"
assert_json_eq "$o" '.comment_version' "v1.0.0" "version comment"

o=$(occ .github/workflows/ci.yml 17)
assert_json_eq "$o" '.ref_type' "other" "branch ref"

o=$(occ .github/workflows/release.yaml 7)
assert_json_eq "$o" '.uses' "acme/checkout@v4" "double quotes stripped, multi-key step"

o=$(occ .github/actions/crlf/action.yml 4)
assert_json_eq "$o" '.ref' "v5" "CRLF stripped from ref"

# 5. --exclude drops a subtree
out=$(bash "$SCRIPT" --root "$FIX/repo-basic" --exclude .github/actions)
assert_json_eq "$out" '.files | length' "2" "exclude drops composite actions"

summary
