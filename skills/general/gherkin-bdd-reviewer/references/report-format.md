# Report Format

By default the reviewer writes one Markdown file to
`docs/reviews/YYYY-MM-DD-bdd-<mode>.md`. Never overwrite — append `-2`, `-3`, … on
collision. Never auto-commit. If the user asked for an inline review, emit the same
structure in the reply instead of writing a file.

## Required Sections

1. Title + metadata block
2. Executive Summary (detailed)
3. Findings, ordered by severity desc, then by `file:line`
4. Conventions Applied note

## Skeleton

```markdown
# Gherkin/BDD Review — <mode>

**Date:** YYYY-MM-DD
**Mode:** all | branch (vs. main) | uncommitted
**Framework:** reqnroll | cucumber-jvm | cucumber-js | unknown
**Scope:** <N> feature files, <M> scenarios (or "<N> changed feature/step files")
**Review strategy:** full | prioritized | chunked
**Report language:** English (default) | <language>

## Executive Summary

| Severity | Count |
|---|---|
| Critical | N |
| Major | N |
| Minor | N |
| Suggestion | N |
| Nitpick | N |

**Top risks:**
1. <one line>
2. <one line>
3. <one line>

**Overall:** <1–2 sentence assessment of suite health>

## Findings

### [Critical][Step-Defs] features/checkout.feature:14
<one-line description>

<recommendation paragraph>

```gherkin
# fix suggestion (or a step-definition snippet for Step-Defs findings)
```

### [Major][Gherkin-Style] features/cart.feature:8
…

## Conventions Applied

<Which repo conventions overrode built-in rules, or "none found — built-in
gherkin-bdd rules used".>
```

## Rules

- **Every finding MUST include a concrete fix** — a `gherkin`-fenced snippet for
  feature-file findings, or a step-definition snippet for `Step-Defs` findings. If the
  fix is structural (no single-snippet rewrite), describe the steps in prose and show
  the most-affected snippet.
- Reference `file:line` — do not paste raw diff content.
- File paths are repo-relative.
- Group findings by severity desc; break ties by file path asc.
- If strategy `chunked` was used, group findings under `## Findings — <file>` subsections.
- If strategy `prioritized` was used, list deferred files at the end under
  `## Files Not Reviewed in Detail`.
- The reviewer **never** edits `.feature` or step-definition files and **never**
  auto-commits — it only writes the report.
