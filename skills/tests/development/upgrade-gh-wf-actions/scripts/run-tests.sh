#!/usr/bin/env bash
# Runs all unit tests for skills/development/upgrade-gh-wf-actions/scripts/.
#
# The fixtures are static files (no nested git repositories), and every test
# that writes works on a temporary copy, so nothing needs cleaning up afterwards.
# `gh` is replaced by mock-gh/gh, so the suite never touches the network.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/../../../../development/upgrade-gh-wf-actions" && pwd)"

if ! command -v jq >/dev/null 2>&1; then
  echo "ERROR: jq is required for tests" >&2
  exit 1
fi

EXIT=0
for t in "$SCRIPT_DIR/unit"/test-*.sh; do
  [[ -f "$t" ]] || continue
  echo
  echo "=== $(basename "$t") ==="
  if ! TESTS_DIR="$SCRIPT_DIR" SKILL_DIR="$SKILL_DIR" bash "$t"; then
    EXIT=1
  fi
done

exit "$EXIT"
