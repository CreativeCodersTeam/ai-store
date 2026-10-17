#!/usr/bin/env python3
"""Regenerate fixtures/scenario-mixed. Run after changing it, then commit the result.

  python skills/tests/development/dep-pr-cleanup/scripts/fixtures/build_fixtures.py
"""

import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from helpers import file_diff, hunk, lockfile, npm, pr, write_scenario  # noqa: E402

IMMORTAL = ("This PR contains the following updates: express ^4.18.2 -> ^4.20.0\n\n"
            "👻 **Immortal**: This PR will be recreated if closed unmerged. Get config help if that's undesired.")


def dockerfile(old, new):
    return file_diff("Dockerfile", hunk([], ["FROM node:%s AS build" % old], ["FROM node:%s AS build" % new],
                                        ["WORKDIR /app"]))


def compose(old, new):
    return file_diff("docker-compose.yml", hunk(["  db:"], ["    image: postgres:%s" % old],
                                                ["    image: postgres:%s" % new]))


def main():
    target = os.path.join(HERE, "scenario-mixed")
    shutil.rmtree(target, ignore_errors=True)
    entries = [
        (pr(101, title="Update dependency lodash to v4.17.21"),
         npm("package.json", ("lodash", "^4.17.20", "^4.17.21")), ["renovate[bot]", "alice"]),
        (pr(102, title="Update all non-major dependencies", checks="FAILURE"),
         npm("package.json", ("express", "^4.18.2", "^4.19.2"), ("lodash", "^4.17.20", "^4.17.21")), None),
        (pr(103, title="Update dependency lodash to v5"),
         npm("package.json", ("lodash", "^4.17.20", "^5.0.0")), None),
        (pr(104, title="Update dependency express to v4.20.0", body=IMMORTAL),
         npm("package.json", ("express", "^4.18.2", "^4.20.0")), None),
        (pr(105, bot="dependabot", title="Bump lodash from 4.17.20 to 4.17.21"),
         npm("package.json", ("lodash", "^4.17.20", "^4.17.21")), None),
        (pr(106, base="release/1.x", title="Update dependency lodash to v4.17.21 (release/1.x)"),
         npm("package.json", ("lodash", "^4.17.20", "^4.17.21")), None),
        (pr(107, title="Lock file maintenance"), lockfile(), None),
        (pr(108, title="Update Rust crate serde to v1.0.210"),
         file_diff("Cargo.toml", hunk(["[dependencies]"], ['serde = "1.0.200"'], ['serde = "1.0.210"'])), None),
        (pr(109, title="Update dependency express to v4.20.0"),
         npm("package.json", ("express", "^4.18.2", "^4.20.0")), None),
        (pr(110, bot="dependabot", title="Bump actions/checkout from 4 to 5"),
         file_diff(".github/workflows/ci.yml", hunk(["    steps:"], ["      - uses: actions/checkout@v4"],
                                                    ["      - uses: actions/checkout@v5"])), None),
        (pr(111, bot="dependabot", title="Bump the docker group with 2 updates"),
         dockerfile("20.11-alpine", "20.12-alpine") + compose("16.3", "16.4"), None),
        (pr(112, bot="dependabot", title="Bump node from 20.11-alpine to 20.15-alpine", draft=True),
         dockerfile("20.11-alpine", "20.15-alpine"), None),
        (pr(113, bot="dependabot", title="Bump postgres from 16.3 to 16.5"), compose("16.3", "16.5"), None),
    ]
    write_scenario(target, entries)
    print("wrote", target)


if __name__ == "__main__":
    main()
