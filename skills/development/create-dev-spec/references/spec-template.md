# Specification Template

Used for both the draft (`docs/draft/spec_<slug>.md`) and the final spec
(`docs/specs/<slug>.md`). The draft adds a status header at the top and a *Review Notes*
section at the end; the spec has neither. Every other section appears in both, in this
order, always. A section with no content reads `n/a — <reason>`; the reason is part of the
document because "not applicable" is itself a decision the reader wants to see.

Write the document in the language decided at interview item `L-1`. Headings are translated
too; the structure stays.

---

```markdown
<!-- Draft only: -->
> **Status:** DRAFT — awaiting review
> **Date:** YYYY-MM-DD
> **Source:** <ticket / message / file the requirement came from>

# <Title — the requirement in one line>

## 1. Summary

Three to five sentences: what is being built or changed, for whom, and why now. A reader
who stops here should know whether this document concerns them.

## 2. Goals / Non-Goals

**Goals** — bullet list of what must be true when this is done. Each goal is checkable.

**Non-Goals** — bullet list of things a reader might reasonably expect this to cover and it
deliberately does not. Non-goals are where scope creep is refused in writing.

## 3. Context

What exists today that this builds on or replaces: current behavior, affected components,
relevant constraints (contracts, regulations, platform limits), and the terms the rest of
the document uses. Link to code, tickets, or docs rather than restating them.

## 4. Functional Requirements

Numbered `FR-1`, `FR-2`, … Each requirement is one testable statement in the form "the
system shall …" or "when X, the system does Y". Group under sub-headings if there are more
than ~8. Include business rules, validation, permissions, and error behavior here — not in
prose paragraphs elsewhere.

## 5. Non-Functional Requirements

Numbered `NFR-1`, … Performance, scale, availability, security, privacy, accessibility,
observability, compatibility. Each with a measurable target where one exists ("p95 under
300 ms at 50 req/s") or an explicit "no target — best effort" where the user decided so.

## 6. Design / Data / API

The shape of the solution as far as the interview settled it: data model changes, API
contracts (endpoints, payloads, status codes), UI flows, integration points, background
jobs. Diagrams as text (Mermaid or ASCII). This section describes *what* the interfaces
are, not *how* the code is organized — implementation detail belongs to the implementer.

## 7. Acceptance Criteria

Numbered `AC-1`, … Concrete scenarios that, when all pass, mean the goals are met. Prefer
Given / When / Then. Every functional requirement should be reachable from at least one
acceptance criterion; every criterion should name the requirement(s) it verifies.

## 8. Open Questions

Only questions the user consciously deferred. Each with: the question, why it can wait,
who decides or what event triggers the decision. An open question with no owner and no
trigger is not open — it is unresolved, and belongs back in the interview.

## 9. Out of Scope

Related work that was identified and explicitly excluded from this specification, one line
each with the reason (later phase, separate ticket, not worth it). Distinct from Non-Goals:
Non-Goals say what this feature is *not*; Out of Scope says what adjacent work is *deferred*.

## 10. Decisions Log

The interview record, verbatim from the running log:

| ID | Question | Decision | Rationale | Origin |
|---|---|---|---|---|
| L-1 | Document language | … | … | proposal / user's own / draft edit |
| L-2 | Slug | … | … | … |
| Q-1 | … | … | … | … |
| I-1 | … | … | … | … |

Rejected ideas stay in the log with their rejection — a reader who has the same idea later
finds out in one line why it was not done.

<!-- Draft only: -->
## Review Notes

- Points I am unsure about: …
- Ideas rejected during the interview (so they are not re-proposed): …
- Sections filled thinly, and why: …
```
