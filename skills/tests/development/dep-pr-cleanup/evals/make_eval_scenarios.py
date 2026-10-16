#!/usr/bin/env python3
"""Build one sandbox per eval run for the dep-pr-cleanup skill-behaviour evals.

  python make_eval_scenarios.py <run-dir>

Creates
  <run-dir>/sandbox/data/     scenario-mixed, as repository dep-pr-cleanup-eval/shop
  <run-dir>/sandbox/repo/     a git working copy whose origin points at that (non-existent) repository
  <run-dir>/sandbox/bin/gh    a shim running the mock gh; every call is logged to sandbox/gh-calls.log
  <run-dir>/outputs/          empty, for the run's outputs

Run commands inside the sandbox with PATH=<run-dir>/sandbox/bin:$PATH so `gh` is the mock.
"""

import json
import os
import shutil
import stat
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(os.path.dirname(HERE), "scripts")
MIXED = os.path.join(SCRIPTS, "fixtures", "scenario-mixed")
MOCK = os.path.join(SCRIPTS, "mock_gh", "gh.py")
REPO = "dep-pr-cleanup-eval/shop"

PACKAGE_JSON = {
    "name": "shop", "version": "1.0.0", "private": True,
    "dependencies": {"express": "^4.18.2", "lodash": "^4.17.20"},
}


def git(cwd, *args):
    subprocess.run(["git"] + list(args), cwd=cwd, check=True, capture_output=True)


def main(run_dir):
    run_dir = os.path.abspath(run_dir)
    sandbox = os.path.join(run_dir, "sandbox")
    shutil.rmtree(sandbox, ignore_errors=True)
    data, repo, bin_dir = (os.path.join(sandbox, d) for d in ("data", "repo", "bin"))
    shutil.copytree(MIXED, data)
    with open(os.path.join(data, "repo.json"), "w", encoding="utf-8") as handle:
        json.dump({"nameWithOwner": REPO, "defaultBranchRef": {"name": "main"}}, handle)

    os.makedirs(repo)
    with open(os.path.join(repo, "package.json"), "w", encoding="utf-8") as handle:
        json.dump(PACKAGE_JSON, handle, indent=2)
    with open(os.path.join(repo, "README.md"), "w", encoding="utf-8") as handle:
        handle.write("# shop\n")
    git(repo, "init", "-q", "-b", "main")
    git(repo, "-c", "user.name=eval", "-c", "user.email=eval@example.invalid", "add", "package.json", "README.md")
    git(repo, "-c", "user.name=eval", "-c", "user.email=eval@example.invalid", "commit", "-q", "-m", "init")
    git(repo, "remote", "add", "origin", "https://github.com/%s.git" % REPO)

    os.makedirs(bin_dir)
    shim = os.path.join(bin_dir, "gh")
    with open(shim, "w", encoding="utf-8", newline="\n") as handle:
        handle.write('#!/bin/sh\nMOCK_GH_DATA="%s" MOCK_GH_LOG="%s" exec "%s" "%s" "$@"\n'
                     % (data, os.path.join(sandbox, "gh-calls.log"), sys.executable, MOCK))
    os.chmod(shim, os.stat(shim).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    open(os.path.join(sandbox, "gh-calls.log"), "w").close()
    os.makedirs(os.path.join(run_dir, "outputs"), exist_ok=True)
    print(json.dumps({"repo": repo, "bin": bin_dir, "log": os.path.join(sandbox, "gh-calls.log")}))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.stderr.write(__doc__)
        sys.exit(1)
    main(sys.argv[1])
