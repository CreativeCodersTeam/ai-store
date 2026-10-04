#!/usr/bin/env bash
set -u
TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TESTS_DIR="${TESTS_DIR:-$(cd "$TEST_DIR/.." && pwd)}"
SKILL_DIR="${SKILL_DIR:-$(cd "$TESTS_DIR/../../../../development/upgrade-gh-wf-actions" && pwd)}"
FIX="$TESTS_DIR/fixtures"
SCAN_SCRIPT="$SKILL_DIR/scripts/scan-actions.sh"
SCRIPT="$SKILL_DIR/scripts/check-updates.sh"
# shellcheck source=../helpers.sh
source "$TESTS_DIR/helpers.sh"

export PATH="$TESTS_DIR/mock-gh:$PATH"
export MOCK_GH_DATA="$FIX/gh-data"
NOW=2026-10-04T00:00:00Z

TMP=$(mktemp -d "${TMPDIR:-/tmp}/test-check-updates.XXXXXX")
trap 'rm -rf "$TMP"' EXIT
bash "$SCAN_SCRIPT" --root "$FIX/repo-basic" > "$TMP/scan.json"

sha() { jq -r --arg r "$1" --arg t "$2" '.[$r][$t]' "$FIX/shas.json"; }
grp() { printf '%s' "$out" | jq -c --arg r "$1" --arg f "$2" '.groups[] | select(.repo == $r and .ref == $f)'; }
rows() { printf '%s' "$1" | jq -r '[.rows[] | "\(.kind):\(.target_version):\(.major):\(.downgrade)"] | join(" ")'; }

# 1. usage, auth, malformed input
bash "$SCRIPT" >/dev/null 2>&1; assert_exit $? 1 "missing --scan"
bash "$SCRIPT" --scan "$TMP/scan.json" --min-age-days -1 >/dev/null 2>&1; assert_exit $? 1 "negative min age"
bash "$SCRIPT" --scan "$TMP/scan.json" --now yesterday >/dev/null 2>&1; assert_exit $? 1 "bad --now"
MOCK_GH_AUTH=fail bash "$SCRIPT" --scan "$TMP/scan.json" >/dev/null 2>&1; assert_exit $? 2 "gh not authenticated"
echo '{"foo":1}' > "$TMP/bad.json"
bash "$SCRIPT" --scan "$TMP/bad.json" >/dev/null 2>&1; assert_exit $? 3 "malformed scan"

# 2. default run (7 days)
export MOCK_GH_LOG="$TMP/gh.log"
out=$(bash "$SCRIPT" --scan "$TMP/scan.json" --now "$NOW"); rc=$?
assert_exit "$rc" 0 "default run"
assert_json_eq "$out" '.min_age_days' "7" "default min age"
assert_json_eq "$out" '.now' "$NOW" "--now honoured"
assert_json_eq "$out" '[.groups[].rows[].id] | . == [range(1; length + 1)]' "true" "row ids are 1..n"
assert_json_eq "$out" '.errors[0].repo' "missing/repo" "unreachable repo reported"
assert_json_eq "$out" '.scan_skipped | length' "3" "scan skips passed through"

# floating v4 resolves to v4.3.0 (4 days old): major upgrade to v5.0.0 plus a
# downgrade pin to v4.2.2, v5.1.0 (3 days) is too young.
g=$(grp acme/checkout v4)
assert_json_eq "$g" '.current_version' "v4.3.0" "floating v4 resolved"
assert_json_eq "$g" '.current_source' "floating-resolved" "floating source"
assert_json_eq "$g" '.occurrences | length' "2" "v4 used twice"
assert_eq "$(rows "$g")" "upgrade:v5.0.0:true:false pin:v4.2.2:false:true" "v4 rows"
assert_json_eq "$g" '.rows[0].target_sha' "$(sha checkout v5.0.0)" "major target sha"
assert_json_eq "$g" '.rows[0].age_days' "33" "release age"
assert_json_eq "$g" '.rows[0].age_reliable' "true" "release age is reliable"
assert_json_eq "$g" '.rows[0].immutable' "true" "immutable flag passed through"
assert_json_eq "$g" '.rows[0].compare_url' "https://github.com/acme/checkout/compare/v4.3.0...v5.0.0" "compare url"
assert_json_eq "$g" '.rows[1].target_sha' "$(sha checkout v4.2.2)" "annotated tag dereferenced to commit"
assert_json_eq "$g" '[.too_young[] | "\(.version):\(.eligible_in_days)"] | join(",")' "v5.1.0:4" "too young"
assert_json_eq "$g" '.status' "upgradeable" "v4 status"

# prerelease v6 and draft v7 are never offered
assert_json_eq "$out" '[.groups[].rows[].target_version] | map(select(. == "v6.0.0" or . == "v7.0.0")) | length' "0" \
  "prerelease and draft excluded"

g=$(grp acme/checkout v3.6.0)
assert_json_eq "$g" '.current_source' "ref" "exact ref"
assert_eq "$(rows "$g")" "upgrade:v5.0.0:true:false pin:v3.6.0:false:false" "exact ref gets major + pin"

g=$(grp acme/checkout "$(sha checkout v4.2.2)")
assert_json_eq "$g" '.current_version' "v4.2.2" "uncommented sha resolved"
assert_json_eq "$g" '.current_source' "sha-lookup" "sha lookup source"
assert_eq "$(rows "$g")" "upgrade:v5.0.0:true:false" "sha pin gets no pin row"

g=$(grp acme/checkout "$(sha checkout v4.0.0)")
assert_json_eq "$g" '.current_version' "v4.0.0" "stale comment ignored"
assert_json_eq "$g" '.notes[0] | test("stale")' "true" "stale comment reported"
assert_eq "$(rows "$g")" "upgrade:v5.0.0:true:false upgrade:v4.2.2:false:false" "major and same-major rows"

g=$(grp acme/tagonly v1.0.0)
assert_eq "$(rows "$g")" "upgrade:v1.1.0:false:false" "tag-only upgrade"
assert_json_eq "$g" '.rows[0].age_source' "tag" "tag age source"
assert_json_eq "$g" '.rows[0].age_reliable' "false" "tag age unreliable"
assert_json_eq "$g" '.rows[0].age_days' "12" "tagger date with negative offset crosses a day"
assert_json_eq "$g" '.rows[0].release_url' "https://github.com/acme/tagonly/tree/v1.1.0" "tag url"
assert_json_eq "$g" '[.too_young[].version] | join(",")' "v2.0.0" "rc tag ignored, v2 too young"
assert_json_eq "$g" '.occurrences | length' "2" "workflow and composite grouped"

g=$(grp acme/multi v2)
assert_json_eq "$g" '.actions | join(",")' "acme/multi/.github/workflows/reusable.yml,acme/multi/analyze,acme/multi/init" "subpaths grouped"
assert_eq "$(rows "$g")" "pin:v2.1.0:false:false" "pin only"
assert_json_eq "$g" '.status' "pin-only" "pin-only status"

g=$(grp acme/old "$(sha old v1.0.0)")
assert_json_eq "$g" '.current_source' "comment" "comment verified via extra lookup"
assert_eq "$(rows "$g")" "upgrade:v2.0.0:true:false" "old sha major upgrade"
grep -q 'repos/acme/old/commits/refs/tags/v1.0.0' "$TMP/gh.log" \
  && assert_eq ok ok "extra lookup for tag outside the list" || fail "extra lookup for tag outside the list"
grep -q 'repos/acme/checkout/commits' "$TMP/gh.log" \
  && fail "no extra lookup for known tags" || assert_eq ok ok "no extra lookup for known tags"

g=$(grp acme/branchy main)
assert_json_eq "$g" '.current_source' "branch" "branch ref"
assert_eq "$(rows "$g")" "upgrade:v1.0.0:null:false" "branch gets latest"

g=$(grp acme/checkout v5)
assert_json_eq "$g" '.current_version' "v5.1.0" "crlf v5 resolved"
assert_eq "$(rows "$g")" "pin:v5.0.0:false:true" "too-young current gets downgrade pin"

g=$(grp missing/repo v1)
assert_json_eq "$g" '.status' "error" "missing repo status"
assert_json_eq "$g" '.rows | length' "0" "missing repo has no rows"

# 3. min age 0: everything published counts
out=$(bash "$SCRIPT" --scan "$TMP/scan.json" --now "$NOW" --min-age-days 0)
assert_eq "$(rows "$(grp acme/checkout v4)")" "upgrade:v5.1.0:true:false pin:v4.3.0:false:false" "min age 0"

# 4. min age 40: v5.0.0 (33 days) is no longer eligible
out=$(bash "$SCRIPT" --scan "$TMP/scan.json" --now "$NOW" --min-age-days 40)
g=$(grp acme/checkout v4)
assert_eq "$(rows "$g")" "pin:v4.2.2:false:true" "min age 40 rows"
assert_json_eq "$g" '[.too_young[].version] | join(",")' "v5.1.0,v5.0.0" "min age 40 too young"
assert_json_eq "$g" '.status' "pin-only" "min age 40 status"
g=$(grp acme/multi v2)
assert_json_eq "$g" '.too_young | length' "0" "multi v2 old enough"

# 5. release-note flags, current warnings, runtimes (default run again)
out=$(bash "$SCRIPT" --scan "$TMP/scan.json" --now "$NOW")
g=$(grp acme/checkout v4)
assert_json_eq "$g" '.rows[0].notes_flags | map(.version) | join(",")' "v5.0.0" "flags only from (current, target]"
assert_json_eq "$g" '.rows[0].notes_flags[0].lines | join(" | ")' \
  "Breaking changes | Requires runner v2.327.1 or later" "flagged lines trimmed, CR stripped, unrelated line dropped"
assert_json_eq "$g" '.rows[1].notes_flags | length' "0" "pin row has no flags"
assert_json_eq "$g" '.current_warnings | length' "0" "no deprecation announced after v4.3.0"
assert_json_eq "$g" '[.runtimes[] | "\(.action)=\(.using)"] | join(",")' "acme/checkout=node20" "current runtime"
assert_json_eq "$g" '[.rows[] | .target_runtimes[0].using] | join(",")' "node24,node20" "target runtimes per row"

g=$(grp acme/checkout v3.6.0)
assert_json_eq "$g" '[.current_warnings[] | "\(.version): \(.lines[0])"] | join(",")' \
  "v4.3.0: Deprecation: v3 will stop working on 2026-12-01. Please upgrade." "deprecation of the current version surfaced"
assert_json_eq "$g" '.rows[0].notes_flags | map(.version) | join(",")' "v4.3.0,v5.0.0" "flags across several releases"
assert_json_eq "$g" '.runtimes[0].using' "node16" "old runtime reported"

g=$(grp acme/tagonly v1.0.0)
assert_json_eq "$g" '.runtimes[0].using' "composite" "action.yaml fallback and composite runtime"
assert_json_eq "$g" '.rows[0].notes_flags | length' "0" "tag-only repo has no notes"
assert_json_eq "$g" '.rows[0].target_runtimes[0].using' "composite" "target runtime via action.yaml"

g=$(grp acme/multi v2)
assert_json_eq "$g" '[.runtimes[] | "\(.action)=\(.using)"] | join(",")' \
  "acme/multi/analyze=null,acme/multi/init=node20" "subpath runtimes, unreadable one is null, reusable workflow skipped"
assert_json_eq "$g" '[.rows[0].target_runtimes[] | "\(.action)=\(.using)"] | join(",")' \
  "acme/multi/analyze=null,acme/multi/init=node20" "target runtimes per subpath"

g=$(grp missing/repo v1)
assert_json_eq "$g" '"\(.runtimes | length) \(.current_warnings | length)"' "0 0" "error group has empty lists"

summary
