# Member-Specific Documentation Rules

This reference covers detailed wording conventions for documenting TypeScript/Angular members with TSDoc/JSDoc comments.

## Methods and functions

- Document parameters using the `@param` tag in the form `@param name - description`.
  - The description should be a noun phrase that describes the parameter.
  - Do **not** restate the parameter's type — TypeScript already declares it. Describe its meaning, not its type.
- Document return values using the `@returns` tag.
  - The description should be a noun phrase that describes the return value.
  - For methods returning an `Observable<T>` or `Promise<T>`, describe what the stream/promise *emits or resolves to*, not the wrapper type.
- Use the `@throws` tag to document errors a method can throw.
  - Reference the error type in braces: `@throws {HttpErrorResponse} ...`.
  - The description should explain the conditions under which the error is thrown. Start with the word "When".

## Constructors

- Pure DI constructors usually need no doc comment — document the **class** instead.
- When a constructor carries real logic, document it with the summary "Creates an instance of `ClassName`."
  - If it has meaningful parameters, document them with `@param`.
  - If overloaded, the summary should describe the specific overload.

## Accessors and properties

- For `get`/`set` accessor pairs start the summary with "Gets or sets"; for a getter only, "Gets"; for a setter only, "Sets" — continued by a noun phrase describing the value (e.g. "Gets or sets the request timeout in milliseconds.").
- For plain fields, write a noun-phrase summary describing what the field holds.

## Angular bindings

- **Inputs** (`input()` / `input.required<T>()` / `@Input()`): summarize what the input controls and its effect, e.g. "The label shown above the field." Note the default and whether it is required (`input.required<T>()` / `@Input({ required: true })`).
- **Outputs** (`output()` / `@Output()`): summarize the event and *when* it fires, e.g. "Emits the selected item when the user confirms the dialog."
- **Two-way (`model()`)**: describe the bound value and that it is read and written by the parent.
- **Signals**: for an exposed `signal`/`computed`, describe the value it represents; for a `WritableSignal` also note who is expected to update it.

## Errors

The `@throws` rules are defined under "Methods and functions" above. In addition, for Angular/RxJS code:

- `@throws` documents errors thrown **synchronously** on call. Errors delivered asynchronously — an `Observable` error notification or a rejected `Promise` — are part of the return value: document them in `@returns` or `@remarks` (e.g. "… Errors with `HttpErrorResponse` when the request fails.").
