# Fundamentals ConfigureAwait & Options-Deviation Cross-Ref Test (Findings M-2, M-3)

Test artifact per `superpowers:writing-skills` (RED → GREEN → REFACTOR) for the
2026-08-02 fix of Findings M-2 and M-3 in
`docs/analysis/2026-08-02-dotnet-skills-review.md`:

- **M-2:** the `ConfigureAwait(false)` rule existed in three scattered,
  slightly divergent phrasings (`dotnet-dev/references/REFERENCE.md` — "in
  library code (not in tests)"; `dotnet-sdk-builder/references/http-client-patterns.md`
  — "on all awaits", no rationale; `dotnet-reviewer/references/review-checklist-performance.md`)
  but was absent from its natural home,
  `dotnet-fundamentals/references/modern-patterns.md`, where the other async
  idioms (CancellationToken, `OperationCanceledException`) live.
- **M-3:** the `AddXxx` library-registration pattern exists in both
  `dotnet-fundamentals/references/dependency-injection.md`
  (`BindConfiguration` + `ValidateDataAnnotations`, `required`/`init` options)
  and `dotnet-sdk-builder/references/di-patterns.md` (`Configure` +
  `IValidateOptions<T>`, mutable options) — the deliberate deviation was
  documented only on the sdk-builder side.

## Method

Single-sourcing per the C-7 pattern: rule + rationale moved into fundamentals,
the scattered sites reduced to context hooks referencing it; the deviation
note mirrored into fundamentals. Verified by a fresh subagent (no file access)
that (1) answers the ConfigureAwait rule strictly from the new section,
(2) accuracy-checks its claims, (3) accuracy-checks the new deviation note's
C# semantics, (4) compares it against the sdk-builder deviation text for
contradictions.

## RED — Baseline, 2026-08-02

Grep evidence: zero `ConfigureAwait` occurrences in
`dotnet-fundamentals/references/modern-patterns.md` — the rule was not
findable at its designated home. The three scattered phrasings disagreed on
the exclusion ("not in tests" vs. "not application code"). On the M-3 side,
`dependency-injection.md` presented `required`/`init` + `BindConfiguration`
as the only pattern, with no pointer to the sdk-builder deviation.

## GREEN — Fixes, 2026-08-02

- `modern-patterns.md`: new **`ConfigureAwait(false)`** section — rule
  (library code yes, application/test code no), code example, both rationales
  (SynchronizationContext capture / sync-over-async deadlock; ASP.NET Core and
  Generic Host have no context to capture), consistency caveat.
- The three scattered sites now state the same rule and reference
  `dotnet-fundamentals` (modern-patterns.md); the REFERENCE.md "(not in
  tests)" shorthand corrected to "in library code only".
- `dependency-injection.md`: deviation note added after the Library Extension
  Method Pattern, mirroring the sdk-builder text.

Probe results: rule "fully answerable from the passage, including both
rationales"; accuracy "no material errors found" (noted nuances:
`TaskScheduler.Current` capture also suppressed; some test frameworks install
a `SynchronizationContext` — the "tests count as application code"
simplification "matches accepted Microsoft/community guidance"); deviation
texts "describe the same deviation compatibly from both sides, with no
contradiction", cross-references "line up correctly".

## REFACTOR — 2026-08-02

The probe flagged one looseness in the new deviation note: lumping
`BindConfiguration` under "do not fit (a configure delegate cannot satisfy
`required` members …)" misattributes the reason — the modern
`ConfigurationBinder` *can* set `init`/`required` members; `BindConfiguration`
merely stops applying because the delegate replaces it as the configuration
source. Note reworded accordingly ("…and the delegate replaces
`BindConfiguration` as the configuration source"), adopting the verifier's
framing verbatim in substance; no further round needed.

## Result

M-2 and M-3 fixed; one REFACTOR round (BindConfiguration attribution).
Consistency grep confirms every rule mention under `skills/dotnet/` now states
the same library-code rule and points to fundamentals. Re-run this probe
whenever the ConfigureAwait section or either deviation note changes.

---

## Amendment 2026-08-02 — GUI apps (user feedback)

The initial section's binary split (library → yes; application → no) omitted
GUI application code. User feedback: WPF, MAUI, and Avalonia install a
`SynchronizationContext`, so `ConfigureAwait(false)` is needed there too — a
real gap, since MAUI is explicitly in the skill description's scope.

**Change:** the rule sentence now names three categories (library ·
server/headless application · GUI application), and a new bullet **"GUI apps
sit in between"** carries the differentiated rule: WPF, WinForms, MAUI, and
Avalonia install a `SynchronizationContext` on the UI thread — use
`ConfigureAwait(false)` on every `await` whose continuation does not touch the
UI; omit it where code after the `await` updates controls or view state (that
continuation must resume on the UI thread); the same captured context is why
`.Result`/`.Wait()` on the UI thread deadlocks. Hooks aligned: the
`dotnet-dev` REFERENCE hook now defers to the fundamentals rule instead of
restating a two-way shorthand; the reviewer performance checklist carries the
GUI differentiation ("also on awaits whose continuation does not touch the
UI"). The sdk-builder hook is unchanged (SDK clients are library code).

**Re-probe (per this artifact's own re-run rule):** fresh subagent, section
text only. Both scenario questions decidable from the text (button-click
handler updating `Label.Text` → omit; I/O-only helper → use); framework claims
verified correct per framework (WPF `DispatcherSynchronizationContext`,
WinForms `WindowsFormsSynchronizationContext`, MAUI via the platform's
main-thread context, Avalonia `AvaloniaSynchronizationContext`); "no wrong
claims found." Two nuances noted as non-errors and accepted as written
(early `ConfigureAwait(false)` moves later code off the UI thread — implicitly
covered by the "code after the await" phrasing; xUnit v2's historical
`SynchronizationContext`, removed in v3, makes the blanket "tests" exemption
slightly loose). No REFACTOR round needed.
