# upgrade-gh-wf-actions — script tests

Unit tests for `skills/development/upgrade-gh-wf-actions/scripts/`. `gh` is replaced by
`mock-gh/gh`, so the suite never touches the network and needs no GitHub login.

```bash
S=skills/tests/development/upgrade-gh-wf-actions/scripts
bash $S/run-tests.sh                     # all unit tests
bash $S/unit/test-check-updates.sh       # one test file
```

Requires `bash` 3.2+, `jq`. Nothing to clean up: the fixtures are static files, and the tests that
write (`test-apply-pins.sh`) work on a copy in a temporary directory.

## Fixtures

| Path                                | Content                                                                                   |
| ----------------------------------- | ----------------------------------------------------------------------------------------- |
| `fixtures/repo-basic/`              | Workflows and composite actions covering every ref shape: floating and exact tags, quoted values, SHA pins with, without, and with a stale version comment, subpath actions, a reusable workflow, a branch ref, local and `docker://` refs, a ref without `@`, a CRLF file, and a non-YAML file inside `.github/workflows/` |
| `fixtures/repo-empty/`              | No workflows at all                                                                        |
| `fixtures/gh-data/graphql/O__N.json`| The GraphQL response `check-updates.sh` receives for repository `O/N`                      |
| `fixtures/gh-data/tags/O__N.tsv`    | `tag<TAB>sha` lines answering the individual `commits/refs/tags/<tag>` lookup              |
| `fixtures/gh-data/contents/O__N/REF/PATH` | `action.yml` / `action.yaml` served by the `contents` endpoint at a tag or SHA — the source of `runs.using` |
| `fixtures/shas.json`                | The fake commit SHAs used above, by repository and tag, so tests never hard-code them      |

All ages are computed against `--now 2026-10-04T00:00:00Z`. The `acme/checkout` data is built
so that the floating `v4` tag points at a release only 4 days old, the newest `v5.1.0` is 3 days
old, and `v5.0.0` is 33 days old — which exercises the major row, the downgrade pin, and the
`too_young` list in one group. `acme/tagonly` has no releases; its `v1.1.0` tagger date carries a
`-04:00` offset chosen so that ignoring the offset changes the age in days.

The `.github/` directories under `fixtures/` are inert — GitHub only runs workflows from the
repository root. When running the skill on this repository itself, pass
`--exclude skills/tests` to `scan-actions.sh` so the fixture `action.yml` files are not offered
for upgrade.

## Mock `gh`

`mock-gh/gh` answers `gh auth status` (`MOCK_GH_AUTH=fail` makes it fail), `gh api graphql`
(from `gh-data/graphql/`, a NOT_FOUND error otherwise), `gh api repos/O/N/commits/refs/tags/T`
(from `gh-data/tags/`), and `gh api repos/O/N/contents/PATH?ref=REF` (from `gh-data/contents/`,
base64-encoded like the real API). The GraphQL fixture serves both `check-updates.sh` and
`release-notes.sh`; the release bodies in `acme__checkout.json` drive the `notes_flags` and
`current_warnings` assertions. Set `MOCK_GH_LOG=<file>` to record every call — `test-check-updates.sh`
uses it to assert which individual tag lookups happened.
