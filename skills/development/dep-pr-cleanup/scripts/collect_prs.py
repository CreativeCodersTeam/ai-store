#!/usr/bin/env python3
"""Collect the open pull requests of dependency bots, with their diffs, into one JSON file.

Usage:
  collect_prs.py [--repo OWNER/NAME] [--bot LOGIN]... [--no-default-bots]
                 [--config PATH] [--limit N] [--output FILE]

Writes the full result (including every diff) to --output (default: a new file in the system
temp directory) and prints a short JSON summary with the output path on stdout.

Exit codes: 0 ok (also with zero bot pull requests) · 1 usage · 2 gh missing or not
authenticated · 3 repository or pull request list not readable · 4 malformed config file.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True  # no __pycache__ in the skill or plugin directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from deplib.ghcli import bot_key, gh_command, run_gh  # noqa: E402

DEFAULT_BOTS = ["dependabot[bot]", "renovate[bot]"]
CONFIG_KEYS = {"bots", "includeDefaultBots", "newerCountsAsReplacement", "acrossMajor"}
# `commits` is fetched per bot pull request: in the list query it exceeds GitHub's GraphQL node
# limit for larger --limit values.
PR_FIELDS = ("number,title,url,author,headRefName,headRefOid,baseRefName,isDraft,mergeable,"
             "createdAt,statusCheckRollup,body,isCrossRepository")
FAILING = {"FAILURE", "ERROR", "TIMED_OUT", "CANCELLED", "ACTION_REQUIRED", "STARTUP_FAILURE"}
IMMORTAL_MARKERS = ("This PR will be recreated if closed unmerged", "👻 **Immortal**", "👻 Immortal")


class Fail(Exception):
    def __init__(self, code: int, message: str):
        super().__init__(message)
        self.code = code


def emit(payload: dict) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=True, indent=2) + "\n")


def git_root() -> str:
    try:
        out = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True)
        if out.returncode == 0:
            return out.stdout.decode("utf-8", "replace").strip()
    except OSError:
        pass
    return os.getcwd()


def load_config(path: str, explicit: bool) -> dict:
    if not os.path.isfile(path):
        if explicit:
            raise Fail(4, "config file not found: %s" % path)
        return {}
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, ValueError) as error:
        raise Fail(4, "cannot read config file %s: %s" % (path, error))
    if not isinstance(data, dict):
        raise Fail(4, "config file %s must contain a JSON object" % path)
    unknown = sorted(set(data) - CONFIG_KEYS)
    if unknown:
        raise Fail(4, "unknown keys in %s: %s" % (path, ", ".join(unknown)))
    if "bots" in data and not (isinstance(data["bots"], list) and all(isinstance(b, str) for b in data["bots"])):
        raise Fail(4, "\"bots\" must be a list of strings")
    for key in ("includeDefaultBots", "newerCountsAsReplacement", "acrossMajor"):
        if key in data and not isinstance(data[key], bool):
            raise Fail(4, "\"%s\" must be true or false" % key)
    return data


def checks_state(rollup: list) -> str:
    if not rollup:
        return "none"
    pending = False
    for item in rollup:
        if item.get("__typename") == "StatusContext" or "state" in item and "status" not in item:
            state = (item.get("state") or "").upper()
            if state in FAILING:
                return "failure"
            if state in ("PENDING", "EXPECTED", ""):
                pending = True
        else:
            if (item.get("status") or "").upper() != "COMPLETED":
                pending = True
            elif (item.get("conclusion") or "").upper() in FAILING:
                return "failure"
    return "pending" if pending else "success"


def main(argv: list) -> int:
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--repo")
    parser.add_argument("--bot", action="append", default=[])
    parser.add_argument("--no-default-bots", action="store_true")
    parser.add_argument("--config")
    parser.add_argument("--limit", type=int, default=300)
    parser.add_argument("--output")
    try:
        args = parser.parse_args(argv)
    except SystemExit as exit_:
        return 0 if exit_.code == 0 else 1
    if args.limit < 1:
        sys.stderr.write("--limit must be positive\n")
        return 1

    try:
        if gh_command() is None:
            raise Fail(2, "gh (GitHub CLI) is not installed or not on PATH")
        code, _, err = run_gh(["auth", "status"])
        if code == 127:
            raise Fail(2, "gh (GitHub CLI) cannot be run: %s" % err.strip())
        if code != 0:
            raise Fail(2, "gh is not authenticated: %s" % err.strip())

        config_path = args.config or os.path.join(git_root(), ".github", "dep-pr-cleanup.json")
        config = load_config(config_path, explicit=bool(args.config))

        bots, sources = [], {}

        def add(login: str, source: str) -> None:
            key = bot_key(login)
            if key and key not in sources:
                bots.append(key)
                sources[key] = source

        include_defaults = not args.no_default_bots and config.get("includeDefaultBots", True)
        if include_defaults:
            for login in DEFAULT_BOTS:
                add(login, "default")
        for login in config.get("bots", []):
            add(login, "config")
        for login in args.bot:
            add(login, "argument")
        if not bots:
            raise Fail(1, "no bots to look for (default bots disabled and none given)")

        code, out, err = run_gh(["repo", "view"] + ([args.repo] if args.repo else []) +
                                ["--json", "nameWithOwner,defaultBranchRef"])
        if code != 0:
            raise Fail(3, "cannot resolve the repository: %s" % err.strip())
        repo_info = json.loads(out)
        repo = repo_info["nameWithOwner"]
        default_branch = (repo_info.get("defaultBranchRef") or {}).get("name")

        code, out, err = run_gh(["pr", "list", "--repo", repo, "--state", "open", "--limit", str(args.limit),
                                 "--json", PR_FIELDS])
        if code != 0:
            raise Fail(3, "cannot list pull requests: %s" % err.strip())
        listed = json.loads(out)
    except Fail as failure:
        sys.stderr.write(str(failure) + "\n")
        return failure.code
    except (ValueError, KeyError) as error:
        sys.stderr.write("unexpected gh output: %s\n" % error)
        return 3

    prs, other_authors = [], 0
    for item in listed:
        author = item.get("author") or {}
        key = bot_key(author.get("login"))
        if key not in sources:
            other_authors += 1
            continue
        code, out, err = run_gh(["pr", "view", str(item["number"]), "--repo", repo, "--json", "commits"])
        commits = None
        if code == 0:
            try:
                commits = json.loads(out).get("commits") or []
            except ValueError:
                commits = None
        if commits is None:
            non_bot = ["unknown (commits not readable)"]
        else:
            non_bot = sorted({
                (a.get("login") or a.get("email") or a.get("name") or "unknown")
                for commit in commits
                for a in commit.get("authors") or []
                if bot_key(a.get("login")) != key
            })
        body = item.get("body") or ""
        code, diff, err = run_gh(["pr", "diff", str(item["number"]), "--repo", repo, "--color", "never"])
        prs.append({
            "number": item["number"],
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "bot": key,
            "author_login": author.get("login"),
            "base": item.get("baseRefName"),
            "head_ref": item.get("headRefName"),
            "head_sha": item.get("headRefOid"),
            "is_draft": bool(item.get("isDraft")),
            "mergeable": item.get("mergeable"),
            "checks": checks_state(item.get("statusCheckRollup") or []),
            "created_at": item.get("createdAt"),
            "cross_repository": bool(item.get("isCrossRepository")),
            "immortal": any(marker in body for marker in IMMORTAL_MARKERS),
            "non_bot_commit_authors": non_bot,
            "diff": diff if code == 0 else None,
            "diff_error": None if code == 0 else (err.strip() or "gh pr diff failed"),
        })

    result = {
        "repo": repo,
        "default_branch": default_branch,
        "collected_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "bots": [{"login": b, "source": sources[b]} for b in bots],
        "config": {"path": config_path if config else None, "values": config},
        "limit": args.limit,
        "truncated": len(listed) >= args.limit,
        "other_open_prs": other_authors,
        "prs": sorted(prs, key=lambda pr: pr["number"]),
    }

    output = args.output or os.path.join(
        tempfile.gettempdir(), "dep-pr-cleanup-%s-%s.json" % (
            repo.replace("/", "__"), datetime.datetime.now().strftime("%Y%m%d%H%M%S")))
    os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True)
    with open(output, "w", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)

    emit({
        "output": os.path.abspath(output),
        "repo": repo,
        "default_branch": default_branch,
        "bots": result["bots"],
        "config": result["config"],
        "bot_prs": len(prs),
        "diff_errors": [pr["number"] for pr in prs if pr["diff_error"]],
        "other_open_prs": other_authors,
        "truncated": result["truncated"],
    })
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
