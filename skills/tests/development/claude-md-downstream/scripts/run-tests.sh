#!/usr/bin/env bash
# Runs all unit tests.
#
# The fixtures are nested git repositories. They are rebuilt from scratch before
# every run and removed again afterwards, so no stray .git directory is ever
# left inside this repository — a nested .git confuses `git status`, `git add`,
# grep-based tooling and editors, and a fixture that survives between runs also
# silently accumulates whatever the previous run did to it (test-fetch-upstream
# adds a commit to the upstream fixture, for one).
#
# Set KEEP_FIXTURES=1 to leave them in place for debugging a failure. Remember
# to run clean-fixtures.sh afterwards.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/../../../../development/claude-md-downstream" && pwd)"

if ! command -v jq >/dev/null 2>&1; then
  echo "ERROR: jq is required for tests" >&2
  exit 1
fi

cleanup() {
  if [[ "${KEEP_FIXTURES:-0}" == "1" ]]; then
    echo
    echo "KEEP_FIXTURES=1 — fixtures left in $SCRIPT_DIR/fixtures"
    echo "Run 'bash $SCRIPT_DIR/clean-fixtures.sh' when done."
  else
    bash "$SCRIPT_DIR/clean-fixtures.sh" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

EXIT=0
for t in "$SCRIPT_DIR/unit"/test-*.sh; do
  [[ -f "$t" ]] || continue
  echo
  echo "=== $(basename "$t") ==="
  # Each test rebuilds the fixtures itself, so running one directly behaves
  # exactly like running it here.
  if ! TESTS_DIR="$SCRIPT_DIR" SKILL_DIR="$SKILL_DIR" bash "$t"; then
    EXIT=1
  fi
done

exit "$EXIT"
