# claude-md-downstream — script tests

Unit tests for `skills/development/claude-md-downstream/scripts/`. Everything runs against local
git fixtures; the suite never touches the network.

```bash
S=skills/tests/development/claude-md-downstream/scripts
bash $S/run-tests.sh                      # all unit tests — rebuilds fixtures, cleans up after
bash $S/unit/test-match-version.sh        # one test file — rebuilds fixtures, leaves them behind
bash $S/clean-fixtures.sh                 # remove the fixtures (needed after a standalone run)
```

Requires `bash` 3.2+, `git`, `jq`, `python3`.

## The fixtures are rebuilt for every run, and never kept

**Each test file rebuilds the fixtures from scratch before it does anything, and `run-tests.sh`
removes them again when it finishes.** Treat that as the contract — a new test file must call
`fixtures/make-fixtures.sh` itself rather than assume a fixture is lying around.

Two reasons, both learned the hard way:

- **The fixtures are nested git repositories.** A `.git` directory inside a working repository is
  a persistent nuisance: `git status` and `git add` behave oddly around it, editors and search
  tooling walk into it, and it is easy to commit something unintended. `fixtures/.gitignore` is a
  second line of defence, not the first — the fixtures simply should not survive a test run.
- **Fixtures that persist accumulate state.** `test-fetch-upstream.sh` deliberately adds a commit
  to the upstream fixture to prove the refresh picks it up. A second run against the surviving
  fixture would start from a different history than the first, and the tests resolve commit SHAs
  dynamically precisely because of this.

`run-tests.sh` cleans up through an `EXIT` trap, so it also cleans up when a test fails. Set
`KEEP_FIXTURES=1` to keep them for debugging; it prints the path and reminds you to clean up.

Running a single test file directly rebuilds the fixtures but does **not** remove them — run
`clean-fixtures.sh` afterwards.

## What the fixtures provide

`fixtures/make-fixtures.sh` builds one fake upstream repository and one downstream repository per
state the skill has to recognise. It wipes whatever is there first, so it is safe to call at the
top of every test.

The upstream history is deliberately awkward, because that is where the script earns its keep:

| Commit | Template path                         | Content                                  |
| ------ | ------------------------------------- | ---------------------------------------- |
| 1      | `claude/claude-md-template.md`        | v1 — two sections                        |
| 2      | `claude/claude-md-template.md`        | v2 — adds the coding guidelines section  |
| 3      | `claude/claude-md-template.repo.md`   | v3 — **renamed**, tightens the commit rule |
| 4      | (readme only)                         | an unrelated commit the walk must filter out |

Commit 3 also adds an empty `claude/claude-md-template.user.md`, which is what the user-mode test
uses to check the `empty-template` path.

| Downstream fixture       | Holds                          | Expected status       |
| ------------------------ | ------------------------------ | --------------------- |
| `downstream-identical`   | v3 verbatim                    | `identical`           |
| `downstream-crlf`        | v3 with CRLF + trailing space  | `identical`           |
| `downstream-older`       | v1 verbatim, plus nested dirs  | `known-older-version` |
| `downstream-diverged`    | v2 + a bent rule + own section | `diverged`            |
| `downstream-nolocal`     | no `CLAUDE.md`                 | `no-local-file`       |

`downstream-older` matching v1 is the point of the rename in commit 3: without `git log --follow`
the history stops at the rename and the file is misreported as `diverged`.

`fake-home/` serves as `$HOME` for the user-mode tests.

## Notes for maintainers

- **SHAs are not stable.** Fixtures are rebuilt with fresh timestamps, so tests resolve commits
  through `git log` rather than hard-coding them.
- **`--reverse` does not combine with `--follow`.** The tests index the newest-first log from the
  end instead. The script has the same constraint.
- **The non-repo test uses `mktemp -d`, not a fixture.** A directory under `skills/` is still
  inside this repository, so `git rev-parse --show-toplevel` would succeed there and the exit-3
  path would never be reached.
- **Fixtures are nested git repositories.** See the section above: build them per run, never
  leave them behind. `fixtures/.gitignore` is the backstop, not the mechanism.
- Changing a script's exit codes or JSON keys means updating its `SKILL.md` step **and** the
  matching `unit/test-<name>.sh`.
