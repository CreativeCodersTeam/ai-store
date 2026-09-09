# XML-Docs Langword & Canonical Example Test (Findings X-1, X-2)

Test artifact per `superpowers:writing-skills` (RED → GREEN → Verify) for the
2026-07-22 fix of Findings X-1/X-2 in
`docs/reviews/2026-07-21-dotnet-skills-review.md`: `dotnet-xmldocs` recommended
`<see langword>` for type keywords like `int`/`bool` (X-1), and contained no
complete worked example anywhere (X-2).

## Method

A fresh general-purpose subagent (a) marks up a sentence containing `int` per
the guidance and checks it against real Microsoft convention, and (b) fully
documents a Try-pattern method using only the skill text, listing every point
of uncertainty/interpolation.

## RED — Baseline (old texts), 2026-07-22

- X-1: Following the text yields `<see langword="int" />` — "This is wrong"
  per Microsoft convention (type keywords link via `cref` to their BCL types;
  langword is for unlinkable keywords like `null`/`true`/`false`). The rule was
  also internally incoherent: "bullets 1 and 3 give contradictory instructions
  for the same token, and the 'etc.' makes the boundary of the contradiction
  unknowable."
- X-2: **Nine** documented uncertainties in producing a doc block from the
  prose rules alone (summary wording entirely uncovered; formula-vs-noun-phrase
  precedence conflict; out-param failure value; exception paramref usage;
  punctuation/tag style; …). Verdict: "The skill's rules describe the
  Microsoft house style accurately enough to *recognize* correct output but
  not precisely enough to *generate* it without interpolation." Bonus finding
  (#5): the skill's out-param formula said "treated as uninitialized" where
  real Microsoft docs say "**passed** uninitialized."

## GREEN — Fixes, 2026-07-22

- X-1 (`SKILL.md`): langword bullet split — langword only for keywords with no
  type to link to (`null`, `true`, `false`, modifiers); type keywords
  (`int`, `bool`, `string`, `decimal`) explicitly routed to `<see cref>` with
  the `System.Int32` resolution rationale. Member-rules pointer now announces
  the canonical example.
- X-2 (`member-documentation-rules.md`): new "Canonical Example" section — a
  TryParse-shaped method (per the baseline's own recommendation) exercising
  summary, Boolean param, out param with failure value, Boolean return,
  exception with `<paramref>` + `<see langword="null" />`, and
  `<example>`/`<code language="csharp">`; prefixed with an explicit precedence
  note (specific formulas override the general noun-phrase/article rules).
  The "treated as uninitialized" wording corrected to Microsoft's verbatim
  "passed uninitialized."

## Verify — 2026-07-22

- (a) `int` now → `<see cref="int" />`; "the rule is now coherent … matches
  actual Microsoft convention."
- (b) A NEW Try-pattern method (`TryReadHeader`) was documented in clean
  Microsoft style; all five prose-only uncertainty classes "resolved" by the
  example (summary template, precedence, failure-value clause, exception
  markup, punctuation/tag style). Remaining open points are genuine
  judgment-call variance (side-effect mention in summaries, optional cref in
  summary prose, optionality of `<example>`), accepted as depth trade-offs per
  writing-skills' one-excellent-example principle.
- (c) "This parameter is passed uninitialized." confirmed as "verbatim
  Microsoft wording" (Int32.TryParse, DateTime.TryParse, TryGetValue, …).

## Result

The langword/cref boundary is correct and coherent; the skill can now
*generate* Microsoft-style docs, not just recognize them. No REFACTOR round
needed. Re-run this probe whenever the langword guidance or the canonical
example changes.
