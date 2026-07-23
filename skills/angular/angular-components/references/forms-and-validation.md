# Forms & Validation

Forms are the client analogue of model binding + validation. Prefer **reactive forms** for anything non-trivial.

## Reactive vs Template-Driven

| Style | Use for |
|-------|---------|
| **Reactive** (`FormGroup`/`FormControl`) | Most forms — typed, testable, composable, dynamic validation |
| **Template-driven** (`ngModel`) | Trivial, mostly-static forms with little logic |

## Typed Reactive Forms

Use `NonNullableFormBuilder` for typed, non-null controls. The form's value type is inferred — the analogue of a strongly-typed request DTO.

```typescript
export class CreateOrderComponent {
  private readonly fb = inject(NonNullableFormBuilder);

  readonly form = this.fb.group({
    customerName: this.fb.control('', [Validators.required, Validators.maxLength(100)]),
    quantity: this.fb.control(1, [Validators.required, Validators.min(1)]),
    notificationEmail: this.fb.control('', [Validators.email]),
  });

  submit() {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    const value = this.form.getRawValue(); // { customerName: string; quantity: number; notificationEmail: string }
    // ... send value
  }
}
```

## Built-in Validators

`Validators.required`, `min`/`max`, `minLength`/`maxLength`, `email`, `pattern`. Compose as an array on each control.

## Custom & Cross-Field Validators

A validator is a function returning `ValidationErrors | null`. Apply control-level validators on the control, cross-field validators on the group.

```typescript
export function forbiddenWord(word: string): ValidatorFn {
  return (c) => (String(c.value).includes(word) ? { forbiddenWord: { word } } : null);
}

export const passwordsMatch: ValidatorFn = (group) =>
  group.get('password')!.value === group.get('confirm')!.value ? null : { mismatch: true };
```

## Async Validators

For server-side checks (e.g. "is this email taken?"), use an async validator that returns an `Observable<ValidationErrors | null>`; debounce to avoid hammering the API.

```typescript
export function uniqueEmail(api: UserApi): AsyncValidatorFn {
  return (c) =>
    timer(300).pipe(
      switchMap(() => api.emailExists(c.value)),
      map((exists) => (exists ? { emailTaken: true } : null)),
    );
}
```

## Displaying Errors

Show messages only after the control is touched/dirty, and keep them accessible (`aria-describedby`, `role="alert"`). This is the client equivalent of returning `ValidationProblemDetails`.

```html
@if (form.controls.customerName.touched && form.controls.customerName.invalid) {
  <p role="alert">Customer name is required (max 100 characters).</p>
}
```

## Experimental: Signal Forms

Angular 20 ships **Signal Forms** (`@angular/forms/signals`) as an experimental, signal-based forms model — form state and validation expressed as signals rather than `FormGroup`/`FormControl`. It is **experimental** (API may change); keep **typed reactive forms the default** for production. Track it for greenfield, signal-first apps and evaluate before adopting widely.

## Related Skills

- **[angular-fundamentals](../../angular-fundamentals/SKILL.md)** — Typed config validated at bootstrap uses the same fail-fast mindset
- **[angular-components](../SKILL.md)** — Core Angular UI skill
