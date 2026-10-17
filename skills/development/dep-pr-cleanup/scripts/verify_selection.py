#!/usr/bin/env python3
"""Check, right before closing, that the selected pull requests are still safe to close.

Usage:
  verify_selection.py --before ANALYSIS.json --after ANALYSIS.json --select N[,N...]

Both files are analyze_prs.py results: --before is the analysis the user decided on, --after a
fresh collect + analyze with the same options and pair modes. A selected pull request is safe
when it is still obsolete, its head commit is unchanged, and every pull request that covered
it before is still open with an unchanged head commit.

Prints {"safe": [...], "changed": [{"number", "reasons"}]} on stdout.
Exit codes: 0 every selected pull request is safe · 1 usage · 3 malformed input ·
4 at least one selected pull request changed (close only the "safe" ones, or re-run).
"""

from __future__ import annotations

import argparse
import json
import sys


def load(path: str) -> dict:
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data.get("prs"), list) or not isinstance(data.get("proposals"), list):
        raise ValueError("not an analyze_prs.py result")
    return data


def main(argv: list) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--before", required=True)
    parser.add_argument("--after", required=True)
    parser.add_argument("--select", required=True)
    try:
        args = parser.parse_args(argv)
        selected = [int(part.strip().lstrip("#")) for part in args.select.split(",") if part.strip()]
    except SystemExit as exit_:
        return 0 if exit_.code == 0 else 1
    except ValueError:
        sys.stderr.write("--select expects pull request numbers, e.g. 101,104\n")
        return 1
    if not selected:
        sys.stderr.write("--select is empty\n")
        return 1

    try:
        before, after = load(args.before), load(args.after)
    except (OSError, ValueError) as error:
        sys.stderr.write("cannot read analysis: %s\n" % error)
        return 3

    before_prs = {p["number"]: p for p in before["prs"]}
    after_prs = {p["number"]: p for p in after["prs"]}
    before_props = {p["number"]: p for p in before["proposals"]}
    after_props = {p["number"]: p for p in after["proposals"]}

    unknown = [n for n in selected if n not in before_props]
    if unknown:
        sys.stderr.write("not proposed in --before: %s\n" % unknown)
        return 1

    safe, changed = [], []
    for number in selected:
        reasons = []
        now = after_prs.get(number)
        if now is None:
            reasons.append("#%d is no longer open" % number)
        else:
            if now["head_sha"] != before_prs[number]["head_sha"]:
                reasons.append("#%d has new commits" % number)
            if number not in after_props:
                reasons.append("#%d is no longer proposed as obsolete (status: %s)" % (number, now["status"]))
        for coverer in before_props[number]["covered_by"]:
            other = after_prs.get(coverer)
            if other is None:
                reasons.append("covering #%d is no longer open" % coverer)
            elif other["head_sha"] != before_prs[coverer]["head_sha"]:
                reasons.append("covering #%d has new commits" % coverer)
        if reasons:
            changed.append({"number": number, "reasons": reasons})
        else:
            safe.append(number)

    sys.stdout.write(json.dumps({"safe": safe, "changed": changed}, ensure_ascii=True, indent=2) + "\n")
    return 4 if changed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
