#!/usr/bin/env bash
# Builds the git fixtures for the claude-md-downstream unit tests.
#
# One fake upstream repository whose template history includes a rename (so the
# --follow trail is actually exercised), plus downstream repositories in each of
# the states the skill has to recognise. Everything is local — the tests never
# touch the network.
#
# Re-runnable: wipes and rebuilds.

set -euo pipefail

FIX="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

G() { git -c user.name=fixture -c user.email=fixture@example.com -C "$1" "${@:2}"; }

new_repo() {
  local d=$1
  rm -rf "$d"; mkdir -p "$d"
  git init -q "$d"
  git -C "$d" symbolic-ref HEAD refs/heads/main
  git -C "$d" config user.name fixture
  git -C "$d" config user.email fixture@example.com
  git -C "$d" config core.autocrlf false
}

# --- template versions ------------------------------------------------------

v1() {
  cat <<'EOF'
# General Instructions

- Always answer in English.
- Read the code, not the comments.

# Git Commit Instructions

- You MUST not git commit files unless explicitly asked to do so by the user.
EOF
}

v2() {
  cat <<'EOF'
# General Instructions

- Always answer in English.
- Read the code, not the comments.

# Git Commit Instructions

- You MUST not git commit files unless explicitly asked to do so by the user.

# Coding Guidelines

- Minimum code that solves the problem. Nothing speculative.
EOF
}

# v3 lives under the renamed path and tightens the commit rule.
v3() {
  cat <<'EOF'
# General Instructions

- Always answer in English.
- Read the code, not the comments.

# Git Commit Instructions

- You MUST not git commit files unless explicitly asked to do so by the user.
- Stage files by name (never git add -A).

# Coding Guidelines

- Minimum code that solves the problem. Nothing speculative.
EOF
}

# v2 plus a project-specific section and a bent rule — the diverged case.
local_diverged() {
  cat <<'EOF'
# General Instructions

- Always answer in English.
- Read the code, not the comments.

# Git Commit Instructions

- You MUST not git commit files unless explicitly asked to do so by the user.
- Commits on main are forbidden; branch first.

# Coding Guidelines

- Minimum code that solves the problem. Nothing speculative.

# Build and Test

- Run `make check` before handing anything back.
EOF
}

# --- upstream ---------------------------------------------------------------

UP="$FIX/upstream"
new_repo "$UP"
mkdir -p "$UP/claude"

v1 > "$UP/claude/claude-md-template.md"
G "$UP" add claude/claude-md-template.md
G "$UP" commit -q -m "Add the CLAUDE.md template"

v2 > "$UP/claude/claude-md-template.md"
G "$UP" add claude/claude-md-template.md
G "$UP" commit -q -m "Add coding guidelines to the template"

git -C "$UP" mv claude/claude-md-template.md claude/claude-md-template.repo.md
v3 > "$UP/claude/claude-md-template.repo.md"
: > "$UP/claude/claude-md-template.user.md"
G "$UP" add -A claude
G "$UP" commit -q -m "Split the template into repo and user variants, harden the commit rule"

# Unrelated commits so the history walk has to filter.
echo "# readme" > "$UP/README.md"
G "$UP" add README.md
G "$UP" commit -q -m "Add a readme"

# --- downstream repositories ------------------------------------------------

# Already on the current template.
D="$FIX/downstream-identical"
new_repo "$D"
v3 > "$D/CLAUDE.md"
G "$D" add CLAUDE.md
G "$D" commit -q -m "Add CLAUDE.md"

# The oldest template verbatim — matching it requires following the rename.
D="$FIX/downstream-older"
new_repo "$D"
v1 > "$D/CLAUDE.md"
mkdir -p "$D/src/nested/deep"
echo "x" > "$D/src/nested/deep/file.txt"
G "$D" add -A
G "$D" commit -q -m "Add CLAUDE.md"

# Local edits on top of v2.
D="$FIX/downstream-diverged"
new_repo "$D"
local_diverged > "$D/CLAUDE.md"
G "$D" add CLAUDE.md
G "$D" commit -q -m "Add CLAUDE.md"

# CRLF and trailing whitespace on the current template — normalisation must see
# through this and still report identical.
D="$FIX/downstream-crlf"
new_repo "$D"
v3 | sed 's/$/   /' | awk '{ printf "%s\r\n", $0 }' > "$D/CLAUDE.md"
printf '\n\n\n' >> "$D/CLAUDE.md"
G "$D" add CLAUDE.md
G "$D" commit -q -m "Add CLAUDE.md with CRLF"

# A repository without a CLAUDE.md.
D="$FIX/downstream-nolocal"
new_repo "$D"
echo "x" > "$D/file.txt"
G "$D" add file.txt
G "$D" commit -q -m "Initial"

# Not a git repository at all.
rm -rf "$FIX/not-a-repo"; mkdir -p "$FIX/not-a-repo"
echo "x" > "$FIX/not-a-repo/file.txt"

# A fake HOME for user-mode tests: ~/.claude/CLAUDE.md holds the v3 text, while
# the user template upstream is empty — so user mode must report empty-template.
rm -rf "$FIX/fake-home"
mkdir -p "$FIX/fake-home/.claude"
v3 > "$FIX/fake-home/.claude/CLAUDE.md"

rm -rf "$FIX/cache"

echo "Fixtures built in $FIX"
