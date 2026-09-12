# development — explicit invocation only: no skill in the category loads from a task description

Covers the `description` frontmatter of all six skills under `skills/development/` and the
**Explicit invocation.** paragraph in each `SKILL.md` body. Shared, because the change landed in
every skill of the category at once.

Until 2026-09-11, five of the six descriptions were auto-trigger descriptions: "Use when the user
wants to …" followed by task phrasings — "spec this out", "why does X happen", "clean this up",
"implement docs/plans/<slug>.md", "Entwicklungsplan erstellen". Each of these workflows is long,
interactive, and writes documents into `docs/`; a skill that starts because a request *resembled*
its trigger list turns a two-line answer into a multi-phase interview the user never asked for.
The decision was to make the whole category load only on `/name` (`/cc-ai-dev:name` as a plugin),
on the skill name in the prompt, or on a hand-off from another skill — the pattern `auto-loop`,
`dotnet-reviewer`, and `angular-reviewer` already use.

## Why this is not a fixture test

Triggering is decided from the skill list alone, before any file is read. So the test is the skill
list: a fresh sub-agent, no file access, no tools, sees the six descriptions in exactly the form
Claude Code shows them and classifies requests. `refactor-workflow-test.md` notes that its own
probe does not measure triggering; this artifact is where that is measured.

## The probe

Thirteen requests. Six must load a skill; seven must not. The negatives carry the weight — every
one of them is a phrasing the old descriptions listed verbatim as a trigger, plus two harder cases:
9 (a plan path in `docs/plans/` without the skill name) and 12 (the verb "refactor" in a sentence,
which is not the name of the skill). Since the descriptions became English-only (GREEN 2), 11 is a
generalisation negative: "Entwicklungsplan erstellen" no longer appears verbatim in any negative
list, and the skill must still not load.

| | Request | Expected |
|---|---|---|
| 1 | `/diagnose-bug` + pasted stack trace | diagnose-bug |
| 2 | "Run create-dev-spec for the CSV export feature." | create-dev-spec |
| 3 | `/cc-ai-dev:refactor src/billing` | refactor |
| 4 | "run implement-dev-plan on docs/plans/checkout.md" | implement-dev-plan |
| 5 | Hand-off: inside create-dev-plan Phase 1, user chose (a) "run create-dev-spec first" | create-dev-spec |
| 6 | "auto loop: alle Tests grün, Budget 6 Runden, Scope src/parser" | auto-loop |
| 7 | "This test fails sometimes, it worked yesterday, why?" + Jest stack trace | none |
| 8 | "Clean up this module, there is a lot of duplication in src/services/orders.ts." | none |
| 9 | "Implement docs/plans/checkout.md" | none |
| 10 | "Spec this out properly before we write code: we need a nightly job that …" | none |
| 11 | "Entwicklungsplan für das Feature erstellen" | none |
| 12 | "Refactor the UserService to use the repository pattern." | none |
| 13 | "Just keep going until the tests pass." | none |

Harness: one `general-purpose` sub-agent per round, prompt = "do NOT read files, do NOT use
tools" + the six descriptions as a `- name: description` list (folded YAML flattened to one line
each) + the thirteen requests + "which ONE skill, if any, would you load; confidence; one reason;
table only". The agent is told to answer from what the descriptions actually say, not from what it
thinks the policy should be.

## Rounds

**RED — 2026-09-11, old descriptions** (`main` at `9104b15`): 7/13.

| | Loaded | Conf. | Agent's reason (abridged) |
|---|---|---|---|
| 1–6 | as expected | high | name, slash command, or hand-off |
| 7 | **diagnose-bug** | high | "fails sometimes" + "worked yesterday" + stack trace match the flaky-test triggers |
| 8 | **refactor** | high | "clean up" and "duplication" with a file scope match the triggers |
| 9 | **implement-dev-plan** | high | "implement docs/plans/<slug>.md" is a verbatim example in the description |
| 10 | **create-dev-spec** | high | "spec this out" is verbatim trigger phrasing |
| 11 | **create-dev-plan** | high | "Entwicklungsplan erstellen" is a listed German trigger |
| 12 | **refactor** | medium | "Refactor <class>" matches the trigger; scope may be pushed back on |
| 13 | none | high | auto-loop excludes "keep going" |

Six of seven negatives fired, all but one at high confidence, each citing a phrase the description
itself listed. Only `auto-loop`, which already had the explicit-only pattern, behaved. The
baseline is not a judgement failure of the agent — the descriptions told it to load.

**Fix.** Every description rewritten to one shape: `Use only when explicitly requested by name —
"<name>", "<name with space>", "/<name>", "/cc-ai-dev:<name>", "run <name>" — or when another
skill hands off to it by name, to <purpose>.` then two or three sentences on what the skill
produces and never does (so the model picks correctly once it *is* named, and the `/` listing
stays informative), then `Must NOT activate on its own for "<the former trigger phrases>", … or
any other <kind of> request that does not name the skill.` The `refactor` description adds the
sentence *The verb "refactor" inside a request is not an invocation.* because its name is an
ordinary verb. `auto-loop` gained the two slash aliases. Each body gained an **Explicit
invocation.** paragraph after its Core Principle / Contract, modelled on `auto-loop`'s. README
category table, Development section, and `plugin.json` say "explicit invocation only". All
descriptions dropped below 860 characters; the validator's three "approaching the limit" warnings
are gone.

**GREEN — 2026-09-11, new descriptions:** 13/13, every answer at high confidence.

| | Loaded | Agent's reason (abridged) |
|---|---|---|
| 1–4 | as expected | a listed invocation form (`/name`, `/cc-ai-dev:name`, "name starten" at the time) or the name in the prompt |
| 5 | create-dev-spec | "when another skill hands off to it by name" — the user chose that hand-off |
| 6 | auto-loop | "auto loop" is a listed name form, followed by loop parameters |
| 7–11, 13 | none | each cited the matching entry of the *Must NOT activate on its own* list |
| 12 | none | cited *the verb "refactor" inside a request is not an invocation* |

The two hard negatives held: 9 was refused on the exact phrase the old description had listed as
an example, and 12 on the sentence added for the verb/name ambiguity. Both are therefore
load-bearing — remove either and re-run before merging.

**Follow-up fix, same day.** All German text removed from the six descriptions: the aliases
`"<name> starten"` became `"run <name>"` (`"run the refactor skill"`, `"run auto-loop"`), and the
negative-list entries `"Entwicklungsplan erstellen"`, `"setze den Plan um"`, `"aufräumen"` became
`"create a development plan"`, `"work through the plan"`, `"tidy this up"`. Scenario 4 now uses the
new alias. Scenarios 6 and 11 stay German on purpose: 6 still contains the listed name form
"auto loop", 11 tests the negative list generalising beyond its listed phrases.

**GREEN 2 — 2026-09-11, descriptions English-only:** 13/13, every answer at high confidence.

| | Loaded | Agent's reason (abridged) |
|---|---|---|
| 1–4 | as expected | a listed invocation form; 2 and 4 matched `"run <name>"` verbatim |
| 5 | create-dev-spec | named hand-off, and the user's choice literally says "run create-dev-spec" |
| 6 | auto-loop | "auto loop" is a listed form; the German body only supplies criteria, budget, scope |
| 7–10, 12, 13 | none | each cited the matching *Must NOT activate on its own* entry or the verb/name sentence |
| 11 | none | recognised as German for "create a development plan" and refused under "any other planning request that does not name the skill" |

The generalisation negative held: with no German phrase left in the list, the catch-all clause
*or any other … request that does not name the skill* carried scenario 11 on its own.

## Re-run when

- any `description` in `skills/development/` changes, including adding an alias;
- a skill is added to the category (add it to the skill list and one positive + one negative
  request for it);
- the **Explicit invocation.** paragraph is removed or reworded in any skill;
- the plugin is renamed (the `/cc-ai-dev:` aliases in every description and body must follow);
- a skill outside this category is given a description that overlaps with one of these six — the
  probe only shows that the six do not fire, not that something else does.
