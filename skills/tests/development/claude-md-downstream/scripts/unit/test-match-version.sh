#!/usr/bin/env bash
set -u
TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TESTS_DIR="${TESTS_DIR:-$(cd "$TEST_DIR/.." && pwd)}"
SKILL_DIR="${SKILL_DIR:-$(cd "$TESTS_DIR/../../../../development/claude-md-downstream" && pwd)}"
FIX="$TESTS_DIR/fixtures"
SCRIPT="$SKILL_DIR/scripts/match-version.sh"
FETCH="$SKILL_DIR/scripts/fetch-upstream.sh"
# shellcheck source=../helpers.sh
source "$TESTS_DIR/helpers.sh"

# The fixtures are nested git repositories and are never kept between runs, so
# build them fresh here. make-fixtures.sh wipes and rebuilds, which also undoes
# whatever an earlier test file did to them.
bash "$TESTS_DIR/fixtures/make-fixtures.sh" >/dev/null

CACHE="$FIX/cache/upstream"
[[ -d "$CACHE/.git" ]] || bash "$FETCH" --repo-url "$FIX/upstream" --cache-dir "$CACHE" >/dev/null 2>&1

# Fixture SHAs are rebuilt with fresh timestamps, so resolve them rather than
# hard-coding. git log lists newest first, and --reverse is unreliable together
# with --follow, so index from the end instead: V3 newest, V1 oldest.
TEMPLATE_LOG=$(git -C "$FIX/upstream" log --follow --format=%H -- claude/claude-md-template.repo.md)
V3=$(printf '%s\n' "$TEMPLATE_LOG" | sed -n 1p)
V2=$(printf '%s\n' "$TEMPLATE_LOG" | sed -n 2p)
V1=$(printf '%s\n' "$TEMPLATE_LOG" | sed -n 3p)
[[ -n "$V1" && -n "$V2" && -n "$V3" ]] || { echo "fixture history incomplete — rebuild fixtures" >&2; exit 1; }

run() { bash "$SCRIPT" --cache-dir "$CACHE" "$@" 2>/dev/null; }

# 1. the current template verbatim
out=$(run --mode repo --start-dir "$FIX/downstream-identical"); rc=$?
assert_exit "$rc" 0 "identical exit code"
assert_json_eq "$out" '.status' "identical" "identical status"
assert_json_eq "$out" '.local_file' "$FIX/downstream-identical/CLAUDE.md" "identical local_file"
assert_json_eq "$out" '.template_path' "claude/claude-md-template.repo.md" "repo mode template path"

# 1b. `identical` names the commit that last changed the template, NOT the
#     branch tip — the fixture's tip is the unrelated "Add a readme" commit.
tip=$(git -C "$FIX/upstream" rev-parse main)
assert_json_eq "$out" '.matched.sha' "$V3" "identical names the last template commit"
[[ "$tip" != "$V3" ]] && assert_eq ok ok "fixture tip really is an unrelated commit" \
  || fail "fixture tip really is an unrelated commit (tip == V3, test is toothless)"
assert_json_eq "$out" '.matched.path' "claude/claude-md-template.repo.md" "identical matched path"
assert_json_eq "$out" '.commit_urls' "false" "local upstream reports commit_urls false"

# 2. CRLF, trailing whitespace and trailing blank lines are normalised away
out=$(run --mode repo --start-dir "$FIX/downstream-crlf")
assert_json_eq "$out" '.status' "identical" "crlf file still counts as identical"

# 3. the oldest template verbatim — only found by following the rename
out=$(run --mode repo --start-dir "$FIX/downstream-older"); rc=$?
assert_exit "$rc" 0 "known-older exit code"
assert_json_eq "$out" '.status' "known-older-version" "known-older status"
assert_json_eq "$out" '.matched.sha' "$V1" "known-older matches the first template commit"
assert_json_eq "$out" '.behind_by' "2" "known-older is two template changes behind"
assert_json_eq "$out" '.matched.path' "claude/claude-md-template.md" "matched path is the pre-rename name"
assert_json_eq "$out" '.history | length' "3" "history covers all three template commits"
mf=$(printf '%s' "$out" | jq -r .files.matched)
[[ -s "$mf" ]] && assert_eq ok ok "matched version materialised" || fail "matched version materialised"

# 3b. the documented invariant: history includes the matched commit, and
#     behind_by is its index — a "since then" list that includes it is off by one.
at_idx=$(printf '%s' "$out" | jq -r '.history[.behind_by].sha')
assert_json_eq "$out" '.history[.behind_by].sha' "$(printf '%s' "$out" | jq -r .matched.sha)" \
  "history[behind_by] is the matched commit"
assert_eq "$at_idx" "$V1" "history[behind_by] resolves to the oldest template commit"
hl=$(printf '%s' "$out" | jq '.history | length')
bb=$(printf '%s' "$out" | jq '.behind_by')
assert_eq "$((hl - 1))" "$bb" "behind_by is one less than the full history length"

# 4. a local upstream has no browsable commit view, so no link is invented
assert_json_eq "$out" '.matched.url' "null" "local upstream yields no commit url"
nulls=$(printf '%s' "$out" | jq '[.history[] | select(.url == null)] | length')
assert_eq "$nulls" "3" "every history entry omits the url too"

# 4b. a GitHub remote does get a link. match-version.sh only reads the remote
#     url, so pointing it at github.com without fetching is enough.
orig_origin=$(git -C "$CACHE" remote get-url origin)
git -C "$CACHE" remote set-url origin "https://github.com/acme/ai-store.git"
gh_out=$(run --mode repo --start-dir "$FIX/downstream-older")
assert_json_eq "$gh_out" '.matched.url' "https://github.com/acme/ai-store/commit/$V1" "github https remote yields a commit url"
git -C "$CACHE" remote set-url origin "git@github.com:acme/ai-store.git"
gh_out=$(run --mode repo --start-dir "$FIX/downstream-older")
assert_json_eq "$gh_out" '.matched.url' "https://github.com/acme/ai-store/commit/$V1" "github scp remote yields a commit url"
git -C "$CACHE" remote set-url origin "https://gitlab.com/acme/ai-store.git"
gh_out=$(run --mode repo --start-dir "$FIX/downstream-older")
assert_json_eq "$gh_out" '.matched.url' "https://gitlab.com/acme/ai-store/-/commit/$V1" "gitlab remote uses its own commit path"
gh_out=$(run --mode repo --start-dir "$FIX/downstream-identical")
assert_json_eq "$gh_out" '.commit_urls' "true" "a github remote reports commit_urls true"
git -C "$CACHE" remote set-url origin "$orig_origin"

# 4c. the work directory is tied to this cache, not shared between upstreams
wd=$(printf '%s' "$out" | jq -r .work_dir)
case "$wd" in
  "$CACHE"-work/repo) assert_eq ok ok "work dir is scoped to the cache" ;;
  *) fail "work dir is scoped to the cache (got: $wd)" ;;
esac

# 5. repo mode resolves the repository root from any subdirectory
out=$(run --mode repo --start-dir "$FIX/downstream-older/src/nested/deep")
assert_json_eq "$out" '.local_file' "$FIX/downstream-older/CLAUDE.md" "nested start-dir resolves to the repo root"
assert_json_eq "$out" '.status' "known-older-version" "nested start-dir yields the same status"

# 6. locally edited on top of v2
out=$(run --mode repo --start-dir "$FIX/downstream-diverged"); rc=$?
assert_exit "$rc" 0 "diverged exit code"
assert_json_eq "$out" '.status' "diverged" "diverged status"
assert_json_eq "$out" '.matched' "null" "diverged has no exact match"
assert_json_eq "$out" '.best_base.sha' "$V2" "diverged base is the second template commit"
assert_json_eq "$out" '.behind_by' "1" "diverged is one template change behind its base"
bf=$(printf '%s' "$out" | jq -r .files.base)
cf=$(printf '%s' "$out" | jq -r .files.current)
[[ -s "$bf" && -s "$cf" ]] && assert_eq ok ok "base and current materialised" || fail "base and current materialised"
sim=$(printf '%s' "$out" | jq -r .best_base.similarity)
awk -v s="$sim" 'BEGIN { exit !(s > 0.5 && s < 1.0) }' \
  && assert_eq ok ok "diverged similarity is plausible ($sim)" \
  || fail "diverged similarity is plausible (got $sim)"

# 7. similarity ranking prefers v2 over v1 and v3 for this file
s1=$(printf '%s' "$out" | jq -r --arg s "$V1" '.history[] | select(.sha==$s) | .similarity')
s2=$(printf '%s' "$out" | jq -r --arg s "$V2" '.history[] | select(.sha==$s) | .similarity')
awk -v a="$s2" -v b="$s1" 'BEGIN { exit !(a > b) }' \
  && assert_eq ok ok "v2 scores higher than v1" \
  || fail "v2 scores higher than v1 ($s2 vs $s1)"

# 8. no CLAUDE.md in the repository
out=$(run --mode repo --start-dir "$FIX/downstream-nolocal"); rc=$?
assert_exit "$rc" 0 "no-local exit code"
assert_json_eq "$out" '.status' "no-local-file" "no-local status"
assert_json_eq "$out" '.local_exists' "false" "no-local local_exists"
cf=$(printf '%s' "$out" | jq -r .files.current)
[[ -s "$cf" ]] && assert_eq ok ok "current template still materialised for creation" || fail "current template still materialised for creation"

# 9. user mode targets $HOME/.claude/CLAUDE.md; upstream's user template is empty
out=$(HOME="$FIX/fake-home" run --mode user); rc=$?
assert_exit "$rc" 0 "user mode exit code"
assert_json_eq "$out" '.status' "empty-template" "empty user template reported"
assert_json_eq "$out" '.local_file' "$FIX/fake-home/.claude/CLAUDE.md" "user mode local_file"
assert_json_eq "$out" '.template_path' "claude/claude-md-template.user.md" "user mode template path"

# 10. a template path that never existed upstream
out=$(run --mode repo --start-dir "$FIX/downstream-identical" --template-path claude/nope.md)
assert_json_eq "$out" '.status' "no-template" "missing template path reported"

# 11. user mode does not need a git repository
out=$(HOME="$FIX/fake-home" bash "$SCRIPT" --cache-dir "$CACHE" --mode user --start-dir "$FIX/not-a-repo" 2>/dev/null); rc=$?
assert_exit "$rc" 0 "user mode outside a repo still runs"

# 12. repo mode outside a git repository — must be outside this repository too,
#     so use a temp directory rather than the fixture under skills/.
OUTSIDE=$(mktemp -d)
run --mode repo --start-dir "$OUTSIDE" >/dev/null; assert_exit "$?" 3 "not-a-repo exit code"
rm -rf "$OUTSIDE"

# 13. an unusable cache
bash "$SCRIPT" --cache-dir "$FIX/not-a-repo" --mode repo --start-dir "$FIX/downstream-identical" >/dev/null 2>&1
assert_exit "$?" 2 "bad cache exit code"

# 14. --max-history truncates the walk
out=$(run --mode repo --start-dir "$FIX/downstream-diverged" --max-history 1)
assert_json_eq "$out" '.history | length' "1" "--max-history truncates the history"

# 15. argument handling
bash "$SCRIPT" --help >/dev/null 2>&1; assert_exit "$?" 0 "--help exit code"
bash "$SCRIPT" --cache-dir "$CACHE" >/dev/null 2>&1; assert_exit "$?" 1 "missing --mode exit code"
bash "$SCRIPT" --cache-dir "$CACHE" --mode sideways >/dev/null 2>&1; assert_exit "$?" 1 "invalid --mode exit code"
bash "$SCRIPT" --cache-dir "$CACHE" --mode repo --max-history 0 >/dev/null 2>&1; assert_exit "$?" 1 "invalid --max-history exit code"

summary
