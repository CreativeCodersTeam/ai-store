#!/usr/bin/env python3
"""Grade the mechanically checkable assertions of a claude-md-downstream eval run.

Most of what these evals test is judgement — whether a conflict was framed so a
user could rule on it. But a good half of each assertion list is a fact about
files on disk: did the project's own sections survive, was a backup written, did
anything get committed. Those are checked here so the same verdict comes out
every time and every iteration is comparable.

Usage: grade-mechanical.py <eval-id> <run-dir> [--json]

<run-dir> is the run directory holding outputs/ and scenario/. Emits the
expectations array the eval viewer expects: {text, passed, evidence}.
"""

import json
import subprocess
import sys
from pathlib import Path

REPO_BY_EVAL = {0: "repo-diverged", 1: "repo-older", 2: "repo-current"}


def read(p: Path) -> str:
    try:
        return p.read_text(errors="replace")
    except OSError:
        return ""


def commit_count(repo: Path) -> int:
    try:
        out = subprocess.run(
            ["git", "-C", str(repo), "rev-list", "--count", "HEAD"],
            capture_output=True, text=True, check=True).stdout.strip()
        return int(out)
    except (subprocess.CalledProcessError, ValueError, OSError):
        return -1


def check(text, passed, evidence):
    return {"text": text, "passed": bool(passed), "evidence": evidence}


def contains(hay: str, needle: str):
    """Case-insensitive substring test, whitespace-insensitive.

    Agents reflow prose, so a rule that upstream wrote across two lines may come
    back on one. Comparing on collapsed whitespace keeps that from reading as a
    lost rule.
    """
    norm = " ".join(hay.split()).lower()
    return " ".join(needle.split()).lower() in norm


def grade(eval_id: int, run_dir: Path):
    out = run_dir / "outputs"
    scenario = run_dir / "scenario"
    repo = scenario / REPO_BY_EVAL[eval_id]
    upstream = scenario / "upstream-ai-store"

    final = read(out / "final-CLAUDE.md")
    report = read(out / "report.md")
    questions = read(out / "questions.md")
    backups = sorted(repo.glob("CLAUDE.md.bak-*"))
    commits = commit_count(repo)

    current_template = ""
    try:
        current_template = subprocess.run(
            ["git", "-C", str(upstream), "show", "HEAD:claude/claude-md-template.repo.md"],
            capture_output=True, text=True, check=True).stdout
    except (subprocess.CalledProcessError, OSError):
        pass

    r = []

    if eval_id == 0:
        r.append(check(
            "The project's 'Build and Test' section survives verbatim in the final CLAUDE.md",
            contains(final, "Build with `./gradlew build`")
            and contains(final, "docker compose up -d db"),
            "both Build and Test rules found" if contains(final, "docker compose up -d db")
            else "at least one Build and Test rule is missing"))
        r.append(check(
            "The project's 'Deployment' section survives verbatim in the final CLAUDE.md",
            contains(final, "Deployments run from CI only"),
            "found" if contains(final, "Deployments run from CI only") else "missing"))
        r.append(check(
            "The local 'Never commit on main' instruction is still present in the final CLAUDE.md",
            contains(final, "Never commit on main"),
            "found" if contains(final, "Never commit on main") else "missing"))
        r.append(check(
            "The upstream verification rule was applied to the final CLAUDE.md",
            contains(final, "verify that your changes are complete"),
            "found" if contains(final, "verify that your changes are complete") else "missing"))
        r.append(check(
            "The upstream 'Stage files by name' clause was applied to the final CLAUDE.md",
            contains(final, "Stage files by name"),
            "found" if contains(final, "Stage files by name") else "missing"))
        r.append(check(
            "The upstream 'unless another specific language is expressly requested' clause was applied",
            contains(final, "unless another specific language is expressly requested"),
            "found" if contains(final, "unless another specific language is expressly requested")
            else "missing"))
        r.append(check(
            "Presents the commit-rule conflict on its own, showing both the upstream and the local wording",
            contains(questions, "Stage files by name") and contains(questions, "Never commit on main"),
            f"questions.md is {len(questions)} chars; "
            f"upstream wording {'present' if contains(questions, 'Stage files by name') else 'absent'}, "
            f"local wording {'present' if contains(questions, 'Never commit on main') else 'absent'}"))
        r.append(check(
            "A timestamped backup of the previous CLAUDE.md exists next to it",
            len(backups) == 1,
            f"{len(backups)} backup file(s): {[b.name for b in backups]}"))

    elif eval_id == 1:
        same = " ".join(final.split()) == " ".join(current_template.split())
        r.append(check(
            "After approval the final CLAUDE.md equals the current upstream template",
            same and bool(current_template),
            "matches the upstream template" if same else "differs from the upstream template"))
        # The eval upstream is a local mirror, so there is no web view to link to.
        # A link here would have to have been invented, which is the failure mode.
        fabricated = f"{scenario}/commit/" in report or "upstream-ai-store/commit/" in report
        has_sha = any(len(w.strip(".,()`")) >= 7 and all(c in "0123456789abcdef"
                      for c in w.strip(".,()`")[:7]) and w.strip(".,()`")[:7].isalnum()
                      for w in report.split())
        r.append(check(
            "Reports the matched commit by SHA and does not fabricate a link for the mirror upstream",
            has_sha and not fabricated,
            ("a commit SHA is reported" if has_sha else "no commit SHA found")
            + ("; a fabricated mirror link is present" if fabricated else "; no fabricated link")))
        r.append(check(
            "A timestamped backup of the previous CLAUDE.md exists next to it",
            len(backups) == 1,
            f"{len(backups)} backup file(s): {[b.name for b in backups]}"))

    elif eval_id == 2:
        same = " ".join(final.split()) == " ".join(current_template.split())
        r.append(check(
            "CLAUDE.md is byte-identical to before the run",
            same and bool(current_template),
            "unchanged" if same else "the file was modified"))
        r.append(check(
            "No backup file was created",
            len(backups) == 0,
            f"{len(backups)} backup file(s): {[b.name for b in backups]}"))
        # A run that asked nothing still writes questions.md saying so, so file
        # length proves nothing. Look for an actual question instead, and let an
        # explicit "none arose" statement settle it.
        said_none = any(m in " ".join(questions.split()).lower() for m in
                        ("no question", "none arose", "nothing was asked", "no questions arose"))
        asked = "?" in questions and not said_none
        r.append(check(
            "Asked the user nothing",
            not asked,
            "questions.md states that none arose" if said_none
            else ("a question is present" if asked else "no question found")))

        # Restraint is the point of this eval: with nothing to decide, anything
        # offered is work the user did not ask for. Target the offer itself
        # rather than the report's length, which only correlates with it.
        offers = [phrase for phrase in
                  ("would you like", "shall i", "do you want", "i recommend",
                   "you may want", "worth considering", "i suggest", "i'd suggest",
                   "one observation", "worth relaying")
                  if phrase in " ".join(report.split()).lower()]
        r.append(check(
            "The report is brief — no offers, no proposals, no follow-up work",
            not offers,
            f"unsolicited offer/suggestion phrasing: {offers}" if offers
            else "no offers or suggestions in the report"))

    # Applies to every eval: the skill must never commit.
    r.append(check(
        "No git commit was created in the scenario repository",
        commits == 1,
        f"HEAD is {commits} commit(s) deep (1 = the fixture's initial commit)"))

    return r


def main():
    args = [a for a in sys.argv[1:] if a != "--json"]
    if len(args) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    results = grade(int(args[0]), Path(args[1]))
    print(json.dumps({"expectations": results}, indent=2))
    failed = [e for e in results if not e["passed"]]
    print(f"\n{len(results) - len(failed)}/{len(results)} mechanical checks passed",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
