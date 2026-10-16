"""Shared helpers for the dep-pr-cleanup tests: paths, diff builders, scenario writer."""

from __future__ import annotations

import json
import os
import subprocess
import sys

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(TESTS_DIR, "..", "..", "..", "..", ".."))
SKILL_DIR = os.path.join(REPO_ROOT, "skills", "development", "dep-pr-cleanup")
SCRIPTS_DIR = os.path.join(SKILL_DIR, "scripts")
MOCK_GH = os.path.join(TESTS_DIR, "mock_gh", "gh.py")
FIXTURES = os.path.join(TESTS_DIR, "fixtures")

if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)


# -- diff builders ----------------------------------------------------------------------------

def hunk(context=(), removed=(), added=(), after=()):
    lines = [" " + c for c in context] + ["-" + r for r in removed] + ["+" + a for a in added] + \
            [" " + c for c in after]
    old = len(context) + len(removed) + len(after)
    new = len(context) + len(added) + len(after)
    return "@@ -10,%d +10,%d @@\n%s\n" % (old, new, "\n".join(lines))


def file_diff(path, *hunks):
    return ("diff --git a/{p} b/{p}\nindex 1111111..2222222 100644\n--- a/{p}\n+++ b/{p}\n".format(p=path)
            + "".join(hunks))


def npm(path, *changes):
    """changes: (name, old_spec, new_spec)"""
    return file_diff(path, *[
        hunk(['  "dependencies": {'], ['    "%s": "%s",' % (n, o)], ['    "%s": "%s",' % (n, v)], ['  },'])
        for n, o, v in changes])


def lockfile(path="package-lock.json"):
    return file_diff(path, hunk(['    "node_modules/x": {'], ['      "version": "1.0.0",'],
                                ['      "version": "1.0.1",']))


# -- scenarios --------------------------------------------------------------------------------

def pr(number, bot="renovate", title=None, base="main", draft=False, mergeable="MERGEABLE",
       checks="SUCCESS", body="", head_sha=None):
    rollup = [] if checks is None else [{"__typename": "CheckRun", "name": "ci", "status":
                                         "IN_PROGRESS" if checks == "PENDING" else "COMPLETED",
                                         "conclusion": "" if checks == "PENDING" else checks}]
    return {
        "number": number,
        "title": title or "Update dependencies (#%d)" % number,
        "url": "https://github.com/acme/shop/pull/%d" % number,
        "author": {"is_bot": True, "login": "app/" + bot},
        "headRefName": "%s/branch-%d" % (bot, number),
        "headRefOid": head_sha or ("%040x" % number),
        "baseRefName": base,
        "isDraft": draft,
        "mergeable": mergeable,
        "createdAt": "2026-10-%02dT08:00:00Z" % (number % 28 + 1),
        "statusCheckRollup": rollup,
        "body": body,
        "isCrossRepository": False,
    }


def write_scenario(directory, entries, repo="acme/shop", default_branch="main"):
    """entries: list of (pr_dict, diff_text_or_None, commit_logins_or_None)."""
    os.makedirs(os.path.join(directory, "diffs"), exist_ok=True)
    os.makedirs(os.path.join(directory, "commits"), exist_ok=True)
    with open(os.path.join(directory, "repo.json"), "w", encoding="utf-8") as handle:
        json.dump({"nameWithOwner": repo, "defaultBranchRef": {"name": default_branch}}, handle)
    with open(os.path.join(directory, "prs.json"), "w", encoding="utf-8") as handle:
        json.dump([entry[0] for entry in entries], handle, indent=1)
    for item, diff, commit_logins in entries:
        if diff is not None:
            with open(os.path.join(directory, "diffs", "%d.diff" % item["number"]), "w",
                      encoding="utf-8", newline="\n") as handle:
                handle.write(diff)
        if commit_logins is not None:
            with open(os.path.join(directory, "commits", "%d.json" % item["number"]), "w",
                      encoding="utf-8") as handle:
                json.dump({"commits": [{"authors": [{"login": login}]} for login in commit_logins]}, handle)


def run_script(name, args, scenario=None, mode="", env_extra=None, cwd=None):
    env = dict(os.environ)
    env["DEP_PR_CLEANUP_GH"] = MOCK_GH
    env["MOCK_GH_DATA"] = scenario or ""
    env["MOCK_GH_MODE"] = mode
    env.pop("MOCK_GH_LOG", None)
    env.update(env_extra or {})
    completed = subprocess.run([sys.executable, os.path.join(SCRIPTS_DIR, name)] + list(args),
                               capture_output=True, env=env, cwd=cwd)
    return (completed.returncode, completed.stdout.decode("utf-8", "replace"),
            completed.stderr.decode("utf-8", "replace"))
