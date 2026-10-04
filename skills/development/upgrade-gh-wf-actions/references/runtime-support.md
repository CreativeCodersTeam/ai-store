# JavaScript runtime support on GitHub Actions

`check-updates.sh` reports `runs.using` of each action at the version in use (`runtimes[]`)
and at every offered target (`rows[].target_runtimes[]`). The script does not judge the value;
this file does. It is the single place to update when GitHub changes runtime support.

**State as of 2026-10-04**, from the GitHub changelog:

| `runs.using`               | Status                                                                                      |
| -------------------------- | ------------------------------------------------------------------------------------------- |
| `node24`                   | Current runtime on GitHub-hosted runners                                                     |
| `node20`                   | **Removed on 2026-09-23.** Runners execute such actions on Node 24 instead; the `ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION` opt-out no longer exists |
| `node16`, `node12`         | Removed earlier (Node 16 end of life for Actions: 2024)                                       |
| `composite`, `docker`      | Not a JavaScript runtime — nothing to report                                                  |
| `null`                     | `action.yml` could not be read — say "runtime unknown", do not guess                          |

Sources:
[Node 20 is no longer available in GitHub Actions (2026-09-23)](https://github.blog/changelog/2026-09-23-node-20-is-no-longer-available-in-github-actions/) ·
[Deprecation of Node 20 on GitHub Actions runners (2025-09-19)](https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/) ·
[End of life for Actions Node16 (2024-09-25)](https://github.blog/changelog/2024-09-25-end-of-life-for-actions-node16/)

## What it means for the table

- A **current** runtime below `node24` means the version in use declares a runtime GitHub no
  longer provides. It still runs — forced onto Node 24 — but it was never tested there by its
  maintainers. Say so under the table for that action.
- A **target** runtime below `node24` is the more important finding: the user would be pinning
  to a version that already declares an unsupported runtime. Mark the row with ⚠ and name the
  runtime in the option description. This typically hits same-major and pin rows of first-party
  actions whose node24 support only shipped in a new major.
- Self-hosted runners: Node 24 does not run on macOS ≤ 13.4 or ARM32 (same changelog). Mention it
  only when the workflow's `runs-on` shows a self-hosted runner.

If this file's date is far behind the current date, the table may be outdated — state the date
when you rely on it.
