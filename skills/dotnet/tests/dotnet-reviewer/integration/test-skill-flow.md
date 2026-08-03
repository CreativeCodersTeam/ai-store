# Smoke Test — End-to-End Skill Flow

Manual checklist a human walks through once before declaring the skill ready.
Time budget: ~15 minutes. Use `skills/dotnet/tests/dotnet-reviewer/fixtures/repo-net10` as the
working directory.

## Prerequisites

- [ ] `bash skills/dotnet/tests/dotnet-reviewer/run-tests.sh` passes (all unit tests green).
- [ ] A `dotnet` SDK able to build the fixture TFMs is on `PATH` (or use the mocked path on a machine without SDK).
- [ ] You have a Copilot-compatible client that loads skills from this directory.

## Activation

- [ ] Type a generic prompt like "please review my changes" — skill MUST NOT activate.
- [ ] Type "use dotnet-reviewer to review my changes" — skill activates.
- [ ] Type "dotnet code review" — skill activates.
- [ ] Type "dotnet review please" — skill activates.

## Interactive Prompt

- [ ] Skill asks for mode (uncommitted | branch).
- [ ] Skill asks build/format/test (defaults to all No).
- [ ] Skill asks for report language (defaults to English).
- [ ] Invalid mode input is re-prompted, not silently accepted.

## Version Detection

- [ ] On `repo-net10`: SDK detected as `10.0.100`, target framework `net10.0`, report header shows
      `Version origin: repo:App.csproj` and `Checklist: review-checklist-net10.md`.
- [ ] On `repo-net8`: skill does **not** abort — it reviews with the general checklists and the
      header states `Checklist: general checklists only (no checklist for net8.0)`.
- [ ] On `repo-props-tfm`: target framework `net10.0` resolved from `Directory.Build.props`, header
      shows `Version origin: repo:Directory.Build.props`.
- [ ] On `repo-no-project`: skill falls back to the latest LTS and states
      `Version origin: default-lts` — it does not abort.
- [ ] Explicit directive ("review it as net8.0") in `repo-net10` overrides detection and the header
      shows `Version origin: user`.
- [ ] On `repo-malformed-csproj`: skill prompts whether to proceed without version awareness.

## Diff Collection

- [ ] Uncommitted mode picks up `src/New.cs` (the unstaged file).
- [ ] `static.min.js` and `wwwroot/lib/vendor.js` are excluded.
- [ ] Branch mode against missing `main` aborts with a clear message.
- [ ] Empty-diff repo reports "no changes to review" and exits.

## Large-Diff Strategy Gate

- [ ] On `repo-large-diff`, skill detects > 2000 LOC / > 50 files and offers B/C/D.
- [ ] Choosing C: report includes prioritized files first, "Files Not Reviewed in Detail" section at the end.
- [ ] Choosing D: report is grouped by file under `## Findings — <file>` subheaders.
- [ ] Choosing B: header notes "full review under high token cost".

## Tool Integration (with a real `dotnet` SDK)

- [ ] Build only: report appendix lists `dotnet build` summary.
- [ ] Format only: violations appear as `Suggestion` findings.
- [ ] Test only: failures appear as `Critical` findings.

## Report

- [ ] Report file written to `docs/reviews/YYYY-MM-DD-<branch>-<mode>.md`.
- [ ] No auto-commit happens.
- [ ] Re-running creates `*-2.md` (no overwrite).
- [ ] Executive Summary contains: counts table, top-3 risks, LOC + file count, scope description.
- [ ] At least one finding includes a `csharp` fenced code block as a fix suggestion.
- [ ] Severity ordering: Critical → Major → Minor → Suggestion → Nitpick.
- [ ] Chat output is one file path + one-line summary, nothing else.

## Failure Modes

- [ ] Killing the skill mid-run leaves no half-written report.
- [ ] Running with `dotnet` not on `PATH` and all tool flags off: review still produced.
- [ ] Running with secrets in environment: secrets do not appear in report or logs.

## Sign-off

- [ ] Walked through by: __________
- [ ] Date: __________
- [ ] Notes: __________
