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

The library's `package.json` declares Angular/RxJS as **peer** dependencies (so consumers dedupe a single Angular instance), not direct dependencies.

### Peer version resolution

Resolve every peer version (`@angular/*` and `rxjs` alike) at generation time — never copy fixed
numbers from this template. Apply the cascade in
[angular-version.md](../../angular-fundamentals/references/angular-version.md):

1. A version the user explicitly requested wins.
2. Otherwise use the version installed in the target workspace: the Angular major already detected
   in Step 2 of the workflow, and the workspace's `rxjs` range from its `package.json`.
3. Only when there is no existing workspace context (freshly created workspace): use the latest
   stable version (`npm view @angular/core dist-tags.latest`, `npm view rxjs dist-tags.latest`).

```jsonc
{
  "name": "@mycompany/github",
  "version": "1.0.0",
  "peerDependencies": {
    // resolved at generation time — see "Peer version resolution" above
    "@angular/core": "^<angular-major>.0.0",
    "@angular/common": "^<angular-major>.0.0",
    "rxjs": "^<rxjs-version>"
  },
  "sideEffects": false
}
```

This library `package.json` is maintained **by hand** (npm has no `--save-peer`) — the hand-edit ban in `angular-package-manager` explicitly exempts it. Packages that must be *installed* in the workspace go through the `angular-package-manager` skill instead.

Build and publish:

```bash
ng build github
cd dist/github && npm publish
```

`sideEffects: false` keeps the library tree-shakable; `provideXxx()` is the only entry point and pulls in only what is used.
