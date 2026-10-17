#!/usr/bin/env python3
"""Find overlapping and obsolete bot pull requests in the output of collect_prs.py.

Usage:
  analyze_prs.py --input FILE [--newer yes|no] [--across-major yes|no]
                 [--pair-mode COVERER:COVERED=exact|newer|any]... [--output FILE]

Prints the analysis as JSON on stdout (diffs are not repeated) and, with --output, also writes it
to that file. Reads no network; run it again with other options or pair modes at no cost.

Exit codes: 0 ok · 1 usage · 3 malformed or unreadable input.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

sys.dont_write_bytecode = True  # no __pycache__ in the skill or plugin directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from deplib import versions  # noqa: E402
from deplib.coverage import MODES, Analysis, overlaps, relation  # noqa: E402
from deplib.diffparse import parse_diff  # noqa: E402
from deplib.manifests import analyse_file  # noqa: E402

_PAIR = re.compile(r"^#?(\d+):#?(\d+)=(exact|newer|any)$")
_RENOVATE_MAJOR_TITLE = re.compile(r"\bto v?\d+(?:\s*\(major\))?\s*$", re.IGNORECASE)


def yes_no(value: str) -> bool:
    lowered = value.lower()
    if lowered in ("yes", "true", "1", "ja"):
        return True
    if lowered in ("no", "false", "0", "nein"):
        return False
    raise argparse.ArgumentTypeError("expected yes or no")


def update_json(update) -> dict:
    to_version = versions.parse(update.to_value, update.ecosystem, update.to_hint)
    from_version = versions.parse(update.from_value, update.ecosystem, update.from_hint)
    rel = versions.compare(to_version, from_version)
    return {
        "ecosystem": update.ecosystem,
        "name": update.name,
        "path": update.path,
        "from": update.from_value + (" (%s)" % update.from_hint if update.from_hint else ""),
        "to": update.to_value + (" (%s)" % update.to_hint if update.to_hint else ""),
        "major_change": True if rel == versions.NEWER_MAJOR else (None if rel == versions.INCOMPARABLE else False),
    }


def short_target(update) -> str:
    return update.to_value + (" (%s)" % update.to_hint if update.to_hint else "")


def main(argv: list) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--newer", type=yes_no, default=True)
    parser.add_argument("--across-major", type=yes_no, default=False)
    parser.add_argument("--pair-mode", action="append", default=[])
    parser.add_argument("--output")
    try:
        args = parser.parse_args(argv)
    except SystemExit as exit_:
        return 0 if exit_.code == 0 else 1

    overrides = {}
    for value in args.pair_mode:
        match = _PAIR.match(value.strip())
        if not match:
            sys.stderr.write("invalid --pair-mode %r (expected COVERER:COVERED=exact|newer|any)\n" % value)
            return 1
        overrides[(int(match.group(1)), int(match.group(2)))] = match.group(3)

    try:
        with open(args.input, encoding="utf-8") as handle:
            collected = json.load(handle)
        raw_prs = collected["prs"]
        if not isinstance(raw_prs, list):
            raise ValueError("prs is not a list")
    except (OSError, ValueError, KeyError, TypeError) as error:
        sys.stderr.write("cannot read %s: %s\n" % (args.input, error))
        return 3

    prs = []
    try:
        for raw in raw_prs:
            reasons, lockfiles, updates = [], [], []
            if raw.get("diff_error"):
                reasons.append("diff not available: %s" % raw["diff_error"])
            else:
                for diff_file in parse_diff(raw.get("diff") or ""):
                    result = analyse_file(diff_file)
                    if result.kind == "lockfile":
                        lockfiles.append(result.path)
                    reasons.extend(result.problems)
                    updates.extend(result.updates)
                if not updates and not reasons:
                    reasons.append("no dependency update found in the manifests (only lockfiles or no changes)")
            prs.append({
                "number": int(raw["number"]),
                "raw": raw,
                "bot": raw["bot"],
                "base": raw["base"],
                "evaluable": not reasons,
                "reasons": reasons,
                "lockfiles": lockfiles,
                "updates": updates,
            })
    except (KeyError, TypeError, ValueError) as error:
        sys.stderr.write("malformed pull request entry: %s\n" % error)
        return 3

    unknown = sorted({n for pair in overrides for n in pair} - {pr["number"] for pr in prs})
    if unknown:
        sys.stderr.write("--pair-mode names pull requests that were not collected: %s\n" % unknown)
        return 1

    analysis = Analysis(prs, newer=args.newer, across_major=args.across_major, overrides=overrides)
    outcome = analysis.run()
    obsolete = outcome["obsolete"]
    by_number = {pr["number"]: pr for pr in prs}

    def flags(raw: dict) -> dict:
        return {
            "is_draft": raw.get("is_draft", False),
            "mergeable": raw.get("mergeable"),
            "checks": raw.get("checks"),
            "immortal": raw.get("immortal", False),
            "non_bot_commit_authors": raw.get("non_bot_commit_authors", []),
            "cross_repository": raw.get("cross_repository", False),
            "renovate_major_title": raw.get("bot") == "renovate" and bool(_RENOVATE_MAJOR_TITLE.search(raw.get("title", ""))),
        }

    def coverer_warnings(number: int) -> list:
        raw = by_number[number]["raw"]
        notes = []
        if raw.get("is_draft"):
            notes.append("#%d is a draft" % number)
        if raw.get("mergeable") == "CONFLICTING":
            notes.append("#%d has merge conflicts" % number)
        if raw.get("checks") == "failure":
            notes.append("#%d has failing checks" % number)
        elif raw.get("checks") == "pending":
            notes.append("#%d has pending checks" % number)
        return notes

    proposals = []
    for number in sorted(obsolete):
        raw = by_number[number]["raw"]
        details, chosen = [], set()
        for item in analysis.explain(number, obsolete[number]):
            update, pick = item["update"], item["chosen"]
            other_update = next(u for u in by_number[pick[0]]["updates"] if u.identity == update.identity
                                and relation(u, update) == pick[1])
            chosen.add(pick[0])
            details.append({
                "ecosystem": update.ecosystem, "name": update.name, "path": update.path,
                "to": short_target(update), "by": pick[0], "by_to": short_target(other_update),
                "relation": pick[1],
                "also_covered_by": sorted(c for c, _ in item["coverers"] if c != pick[0]),
            })
        warnings = []
        if raw.get("immortal"):
            warnings.append("Renovate marks #%d as immortal: it will be recreated after closing" % number)
        if flags(raw)["renovate_major_title"]:
            warnings.append("closing #%d makes Renovate ignore every future update of this major version" % number)
        if raw.get("non_bot_commit_authors"):
            warnings.append("#%d contains commits by %s; closing discards that work"
                            % (number, ", ".join(raw["non_bot_commit_authors"])))
        for coverer in sorted(chosen):
            warnings.extend(coverer_warnings(coverer))
        proposals.append({"number": number, "title": raw.get("title", ""), "url": raw.get("url", ""),
                          "covered_by": sorted(chosen), "details": details, "warnings": warnings})

    overlap_json, toggles = [], []
    for item in overlaps(prs, analysis):
        a, b = item["a"], item["b"]
        shared = []
        newer_counts = {(a, b): [0, 0], (b, a): [0, 0]}
        for ua, ub, rel in item["shared"]:
            if rel == versions.NEWER:
                label, newer_counts[(a, b)][0] = "a-newer", newer_counts[(a, b)][0] + 1
            elif rel == versions.NEWER_MAJOR:
                label, newer_counts[(a, b)][1] = "a-newer-major", newer_counts[(a, b)][1] + 1
            elif rel == versions.OLDER:
                back = relation(ub, ua)
                if back == versions.NEWER_MAJOR:
                    label, newer_counts[(b, a)][1] = "b-newer-major", newer_counts[(b, a)][1] + 1
                else:
                    label, newer_counts[(b, a)][0] = "b-newer", newer_counts[(b, a)][0] + 1
            else:
                label = rel
            shared.append({"ecosystem": ua.ecosystem, "name": ua.name, "path": ua.path,
                           "a_to": short_target(ua), "b_to": short_target(ub), "relation": label})
        counted = item["not_counted_reason"] is None
        overlap_json.append({
            "a": a, "b": b, "counted": counted, "not_counted_reason": item["not_counted_reason"],
            "mode_a_covers_b": analysis.mode(a, b), "mode_b_covers_a": analysis.mode(b, a),
            "shared": shared,
        })
        if counted:
            for (coverer, covered), (newer, newer_major) in newer_counts.items():
                if newer or newer_major:
                    mode = analysis.mode(coverer, covered)
                    counted = (newer if mode in ("newer", "any") else 0) + (newer_major if mode == "any" else 0)
                    counts_now = "all" if counted == newer + newer_major else ("none" if counted == 0 else "some")
                    toggles.append({
                        "coverer": coverer, "covered": covered, "mode": mode,
                        "source": "override" if (coverer, covered) in overrides else "default",
                        "newer_updates": newer, "newer_major_updates": newer_major,
                        # Whether the newer targets of this pair count as cover now, and the mode
                        # that flips that: "exact" stops them counting, "any" makes all count.
                        "counts_now": counts_now,
                        "switch_to": "exact" if counts_now == "all" else "any",
                    })

    pr_json = []
    for pr in sorted(prs, key=lambda p: p["number"]):
        raw = pr["raw"]
        status = "unevaluable" if not pr["evaluable"] else ("obsolete" if pr["number"] in obsolete else "kept")
        pr_json.append({
            "number": pr["number"], "title": raw.get("title", ""), "url": raw.get("url", ""),
            "bot": pr["bot"], "base": pr["base"], "head_sha": raw.get("head_sha"),
            "status": status, "update_count": len(pr["updates"]),
            "updates": [update_json(u) for u in pr["updates"]],
            "unevaluable_reasons": pr["reasons"], "ignored_lockfiles": pr["lockfiles"],
            "flags": flags(raw),
        })

    warnings = []
    if collected.get("truncated"):
        warnings.append("the pull request list hit the limit of %s; re-collect with a higher --limit"
                        % collected.get("limit"))

    result = {
        "repo": collected.get("repo"),
        "default_branch": collected.get("default_branch"),
        "collected_at": collected.get("collected_at"),
        "bots": collected.get("bots"),
        "options": {
            "newer_counts_as_replacement": args.newer,
            "across_major": args.across_major,
            "default_mode": analysis.default,
            "pair_modes": [{"coverer": c, "covered": d, "mode": m} for (c, d), m in sorted(overrides.items())],
        },
        "summary": {
            "bot_prs": len(prs),
            "evaluable": sum(1 for p in prs if p["evaluable"]),
            "unevaluable": sum(1 for p in prs if not p["evaluable"]),
            "obsolete": len(proposals),
            "kept": sum(1 for p in pr_json if p["status"] == "kept"),
        },
        "proposals": proposals,
        "overlaps": overlap_json,
        "pair_toggles": toggles,
        "prs": pr_json,
        "warnings": warnings,
    }
    text = json.dumps(result, ensure_ascii=True, indent=2)
    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(text + "\n")
    sys.stdout.write(text + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
