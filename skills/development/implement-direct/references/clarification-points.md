# Clarification Points (Phase 2)

A plan would have frozen these eight decisions before implementation. Without a plan they are
open, and an open decision does not stay open — it gets made silently by whoever writes the first
file. This phase makes them visible and gives them to the user, one at a time, with proposals that
come from the codebase rather than from the model's defaults.

## How a point is presented

Every point is one call of the structured question tool, in order 1 → 8. The call contains:

- **The point's name and what it must settle** (the table in `SKILL.md`), in one line.
- **The `G-n` gaps assigned to it** in Phase 1, restated in one line each.
- **2–4 proposals**, the recommended one first and marked "(Recommended)". Each proposal is
  concrete (a name, a path, a shape), and each carries its evidence and its consequence in one
  sentence: *"Vertical slice under `src/orders/export/` — matches the three existing slices
  (`src/orders/list/`, `src/orders/get/`, `src/orders/cancel/`); keeps the router a one-line
  registration."*
- **The free-form escape.** If the tool adds one automatically (Claude Code's does), nothing
  more; otherwise the last option is "Something else — I'll describe it".

The recommendation is yours to make and to justify. A proposal without evidence ("the usual
layered approach") is a default, not a proposal; if you cannot cite a file, say that the codebase
gives no precedent and explain the recommendation from the requirement instead.

Wait for the answer. Record it as `D-n` with origin *recommended accepted* or *user's own*. Then
derive the next point's proposals — an answer may change them: a chosen structure changes the
naming proposals; a chosen error shape changes the API-contract proposals.

## The eight points

### 1. Structure

Target project, package, or module; folder layout for the new files; whether a new project,
package, or module is created. Evidence: the existing tree, the build manifests found in Phase 1,
how the last comparable feature was placed (`git log --diff-filter=A` on a sibling feature helps).

### 2. Architecture

Layering (controller / service / repository, hexagonal, vertical slices, plain modules); where the
boundaries are; dependency wiring and lifetimes where the stack has them (DI containers, module
providers, factory functions); public versus internal surface. Evidence: how the existing modules
are wired, what the entry points look like.

### 3. Naming

Type, function, file, and namespace / module names for the things the task will create; suffix
conventions (`Service`, `Handler`, `Options`, `Async`, `.spec` vs `.test`); test naming. Test
names follow the project's convention with no acceptance-criterion marker in them — the
AC-to-tests table carries that link — so this point settles what the convention *is*, not
whether to override it. Evidence: `.editorconfig`, lint configuration, and three existing names
of the same kind.

### 4. API contracts

Request and response shapes, or function signatures for a non-HTTP change; DTO shape; versioning;
the error shape on the wire (problem details, envelope, plain status); OpenAPI or schema
annotations where the stack has them. Evidence: an existing endpoint or public function of the
same kind, its documented contract.

### 5. Error handling

Exceptions versus result types; validation style and where it happens; which errors are logged at
which level; the edge cases the `AC-n` imply (empty input, missing entity, concurrent change,
timeout). Evidence: the existing error middleware or helpers, how sibling code fails.

### 6. Test strategy

Which test types the tasks will carry (unit, integration, acceptance, contract); what is mocked and
what is real (in-memory store, containerised database, real HTTP server); the test framework and
runner already in use; the coverage expectation. The floor is that every `AC-n` is proven, and a
criterion is rarely proven by a single test — the happy path, the boundary, and the error path
are three. Propose per criterion how many tests it takes and which; that proposal becomes the
AC-to-tests table in Phase 3. Evidence: the test layout and framework from Phase 1, an existing
test of a comparable feature.

### 7. Persistence

The store the change touches — relational, document, key-value, filesystem, message log, or none;
entity or schema shape; migrations yes/no and how they are generated; query style (ORM, query
builder, raw); transaction boundaries. Evidence: the existing data layer, the migration folder,
the ORM configuration. `n/a` only when the scanned change touches no store — say which files were
scanned.

### 8. Dependencies

Packages to add, remove, or upgrade; forbidden packages; version policy (central version
management, lockfile discipline, floor versions); whether a stdlib or in-repo alternative exists.
Evidence: the dependency manifest, a central versions file, the lockfile. `n/a` only when no
dependency changes — and a task that later needs one reopens this point as a follow-up question.

## `n/a` and `pre-answered`

Both replace the *question*, never the *presentation*: the point still appears in its turn, with
its status and reason, so the user can object.

- `n/a — <code-referenced reason>`: the point objectively does not apply. The reason names a file
  or a scan ("no persistence — the change is confined to `src/lib/csv.ts`, a pure function; no
  repository or store is imported").
- `pre-answered — <verbatim quote or precise reference>`: the requirement text, a Point-0 answer,
  or an earlier point's answer decides it. Quote it. "The requirement implies X" is not a quote;
  ask.

At Gate 2 the user's confirmation covers the `n/a` and `pre-answered` entries collectively;
correcting one there reopens exactly that point.

## The follow-up check

After point 8, before Gate 2, re-read the eight answers together:

- Does an answer need something another point did not cover? (Point 7 chose a document store the
  repository does not yet use → point 8 needs the client package → new question on 8.)
- Do two answers contradict? (Point 2 chose vertical slices; point 3 adopted a `Service` suffix
  convention that only the layered modules use.)
- Did an answer invalidate a `pre-answered` or `n/a` status?

If anything surfaced, start round *r+1* at point 1. Points with nothing new are presented as
`settled — D-n` in one line without a question; points with a new question are asked as above,
with the new question stated and the proposals recomputed. Rounds are numbered in the decision
table. A third round is a signal: say so, and ask whether the requirement should be taken to
`create-dev-spec` first — the options are **continue this round (Recommended if the open questions
are few and concrete)**, **stop and run create-dev-spec**, **abort**.
