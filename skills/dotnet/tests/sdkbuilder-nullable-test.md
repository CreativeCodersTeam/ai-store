# SDK-Builder Nullable Instruction Test (Finding S-1)

Test artifact per `superpowers:writing-skills` (RED → GREEN → REFACTOR → Verify)
for the 2026-07-22 fix of Finding S-1 in
`docs/reviews/2026-07-21-dotnet-skills-review.md`: `dotnet-sdk-builder/SKILL.md`
Step 2 item 5 instructed "add `#pragma warning disable CS8600` /
`#nullable enable` per source file" — the pragma *disables* a nullable warning
(the opposite of enabling NRT), contradicting the skill's own
`references/project-setup.md`; and "based on version" promised a version
criterion that was never stated.

## Method

A fresh general-purpose subagent receives Step 2 item 5 and the
"Nullable in Existing Projects" section of `project-setup.md` verbatim and
answers: (a) what the pragma technically does, (b) the exact file header per
each excerpt and their consistency, (c) whether a version criterion exists.

## RED — Baseline (old text), 2026-07-22

All three defects confirmed, verbatim:

- (a) The pragma "does the opposite of the intent: it hides one of the
  warnings the feature exists to produce."
- (b) Following SKILL.md literally produces a file with the pragma AND
  `#nullable enable` — "a false sense of a 'nullable-enabled' file that is
  actually blind to one whole class of nullability defect." Inconsistent with
  the reference (which prescribes only `#nullable enable`).
- (c) "No actual version criterion is given" — the "based on version" heading
  supplies a project-state condition, not a version.

## GREEN — New text, 2026-07-22

Item 5 aligned with the reference: new project → `<Nullable>enable</Nullable>`
via the template; existing project with nullable disabled → `#nullable enable`
per **new** file only, project setting untouched, plus the explicit
prohibition "never suppress nullable warnings with `#pragma warning disable`
— fix them." `project-setup.md` unchanged (it was already correct).

## Verify + REFACTOR — 2026-07-22

Re-probe: (a) file headers identical per both excerpts (`#nullable enable`),
"They are consistent"; (b) "There is no reading under which suppressing CS8600
with a pragma is compliant"; (c) no direct contradiction remaining. The
verifier flagged one residual imprecision — "every supported target version
has NRT support" holds only if pre-C#-8 targets are out of scope. REFACTOR:
parenthetical replaced with the verifier's own precise fact — "available since
C# 8 / .NET Core 3.0 — every target this skill generates for."

## Result

The inverted pragma instruction is gone, SKILL.md and reference agree, the
suppress prohibition is explicit, and the version claim is now a stated fact
instead of an unfulfilled criterion. Re-run this probe whenever Step 2 item 5
or `project-setup.md`'s nullable section changes.
