#!/usr/bin/env python3
"""Stand-in for the GitHub CLI used by the dep-pr-cleanup tests.

Selected through DEP_PR_CLEANUP_GH=<this file>. Answers from the scenario directory in
MOCK_GH_DATA:

  repo.json            gh repo view --json ...
  prs.json             gh pr list --json ...      (the --limit argument is honoured)
  diffs/<n>.diff       gh pr diff <n>             (missing file -> exit 1, "diff too large")
  commits/<n>.json     gh pr view <n> --json commits   (missing file -> {"commits": []})
  prs.json             gh pr view <n> [--json ...]     (the pull request's object)
  -                    gh pr close <n> ...             (logged only, always succeeds)

MOCK_GH_MODE: "unauth" fails `auth status`, "no-repo" fails `repo view`, "list-fails" fails
`pr list`. Every call is appended to MOCK_GH_LOG (one JSON array per line) when set.
"""

import json
import os
import sys


def main(argv):
    data = os.environ.get("MOCK_GH_DATA", "")
    mode = os.environ.get("MOCK_GH_MODE", "")
    log = os.environ.get("MOCK_GH_LOG")
    if log:
        with open(log, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(argv) + "\n")

    def read(name):
        with open(os.path.join(data, name), encoding="utf-8") as handle:
            return handle.read()

    if argv[:2] == ["auth", "status"]:
        if mode == "unauth":
            sys.stderr.write("You are not logged into any GitHub hosts.\n")
            return 1
        return 0
    if argv[:2] == ["repo", "view"]:
        if mode == "no-repo":
            sys.stderr.write("GraphQL: Could not resolve to a Repository\n")
            return 1
        sys.stdout.write(read("repo.json"))
        return 0
    if argv[:2] == ["pr", "list"]:
        if mode == "list-fails":
            sys.stderr.write("HTTP 502\n")
            return 1
        prs = json.loads(read("prs.json"))
        if "--limit" in argv:
            prs = prs[: int(argv[argv.index("--limit") + 1])]
        sys.stdout.write(json.dumps(prs))
        return 0
    if argv[:2] == ["pr", "diff"]:
        path = os.path.join(data, "diffs", argv[2] + ".diff")
        if not os.path.isfile(path):
            sys.stderr.write("HTTP 406: Sorry, the diff exceeded the maximum number of lines (20000)\n")
            return 1
        sys.stdout.write(read(os.path.join("diffs", argv[2] + ".diff")))
        return 0
    if argv[:2] == ["pr", "view"] and "commits" in argv:
        path = os.path.join(data, "commits", argv[2] + ".json")
        sys.stdout.write(read(os.path.join("commits", argv[2] + ".json")) if os.path.isfile(path) else '{"commits": []}')
        return 0
    if argv[:2] == ["pr", "view"] and len(argv) > 2:
        found = [p for p in json.loads(read("prs.json")) if str(p["number"]) == argv[2].lstrip("#")]
        if not found:
            sys.stderr.write("no pull requests found\n")
            return 1
        sys.stdout.write(json.dumps(found[0]) if "--json" in argv else "%s #%s\n\n%s\n" % (
            found[0]["title"], found[0]["number"], found[0].get("body", "")))
        return 0
    if argv[:2] == ["pr", "close"] and len(argv) > 2:
        # Writes nothing; the call is in MOCK_GH_LOG, which is what the evals inspect.
        sys.stdout.write("✓ Closed pull request #%s\n" % argv[2].lstrip("#"))
        return 0
    sys.stderr.write("mock gh: unsupported call %r\n" % (argv,))
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
