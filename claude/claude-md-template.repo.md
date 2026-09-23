
# Coding Guidelines

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly and verify them. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists for what you're about to write, name it in one sentence before coding. If the user confirms the original, proceed.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

If skill ponytail is available, use it for implementation tasks.

- No features beyond what was asked.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios. No error handling for scenarios guaranteed impossible by the type system or a same-file invariant. If justifying the skip requires reasoning about callers, keep the check.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- If a refactoring is needed or will improve the code quality, ask the user first.
- Match existing style, even if you'd do it differently. If that style conflicts with these guidelines, see *Priority When Rules Conflict*, rule 3.
- If you notice unrelated dead code, mention it in your final response — don't delete it.

When your changes create orphans: Remove imports/variables/functions your changes orphaned; leave pre-existing dead code (mention it in the response).

# Priority When Rules Conflict

1. A direct instruction from the user in the current session beats every rule in this file.
2. Ask beats guessing or silent assumption.
3. When these guidelines conflict with a convention visible in the code — explicit (a documented rule, e.g. a linter config or CONTRIBUTING.md) or implicit (a consistent pattern across neighbouring files) — do not resolve the conflict yourself. Before writing the affected code, name the guideline, the convention, and where the convention is visible, and ask the user whether to follow the code's convention or the guideline. Collect all conflicts you find up front and ask about them together; an answer applies to that conflict for the rest of the session. A pattern that is not applied consistently is not a convention; follow the guideline. If you cannot ask (sub-agent, non-interactive run), follow the code's convention and list the conflict in your result.
4. On anything specific to this repository, this file beats user-level instructions (`~/.claude/CLAUDE.md`). On everything else — tool preferences, language, personal workflow — the user-level file stands.
5. An explicitly invoked skill owns the workflow for its task; this file governs what that workflow leaves open. If a step of the skill contradicts a rule here, say so before following it.
