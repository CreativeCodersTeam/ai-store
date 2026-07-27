#!/usr/bin/env bash
# run-checks.sh — run optional ng build|lint|test, emit structured JSON.
# Output JSON: {build:{ok,warnings[],errors[]}|null, lint:{ok,violations[]}|null, test:{ok,runner,failed[],duration}|null}
# Always exits 0 (tool failures are reported in JSON, not via exit code) unless usage error.
# NG_BIN env overrides the angular CLI invocation (used by tests); defaults to `npx --no-install ng`.
# The test runner (karma|jest|vitest) is detected from the angular.json test builders;
# Karma-only flags (--browsers) are applied only when Karma is detected.

set -u

usage() {
  cat <<EOF
run-checks.sh — run ng build/lint/test and emit structured JSON

Usage:
  run-checks.sh --repo-root <path> [--build] [--lint] [--test]
  run-checks.sh --help

Each requested check runs independently; failures are reported in JSON, not via exit code.
The test runner (karma/jest/vitest) is detected from angular.json; --browsers is applied only for Karma.
Set NG_BIN to override the Angular CLI invocation (used by tests).
EOF
}

REPO_ROOT=""; DO_BUILD=0; DO_LINT=0; DO_TEST=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-root) REPO_ROOT=${2:-}; shift 2 ;;
    --build) DO_BUILD=1; shift ;;
    --lint)  DO_LINT=1;  shift ;;
    --test)  DO_TEST=1;  shift ;;
    --help|-h) usage; exit 0 ;;
    *) echo "unknown arg: $1" >&2; usage >&2; exit 1 ;;
  esac
done

[[ -n "$REPO_ROOT" && -d "$REPO_ROOT" ]] || { usage >&2; exit 1; }

# Angular CLI invocation. Override with NG_BIN for tests.
NG=${NG_BIN:-"npx --no-install ng"}

run_ng() {
  # captures stdout+stderr into the named variable, returns the exit code
  local _out_var=$1; shift
  local _tmp; _tmp=$(mktemp)
  local _rc=0
  # shellcheck disable=SC2086
  ( cd "$REPO_ROOT" && $NG "$@" ) >"$_tmp" 2>&1 || _rc=$?
  printf -v "$_out_var" '%s' "$(cat "$_tmp")"
  rm -f "$_tmp"
  return "$_rc"
}

json_string() {
  python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()), end="")' <<<"$1"
}

json_string_array() {
  local first=1
  printf '['
  while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    [[ $first -eq 0 ]] && printf ','
    first=0
    printf '%s' "$(json_string "$line")"
  done <<<"$1"
  printf ']'
}

BUILD_JSON="null"
if [[ $DO_BUILD -eq 1 ]]; then
  out=""
  rc=0
  run_ng out build --configuration production || rc=$?
  # ok comes from the exit code; the greps only extract detail lines.
  # Anchored CLI patterns ("✘ [ERROR]", "Error:", "error TS…") avoid false hits
  # on file/chunk names like error-interceptor.ts.
  warnings=$(grep -E '^▲ \[WARNING\]|^Warning:|warning TS[0-9]+' <<<"$out" || true)
  errors=$(grep -E '^[✘X] \[ERROR\]|^Error:|error TS[0-9]+' <<<"$out" || true)
  ok="true"; [[ $rc -ne 0 ]] && ok="false"
  BUILD_JSON=$(printf '{"ok":%s,"warnings":%s,"errors":%s}' \
    "$ok" \
    "$(json_string_array "$warnings")" \
    "$(json_string_array "$errors")")
fi

LINT_JSON="null"
if [[ $DO_LINT -eq 1 ]]; then
  out=""
  rc=0
  run_ng out lint || rc=$?
  # ESLint output lines like "  12:3  error  ..." / "  12:3  warning  ..."
  violations=$(grep -E '^[[:space:]]*[0-9]+:[0-9]+[[:space:]]+(error|warning)' <<<"$out" || true)
  ok="true"; [[ $rc -ne 0 ]] && ok="false"
  LINT_JSON=$(printf '{"ok":%s,"violations":%s}' \
    "$ok" "$(json_string_array "$violations")")
fi

# Detect the configured test runner from the angular.json test builders.
detect_test_runner() {
  python3 - "$REPO_ROOT/angular.json" <<'PY' 2>/dev/null || echo "unknown"
import json, sys
try:
    with open(sys.argv[1]) as f:
        ng = json.load(f)
except Exception:
    print("unknown"); sys.exit(0)
builders = []
for p in (ng.get("projects") or {}).values():
    t = ((p.get("architect") or p.get("targets") or {}).get("test") or {}).get("builder", "")
    builders.append(t)
joined = " ".join(builders)
if "vitest" in joined or "unit-test" in joined:
    print("vitest")
elif "karma" in joined:
    print("karma")
elif "jest" in joined:
    print("jest")
else:
    print("unknown")
PY
}

TEST_JSON="null"
if [[ $DO_TEST -eq 1 ]]; then
  out=""
  rc=0
  runner=$(detect_test_runner)
  TEST_ARGS=(test --watch=false)
  # --browsers is a Karma-only option; the Vitest/Jest builders reject it.
  [[ "$runner" == "karma" ]] && TEST_ARGS+=(--browsers=ChromeHeadless)
  start=$(date +%s)
  run_ng out "${TEST_ARGS[@]}" || rc=$?
  end=$(date +%s)
  # Karma "FAILED", Jest "✕"/"failed", Vitest "×"/"FAIL"/"N failed" summaries
  failed=$(grep -E 'FAILED|✕|×|✗|FAIL |[0-9]+ (failed|failing)' <<<"$out" || true)
  ok="true"; [[ $rc -ne 0 ]] && ok="false"
  TEST_JSON=$(printf '{"ok":%s,"runner":"%s","failed":%s,"duration":%d}' \
    "$ok" "$runner" "$(json_string_array "$failed")" "$((end - start))")
fi

printf '{"build":%s,"lint":%s,"test":%s}\n' "$BUILD_JSON" "$LINT_JSON" "$TEST_JSON"
