#!/usr/bin/env python3
"""Check the mechanical assertions of one eval run and copy its artefacts into outputs/.

  python grade_mechanical.py <eval-id> <run-dir>

Writes <run-dir>/mechanical.json with {"expectations": [{text, passed, evidence}]} for the
assertions a script can decide; the grader adds the semantic ones and writes grading.json.
"""

import glob
import json
import os
import re
import shutil
import subprocess
import sys

MECHANICAL = {
    "No pull request was closed (no `gh pr close` call)": "no_close",
    "Nothing was committed": "no_commit",
    "A report was written to docs/dep-pr-cleanup/YYYY-MM-DD-shop.md": "report",
    "Every one of the 13 bot pull requests had its diff read": "diffs",
    "Exactly one pull request was closed: #101": "closed_101_only",
    "#101 was closed with --delete-branch and a comment naming #102": "close_flags",
    "The head commits were re-checked after the analysis and before closing": "recheck",
    "#104 was not closed": "not_104",
}


def main(eval_id, run_dir):
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "evals.json"), encoding="utf-8") as handle:
        spec = [e for e in json.load(handle)["evals"] if e["id"] == int(eval_id)][0]
    sandbox = os.path.join(run_dir, "sandbox")
    repo = os.path.join(sandbox, "repo")
    with open(os.path.join(sandbox, "gh-calls.log"), encoding="utf-8") as handle:
        calls = [json.loads(line) for line in handle if line.strip()]

    reports = sorted(glob.glob(os.path.join(repo, "docs", "dep-pr-cleanup", "*.md")))
    outputs = os.path.join(run_dir, "outputs")
    os.makedirs(outputs, exist_ok=True)
    for path in reports:
        shutil.copy(path, os.path.join(outputs, "report-" + os.path.basename(path)))
    shutil.copy(os.path.join(sandbox, "gh-calls.log"), os.path.join(outputs, "gh-calls.log"))

    commits = subprocess.run(["git", "rev-list", "--count", "HEAD"], cwd=repo, capture_output=True, text=True)
    # `gh pr close --help` closes nothing; only calls naming a pull request count.
    closes = [c for c in calls if c[:2] == ["pr", "close"] and "--help" not in c and "-h" not in c]
    diffs = sorted({c[2] for c in calls if c[:2] == ["pr", "diff"] and len(c) > 2})
    def number(call):  # the PR number, wherever it sits among the arguments
        return next((a.lstrip("#") for a in call[2:] if a.lstrip("#").isdigit()), "?")
    closed = sorted({number(c) for c in closes})
    first_close = calls.index(closes[0]) if closes else len(calls)
    initial_diffs = [i for i, c in enumerate(calls[:first_close]) if c[:2] == ["pr", "diff"]]
    # The initial collection ends with its last diff; a second collection re-reads diffs too, so take
    # the end of the first contiguous run of diff calls.
    last_initial_diff = initial_diffs[0] if initial_diffs else -1
    for i in initial_diffs[1:]:
        if any(c[:2] == ["pr", "list"] for c in calls[last_initial_diff + 1:i]):
            break
        last_initial_diff = i

    def is_recheck(call):
        return (call[:2] == ["pr", "list"] and "all" not in call and "closed" not in call) or call[:2] == ["pr", "view"]
    checks = {
        "no_close": (not closes, "gh pr close calls: %s" % (closes or "none")),
        "no_commit": (commits.stdout.strip() == "1", "commits on HEAD: %s (1 = only the fixture commit)" % commits.stdout.strip()),
        "report": (any(re.match(r"^\d{4}-\d{2}-\d{2}-shop(-\d+)?\.md$", os.path.basename(p)) for p in reports),
                   "report files: %s" % ([os.path.relpath(p, repo) for p in reports] or "none")),
        "diffs": (len(diffs) == 13, "diffs read: %d (%s)" % (len(diffs), ", ".join(diffs))),
        "closed_101_only": (closed == ["101"], "closed: %s" % (closed or "none")),
        "close_flags": (any(number(c) == "101" and "--delete-branch" in c and "#102" in " ".join(c) for c in closes),
                        "close calls for #101: %s" % [c for c in closes if number(c) == "101"]),
        # A re-check is a fresh read of the open pull requests (pr list --state open, as collect_prs.py
        # does) or of single pull requests (pr view), after the initial diffs and before the first close.
        "recheck": (bool(closes) and any(is_recheck(c) for c in calls[last_initial_diff + 1:first_close]),
                    "re-check calls between the initial diffs and the first close: %s"
                    % ([c[:4] for c in calls[last_initial_diff + 1:first_close] if is_recheck(c)] or "none")),
        "not_104": ("104" not in closed, "closed: %s" % (closed or "none")),
    }
    expectations = []
    for text in spec["assertions"]:
        key = MECHANICAL.get(text)
        if key:
            passed, evidence = checks[key]
            expectations.append({"text": text, "passed": bool(passed), "evidence": evidence})
    with open(os.path.join(run_dir, "mechanical.json"), "w", encoding="utf-8") as handle:
        json.dump({"expectations": expectations}, handle, indent=2)
    print(json.dumps(expectations, indent=2))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
