# ASP.NET Auth Reference Gap Test (Finding A-1)

Test artifact per `superpowers:writing-skills` (RED → GREEN → Verify) for the
2026-07-22 fix of Finding A-1 in
`docs/reviews/2026-07-21-dotnet-skills-review.md`: `dotnet-aspnet/references/auth.md`
(66 words) did not deliver on the index's promise of "detailed patterns and
code samples" — `OrderOwnerRequirement` was referenced but never defined,
`IAuthorizationHandler` appeared only as a bullet, and `TokenValidationParameters`,
handler registration, and resource evaluation were absent entirely.

## Method

Reference skills are tested by application/gap probing: a fresh general-purpose
subagent receives the complete auth.md verbatim and must implement "users may
only edit their own orders" (`PUT /orders/{id}`) using ONLY the reference,
marking every element it has to invent.

## RED — Baseline (old auth.md), 2026-07-22

Verdict: "The reference is NOT sufficient." Thirteen invented elements,
including every load-bearing piece of the enforcement path: the requirement
type, the `AuthorizationHandler<TRequirement, TResource>` base class and
`HandleRequirementAsync` signature, `context.Succeed`, handler DI registration,
`UseAuthentication`/`UseAuthorization`, and — "**biggest gap**" —
`IAuthorizationService.AuthorizeAsync` itself:

> A developer without that knowledge could register the policy but could not
> enforce it; worse, the reference's attribute-based guidance would tempt them
> into `[Authorize(Policy = "CanEditOrder")]` on the action, which silently
> fails … because no resource is supplied to the handler.

That attribute trap (sharper than the report's finding) was carried into the
fix as an explicit warning.

## GREEN — New auth.md, 2026-07-22

Rewritten (existing correct content preserved): JWT section gains
`TokenValidationParameters` (issuer/audience/lifetime, `ClockSkew` default
note), the middleware calls, the NuGet package pointer, and the OIDC-metadata
note. New "Resource-Based Authorization (IAuthorizationHandler)" section
defines the previously missing `OrderOwnerRequirement`, a complete
`OrderOwnerHandler`, its singleton registration (with the scoped-dependency
exception), the imperative `IAuthorizationService.AuthorizeAsync` evaluation in
a full `PUT` action (load → `NotFound` → authorize → `Forbid`), the explicit
do-NOT-use-the-policy-as-action-attribute warning, and the
`Succeed`-vs-`Fail` semantics rule.

## Verify — 2026-07-22

Same gap probe against the new reference:

> [INVENTED] elements: **none.** … **Summary: the reference is sufficient for
> the auth mechanics of this task.**

Remaining marks were all [DOMAIN] (entity shape, service, DTO, usings) —
explicitly out of scope for an auth reference. One soft observation (OwnerId
string-vs-Guid comparability) was classified as domain modeling, not an auth
gap.

## Result

The reference now delivers what the index promises; the silent-failure
attribute trap is documented. No REFACTOR round needed. Re-run this probe
whenever `auth.md` or the reference index entry in `dotnet-aspnet/SKILL.md`
changes.
