#!/usr/bin/env bash
# Copies the diagnose-bug eval fixtures to a target directory and gives each one the git
# history the eval prompts assume. Usage: setup-fixtures.sh <target-dir>
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="${1:?usage: setup-fixtures.sh <target-dir>}"
mkdir -p "$TARGET"
commit() { git -C "$1" add -A && git -C "$1" -c user.name=fixture -c user.email=fixture@example.com commit -q -m "$2"; }

for name in monthly-report bank-statement expense-importer; do
  dest="$TARGET/$name"
  rm -rf "$dest"
  cp -R "$HERE/fixtures/$name" "$dest"
  git -C "$dest" init -q
  case "$name" in
    monthly-report)   commit "$dest" "Monthly report CLI" ;;
    expense-importer) commit "$dest" "Expense importer" ;;
    bank-statement)
      # Eval 1 assumes a Node 10 -> 24 bump as the most recent commit.
      printf '10\n' > "$dest/.nvmrc"; commit "$dest" "Statement rendering with running balance"
      printf '24\n' > "$dest/.nvmrc"; commit "$dest" "Bump Node to 24 for CI runners" ;;
  esac
  echo "$dest"
done
