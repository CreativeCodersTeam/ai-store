#!/usr/bin/env bash
set -u
TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TESTS_DIR="${TESTS_DIR:-$(cd "$TEST_DIR/.." && pwd)}"
SKILL_DIR="${SKILL_DIR:-$(cd "$TESTS_DIR/../../../../development/upgrade-gh-wf-actions" && pwd)}"
FIX="$TESTS_DIR/fixtures"
SCAN_SCRIPT="$SKILL_DIR/scripts/scan-actions.sh"
CHECK_SCRIPT="$SKILL_DIR/scripts/check-updates.sh"
SCRIPT="$SKILL_DIR/scripts/apply-pins.sh"
# shellcheck source=../helpers.sh
source "$TESTS_DIR/helpers.sh"

export PATH="$TESTS_DIR/mock-gh:$PATH"
export MOCK_GH_DATA="$FIX/gh-data"
NOW=2026-10-04T00:00:00Z

TMP=$(mktemp -d "${TMPDIR:-/tmp}/test-apply-pins.XXXXXX")
trap 'rm -rf "$TMP"' EXIT
REPO="$TMP/repo"
cp -R "$FIX/repo-basic" "$REPO"
chmod +x "$REPO/.github/workflows/release.yaml"

bash "$SCAN_SCRIPT" --root "$REPO" > "$TMP/scan.json"
bash "$CHECK_SCRIPT" --scan "$TMP/scan.json" --now "$NOW" > "$TMP/updates.json"

sha() { jq -r --arg r "$1" --arg t "$2" '.[$r][$t]' "$FIX/shas.json"; }
row_id() {  # repo ref kind target_version
  jq -r --arg r "$1" --arg f "$2" --arg k "$3" --arg v "$4" \
    '.groups[] | select(.repo == $r and .ref == $f) | .rows[] | select(.kind == $k and .target_version == $v) | .id' \
    "$TMP/updates.json"
}
line() { sed -n "${2}p" "$REPO/$1"; }
snapshot() { (cd "$REPO" && find . -type f -exec cksum {} + | sort); }

V4_MAJOR=$(row_id acme/checkout v4 upgrade v5.0.0)
V4_PIN=$(row_id acme/checkout v4 pin v4.2.2)
TAGONLY=$(row_id acme/tagonly v1.0.0 upgrade v1.1.0)
STALE_SAME=$(row_id acme/checkout "$(sha checkout v4.0.0)" upgrade v4.2.2)
CRLF_PIN=$(row_id acme/checkout v5 pin v5.0.0)
[[ -n "$V4_MAJOR" && -n "$V4_PIN" && -n "$TAGONLY" && -n "$STALE_SAME" && -n "$CRLF_PIN" ]] \
  || { echo "fixture rows missing — check test-check-updates.sh first" >&2; exit 1; }

BEFORE=$(snapshot)

# 1. usage, unknown id, overlap — nothing written
bash "$SCRIPT" --updates "$TMP/updates.json" --select a,b --root "$REPO" >/dev/null 2>&1
assert_exit $? 1 "non-numeric selection"
bash "$SCRIPT" --updates "$TMP/updates.json" --select 999 --root "$REPO" >/dev/null 2>&1
assert_exit $? 3 "unknown row id"
out=$(bash "$SCRIPT" --updates "$TMP/updates.json" --select "$V4_MAJOR,$V4_PIN" --root "$REPO" 2>/dev/null); rc=$?
assert_exit "$rc" 5 "overlapping rows"
assert_json_eq "$out" '.conflicts | length' "2" "both v4 lines reported"
assert_eq "$(snapshot)" "$BEFORE" "nothing written on usage errors and overlap"

# 2. apply four rows
out=$(bash "$SCRIPT" --updates "$TMP/updates.json" --select "$V4_MAJOR,$TAGONLY,$STALE_SAME,$CRLF_PIN" --root "$REPO"); rc=$?
assert_exit "$rc" 0 "apply"
assert_json_eq "$out" '.applied | length' "6" "six lines rewritten"
assert_json_eq "$out" '.files | length' "4" "four files touched"
assert_json_eq "$out" "[.applied[] | select(.id == $V4_MAJOR)] | .[0] | \"\(.target_sha) \(.target_version)\"" \
  "$(sha checkout v5.0.0) v5.0.0" "applied entry carries target sha and version"

S5=$(sha checkout v5.0.0)
assert_eq "$(line .github/workflows/ci.yml 9)" "      - uses: acme/checkout@$S5 # v5.0.0" "floating tag pinned"
assert_eq "$(line .github/workflows/release.yaml 7)" "        uses: \"acme/checkout@$S5\" # v5.0.0" "quotes kept"
assert_eq "$(line .github/workflows/ci.yml 11)" \
  "      - uses: acme/tagonly@$(sha tagonly v1.1.0) # v1.1.0 keep: needed for legacy build" "prose comment kept"
assert_eq "$(line .github/actions/composite/action.yaml 4)" \
  "    - uses: acme/tagonly@$(sha tagonly v1.1.0) # v1.1.0" "every occurrence of the group"
assert_eq "$(line .github/workflows/ci.yml 16)" \
  "      - uses: acme/checkout@$(sha checkout v4.2.2) # v4.2.2" "stale version comment replaced"
assert_eq "$(line .github/workflows/ci.yml 10)" "      - uses: 'acme/checkout@v3.6.0'" "unselected line untouched"
assert_eq "$(sed -n 4p "$REPO/.github/actions/crlf/action.yml" | od -An -c | tr -d ' \n' | tail -c 4)" '\r\n' "CRLF kept"
assert_eq "$(sed -n 1p "$REPO/.github/actions/crlf/action.yml" | od -An -c | tr -d ' \n' | tail -c 4)" '\r\n' "CRLF kept on other lines"
[[ -x "$REPO/.github/workflows/release.yaml" ]] && assert_eq ok ok "file mode kept" || fail "file mode kept"
assert_eq "$(wc -l < "$REPO/.github/workflows/ci.yml" | tr -d ' ')" "$(wc -l < "$FIX/repo-basic/.github/workflows/ci.yml" | tr -d ' ')" \
  "line count unchanged"

# 3. the rewritten lines scan as verified SHA pins
bash "$SCAN_SCRIPT" --root "$REPO" > "$TMP/scan2.json"
assert_json_eq "$(cat "$TMP/scan2.json")" \
  '[.occurrences[] | select(.file == ".github/workflows/ci.yml" and .line == 9)] | .[0] | "\(.ref_type) \(.comment_version)"' \
  "sha v5.0.0" "rescan sees the pin"
bash "$CHECK_SCRIPT" --scan "$TMP/scan2.json" --now "$NOW" > "$TMP/updates2.json"
assert_json_eq "$(cat "$TMP/updates2.json")" \
  "[.groups[] | select(.repo == \"acme/checkout\" and .ref == \"$S5\")] | .[0] | \"\(.current_source) \(.status)\"" \
  "comment blocked-by-age" "pinned v5.0.0 verified via comment, v5.1.0 still too young"

# 4. stale plan: the lines moved on — nothing written, exit 4
AFTER=$(snapshot)
out=$(bash "$SCRIPT" --updates "$TMP/updates.json" --select "$V4_MAJOR,$V4_PIN" --root "$REPO" 2>/dev/null); rc=$?
assert_exit "$rc" 5 "overlap is checked before drift"
out=$(bash "$SCRIPT" --updates "$TMP/updates.json" --select "$V4_MAJOR,$(row_id acme/multi v2 pin v2.1.0)" --root "$REPO" 2>/dev/null); rc=$?
assert_exit "$rc" 4 "drifted lines"
assert_json_eq "$out" '.failed | length' "2" "both drifted v4 lines reported"
assert_eq "$(snapshot)" "$AFTER" "all-or-nothing: valid multi row not written either"

summary
