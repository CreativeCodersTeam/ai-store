#!/usr/bin/env bash
# Removes every generated fixture, including the nested git repositories and the
# cached upstream clone. Only the generator and the .gitignore survive.
#
# Nested .git directories inside a working repository are a nuisance — they
# confuse git, editors and search tooling — so nothing here is meant to persist
# between test runs.

set -euo pipefail
FIX="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/fixtures"

find "$FIX" -mindepth 1 -maxdepth 1 \
  ! -name '.gitignore' ! -name 'make-fixtures.sh' \
  -exec rm -rf {} +

echo "Fixtures removed from $FIX"
