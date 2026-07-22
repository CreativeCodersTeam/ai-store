# Member-Specific Documentation Rules

## Methods

- Use `<param>` to describe method parameters.
  - The description should be a noun phrase that doesn't specify the data type.
  - Begin with an introductory article.
  - If the parameter is a flag enum, start the description with "A bitwise combination of the enumeration values that specifies...".
  - If the parameter is a non-flag enum, start the description with "One of the enumeration values that specifies...".
  - If the parameter is a Boolean, the wording should be of the form "`<see langword="true" />` to ...; otherwise, `<see langword="false" />`.".
  - If the parameter is an "out" parameter, the wording should be of the form "When this method returns, contains .... This parameter is passed uninitialized.".
- Use `<paramref>` to reference parameter names in documentation.
- Use `<typeparam>` to describe type parameters in generic types or methods.
- Use `<typeparamref>` to reference type parameters in documentation.
- Use `<returns>` to describe what the method returns.
  - The description should be a noun phrase that doesn't specify the data type.
  - Begin with an introductory article.
  - If the return type is Boolean, the wording should be of the form "`<see langword="true" />` if ...; otherwise, `<see langword="false" />`.".

## Constructors

- The summary wording should be "Initializes a new instance of the <Class> class [or struct].".

## Properties

- The `<summary>` should start with:
  - "Gets or sets..." for a read-write property.
  - "Gets..." for a read-only property.
  - "Gets [or sets] a value that indicates whether..." for properties that return a Boolean value.
- Use `<value>` to describe the value of the property.
  - The description should be a noun phrase that doesn't specify the data type.
  - If the property has a default value, add it in a separate sentence, for example, "The default is `<see langword="false" />`".
  - If the value type is Boolean, the wording should be of the form "`<see langword="true" />` if ...; otherwise, `<see langword="false" />`. The default is ...".

## Canonical Example

This example anchors the rules above. Note the precedence: where a specific
formula applies (Boolean parameter/return, out parameter), it overrides the
general noun-phrase and introductory-article rules.

```csharp
/// <summary>
/// Converts the string representation of a monetary amount to its
/// <see cref="decimal" /> equivalent. A return value indicates whether the
/// conversion succeeded.
/// </summary>
/// <param name="text">A string that contains the amount to convert.</param>
/// <param name="strict"><see langword="true" /> to reject leading or trailing
/// whitespace in <paramref name="text" />; otherwise, <see langword="false" />.</param>
/// <param name="amount">When this method returns, contains the parsed amount if
/// the conversion succeeded, or zero if it failed. This parameter is passed
/// uninitialized.</param>
/// <returns><see langword="true" /> if <paramref name="text" /> was converted
/// successfully; otherwise, <see langword="false" />.</returns>
/// <exception cref="ArgumentNullException"><paramref name="text" /> is
/// <see langword="null" />.</exception>
/// <example>
/// <code language="csharp">
/// if (MoneyParser.TryParseAmount("42.50", strict: true, out var amount))
///     Console.WriteLine(amount);
/// </code>
/// </example>
public static bool TryParseAmount(string text, bool strict, out decimal amount)
```

## Exceptions

- Use `<exception cref>` to document exceptions thrown by constructors, properties, indexers, methods, operators, and events.
- Document all exceptions thrown directly by the member.
- For exceptions thrown by nested members, document only the exceptions users are most likely to encounter.
- The description of the exception describes the condition under which it's thrown.
  - Omit "Thrown if ..." or "If ..." at the beginning of the sentence. Just state the condition directly, for example "An error occurred when accessing a Message Queuing API."
