# Coding Guidelines

## 1. Think Before Coding

- If multiple interpretations exist, present them — don't pick silently.

## 2. Simplicity First

- No features beyond what was asked.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for scenarios guaranteed impossible by the type system or a same-file invariant. If justifying the skip requires reasoning about callers, keep the check.
- Before implementing, check the code your change touches for a refactoring that would make the change simpler or the result clearer (duplication, a function doing too much, a missing abstraction). If you find one, offer the paths as a choice before coding: (a) the minimal change without refactoring, (b) the refactoring first, then the change, and (c) a simpler approach to the task itself, if one exists. State each path's scope, risk, and benefit, and continue only with the path the user picks. If you find none, say so in one sentence. If you cannot ask, take (a) and list the refactoring in your result.
- A refactoring changes structure, not behaviour. Keep it a separate step from the requested change.

## 3. Surgical Changes

When editing existing code:
- Refactor only on a path the user picked (see *Simplicity First*).
- Match existing style, even if you'd do it differently. If that style conflicts with these guidelines, see *Priority When Rules Conflict*, rule 3.
- If you notice unrelated dead code, mention it in your final response — don't delete it.

When your changes create orphans, remove the imports, variables, and functions your changes orphaned.

# Priority When Rules Conflict

1. A direct instruction from the user in the current session beats every rule in this file.
2. Ask beats guessing or silent assumption.
3. When these guidelines conflict with a convention visible in the code — explicit (a documented rule, e.g. a linter config or CONTRIBUTING.md) or implicit (a consistent pattern across neighbouring files) — do not resolve the conflict yourself. Before writing the affected code, name the guideline, the convention, and where the convention is visible, and ask the user whether to follow the code's convention or the guideline. Collect all conflicts you find up front and ask about them together; an answer applies to that conflict for the rest of the session. A pattern that is not applied consistently is not a convention; follow the guideline. If you cannot ask (sub-agent, non-interactive run), follow the code's convention and list the conflict in your result.
4. On anything specific to this repository, this file beats user-level instructions (`~/.claude/CLAUDE.md`). On everything else — tool preferences, language, personal workflow — the user-level file stands.
5. An explicitly invoked skill owns the workflow for its task; this file governs what that workflow leaves open. If a step of the skill contradicts a rule here, say so before following it.
