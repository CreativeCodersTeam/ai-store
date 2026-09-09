# Fundamentals Primary-Constructors Depth Test (Finding H-3)

Test artifact per `superpowers:writing-skills` (RED → GREEN → REFACTOR → Verify)
for the 2026-08-05 fix of Finding H-3 in
`docs/analysis/2026-08-02-dotnet-skills-review.md`: the "Primary Constructors"
section of `dotnet-fundamentals/references/modern-patterns.md` consisted of a
single bullet covering only the middleware special case (duplicating
`dotnet-aspnet/references/middleware.md`), while the skill's frontmatter
description advertises primary constructors and the reviewer checklist
(`review-checklist-net10.md`) flags the legacy `ctor + private readonly field`
style — with no knowledge base behind either.

Scope of the fix, beyond filling the stub: the **decision basis was
sharpened** — explicit decision rules (primary constructor vs. `readonly`
field assignment vs. classic constructor) replace the previous vague
preference, and the reviewer-checklist bullet was aligned to restate the same
rules with a pointer to the canonical home (single-sourcing convention).

## Method

Reference docs are tested by retrieval: a fresh general-purpose subagent
receives the section verbatim (no file access, no tools, "do not fill gaps
from your own knowledge") and answers: (a) how to inject dependencies into a
DI service via primary constructor; (b) are captured parameters readonly /
what are the capturing semantics; (c) how does a `record` primary constructor
differ from a plain `class` one; (d) when to prefer a classic constructor
with `readonly` fields; (e) does the document explain or merely assert. The
GREEN and Verify probes additionally run an accuracy pass (f): flag every
factually wrong, imprecise, or misleading claim using the prober's own C#
knowledge.

## RED — Baseline (one-bullet stub), 2026-08-05

Baseline content in full (`modern-patterns.md:5-7`):

> ## Primary Constructors (since C# 12)
>
> - For middleware, inject scoped services via `InvokeAsync` parameters, not the primary constructor.

Probe result: (a)–(d) — **not answerable from the text** (verbatim, four
times); (e) verbatim:

> It merely asserts a special case; it does not explain the pattern. […] That
> single bullet is a middleware-specific exception. The baseline it excepts
> from — what primary constructors are, how they are normally used for DI,
> their capture/readonly semantics, record differences, or when to avoid
> them — is absent entirely.

## GREEN — Rewrite, 2026-08-05

Section rewritten: syntax + DI-standard-case example (`OrderService` with
captured `repository`/`logger` used directly), a "Capturing semantics"
subsection (compiler-synthesized unspeakable field, **not `readonly`**,
double-capture trap), a `class`-vs.-`record` contrast, and a "Decision rules"
subsection with three explicit rules (store-and-use → primary ctor, no mirror
fields; readonly/guard needed → `private readonly` field assignment or
classic ctor per project style; multiple ctors / construction logic → classic
ctor) plus the middleware hook now *linking* to
`dotnet-aspnet/references/middleware.md` instead of duplicating it.

Probe result: (a)–(d) answered from the text with citations; (e): "largely
explanatory rather than purely prescriptive".

## REFACTOR — 2026-08-05 (two rounds)

**Round 1** — the GREEN accuracy pass (f) flagged four substantive
imprecisions, all fixed:

1. Heading "since C# 12" ignored that record primary constructors predate
   C# 12.
2. "primary constructors support only one parameter list" overstated the
   restriction (extra ctors are legal, they must chain via `: this(...)`) →
   rule now states the chaining requirement and why it gets awkward.
3. Record bullet attributed value-based equality to the primary constructor
   (it comes from record-ness) and ignored that positional `record struct`
   properties are mutable → both qualified.
4. "in scope throughout the class body" ignored static members → now "in
   scope in instance members, initializers, and the base clause (not in
   static members)"; the `repository = null` example also noted the NRT
   warning nuance.

**Round 2** — a fresh verify probe against the round-1 text confirmed (a)–(d)
retrievable with quotes but found two remaining imprecisions, both fixed:

5. "records since C# 9" still conflated record classes (C# 9) with record
   structs (C# 10) → heading now names both.
6. The double-capture bullet omitted that the compiler warns (CS9124) →
   warning added.

## Verify — 2026-08-05

Final accuracy-only probe against the round-2 text: **"No outright factual
errors."** Its two precision remarks were applied directly: CS9124 fires only
for the field-initializer case, so the bullet now states that body-level
assignments cause the same drift *un-warned*; and "they are just private
captures" was aligned with the capture rule ("a parameter used in member
bodies becomes a private capture"). The probe's residual nitpicks (positional
parameters matching an existing member suppress the synthesized property;
`default(S)` bypassing a struct primary constructor; CS9113 for unread
parameters) are intentional omissions — edge cases beyond a fundamentals
reference, none contradicting the text.

Re-run this probe when the Primary Constructors section, the reviewer
checklist bullet (Language Idioms), or the C# language rules for primary
constructors change (new C# version).

## Single-sourcing check — 2026-08-05

`grep -rn -i "primary constructor" skills --include="*.md"`: canonical home is
`dotnet-fundamentals/references/modern-patterns.md`; the middleware special
case stays canonical in `dotnet-aspnet/references/middleware.md` (now linked
from the home, no longer duplicated);
`dotnet-reviewer/references/review-checklist-net10.md:9` restates the decision
rules identically with a "rule home" pointer;
`dotnet-aspnet/references/project-and-endpoints.md:43` carries a one-line hook.
All other hits are mentions (descriptions, reference lists), not rule
restatements.
