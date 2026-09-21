#!/usr/bin/env bash
# match-version.sh — locate the local CLAUDE.md in the upstream template's history.
#
# Answers the three questions the skill branches on: is the local file the current
# template, is it an older template verbatim, or has it drifted? For the drifted
# case it also names the historical version it resembles most, which becomes the
# merge base — without one, local edits and upstream edits cannot be told apart.
#
# Comparison is whitespace-normalised (CRLF stripped, trailing spaces removed,
# trailing blank lines dropped) so a line-ending difference is not reported as
# a content change.
#
# Output JSON: {mode, local_file, local_exists, template_path, repo_url, branch,
#               head_sha, status, behind_by, matched, best_base, history[], work_dir, files}
#   history  lists every commit that touched the template, newest first, the
#            matched or base commit INCLUDED (it sits at index behind_by).
#   behind_by counts upstream COMMITS newer than the matched or base version —
#            not the number of rules that changed, and one less than the history
#            length when the full history was walked.
#   .url on a commit is null unless the remote is a GitHub or GitLab URL whose
#            web layout is known; a mirror or bare path yields no link, and the
#            top-level commit_urls says so once, for callers whose history is empty.
#   matched  is the commit the local file equals: the newest template-changing
#            commit for `identical`, the older one for `known-older-version`.
# Materialised template versions are written to <cache-dir>-work/<mode>/ — a
# sibling of the cache, not a directory inside it.
#   status ∈ identical | known-older-version | diverged
#          | no-local-file | empty-template | no-template
#
# Exit codes: 0 ok (status carries the outcome), 1 usage,
#             2 cache directory unusable, 3 repo mode outside a git repository.

set -u

CACHE_DIR="" MODE="" START_DIR="$PWD" TEMPLATE_PATH="" BRANCH="" MAX_HISTORY=50

usage() {
  cat <<EOF
match-version.sh — match a local CLAUDE.md against the upstream template history

Usage:
  match-version.sh --cache-dir <path> --mode repo|user
                   [--start-dir <path>] [--template-path <path>]
                   [--branch <name>] [--max-history <n>]
  match-version.sh --help

Targets:
  repo  <git-toplevel-of-start-dir>/CLAUDE.md  vs claude/claude-md-template.repo.md
  user  \$HOME/.claude/CLAUDE.md                vs claude/claude-md-template.user.md

The repo target is always the repository root, whatever directory --start-dir names.

Materialised template versions land in <cache-dir>-work/<mode>/, beside the
cache rather than inside it, so the clone stays a clean checkout.

Exit codes:
  0  success — read .status for the outcome
  1  usage error
  2  cache directory is not a usable clone
  3  --mode repo but --start-dir is not inside a git repository
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --cache-dir)     CACHE_DIR=${2:-};     shift 2 ;;
    --mode)          MODE=${2:-};          shift 2 ;;
    --start-dir)     START_DIR=${2:-};     shift 2 ;;
    --template-path) TEMPLATE_PATH=${2:-}; shift 2 ;;
    --branch)        BRANCH=${2:-};        shift 2 ;;
    --max-history)   MAX_HISTORY=${2:-};   shift 2 ;;
    --help|-h)       usage; exit 0 ;;
    *) echo "unknown arg: $1" >&2; usage >&2; exit 1 ;;
  esac
done

[[ -n "$CACHE_DIR" && -n "$MODE" ]] || { usage >&2; exit 1; }
case "$MODE" in repo|user) ;; *) echo "invalid --mode: $MODE" >&2; exit 1 ;; esac
[[ "$MAX_HISTORY" =~ ^[0-9]+$ && "$MAX_HISTORY" -gt 0 ]] || { echo "invalid --max-history: $MAX_HISTORY" >&2; exit 1; }
[[ -d "$CACHE_DIR/.git" ]] || { echo "not a git clone: $CACHE_DIR" >&2; exit 2; }

if [[ -z "$TEMPLATE_PATH" ]]; then
  case "$MODE" in
    repo) TEMPLATE_PATH="claude/claude-md-template.repo.md" ;;
    user) TEMPLATE_PATH="claude/claude-md-template.user.md" ;;
  esac
fi

if [[ -z "$BRANCH" ]]; then
  BRANCH=$(git -C "$CACHE_DIR" symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null | sed 's|^origin/||')
  [[ -n "$BRANCH" ]] || BRANCH="main"
fi
REF="origin/$BRANCH"
git -C "$CACHE_DIR" rev-parse --verify --quiet "$REF" >/dev/null || { echo "ref not found: $REF" >&2; exit 2; }
HEAD_SHA=$(git -C "$CACHE_DIR" rev-parse "$REF")
REPO_URL=$(git -C "$CACHE_DIR" remote get-url origin 2>/dev/null || echo "")

json_str() { printf '%s' "${1:-}" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()), end="")'; }

# Commit URLs are only emitted for remotes whose web layout is actually known.
# A mirror, a bare path or an unrecognised host would otherwise yield a link
# that looks clickable and goes nowhere, which is worse than no link at all —
# the reports are meant to let a user verify a claim.
web_url_for() {
  local sha=$1 base
  base=$(printf '%s' "$REPO_URL" | sed -e 's|\.git$||')
  case "$REPO_URL" in
    https://github.com/*|http://github.com/*)
      printf '%s/commit/%s' "$base" "$sha" ;;
    git@github.com:*)
      printf 'https://github.com/%s/commit/%s' "${base#git@github.com:}" "$sha" ;;
    https://gitlab.com/*|http://gitlab.com/*)
      printf '%s/-/commit/%s' "$base" "$sha" ;;
    git@gitlab.com:*)
      printf 'https://gitlab.com/%s/-/commit/%s' "${base#git@gitlab.com:}" "$sha" ;;
    *) return 1 ;;
  esac
}

# JSON string, or the literal null when no URL can be built.
url_json() {
  local u
  if u=$(web_url_for "$1"); then json_str "$u"; else printf 'null'; fi
}

# --- resolve the local file -------------------------------------------------
case "$MODE" in
  repo)
    [[ -d "$START_DIR" ]] || { echo "not a directory: $START_DIR" >&2; exit 1; }
    ROOT=$(git -C "$START_DIR" rev-parse --show-toplevel 2>/dev/null || true)
    [[ -n "$ROOT" ]] || { echo "not inside a git repository: $START_DIR" >&2; exit 3; }
    LOCAL_FILE="$ROOT/CLAUDE.md"
    ;;
  user)
    LOCAL_FILE="$HOME/.claude/CLAUDE.md"
    ;;
esac

WORK_DIR="${CACHE_DIR}-work/$MODE"
mkdir -p "$WORK_DIR" || { echo "cannot create work dir: $WORK_DIR" >&2; exit 2; }
WORK_DIR=$(cd "$WORK_DIR" && pwd)
rm -f "$WORK_DIR"/template-*.md

# --- helpers ----------------------------------------------------------------

# Strip CR, trailing whitespace and trailing blank lines so formatting noise
# does not masquerade as a content difference.
normalize() {
  sed -e 's/\r$//' -e 's/[[:space:]]*$//' | awk '
    { lines[NR] = $0 }
    END { last = NR
          while (last > 0 && lines[last] == "") last--
          for (i = 1; i <= last; i++) print lines[i] }'
}

# Similarity in [0,1]: 1 minus the share of lines the two files do not share.
similarity() {
  local a=$1 b=$2 changed la lb
  changed=$(diff "$a" "$b" | grep -c '^[<>]' || true)
  la=$(wc -l < "$a" | tr -d ' ')
  lb=$(wc -l < "$b" | tr -d ' ')
  awk -v c="$changed" -v la="$la" -v lb="$lb" \
    'BEGIN { t = la + lb; if (t == 0) { print "1.0000" } else { s = 1 - c / t; if (s < 0) s = 0; printf "%.4f\n", s } }'
}

emit() {
  local status=$1 behind=$2 matched=$3 base=$4 history=$5
  local urls=false
  web_url_for 0000000 >/dev/null 2>&1 && urls=true
  printf '{"mode":"%s","local_file":%s,"local_exists":%s,"template_path":%s,"repo_url":%s,"commit_urls":%s,"branch":"%s","head_sha":"%s","status":"%s","behind_by":%s,"matched":%s,"best_base":%s,"history":%s,"work_dir":%s,"files":{"current":%s,"matched":%s,"base":%s,"local":%s}}\n' \
    "$MODE" "$(json_str "$LOCAL_FILE")" "$LOCAL_EXISTS" "$(json_str "$TEMPLATE_PATH")" \
    "$(json_str "$REPO_URL")" "$urls" "$BRANCH" "$HEAD_SHA" "$status" "$behind" \
    "$matched" "$base" "$history" "$(json_str "$WORK_DIR")" \
    "$(json_str "$CURRENT_FILE")" "$(json_str "$MATCHED_FILE")" "$(json_str "$BASE_FILE")" "$(json_str "$LOCAL_FILE")"
}

LOCAL_EXISTS=false
[[ -f "$LOCAL_FILE" ]] && LOCAL_EXISTS=true
CURRENT_FILE="" MATCHED_FILE="" BASE_FILE=""

# --- template at HEAD -------------------------------------------------------
CURRENT_FILE="$WORK_DIR/template-current.md"
if ! git -C "$CACHE_DIR" show "$REF:$TEMPLATE_PATH" > "$CURRENT_FILE" 2>/dev/null; then
  rm -f "$CURRENT_FILE"; CURRENT_FILE=""
  emit "no-template" 0 null null "[]"
  exit 0
fi

# The branch tip is frequently a commit that never touched the template, so
# "your file matches <tip>" would name the wrong thing. Resolve the newest
# commit that actually changed the template and report that instead.
tpl_line=$(git -C "$CACHE_DIR" log -1 --follow --format="%H%x1f%cI%x1f%s" "$REF" -- "$TEMPLATE_PATH" 2>/dev/null || true)
TPL_SHA="" TPL_DATE="" TPL_SUBJECT=""
if [[ -n "$tpl_line" ]]; then
  IFS=$'\x1f' read -r TPL_SHA TPL_DATE TPL_SUBJECT <<<"$tpl_line"
fi

current_commit_json() {
  [[ -n "$TPL_SHA" ]] || { printf 'null'; return; }
  printf '{"sha":"%s","short":"%s","date":"%s","subject":%s,"path":%s,"url":%s,"similarity":1.0000}' \
    "$TPL_SHA" "${TPL_SHA:0:7}" "$TPL_DATE" "$(json_str "$TPL_SUBJECT")" \
    "$(json_str "$TEMPLATE_PATH")" "$(url_json "$TPL_SHA")"
}

CURRENT_NORM="$WORK_DIR/.current.norm"
normalize < "$CURRENT_FILE" > "$CURRENT_NORM"
if [[ ! -s "$CURRENT_NORM" ]]; then
  emit "empty-template" 0 null null "[]"
  exit 0
fi

if [[ "$LOCAL_EXISTS" == false ]]; then
  emit "no-local-file" 0 null null "[]"
  exit 0
fi

LOCAL_NORM="$WORK_DIR/.local.norm"
normalize < "$LOCAL_FILE" > "$LOCAL_NORM"

if cmp -s "$LOCAL_NORM" "$CURRENT_NORM"; then
  emit "identical" 0 "$(current_commit_json)" null "[]"
  exit 0
fi

# --- walk the template history ---------------------------------------------
# --follow keeps the trail across renames; --name-only yields the path the file
# carried at each commit, which is what `git show` needs.
shas=() dates=() subjects=() paths=()
cur_sha="" cur_date="" cur_subject=""
while IFS= read -r line; do
  case "$line" in
    C$'\x1f'*)
      IFS=$'\x1f' read -r _ cur_sha cur_date cur_subject <<<"$line"
      ;;
    "")
      ;;
    *)
      if [[ -n "$cur_sha" ]]; then
        shas+=("$cur_sha"); dates+=("$cur_date"); subjects+=("$cur_subject"); paths+=("$line")
        cur_sha=""
      fi
      ;;
  esac
done < <(git -C "$CACHE_DIR" log --follow --max-count="$MAX_HISTORY" \
           --format="C%x1f%H%x1f%cI%x1f%s" --name-only "$REF" -- "$TEMPLATE_PATH" 2>/dev/null)

history_json="["
matched_idx=-1
best_idx=-1
best_sim="0.0000"
first=1

i=0
while [[ $i -lt ${#shas[@]} ]]; do
  sha=${shas[$i]}; path=${paths[$i]}
  ver="$WORK_DIR/.v$i.md"
  if git -C "$CACHE_DIR" show "$sha:$path" > "$ver" 2>/dev/null; then
    normalize < "$ver" > "$ver.norm"
    sim=$(similarity "$LOCAL_NORM" "$ver.norm")
    if [[ $matched_idx -lt 0 ]] && cmp -s "$LOCAL_NORM" "$ver.norm"; then
      matched_idx=$i
    fi
    if awk -v a="$sim" -v b="$best_sim" 'BEGIN { exit !(a > b) }'; then
      best_sim=$sim; best_idx=$i
    fi
    [[ $first -eq 0 ]] && history_json+=","
    first=0
    history_json+=$(printf '{"sha":"%s","short":"%s","date":"%s","subject":%s,"path":%s,"url":%s,"similarity":%s}' \
      "$sha" "${sha:0:7}" "${dates[$i]}" "$(json_str "${subjects[$i]}")" "$(json_str "$path")" \
      "$(url_json "$sha")" "$sim")
  fi
  i=$((i + 1))
done
history_json+="]"

commit_json() {
  local idx=$1 sim=$2
  printf '{"sha":"%s","short":"%s","date":"%s","subject":%s,"path":%s,"url":%s,"similarity":%s}' \
    "${shas[$idx]}" "${shas[$idx]:0:7}" "${dates[$idx]}" "$(json_str "${subjects[$idx]}")" \
    "$(json_str "${paths[$idx]}")" "$(url_json "${shas[$idx]}")" "$sim"
}

if [[ $matched_idx -ge 0 ]]; then
  # The local file is an older template verbatim — nothing local to preserve.
  MATCHED_FILE="$WORK_DIR/template-matched.md"
  cp "$WORK_DIR/.v$matched_idx.md" "$MATCHED_FILE"
  emit "known-older-version" "$matched_idx" "$(commit_json "$matched_idx" "1.0000")" null "$history_json"
  exit 0
fi

base_json=null
behind=0
if [[ $best_idx -ge 0 ]]; then
  behind=$best_idx
  BASE_FILE="$WORK_DIR/template-base.md"
  cp "$WORK_DIR/.v$best_idx.md" "$BASE_FILE"
  base_json=$(commit_json "$best_idx" "$best_sim")
fi
emit "diverged" "$behind" null "$base_json" "$history_json"
