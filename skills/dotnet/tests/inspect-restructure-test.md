# Inspect Restructure Test (Findings I-1, I-2, I-3)

Test artifact per `superpowers:writing-skills` (RED → GREEN → Verify) for the
2026-07-22 fix of Findings I-1/I-2/I-3 in
`docs/reviews/2026-07-21-dotnet-skills-review.md`: `dotnet-inspect/SKILL.md`
carried two nearly identical question→command lists with literal duplicate
lines (I-1), an overloaded `-m` flag plus three spellings for "first N lines"
with no canonical form (I-2), and 2,043 words fully inline with no
`references/` split (I-3).

## Method

**Note on method:** the subagent probes used for all other findings in
`skills/dotnet/tests/` were blocked twice by the permission classifier in this
session. Since the I-1/I-2 defects are mechanical facts (duplicate counts,
flag spellings) and I-3 is a structural property, RED and Verify were performed
with static grep/wc checks instead — objective and re-runnable.

## RED — Baseline (old SKILL.md), 2026-07-22

Captured via grep before the change:

- `"Where is the source code?"` — **2** occurrences (both inside "When to
  Use", lines 40 and 46 of the old file).
- `Default (output|format) is **markdown**` — **2** occurrences, back to back
  in "Key Patterns".
- Two parallel list sections ("Quick Decision Tree" + "When to Use This
  Skill") covering substantially the same question→command mappings.
- `-m N` documented as numeric item limit (line 209) alongside `-m <Name>` as
  member filter; `-5` shorthand used in an example (line 201); three head
  spellings (`-n N`, `--head N`, `-N`) with none designated canonical.
- 2,043 words, no `references/` directory.

## GREEN — Restructure, 2026-07-22

- `SKILL.md` rewritten (641 words): ONE merged "When to Use / Decision Tree"
  list (all unique entries from both old lists preserved, duplicates
  collapsed), markdown-default stated once, Key Patterns/Key
  Syntax/Installation retained, pointer to the new reference. Frontmatter
  description (C-1 state) and Related Skills (C-7 state) untouched.
- New `references/command-reference.md` (1,135 words) holds the moved
  material: command table, version resolution, platform diffs & release
  notes (incl. NU1213 workaround), structured queries, mermaid, search
  scopes, filtering/limiting.
- I-2 canonicalization: examples use only `--head N`/`--tail N` for line
  limits and `-m <Name>` for member filtering; the aliases (`-n N`, `-N`) are
  a one-liner in the reference, and the `-m` numeric/name overload carries an
  explicit disambiguation warning ("use `-m` only for member filtering and
  `--head N` for output limiting").

## Verify — 2026-07-22

Static checks on the new files:

- Duplicates gone: `"Where is the source code?"` ×1, markdown-default ×1,
  list sections ×1.
- No example line uses numeric `-m` or the `-5` shorthand; `--head N` is the
  canonical form in Key Syntax.
- Content preservation: spot-checks for nine distinctive tokens spanning all
  moved sections (`docker pull`, `NU1213`, `--effective`, `graph TD`,
  `--aspnetcore`, `--show-index`, `feeling-lucky`, `--preview`, `--verify`)
  each land in exactly one of the two files; all 11 commands of the old
  Command Reference table are present in the new reference.
- Word counts: SKILL.md 641 (target ≤ ~650), reference 1,135; the ~270-word
  total reduction is the removed duplication.

## Result

One list instead of two, canonical flag forms in every example, and a proper
SKILL.md/reference split per writing-skills' heavy-reference rule. Re-run
these checks (duplicate counts, example-flag grep, token spot-checks)
whenever either file changes; run the retrieval-equivalence probe from the
plan if subagent dispatch is available again.
