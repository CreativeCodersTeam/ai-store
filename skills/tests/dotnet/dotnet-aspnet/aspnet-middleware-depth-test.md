# ASP.NET Middleware Canonical-Depth Test (Finding M-1)

Test artifact per `superpowers:writing-skills` (RED → GREEN → REFACTOR → Verify)
for the 2026-08-02 fix of Finding M-1 in
`docs/analysis/2026-08-02-dotnet-skills-review.md`:
`dotnet-aspnet/references/middleware.md` is declared the single canonical
pipeline ordering by `SKILL.md` ("never order the pipeline from memory"), but
the 38-line file named neither `UseRouting`/`UseStaticFiles` nor
OpenAPI/health-endpoint mapping, gave no placement rule for custom middleware,
and justified nothing — an agent bound to the canonical source had to fill the
gaps from memory anyway.

Relationship to `aspnet-middleware-order-test.md` (A-3): that fix made
`middleware.md` the *only* place holding a sequence (SKILL.md carries none).
This fix expands only `middleware.md`; SKILL.md is untouched, so the A-3
single-sourcing invariant holds and its probe needed no re-run.

## Method

Reference docs are tested by retrieval: a fresh general-purpose subagent
receives the document verbatim (no file access, no tools, "do not fill gaps
from your own knowledge") and answers: (a) where does `UseStaticFiles` belong
and why; (b) why is `UseCors` before `UseAuthentication`; (c) rate limiter
before or after auth, and when would you deviate; (d) where does the shown
`RequestTimingMiddleware` register, per which rule; (e) does the document
explain or merely assert its ordering. The GREEN probe additionally asks (f)
to flag factually wrong claims.

## RED — Baseline (old 38-line file), 2026-08-02

(a), (b), (d) — **not answerable from the text**; (c) only half (position
visible, no deviation criteria); (e) verbatim:

> The document merely asserts its ordering: it states "Order matters" and
> lists a fixed sequence, but explains no ordering relationship between any
> two middlewares. An agent forbidden from ordering the pipeline from memory
> could not handle a project serving static files or hosting OpenAPI
> endpoints — neither `UseStaticFiles` nor any OpenAPI/Swagger middleware …
> appears in the sequence.

## GREEN — Rewrite, 2026-08-02

`middleware.md` rewritten: complete annotated canonical order
(ExceptionHandler → StatusCodePages → HSTS/HTTPS → optional Compression →
StaticFiles → Routing → CORS → AuthN → AuthZ → RateLimiter → OutputCache →
custom slot → `Map…` endpoints), a "Why this order" rationale per decision, an
explicit "Rate limiter vs. auth" trade-off section, and a placement rule for
custom middleware ("after the last middleware whose output it needs, before
the first middleware that must observe its effect"). Configuration stays
delegated to the other references (verified by grep: no `Add…` configuration
in the file).

Probe result: (a)–(d) answered from the text with rationale and citations;
(e): "It explains: every position in the numbered listing has a corresponding
rationale … An agent … could handle static files … and OpenAPI endpoints."

## REFACTOR — 2026-08-02

The GREEN verifier's accuracy pass (f) flagged the CORS rationale as
misleading: "if auth ran first it would reject the preflight" —
`UseAuthentication` does not reject requests; the real mechanism is that the
CORS middleware must answer the preflight itself before it falls through to a
response without CORS headers. Bullet rewritten accordingly.

## Verify — 2026-08-02

Verifier follow-up on the revised bullet: "the revision now attributes the
behavior to the correct mechanism … That resolves my objection." One residual
imprecision ("matches no endpoint … (a 404…)" — endpoint routing commonly
yields a 405 via the HTTP-method fallback) was folded in: the bullet now says
"commonly a 405 or 404, or an auth challenge" and no longer asserts the
preflight matches no endpoint. Remaining verifier notes (server last-chance
500 behind the exception handler; parameterless `UseExceptionHandler()`
requiring registered handlers) were judged acceptable as written — the latter
is explicitly delegated to `error-handling.md`.

## Result

M-1 fixed and verified; one REFACTOR round (CORS mechanism) plus one wording
polish (405/404). Re-run this probe whenever the pipeline ordering or its
rationale in `middleware.md` changes.
