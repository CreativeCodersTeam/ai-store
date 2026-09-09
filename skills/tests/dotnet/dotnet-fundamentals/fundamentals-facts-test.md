# Fundamentals Facts & Trigger Test (Findings F-1–F-4)

Test artifact per `superpowers:writing-skills` (RED → GREEN → REFACTOR → Verify)
for the 2026-07-22 fix of Findings F-1 through F-4 in
`docs/reviews/2026-07-21-dotnet-skills-review.md`, all in
`skills/dotnet/dotnet-fundamentals/`: a catch-all "When to Use" trigger (F-1),
a factually inverted configuration-precedence sentence (F-2), and two
non-compiling code examples (F-3 duplicate constructor, F-4 wrong
`HostApplicationBuilder` API plus a wrong scope-validation claim).

## Method

Reference skills are tested by retrieval: a fresh general-purpose subagent
receives the four passages verbatim and answers (1) config precedence strictly
from the text, (2)/(3) compilability and claim accuracy, (4) whether the first
trigger bullet discriminates.

## RED — Baseline (old texts), 2026-07-22

All four confirmed, partly sharper than the report:

- (1) F-2: "The text contradicts itself … gives conflicting guidance and no
  resolution" — "later sources override earlier ones" vs. "the first source
  that supplies a key wins."
- (2) F-3: does not compile — **CS0111** (duplicate constructor signature) and
  additionally **CS8862** (extra constructor must chain `: this(...)`).
- (3) F-4: does not compile — `HostApplicationBuilder` has no
  `ConfigureContainer<T>(Action<HostBuilderContext,T>)` overload, and its
  `ConfigureContainer` returns `void`, so chaining `.Build()` fails too. The
  scope-validation claim was "inaccurate as stated for the very API the snippet
  uses" — `Host.CreateApplicationBuilder` also validates by default in
  Development.
- (4) F-1: "provides no discriminating criterion … the more specific bullets
  below … become dead weight."

## GREEN — Fixes, 2026-07-22

- F-1 `SKILL.md`: catch-all bullet replaced with an explicit baseline-role
  statement naming the skills that build on it.
- F-2 `configuration.md`: "first source … wins" → "**last** source … wins."
- F-3 `options-pattern.md`: duplicate-constructor example replaced with a
  compiling version that also demonstrates `CurrentValue` + `OnChange`.
- F-4 `dependency-injection.md`: snippet rewritten to
  `builder.Services.AddScoped(...)` on `Host.CreateApplicationBuilder(args)`;
  scope-validation sentence corrected (default-on in Development for both host
  types; explicit opt-in only for bare `new HostBuilder()` / custom factories).

## Verify + REFACTOR — 2026-07-22

Re-probe with the new texts: (1) unambiguous "env var wins", text internally
consistent; (2) compiles (residual notes — undisposed `OnChange` subscription,
unsynchronized field write — are latent-quality remarks, not errors); (3)
compiles, claim "accurate"; (4) "it now communicates a defined role."

The verifier flagged one loading-semantics ambiguity in the new F-1 bullet
("in addition to or instead of"). REFACTOR: appended "so load this skill
alongside them, not instead of them." Verifier follow-up: "Yes, this resolves
it … the specialized skills supplement rather than supersede the baseline."
The "production code" scoping was confirmed intentional (test code is governed
by `dotnet-tester`).

## Result

All four findings fixed and verified; one REFACTOR round on F-1. Re-run this
probe whenever the affected passages in `dotnet-fundamentals` change.
