# Angular Version Cascade Test

Test artifact per `superpowers:writing-skills` (RED → GREEN → REFACTOR → Verify) for the 2026-08-03
mirroring of the .NET version cascade into the Angular family. Sibling artifact:
`skills/tests/dotnet/_shared/version-cascade-test.md`.

## Method

A fresh general-purpose subagent receives the canonical passage
(`angular-fundamentals/references/angular-version.md`) verbatim and **no file access, no tools**, and
answers five scenario questions plus an accuracy check.

## RED — Baseline, 2026-08-03

Angular had a flat baseline note in the router (`angular/SKILL.md`: "written against Angular 21 …
`angular-reviewer` supports Angular 17+") and a correct-but-local cascade in
`angular-library-builder` ("user-specified > workspace version > latest stable"), which no other
skill referenced. `angular-reviewer` hard-aborted below Angular 17 (`detect-angular-version.sh`
exit 4), mirroring the .NET gate that Finding K-1 showed to be unworkable. `README.md` advertised
the category as "Angular 17+ development".

## GREEN — 2026-08-03

`angular-fundamentals/references/angular-version.md` created as the canonical home: explicit user
directive → repo directive → latest stable, plus origin recording, the `(since X)` ≠ target rule,
and a non-interactive path. Router note rewritten to point at it; `angular-library-builder`'s local
cascade reduced to a hook; the Angular-17 gate removed from `angular-reviewer` (frontmatter,
overview, Step 2, "Never Does") and from `detect-angular-version.sh`; `report-format.md` gained a
`Version origin:` line; README category description de-versioned.

## Verify — probe, 2026-08-03

All five scenarios answered correctly, each with the governing sentence quoted:

- (a) user says "Angular 17", workspace pins `^21.0.0` → **17**, origin `user`.
- (b) `"@angular/core": "^19.2.0"` → major **19**, origin `repo:package.json`.
- (c) empty directory → step 3, and the probe correctly noted the passage tells you **not** to trust
  the number written in it ("Verify with `npm view` … rather than trusting a number written down
  here").
- (d) `@angular/core` only in `devDependencies` → covered explicitly by the fallback clause.
- (e) "(since Angular 19)" on a resolved 17 → use the documented alternative and say why; the probe
  correctly flagged that the no-alternative case was unhandled.

## REFACTOR — 2026-08-03

Five defects the probe found were real and were fixed:

1. **The cascade read a declared *range* while claiming to honour the *installed* major.** `^19.2.0`
   is safe (a caret cannot cross a major), but `>=19`, `*`, `latest`, `next`, `workspace:*` and
   git/tarball specs are not. Added the lockfile / `node_modules/@angular/core/package.json` as
   precedence 1, above the manifest, with the range used only as a fallback lower bound.
2. **`peerDependencies` was omitted although "declaring peer dependencies" is a stated use case** —
   exactly the library-repo case, where peers are often the only declaration and are deliberately
   wide (`>=17 <22`). Added as precedence 3 with a rule for picking a point inside a range.
3. **"the workspace's installed major wins" could be read as overriding step 1.** It is phrased as
   an absolute and sits inside step 2. Rewritten as "wins over the step 3 default … an explicit user
   directive still outranks it", and step 1 now says explicitly that it beats the step 2 rule.
4. **The hardcoded "currently Angular 21" was presented as fact.** Angular ships roughly two majors
   a year, and this repo's own `angular-rxjs/SKILL.md` already documents Angular 22 APIs — so the
   number in the router and the number in a reference could not both stay true. Step 3 now resolves
   the latest stable **at runtime** via `npm view @angular/core dist-tags.latest`; Angular 21 is
   retained only as the explicitly-labelled family baseline and offline fallback, and the
   Maintenance section says so.
5. **`npm view` collided with "never stall" when offline.** Added an offline branch: use the
   baseline, record `default-latest (offline; baseline 21)`, state that it was not verified.

Also added: granularity is the major unless a `(since X.Y)` marker forces the minor (resolved from
the lockfile, never from a caret range); monorepo rule (use the `package.json` owning the code, else
name the candidates); Node/TypeScript floor check before generating; conflict recorded alongside the
origin.

## Open — flagged, not silently resolved

The family baseline is stated as Angular 21 in the router, while `angular-rxjs/SKILL.md` documents
Angular 22 (May 2026) APIs. This artifact does not resolve which is correct — verifying the actual
current stable needs network access. Runtime resolution in step 3 means the discrepancy no longer
changes what gets generated, only the offline fallback and the examples' baseline. Re-run this probe
if the baseline is bumped.

## Result

Angular and .NET now resolve versions by the same three-tier rule with the same origin vocabulary,
and neither reviewer gate-keeps on version. Note: `angular-reviewer` has no Bash test suite (see
`CLAUDE.md`) — `detect-angular-version.sh` was syntax-checked and its gate removal verified by hand.

Re-run this probe whenever `angular-version.md`, the router Version-baseline note, or
`angular-reviewer` Step 2 changes.
