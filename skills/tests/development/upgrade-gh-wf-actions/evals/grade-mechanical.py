#!/usr/bin/env python3
"""Mechanical grading for the upgrade-gh-wf-actions evals.

Usage: grade-mechanical.py <eval-id> <run-dir>

<run-dir> holds repo-outdated/ (the scenario after the run) and outputs/response.md.
Writes <run-dir>/grading.json with expectations [{text, passed, evidence}] — the format
the skill-creator eval viewer reads. Checks that need the live GitHub API (SHA belongs to
the tag, release age) call `gh`, so an authenticated gh is required.
"""
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ORIGINAL = {
    # (file, action) -> major version of the original ref
    (".github/workflows/ci.yml", "actions/checkout"): 4,
    (".github/workflows/ci.yml", "actions/setup-node"): 4,
    (".github/workflows/ci.yml", "actions/cache"): 3,
    (".github/workflows/codeql.yml", "actions/checkout"): 4,
    (".github/workflows/codeql.yml", "github/codeql-action/init"): 3,
    (".github/workflows/codeql.yml", "github/codeql-action/analyze"): 3,
    (".github/actions/setup-py/action.yml", "actions/setup-python"): 5,
}
ORIGINAL_REF = {
    (".github/workflows/ci.yml", "actions/checkout"): "v4",
    (".github/workflows/ci.yml", "actions/setup-node"): "v4.0.0",
    (".github/workflows/ci.yml", "actions/cache"): "88522ab9f39a2ea568f7027eddc7d8d8bc9d59c8",
    (".github/workflows/codeql.yml", "actions/checkout"): "v4",
    (".github/workflows/codeql.yml", "github/codeql-action/init"): "v3",
    (".github/workflows/codeql.yml", "github/codeql-action/analyze"): "v3",
    (".github/actions/setup-py/action.yml", "actions/setup-python"): "v5",
}
USES = re.compile(r"^\s*(?:-\s+)?uses:\s*['\"]?([^'\"\s#]+)['\"]?\s*(?:#\s*(.*))?$")
PIN_COMMENT = re.compile(r"^(v?\d+\.\d+\.\d+)\b")
SHA = re.compile(r"^[0-9a-f]{40}$")


def sh(*args, cwd=None):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True)


def gh_json(path):
    r = sh("gh", "api", path)
    return json.loads(r.stdout) if r.returncode == 0 else None


def current_uses(repo):
    """{(file, action): (ref, comment)} for every uses: line in the scenario."""
    out = {}
    for file, _ in ORIGINAL:
        p = repo / file
        for line in p.read_text().splitlines():
            m = USES.match(line)
            if m and "@" in m.group(1):
                action, ref = m.group(1).rsplit("@", 1)
                out[(file, action)] = (ref, (m.group(2) or "").strip())
    return out


def changed(uses):
    """Occurrences whose ref differs from the scenario's original ref."""
    return {k: v for k, v in uses.items() if k in ORIGINAL and v[0] != ORIGINAL_REF[k]}


_tag_cache = {}


def verify_pin(action, sha, version, min_age_days):
    """(sha matches tag, age_days or None) via the live API."""
    repo = "/".join(action.split("/")[:2])
    key = (repo, version)
    if key not in _tag_cache:
        c = gh_json(f"repos/{repo}/commits/refs/tags/{version}")
        rel = gh_json(f"repos/{repo}/releases/tags/{version}")
        age = None
        if rel and rel.get("published_at"):
            pub = datetime.fromisoformat(rel["published_at"].replace("Z", "+00:00"))
            age = (datetime.now(timezone.utc) - pub).days
        _tag_cache[key] = ((c or {}).get("sha"), age)
    tag_sha, age = _tag_cache[key]
    return tag_sha == sha, age


SKILL_SCRIPTS = Path(__file__).resolve().parents[4] / "development" / "upgrade-gh-wf-actions" / "scripts"


def expected_within_major(repo, min_age):
    """(action, version) of every within-major row (same-major upgrade or pin) at grading time.

    Uses the skill's own check-updates.sh as the data source: it is covered by the script unit
    tests, and the live versions drift, so they cannot be hard-coded here.
    """
    scan = sh("bash", str(SKILL_SCRIPTS / "scan-actions.sh"), "--root", str(repo))
    if scan.returncode != 0:
        return []
    upd = subprocess.run(["bash", str(SKILL_SCRIPTS / "check-updates.sh"), "--scan", "-",
                          "--min-age-days", str(min_age)], input=scan.stdout, capture_output=True, text=True)
    if upd.returncode != 0:
        return []
    out = []
    for g in json.loads(upd.stdout)["groups"]:
        for r in g["rows"]:
            if r["major"] is False:
                out.append((g["repo"], r["target_version"]))
    return out


def exp(text, passed, evidence):
    return {"text": text, "passed": bool(passed), "evidence": evidence}


def common_pin_checks(uses, chg, min_age):
    res = []
    bad_format = [f"{k[1]} in {k[0]}: @{v[0]} # {v[1]}" for k, v in chg.items()
                  if not (SHA.match(v[0]) and PIN_COMMENT.match(v[1]))]
    res.append(exp("Every changed uses: line is pinned as @<40-hex sha> # vX.Y.Z",
                   chg and not bad_format,
                   "bad: " + "; ".join(bad_format) if bad_format else f"{len(chg)} pinned lines, all well-formed"))
    mismatched, young, unknown_age = [], [], []
    for (f, action), (ref, comment) in chg.items():
        m = PIN_COMMENT.match(comment)
        if not (SHA.match(ref) and m):
            continue
        ok, age = verify_pin(action, ref, m.group(1), min_age)
        if not ok:
            mismatched.append(f"{action}@{ref[:12]} # {m.group(1)}")
        if age is None:
            unknown_age.append(f"{action} {m.group(1)}")
        elif age < min_age:
            young.append(f"{action} {m.group(1)} ({age}d)")
    res.append(exp("Each pinned SHA is the commit the commented version tag points at",
                   chg and not mismatched, "mismatch: " + "; ".join(mismatched) if mismatched else "all SHAs match their tags"))
    res.append(exp(f"Each new version's release is at least {min_age} days old",
                   chg and not young and not unknown_age,
                   "; ".join([f"too young: {', '.join(young)}"] * bool(young) + [f"no release: {', '.join(unknown_age)}"] * bool(unknown_age))
                   or "all releases old enough"))
    return res


def main():
    eval_id, run_dir = int(sys.argv[1]), Path(sys.argv[2])
    repo = run_dir / "repo-outdated"
    response = (run_dir / "outputs" / "response.md").read_text() if (run_dir / "outputs" / "response.md").exists() else ""
    uses = current_uses(repo)
    chg = changed(uses)
    commits = sh("git", "rev-list", "--count", "HEAD", cwd=repo).stdout.strip()
    local_ok = "uses: ./.github/actions/setup-py" in (repo / ".github/workflows/ci.yml").read_text()
    res = []

    if eval_id == 1:
        res += common_pin_checks(uses, chg, 7)
        crossed = []
        for (f, action), (ref, comment) in chg.items():
            m = PIN_COMMENT.match(comment)
            if m and int(m.group(1).lstrip("v").split(".")[0]) != ORIGINAL[(f, action)]:
                crossed.append(f"{action} in {f}: v{ORIGINAL[(f, action)]} -> {m.group(1)}")
        res.append(exp("No upgrade crosses a major version", chg and not crossed,
                       "crossed: " + "; ".join(crossed) if crossed else "all changes stay within their major"))
        expected = set(ORIGINAL)
        missing = sorted(f"{a} in {f}" for f, a in expected - set(chg))
        res.append(exp("Every remote action occurrence is pinned (checkout x2, setup-node, cache, codeql init+analyze, setup-python in the composite action)",
                       not missing, "not pinned: " + "; ".join(missing) if missing else "all 7 occurrences pinned"))
        init, analyze = uses.get((".github/workflows/codeql.yml", "github/codeql-action/init")), uses.get((".github/workflows/codeql.yml", "github/codeql-action/analyze"))
        res.append(exp("codeql-action init and analyze end on the same SHA", init and analyze and init[0] == analyze[0],
                       f"init={init and init[0][:12]} analyze={analyze and analyze[0][:12]}"))
        c1, c2 = uses.get((".github/workflows/ci.yml", "actions/checkout")), uses.get((".github/workflows/codeql.yml", "actions/checkout"))
        res.append(exp("Both actions/checkout occurrences end on the same SHA", c1 and c2 and c1[0] == c2[0],
                       f"ci={c1 and c1[0][:12]} codeql={c2 and c2[0][:12]}"))
        node20 = re.search(r"node\s?20", response, re.I) is not None
        res.append(exp("The response warns that some chosen targets still declare the removed node20 runtime", node20,
                       "node20 mentioned" if node20 else "no node20 hint"))
        cache_note = re.search(r"(cache[- ]service|legacy|3\.4\.0)", response, re.I) is not None
        res.append(exp("The response reports release-note findings for the applied upgrades (e.g. actions/cache v3.4.0 moving to the new cache service)",
                       cache_note, "cache release-note finding present" if cache_note else "no release-note finding for actions/cache"))

    elif eval_id == 2:
        diff = sh("git", "status", "--porcelain", cwd=repo).stdout.strip()
        res.append(exp("No file in the repository is modified", diff == "", diff or "working tree clean"))
        res.append(exp("The response states the 14-day minimum age", re.search(r"\b14\b", response) is not None,
                       "found '14'" if re.search(r"\b14\b", response) else "no '14' in response"))
        has_table = re.search(r"^\|.*\|.*\|.*\|.*\|", response, re.M) is not None
        res.append(exp("The response contains a table with at least four columns", has_table,
                       "markdown table found" if has_table else "no table"))
        young = re.search(r"codeql[\s\S]{0,400}?(too young|younger than|not yet (eligible|old enough)|eligible in|\b1[0-3] days? old)", response, re.I)
        within = expected_within_major(repo, 14)
        missing = [f"{a} {v}" for a, v in within if not re.search(re.escape(v) + r"\b", response)]
        res.append(exp("For every action the report offers a version within the current major (same-major upgrade or pin) next to the newest major",
                       within and not missing,
                       "missing: " + ", ".join(missing) if missing else "within-major targets named: " + ", ".join(f"{a} {v}" for a, v in within)))
        runtime = re.search(r"node\s?(16|20)", response, re.I) is not None
        res.append(exp("The report warns that the within-major targets still declare a removed runtime (node16/node20)", runtime,
                       "runtime warning present" if runtime else "no node16/node20 mention"))
        res.append(exp("The response mentions the codeql-action releases that are newer but younger than 14 days instead of offering them",
                       young is not None, young.group(0)[-120:] if young else "no too-young mention for codeql-action"))

    elif eval_id == 3:
        targets = {k: v for k, v in chg.items() if k[1] in ("actions/checkout", "actions/setup-node")}
        others = {k: v for k, v in chg.items() if k not in targets}
        res += common_pin_checks(uses, targets, 7)
        want = {k for k in ORIGINAL if k[1] in ("actions/checkout", "actions/setup-node")}
        missing = sorted(f"{a} in {f}" for f, a in want - set(targets))
        res.append(exp("Both checkout occurrences and setup-node are upgraded", not missing,
                       "missing: " + "; ".join(missing) if missing else "all 3 occurrences changed"))
        res.append(exp("cache, codeql-action, and setup-python are left unchanged", not others,
                       "changed: " + "; ".join(f"{a} in {f}" for f, a in others) if others else "untouched"))
        majors = []
        for (f, action), (ref, comment) in targets.items():
            # the version comment of a SHA pin, else the ref itself when it is a tag
            m = PIN_COMMENT.match(comment) or re.match(r"^v?(\d+)", ref)
            if m:
                majors.append(int(m.group(1).lstrip("v").split(".")[0]) > ORIGINAL[(f, action)])
        res.append(exp("The targets are major upgrades (latest allowed version, majors permitted)", majors and all(majors),
                       f"{sum(majors)}/{len(majors)} targets cross a major"))
        reminder = re.search(r"release notes|breaking|changelog|what changed|\bsince v\d", response, re.I) is not None
        res.append(exp("The response points at release notes / breaking changes of the major upgrades", reminder,
                       "mentioned" if reminder else "not mentioned"))
        per_action = all(re.search(a, response, re.I) for a in (r"checkout[^\n]*(breaking|input|permission|node|runner|change)",
                                                                r"setup-node[^\n]*(breaking|input|permission|node|runner|change)"))
        res.append(exp("The response reports release-note findings per upgraded action, not only a link", per_action,
                       "findings for checkout and setup-node" if per_action else "findings missing for at least one action"))

    res.append(exp("The local action reference ./.github/actions/setup-py is unchanged", local_ok, "present" if local_ok else "changed or removed"))
    res.append(exp("Nothing was committed", commits == "1", f"commit count {commits}"))

    passed = sum(e["passed"] for e in res)
    out = {"expectations": res, "summary": {"passed": passed, "failed": len(res) - passed, "total": len(res),
                                             "pass_rate": round(passed / len(res), 2)}}
    (run_dir / "grading.json").write_text(json.dumps(out, indent=2) + "\n")
    print(f"{run_dir.name}: {passed}/{len(res)}")


if __name__ == "__main__":
    main()
