---
name: angular-tsdoc
description: Adds and reviews TSDoc/JSDoc documentation comments on Angular/TypeScript code following TSDoc and Compodoc conventions. Use when writing or reviewing TypeScript that includes public APIs, exported library symbols, complex logic, or when documentation is missing or insufficient. Covers the summary line, @param, @returns, @throws, @remarks, @example, {@link}, and {@inheritDoc}.
---

# Angular / TypeScript Documentation Best Practices

## When to Use

- Writing or reviewing TSDoc/JSDoc comments (`/** ... */`) on TypeScript types and members
- Adding documentation to the public API of a new or existing Angular library or shared module
- Documenting components, services, directives, pipes, and their input/output members (signal `input()`/`output()`/`model()` or `@Input()`/`@Output()`)
- Reviewing missing, insufficient, or non-standard doc comments in TypeScript code
- Generating documentation that feeds Compodoc output or published library typings

## General Guidelines

- Exported/public members of a library or shared API **should** be documented with TSDoc comments.
- It is encouraged to document non-exported members as well, especially if they are complex or not self-explanatory.
- Use the **TSDoc** comment form `/** ... */` (not `//` line comments) so editors, the TypeScript language service, and Compodoc pick it up.

## Guidance for all APIs

- The **first paragraph** of the comment is the summary — a brief, one-sentence, present-tense, third-person description of what the type or member does. (TSDoc has no `<summary>` tag; the leading text *is* the summary.)
- Use `@remarks` for additional information: implementation details, usage notes, or relevant context beyond the one-line summary.
- Use inline **backticks** for language keywords and literals — `` `null` ``, `` `true` ``, `` `undefined` `` — and for short inline code snippets (TSDoc's equivalent of `<c>` / `<see langword>`).
- Use `@example` for usage examples, with a fenced code block inside it:
  ```ts
  /**
   * Slugifies a title for use in a URL.
   *
   * @example
   * ```ts
   * slugify('Hello World'); // 'hello-world'
   * ```
   */
  ```
- Use `{@link Symbol}` to reference other types or members **inline** (in a sentence) — the equivalent of `<see cref>`.
- Use `@see {@link Symbol}` for standalone "see also" references — the equivalent of `<seealso>`.
- Use `{@inheritDoc Symbol}` to inherit documentation from a base class or implemented interface.
  - Unless there is a major behavior change, in which case document the differences explicitly.
- For Angular declarables, document the **public binding surface**: inputs and outputs (`input()`/`output()`/`model()` or `@Input()`/`@Output()`), public methods, and exposed signals/observables. Compodoc renders these per component.

## Member-Specific Rules

See [member-documentation-rules.md](./references/member-documentation-rules.md) for detailed wording conventions for methods (`@param`, `@returns`), constructors, accessors/properties (Gets/Sets patterns), `@Input()`/`@Output()` bindings, and thrown errors (`@throws`).

## Related Skills

- **[angular-components](../angular-components/SKILL.md)** — Component inputs/outputs (`input()`/`output()`/`model()`) and public methods are documented with these conventions
- **[angular-library-builder](../angular-library-builder/SKILL.md)** — Invokes this skill to document generated Angular libraries
- **[angular-reviewer](../angular-reviewer/SKILL.md)** — Code-quality checklist references these conventions for public-API docs
