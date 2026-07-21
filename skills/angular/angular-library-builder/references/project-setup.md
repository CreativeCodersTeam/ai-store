# Project Setup

## New Library Project

In an Angular CLI workspace:

```bash
ng generate library github
```

This scaffolds a buildable library under `projects/github/` configured with ng-packagr, a `public-api.ts`, and `ng-package.json`.

## Recommended Structure

```
projects/github/
  src/
    lib/
      github-client.ts                 # @Injectable typed client
      provide-github.ts                # provideGitHub() entry point
      github-config.ts                 # GitHubConfig + GITHUB_CONFIG token
      github-error.ts                  # typed error(s)
      models/
        repository.ts
        user.ts
    public-api.ts                      # exports the intended public surface only
  ng-package.json
  package.json                         # name, version, peerDependencies
  tsconfig.lib.json
```

## Public API Surface

Export only what consumers should use from `public-api.ts`:

```typescript
export { provideGitHub } from './lib/provide-github';
export { GitHubClient } from './lib/github-client';
export { GitHubConfig } from './lib/github-config';
export { GitHubError } from './lib/github-error';
export * from './lib/models/repository';
export * from './lib/models/user';
```

Keep mappers, interceptors-internals, and helpers **out** of the barrel.

## Packaging (ng-packagr)

The library's `package.json` declares Angular/RxJS as **peer** dependencies (so consumers dedupe a single Angular instance), not direct dependencies:

```jsonc
{
  "name": "@mycompany/github",
  "version": "1.0.0",
  "peerDependencies": {
    "@angular/core": "^19.0.0",
    "@angular/common": "^19.0.0",
    "rxjs": "^7.8.0"
  },
  "sideEffects": false
}
```

Build and publish:

```bash
ng build github
cd dist/github && npm publish
```

`sideEffects: false` keeps the library tree-shakable; `provideXxx()` is the only entry point and pulls in only what is used.

## Related Skills

- **[angular-fundamentals](../../angular-fundamentals/SKILL.md)** — `provideXxx()` and typed-config conventions for the generated project
- **[angular-library-builder](../../angular-library-builder/SKILL.md)** — Parent skill
