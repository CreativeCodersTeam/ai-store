# Options-Pattern Consistency Test (Finding C-5)

Test artifact per `superpowers:writing-skills` (RED → GREEN → Verify) for the
2026-07-22 fix of Finding C-5 in
`docs/reviews/2026-07-21-dotnet-skills-review.md`: `dotnet-fundamentals`
mandates immutable options (`required`/`init`) with `ValidateOnStart()`, while
`dotnet-sdk-builder/references/di-patterns.md` emitted mutable options with
validation merely "Optional but Recommended" and no `ValidateOnStart()`
anywhere — a pattern the `dotnet-reviewer` architecture checklist explicitly
flags ("register `IOptions<T>` without `ValidateOnStart()`").

## Method

A fresh general-purpose subagent receives the three sources verbatim (no file
access) and answers: (a) would the reviewer hook flag SDK code generated
exactly per the builder reference; (b) are the sources consistent; (c) which
options style applies to a new SDK options class, and is the reason stated or
guessed?

## RED — Baseline (old texts), 2026-07-22

All three failures confirmed, verbatim:

- (a) "**Yes, the reviewer hook flags it** … code generated exactly per
  SOURCE 2 deterministically fails the SOURCE 3 check."
- (b) Three contradictions named, including the mechanical one: the
  `Configure(Action<T>)` overload "cannot compile against `init`-only setters,
  so the two styles are not just stylistically but mechanically incompatible" —
  and "a generator and reviewer drawn from the same skill collection are
  guaranteed to disagree."
- (c) "the justification is guessed, not stated. A consumer of these skills
  has no textual way to know whether SOURCE 2 is a deliberate exception or
  simply out of sync with SOURCE 1."

## GREEN — Changes (di-patterns.md only), 2026-07-22

1. Deviation note added to the Options Class rules: mutable `get; set;` is a
   documented, justified exception to `dotnet-fundamentals` (the
   `Action<TOptions>` configure lambda cannot satisfy `required` members or
   assign through `init` setters); fail-fast is preserved via validator +
   `ValidateOnStart()`.
2. `services.AddSingleton<IValidateOptions<…>>` + `AddOptions<…>().ValidateOnStart()`
   added to the canonical `AddXxxCore()` pattern AND the basic pattern, with a
   note that `services.Configure(...)` composes with `AddOptions<T>()` on the
   same default-named instance.
3. "Options Validation (Optional but Recommended)" → "Options Validation
   (Standard)"; every generated SDK ships the validator, registration is part
   of the canonical pattern, "do not treat it as an add-on."

`dotnet-fundamentals` and the reviewer checklist are intentionally unchanged.

## Verify — New texts, 2026-07-22

- (a) "**No, the reviewer hook would not flag it** … the third trigger is
  satisfied by construction", including the closed loophole for the public
  overloads.
- (b) "**Yes, the three sources are now consistent, with one explicitly
  acknowledged and justified deviation**" — fail-fast preserved via substitute
  mechanism, immutability consciously traded and acknowledged as such.
- (c) "the reason is stated, no guessing required."

## Result

Generator, fundamentals, and reviewer no longer disagree; the deviation is
self-documenting. No REFACTOR round needed. Re-run this probe whenever the
options guidance in `dotnet-fundamentals`, `di-patterns.md`, or the reviewer's
DI hook changes.
