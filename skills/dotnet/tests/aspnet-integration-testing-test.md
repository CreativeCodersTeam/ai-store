# ASP.NET Core Integration-Testing Gap Test (Finding H-5)

Test artifact per `superpowers:writing-skills` (RED → GREEN → Verify) for the
2026-08-05 fix of Finding H-5 in
`docs/analysis/2026-08-02-dotnet-skills-review.md`: the most common ASP.NET
Core test type — in-memory integration tests via `WebApplicationFactory` /
`Microsoft.AspNetCore.Mvc.Testing` — was covered by no skill. `dotnet-tester`
excluded integration tests, `dotnet-aspnet` said nothing about testing, while
`dotnet-sdk-builder` and `dotnet-ef-core` both *delegated* "unit and
integration tests" to `dotnet-tester` — a standing contradiction.

## Design (agreed with the user, 2026-08-05)

Hybrid, following the ef-core precedent (domain skill owns its testing
knowledge): new `dotnet-aspnet/references/testing.md` holds the domain
patterns; `dotnet-tester` (workflow) declares in-process integration tests in
scope and binds to that reference. Scope: WebApplicationFactory core, auth
stubbing, EF combination (hook to `dotnet-ef-core/references/testing.md`),
external-HTTP stubbing. Aligned hooks: `dotnet` router row, `dotnet-tester`
description + When-to-Use, `dotnet-aspnet` SKILL.md (When-to-Use, Reference
Index, Related Skills), ef-core `testing.md` back-hook.

## RED — Baseline evidence, 2026-08-05

`grep -rn -i "WebApplicationFactory\|Mvc.Testing" skills/dotnet --include="*.md"`
→ **zero hits** before the fix. `dotnet-tester/SKILL.md:3` excluded
"integration tests that only exercise external systems" while
`dotnet-sdk-builder/SKILL.md:113` and `dotnet-ef-core/SKILL.md:48` delegated
integration tests to it.

## GREEN — Retrieval probe, 2026-08-05

Fresh subagent, `dotnet-aspnet/references/testing.md` only, no other files:
all five retrieval questions (partial-Program trick, service override + why it
wins, auth faking with live policies + 401 path, DB swap + ownership,
external-HTTP stubbing) answered from the text with citations; explain-vs-
assert verdict "mostly explains". Accuracy pass: "no factual defects found"
on all challenged points (ConfigureTestServices ordering, partial Program,
.NET 8+ AuthenticationHandler ctor, RemoveAll namespace, client options,
IClassFixture lifetime, ConfigurePrimaryHttpMessageHandler). Four probe
remarks were applied: the EF Core 9+ trap (must remove
`IDbContextOptionsConfiguration<TContext>` alongside `DbContextOptions<T>`,
else "multiple database providers registered"), the pinned-scheme caveat for
the test auth default, `NoResult()` preferred for offline 401 tests, and a
tightened "registrations win" phrasing.

## Verify — Full eval loop (skill-creator), 2026-08-05

Three realistic tasks against a compiling .NET 10 fixture API (auth-protected
POST, EF-backed GETs, endpoint calling an external typed client), each run by
a fresh subagent twice: with the new reference vs. a pre-fix skill snapshot.
All six runs ended `dotnet test` green — the reference's value showed in
*how*: assertions 17/17 (100%) with skill vs. 15/17 (88.9%) baseline, mean
wall-clock 208.6s vs. 272.9s (~24% faster), tokens comparable.

- Auth (discriminates most): with skill, the prescribed test scheme — 4
  focused tests. Baseline kept the real JWT pipeline and minted self-signed
  HS256 tokens via `PostConfigure` — worked, but ~2× slower and partly
  testing the framework instead of the endpoint.
- EF: with skill green on first run incl. the EF9 double-removal. Baseline's
  invented shared-cache approach hit a mid-run concurrency flaw (500s under
  parallel load) and needed a factory rework.
- External dependency: non-discriminating (both found the interface seam) —
  make the seam less obvious if this eval should carry signal later.

User review of all outputs (eval viewer, 2026-08-05): no complaints.

Re-run the retrieval probe when `testing.md`, the `dotnet-tester` scope, or
the EF Core / Mvc.Testing swap mechanics change (new EF/.NET major version).
