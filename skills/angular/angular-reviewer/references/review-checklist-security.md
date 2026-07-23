# Review Checklist — Security

## Cross-Site Scripting (XSS) & Sanitization

- **`bypassSecurityTrust*`** (`bypassSecurityTrustHtml/Script/Url/Style/ResourceUrl`) on untrusted/user data is forbidden. Flag any usage on non-constant input (A03 Injection).
- Prefer `[innerHTML]` binding (Angular auto-sanitizes) over manual DOM writes. Flag direct `ElementRef.nativeElement.innerHTML =`, `document.write`, or `Renderer2` HTML injection of untrusted data.
- Dynamic `[href]`/`[src]`/`[style]` bindings with user-controlled values — verify they are URL/resource-sanitized; flag `javascript:` URL paths.

## Input Validation

- All forms validate input with `Validators` (built-in + custom) or async validators. Flag forms collecting structured input with no validation.
- API client/SDK methods that forward user input validate or constrain it before sending. Don't trust the server to be the only gate for UX-critical rules.
- Treat all server responses as untrusted when rendering.

## Authentication / Authorization

- Route guards (`CanActivate`/`CanMatch`) protect non-public routes. Flag feature routes that should be guarded but aren't.
- Template-level role checks (`@if (auth.hasRole(...))`) are UX only — the **server** must enforce access. Flag any comment/assumption that client checks are the security boundary.
- Tokens are not logged or placed in URLs. Flag `console.log(token)` and query-string tokens.

## Secrets and Credentials

- **No secrets in the bundle.** Everything in `environment*.ts`, `assets/config.json`, or any shipped code is public. Flag API secrets, client secrets, private keys, or admin tokens (A02/A05).
- OAuth/OIDC uses Authorization Code flow **with PKCE** (no client secret in a SPA). Flag implicit flow or embedded client secrets (A07).
- "Public" provider keys (publishable Stripe key, referrer-restricted Maps key) are acceptable; verify they're the restricted kind.

## Dependencies & Supply Chain

- No known-vulnerable packages (`npm audit`). Flag high/critical advisories introduced by the change (A06).
- New runtime dependencies are justified; avoid pulling large/unmaintained packages for trivial needs.

## HTTP & Data

- HTTPS endpoints only; flag hard-coded `http://` API URLs.
- CORS/credentials handling is intentional; `withCredentials: true` only against trusted origins.
- No sensitive data persisted to `localStorage`/`sessionStorage` (readable by any XSS) (A01).

## OWASP Mapping

When reporting, reference the OWASP Top 10 category in parentheses:
- A01 Broken Access Control
- A02 Cryptographic Failures
- A03 Injection (incl. XSS)
- A04 Insecure Design
- A05 Security Misconfiguration
- A06 Vulnerable & Outdated Components
- A07 Identification & Auth Failures
- A09 Security Logging Failures
- A10 SSRF
