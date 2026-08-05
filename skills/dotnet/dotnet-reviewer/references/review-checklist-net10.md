# Review Checklist — .NET 10

Apply when the highest major resolved in Step 2 is **≥ 10** — either `net10.0` itself, or a newer
target for which no dedicated checklist exists yet (see the selection rule in Step 6.1 of
`SKILL.md`). Below major 10 this file does not apply; the general checklists carry the review.

## Language Idioms

- **Primary constructors** — parameters only stored and used → primary constructor, no mirror fields; `readonly` guarantee or guard clause needed → assignment to a `private readonly` field or classic ctor, per project style; multiple constructors or construction logic → classic ctor (rule home: `dotnet-fundamentals`, `references/modern-patterns.md`). Flag: `ctor + private readonly field` in new code without readonly/guard justification or multiple constructors; a parameter both assigned to a field and used directly (double capture).
- **Collection expressions** — `[1, 2, 3]` over `new[] { 1, 2, 3 }` and `new List<int> { 1, 2, 3 }`. Flag: verbose collection initialization.
- **Required members** — `required` modifier replaces hand-rolled validation in constructors. Flag: throws in constructor for missing init-only properties.
- **`field` keyword** — auto-property backing-field access (preview in 9, stable in 10). Flag: unnecessary backing field declarations.
- **Pattern matching** — list patterns, relational patterns. Flag: chained `if (x.Length > 0 && x[0] == …)`.
- **`init` and `required` together** — for immutable POCOs.

## API Idioms

- `System.Threading.Lock` (new lock type) over `object`-based `lock` for new code.
- `Random.Shared` for non-cryptographic randomness — never `new Random()` in hot path.
- `TimeProvider` for testable time — flag direct `DateTime.UtcNow` in code that should be testable.
- `JsonSerializerContext` (source-gen) over reflection-based `JsonSerializer` on hot paths.

## Project Configuration

- `<Nullable>enable</Nullable>` MUST be on. Flag projects without it.
- `<TreatWarningsAsErrors>true</TreatWarningsAsErrors>` recommended for libraries.
- `<LangVersion>` should not be pinned below the SDK's default unless a comment explains why.
- `ImplicitUsings` enabled — flag stale top-of-file using directives that are already implicit.

## Non-version-specific checks

For language- and runtime-neutral pitfalls (`.Result`/`.Wait()`, `async void`, allocation hot spots, etc.) see `review-checklist-performance.md` and `review-checklist-code-quality.md`. This file covers only what is specific to .NET 10.
