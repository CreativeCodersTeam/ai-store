#!/usr/bin/env bash
# Builds the eval scenario repository for upgrade-gh-wf-actions.
#
# Usage: make-eval-scenarios.sh <target-dir>
# Creates <target-dir>/repo-outdated: a git repository (one commit) whose workflows
# reference real, outdated actions. The evals run against the live GitHub API, so
# the offered versions change over time — assertions check behaviour, not versions.

set -euo pipefail
TARGET="${1:?usage: make-eval-scenarios.sh <target-dir>}"
R="$TARGET/repo-outdated"
rm -rf "$R"
mkdir -p "$R/.github/workflows" "$R/.github/actions/setup-py"

cat > "$R/.github/workflows/ci.yml" <<'YML'
name: CI
on:
  push:
    branches: [main]
  pull_request:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4.0.0
        with:
          node-version: 20
      - uses: actions/cache@88522ab9f39a2ea568f7027eddc7d8d8bc9d59c8 # v3.3.1
        with:
          path: ~/.npm
          key: npm-${{ hashFiles('package-lock.json') }}
      - uses: ./.github/actions/setup-py
      - run: npm ci && npm test
YML

cat > "$R/.github/workflows/codeql.yml" <<'YML'
name: CodeQL
on:
  schedule:
    - cron: '0 3 * * 1'

jobs:
  analyze:
    runs-on: ubuntu-latest
    permissions:
      security-events: write
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v3
        with:
          languages: javascript
      - uses: github/codeql-action/analyze@v3
YML

cat > "$R/.github/actions/setup-py/action.yml" <<'YML'
name: Setup Python
description: Installs Python for the helper scripts
runs:
  using: composite
  steps:
    - uses: actions/setup-python@v5
      with:
        python-version: '3.12'
YML

echo "# demo" > "$R/README.md"
git -C "$R" init -q -b main
git -C "$R" add -A
git -C "$R" -c user.name=eval -c user.email=eval@example.invalid commit -qm "Initial commit"
echo "$R"
