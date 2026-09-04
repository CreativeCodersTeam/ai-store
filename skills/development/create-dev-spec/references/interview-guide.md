# Interview Guide

Depth material for Phase 2 (Collection) and Phase 3 (Interview) of `create-dev-spec`.

Contents:

- [Question categories](#question-categories) — the checklist for Phase 2a
- [Where own ideas come from](#where-own-ideas-come-from) — prompts for Phase 2b
- [Writing a good item](#writing-a-good-item) — options, recommendation, descriptions
- [Worked example](#worked-example) — one item, start to finish
- [Follow-up loop](#follow-up-loop) — what turns an answer into a new item
- [Sizing the interview](#sizing-the-interview) — how many items is right

## Question Categories

Walk every category for every requirement. Most yield one or two items; some yield none,
and "none" is a legitimate result as long as you actually looked. The test for each
category: *could two competent engineers implement this differently and both claim to have
met the requirement as written?*

| Category | Typical gaps |
|---|---|
| **Scope & boundaries** | Where does the feature start and stop? Which existing behavior changes, which stays? Is this one deliverable or the first of several? |
| **Actors & permissions** | Who uses it, who administers it, who must *not* be able to? Roles, tenants, service accounts. |
| **Inputs & outputs** | Exact formats, encodings, sizes, required vs. optional fields, where output goes (file, response, event, UI). |
| **Business rules** | Calculations, ordering, defaults, precedence when rules conflict, what "valid" means. |
| **Edge cases & errors** | Empty input, duplicates, concurrency, partial failure, retries, idempotency, what the user sees when it fails. |
| **Data & persistence** | New or changed entities, retention, history/audit, PII, migrations of existing data. |
| **Integration points** | Other systems called or notified, contracts owned elsewhere, versioning, failure of the other side. |
| **Non-functional needs** | Latency, throughput, volume, availability, security, privacy, accessibility, observability, i18n. |
| **Migration & rollout** | Feature flag? Backfill? Backwards compatibility? Who is affected on day one? |
| **Testing & acceptance** | How will the user know it is done? Which scenarios must demonstrably pass? Test data? |
| **Constraints** | Deadlines, budget, forbidden technologies, team conventions, platform limits, licensing. |

Skip a category only when the requirement makes it moot (a pure refactoring has no
actors question). Note skipped categories in the Phase 2 overview as `— none identified`
so the user can disagree.

## Where Own Ideas Come From

Phase 2b items are things the user did not ask about but should decide. Sources:

- **A simpler cut.** Is there a version with 60 % of the value at 20 % of the effort? Propose
  it as an alternative, not as a replacement — the user may have reasons for the full scope.
- **A risk you see.** Something in the requirement conflicts with existing code, a contract,
  a limit, or a regulation. Name it and propose the mitigation.
- **Cheap now, expensive later.** A capability that costs almost nothing if designed in
  today (an audit field, an idempotency key, a version column) and a migration if added
  next quarter.
- **Convention conflicts.** The requirement implies a pattern the codebase does not use.
  Ask whether to follow the requirement literally or the codebase's convention.
- **Adjacent expectations.** Things stakeholders will assume are included (notifications,
  export, admin UI). Surface them so the user can put them in scope or in Non-Goals.

An idea is written as a proposal with a recommendation, exactly like a question. The user
rejecting it is a successful outcome — it is now a logged decision instead of a surprise
during review.

## Writing a Good Item

Each item becomes one call of the structured question tool (or one of up to four independent
questions in a call). The parts:

- **Question** — the actual decision, as a full sentence ending in a question mark. Include
  the context the user needs to decide, in one or two sentences before the question if the
  item is not self-explanatory.
- **Header** — the item ID or a two-word topic. It is the label the user scans.
- **Options** — 2–4. The first is your recommendation, its label ends in "(Recommended)".
  Every option's description states the *consequence* of choosing it, not a restatement of
  the label: "CSV only — one code path, no library; Excel users must import manually" beats
  "Export as CSV".
- **Escape hatch** — the user must always be able to answer with something of their own.
  Claude Code's tool adds "Other" by itself; do not add a duplicate. Runtimes whose tool
  does not add one get an explicit last option "Something else — I'll describe it".

Options are *mutually exclusive answers to the same question*. If you find yourself listing
independent features as options, you have several items, not one; split them and consider
a multi-select question only when the user genuinely picks any subset.

Avoid:

- an option that is just "no" without a consequence — say what not doing it means;
- a recommendation you cannot justify in one sentence — if you cannot, you have no
  recommendation, and the item is not ready to ask;
- more than four options — the fifth is what "Other" is for.

## Worked Example

Requirement fragment: *"Customers should be able to export their order history."*

Phase 2 produces, among others:

```
Q-3  [Inputs & outputs]  Export format — the requirement says "export" without a format.
I-2  [Cheap now]         Column selection — easy to add now, painful to retrofit into a fixed layout.
```

Phase 3, item `Q-3`, as a tool call:

> **Header:** Q-3 Format
> **Question:** Which file format should the order-history export produce? The current UI
> has no export anywhere, so this sets the convention for later exports too.
>
> 1. **CSV, UTF-8 with BOM (Recommended)** — one code path, opens in Excel on Windows
>    without an import wizard, streams well for large histories.
> 2. **XLSX** — native Excel formatting and multiple sheets, but needs a library and
>    cannot be streamed row by row; large histories are built in memory.
> 3. **Both, user chooses** — most flexible; two code paths to test and maintain.
>
> *(tool adds "Other")*

The user picks option 1. Decision Log entry:

```
| Q-3 | Export format | CSV, UTF-8 with BOM | Streams for large histories; Excel-compatible without import step | proposal |
```

Follow-up check after this answer: "CSV" raises a new gap — delimiter and quoting for
locales that use `;` (German Excel). Append:

```
Q-9  [Inputs & outputs]  CSV delimiter and locale handling — raised by Q-3 (CSV chosen).
```

## Follow-up Loop

After every answered round, scan the answers against these triggers before asking the next
item:

| Trigger | Example |
|---|---|
| An answer names something the list has no item for | "CSV" → delimiter, encoding, date format |
| An answer picks the free-form option | The user's own solution has its own gaps; read it as a mini-requirement and run the categories on it |
| An answer contradicts an earlier decision | Re-ask the earlier item with the new context; do not silently keep either |
| An answer makes a listed item moot | Strike it with a note (`Q-5 — moot: Q-4 chose synchronous processing`) |
| An answer expands scope | Ask whether it is in scope for *this* spec or goes to Out of Scope |
| An answer surprises you | A surprise means your model of the requirement was wrong somewhere; find where and ask |

New items get the next free ID and a note on which answer raised them. The interview ends
only when no unanswered items remain. Two or three loops are normal; more than five in a row
usually means Phase 1 was too shallow — say so and take a moment to re-orient before
continuing.

## Sizing the Interview

There is no fixed count. Rough calibration:

| Requirement | Typical items |
|---|---|
| Small change to existing behavior | 4–8 |
| New feature inside an existing system | 10–20 |
| New system, integration, or anything with external contracts | 20–35 |

Fewer than four items on anything but a trivial change means a category was skipped. More
than forty means items are too granular — merge items that a single decision settles, or
move genuinely deferred ones to Open Questions with an owner and a trigger.

When the user is in a hurry: order the list by how much a wrong guess would cost, ask the
top items first, and batch independent low-cost items four at a time. Do not drop items;
put those you did not reach into the draft's Review Notes so the user sees them at the gate.
