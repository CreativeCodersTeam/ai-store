#!/usr/bin/env python3
"""Mechanical checks for code-design eval runs.

Usage: grade_mechanical.py <project-dir> [--host shop/service.py]

Run it on a scratch copy of a fixture that has `git init` and one baseline commit — never on a
directory inside this repository. It marks untracked files with `git add -N` (intent to add, no
commit) so new files show up in the diff.

Prints JSON with: tests (pass/fail, count), removed non-import lines in pre-existing test files,
net growth of the host file, new production files, longest functions in changed production
files, abstract types (ABC / Protocol) and those with fewer than two nominal subclasses — a
Protocol is implemented structurally, so it always reports 0 there; check Protocols by hand.
"""
import ast
import re
import json
import subprocess
import sys
from pathlib import Path


def git(project, *args):
    return subprocess.run(["git", *args], cwd=project, capture_output=True, text=True).stdout


def main():
    project = Path(sys.argv[1]).resolve()
    host = sys.argv[sys.argv.index("--host") + 1] if "--host" in sys.argv else None

    run = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-t", "."],
        cwd=project, capture_output=True, text=True,
    )
    tail = run.stderr.strip().splitlines()[-3:]
    ran = next((l for l in run.stderr.splitlines() if l.startswith("Ran ")), "")

    git(project, "add", "-N", ".")  # make untracked files visible to diff, no commit
    numstat = git(project, "diff", "--numstat", "HEAD")
    changes = {}
    for line in numstat.strip().splitlines():
        added, deleted, path = line.split("\t")
        changes[path] = (int(added), int(deleted))
    tracked = set(git(project, "ls-tree", "-r", "--name-only", "HEAD").split())

    deleted_in_old_tests = {}
    for p in changes:
        if p.startswith("tests/") and p in tracked:
            removed = [l[1:] for l in git(project, "diff", "-U0", "HEAD", "--", p).splitlines()
                       if l.startswith("-") and not l.startswith("---")]
            removed = [l for l in removed if l.strip() and not re.match(r"\s*(from|import)\s", l)]
            if removed:
                deleted_in_old_tests[p] = removed
    host_growth = None
    if host and host in changes:
        host_growth = changes[host][0] - changes[host][1]
    elif host:
        host_growth = 0

    prod_changed = [p for p in changes if p.endswith(".py") and not p.startswith("tests/")]
    new_prod = [p for p in prod_changed if p not in tracked]

    longest = []
    abstract = {}
    impls = {}
    for p in prod_changed:
        src = (project / p).read_text()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                longest.append((node.end_lineno - node.lineno + 1, f"{p}:{node.lineno} {node.name}"))
    for p in (project).rglob("*.py"):
        if "tests" in p.parts:
            continue
        tree = ast.parse(p.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                bases = [ast.unparse(b) for b in node.bases]
                if any(b.split(".")[-1] in ("ABC", "Protocol") for b in bases):
                    abstract[node.name] = str(p.relative_to(project))
                for b in bases:
                    impls.setdefault(b.split(".")[-1], []).append(node.name)
    single_impl = {name: impls.get(name, []) for name in abstract if len(impls.get(name, [])) < 2}

    longest.sort(reverse=True)
    print(json.dumps({
        "tests_ok": run.returncode == 0,
        "tests_ran": ran,
        "tests_tail": tail,
        "removed_non_import_lines_in_existing_tests": deleted_in_old_tests,
        "host_net_growth": host_growth,
        "changed_production_files": prod_changed,
        "new_production_files": new_prod,
        "longest_functions": longest[:3],
        "abstract_types": abstract,
        "abstract_types_with_lt_2_impls": single_impl,
    }, indent=2))


if __name__ == "__main__":
    main()
