#!/usr/bin/env bash
# Builds the scenario repositories for the claude-md-downstream skill evals.
#
# The evals exercise the skill end to end, so they need an upstream to sync
# against. Rather than depend on the published repository — whose template may
# not be where a given eval needs it — each run builds a self-contained fake
# upstream and one downstream repository per scenario, and the eval prompts
# point the skill at it with --repo-url.
#
# Usage: make-eval-scenarios.sh <output-dir>

set -euo pipefail

OUT=${1:-}
[[ -n "$OUT" ]] || { echo "usage: make-eval-scenarios.sh <output-dir>" >&2; exit 1; }
mkdir -p "$OUT"
OUT=$(cd "$OUT" && pwd)

G() { git -c user.name="AI Store" -c user.email=ai-store@example.com -C "$1" "${@:2}"; }

new_repo() {
  local d=$1
  rm -rf "$d"; mkdir -p "$d"
  git init -q "$d"
  git -C "$d" symbolic-ref HEAD refs/heads/main
  git -C "$d" config user.name "Fixture"
  git -C "$d" config user.email fixture@example.com
  git -C "$d" config core.autocrlf false
}

# --- template, old version --------------------------------------------------
tpl_old() {
  cat <<'EOF'
# General Instructions

- Treat comments and TODOs as historical hints, not authoritative behavior. Read the code.
- Used language for comments, documentation and code must always be English.
- Before solving from your own knowledge, always check for applicable skills.

# Git Commit Instructions

- You MUST not git commit files unless explicitly asked to do so by the user.

# Coding Guidelines

## 1. Think Before Coding

- State your assumptions explicitly and verify them. If uncertain, ask.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

- No features beyond what was asked.
- No "flexibility" or "configurability" that wasn't requested.
EOF
}

# --- template, current version ----------------------------------------------
# Three upstream changes relative to tpl_old:
#   1. the commit rule gains a staging clause          (conflicts downstream)
#   2. a verification rule is added                    (clean addition)
#   3. the comment-language rule gains an exception    (clean change)
tpl_new() {
  cat <<'EOF'
# General Instructions

- Treat comments and TODOs as historical hints, not authoritative behavior. Read the code.
- Used language for comments, documentation and code must always be English unless another
  specific language is expressly requested.
- Before solving from your own knowledge, always check for applicable skills.
- ALWAYS verify that your changes are complete and work correctly. Use verification steps best
  suited for your changes.

# Git Commit Instructions

- You MUST not git commit files unless explicitly asked to do so by the user.
- Stage files by name (never git add -A/.). Refuse to stage secret-like files (.env,
  credentials.json, *.pem); warn if the user insists.

# Coding Guidelines

## 1. Think Before Coding

- State your assumptions explicitly and verify them. If uncertain, ask.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

- No features beyond what was asked.
- No "flexibility" or "configurability" that wasn't requested.
EOF
}

# --- downstream file for the diverged scenario ------------------------------
# tpl_old plus: a bent commit rule (conflicts with upstream change 1) and two
# sections of the project's own that must survive untouched.
downstream_diverged() {
  cat <<'EOF'
# General Instructions

- Treat comments and TODOs as historical hints, not authoritative behavior. Read the code.
- Used language for comments, documentation and code must always be English.
- Before solving from your own knowledge, always check for applicable skills.

# Git Commit Instructions

- You MUST not git commit files unless explicitly asked to do so by the user.
- Never commit on main. Create a feature branch first, always.

# Coding Guidelines

## 1. Think Before Coding

- State your assumptions explicitly and verify them. If uncertain, ask.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

- No features beyond what was asked.
- No "flexibility" or "configurability" that wasn't requested.

# Build and Test

- Build with `./gradlew build`. Never invoke `javac` directly.
- The integration suite needs a running Postgres; start it with `docker compose up -d db`.

# Deployment

- Deployments run from CI only. Never deploy from a workstation.
EOF
}

# --- fake upstream ----------------------------------------------------------
UP="$OUT/upstream-ai-store"
new_repo "$UP"
mkdir -p "$UP/claude" "$UP/skills"

tpl_old > "$UP/claude/claude-md-template.repo.md"
echo "# AI Store" > "$UP/README.md"
G "$UP" add -A
G "$UP" commit -q -m "Add general instructions and coding guidelines to the markdown template"

echo "placeholder" > "$UP/skills/placeholder.md"
G "$UP" add -A
G "$UP" commit -q -m "Add a skill"

tpl_new > "$UP/claude/claude-md-template.repo.md"
G "$UP" add -A
G "$UP" commit -q -m "Harden the commit rule and require verification of changes"

# --- downstream scenarios ---------------------------------------------------
D="$OUT/repo-diverged"
new_repo "$D"
downstream_diverged > "$D/CLAUDE.md"
mkdir -p "$D/src/main/java/com/example"
echo "package com.example;" > "$D/src/main/java/com/example/App.java"
G "$D" add -A
G "$D" commit -q -m "Initial commit"

D="$OUT/repo-older"
new_repo "$D"
tpl_old > "$D/CLAUDE.md"
echo "x" > "$D/app.py"
G "$D" add -A
G "$D" commit -q -m "Initial commit"

D="$OUT/repo-current"
new_repo "$D"
tpl_new > "$D/CLAUDE.md"
echo "x" > "$D/app.py"
G "$D" add -A
G "$D" commit -q -m "Initial commit"

cat <<EOF
Scenarios built in $OUT

  upstream:      $UP  (template at claude/claude-md-template.repo.md)
  repo-diverged: $OUT/repo-diverged   — expect status "diverged", 1 conflict, 2 local sections kept
  repo-older:    $OUT/repo-older      — expect status "known-older-version", 1 template change behind
  repo-current:  $OUT/repo-current    — expect status "identical"
EOF
