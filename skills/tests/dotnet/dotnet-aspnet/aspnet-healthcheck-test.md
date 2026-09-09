# ASP.NET Health-Check Example Test (Finding A-2)

Test artifact per `superpowers:writing-skills` (RED → GREEN → REFACTOR → Verify)
for the 2026-07-23 fix of Finding A-2 in
`docs/reviews/2026-07-21-dotnet-skills-review.md`: the health-check example in
`dotnet-aspnet/references/openapi-and-cross-cutting.md` mapped `/health` with
ALL checks (incl. NpgSql/Redis) while the bullet labeled it "liveness", and
filtered `/health/ready` on a `ready` tag that no registered check carried.

## Method

This fix was preceded by a dedicated user-requested correctness review of both
the finding and the originally proposed fix (2026-07-23, adversarial subagent
instructed to refute both). That review served as the RED baseline. GREEN
applied the corrected fix; a second adversarial probe verified it; one
REFACTOR round followed.

## RED — Adversarial review of finding + original proposal, 2026-07-23

Finding: claims 1 and 2 CONFIRMED against real ASP.NET Core behavior — default
`Predicate = null` runs all checks; an endpoint whose predicate matches zero
checks does NOT 404 but aggregates an empty `HealthReport` to Healthy: "HTTP
200, body 'Healthy', forever, including during a total DB/Redis outage. The
readiness probe is vacuous." Claim 3 (UIResponseWriter package "not
mentioned") NUANCED/overstated: the package name literally matches the
"`AspNetCore.HealthChecks.*`" wildcard bullet; the stronger unclaimed defect
was the missing `using HealthChecks.UI.Client;`.

Original proposed fix: pattern confirmed correct (`Predicate = _ => false` is
the documented Microsoft liveness pattern) but TWO defects found: the `self`
check became a dead registration (matched by neither endpoint — the same
defect class as claim 2, reintroduced), and applying the code verbatim would
break the surrounding bullet (still naming `/health`) while silently removing
the `/health` endpoint. Caveats: C#-12-only `["ready"]` syntax; unstated
UIResponseWriter trade-off; `Degraded` → 200 worth noting.

## GREEN — Corrected fix applied, 2026-07-23

Registration without the orphaned `self` check; version-proof
`tags: new[] { "ready" }`; `/health/live` with `Predicate = _ => false`
(teaching comments state the why); `/health/ready` with the tag filter;
bullets rewritten in the same change (endpoint names synchronized,
zero-match warning, `Degraded` → 200 note, UIResponseWriter with package AND
using directive).

## Verify + REFACTOR — 2026-07-23

Second adversarial probe: (a) runtime semantics CONFIRMED — DB down ⇒
`/health/live` 200 / `/health/ready` 503 (worst-of aggregation, correct k8s
split); (b) no dead registrations; (c) code/prose consistent; (d) compiles on
all LangVersions in living memory; (e)/(f) `Degraded` claim accurate.

Two defects flagged: the missing
`using Microsoft.AspNetCore.Diagnostics.HealthChecks;` (inconsistent rigor —
the doc named the other required using) — FIXED via REFACTOR, plus two cheap
sharpenings adopted (ResponseWriter placement guidance: readiness/UI endpoint,
"pointless on liveness — its report is empty"; `timeout:` clause for hung
connections). The second flag — `dotnet-nuget-manager` as a dangling
pointer — was a FALSE ALARM: the verifier could not see the skill roster; the
skill exists in this collection (`skills/dotnet/dotnet-nuget-manager/`).
Residual note accepted without change: nothing enforces the `ready` tag on
future checks at compile/startup time; the warning bullet is the mitigation.

## Result

The example now demonstrates the pattern its own bullets prescribe; liveness
and readiness carry correct k8s semantics; every registered check is
evaluated; prose and code agree. Re-run the adversarial probe whenever the
Health Checks section changes.
