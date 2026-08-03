#!/usr/bin/env bash
set -u
TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TESTS_DIR="${TESTS_DIR:-$(cd "$TEST_DIR/.." && pwd)}"
SKILL_DIR="${SKILL_DIR:-$(cd "$TESTS_DIR/../../dotnet-reviewer" && pwd)}"
FIX="$TESTS_DIR/fixtures"
SCRIPT="$SKILL_DIR/scripts/detect-dotnet-version.sh"
# shellcheck source=../helpers.sh
source "$TESTS_DIR/helpers.sh"

# 1. Happy path: net10
out=$(bash "$SCRIPT" --repo-root "$FIX/repo-net10" 2>/dev/null); rc=$?
assert_exit "$rc" 0 "net10 exit code"
assert_json_eq "$out" '.sdk' "10.0.100" "net10 sdk"
assert_json_eq "$out" '.target_frameworks[0]' "net10.0" "net10 tfm"
assert_json_eq "$out" '.project_files | length' "1" "net10 project_files count"

# 2. Pre-10 SDK rejected
out=$(bash "$SCRIPT" --repo-root "$FIX/repo-net8" 2>/dev/null); rc=$?
assert_exit "$rc" 4 "net8 exit code"

# 3. Malformed csproj
out=$(bash "$SCRIPT" --repo-root "$FIX/repo-malformed-csproj" 2>/dev/null); rc=$?
assert_exit "$rc" 5 "malformed csproj exit code"

# 4. --help works
out=$(bash "$SCRIPT" --help 2>&1); rc=$?
assert_exit "$rc" 0 "--help exit code"
[[ "$out" == *"detect-dotnet-version"* ]] && \
  assert_eq "ok" "ok" "--help text mentions script name" || \
  fail "--help text mentions script name"

summary
