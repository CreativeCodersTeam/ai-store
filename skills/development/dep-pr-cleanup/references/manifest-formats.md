# Manifest formats

What `analyze_prs.py` (`scripts/deplib/manifests.py`) reads from a pull request diff. Only the
changed lines (`-` / `+`) and the context lines of their hunk are used; the files themselves are
never fetched.

## Identity of an update

An update is **(ecosystem, name, path)** plus its target value. The path is the manifest file:
`lodash` in `web/package.json` and `lodash` in `api/package.json` are different updates, because
updating one manifest does not update the other. Removed and added lines of one change block are
paired by (ecosystem, name); several references with the same name in one block (two `FROM node:`
stages) pair in order.

## Supported files

| Ecosystem | Files | Lines understood | Name |
| --- | --- | --- | --- |
| npm | `package.json` | `"name": "spec"`, `"packageManager": "pnpm@9.1.0+sha…"` | package name; `packageManager:<tool>` |
| NuGet | `*.csproj`, `*.fsproj`, `*.vbproj`, `*.props`, `*.targets`, `packages.config` | `<PackageReference>`, `<PackageVersion>` (central package management), `<GlobalPackageReference>`, `<package id version>`, `<Sdk>`, `<Project Sdk="Name/1.0">`; a multi-line `<Version>` with its `Include` in the context; any other `<Tag>value</Tag>` | package id; `msbuild-property:<Tag>` |
| NuGet | `dotnet-tools.json`, `global.json` | `"version": "x"` with the owning `"name": {` in the context; `"Sdk.Name": "1.0"` (msbuild-sdks) | tool / `sdk` / SDK name |
| Maven | `pom.xml` | `<version>` with `<artifactId>` (and `<groupId>`) of the same `<dependency>`, `<plugin>`, `<parent>`, or `<extension>` in the context; any other `<tag>value</tag>` | `groupId:artifactId` (plugins without group: `org.apache.maven.plugins`); `maven-property:<tag>` |
| Gradle | `build.gradle(.kts)`, `settings.gradle(.kts)` | `"group:artifact:version"`, `id("x") version "y"`, `kotlin("jvm") version "y"`, `val/def/ext.name = "1.2"`, `set("name", "1.2")` | `group:artifact`; `plugin:<id>`; `gradle-variable:<name>` |
| Gradle | `gradle.properties` | `key=1.2` | `gradle-property:<key>` |
| Gradle | `*.versions.toml` | `key = "1.2"`, `lib = "g:a:1.2"`, `{ module = "g:a", version = "…" }`, `{ group, name, version }`, `{ id, version }` | `catalog-version:<key>`; `group:artifact`; `plugin:<id>` |
| GitHub Actions | `.github/workflows/*.yml`, `action.yml` | `uses: owner/repo[/path]@ref` (a 40-hex SHA with `# vX.Y.Z` is ordered by the comment), `uses: docker://image:tag`, `image: image:tag` | `owner/repo[/path]`; image name |
| Docker | `Dockerfile`, `*.Dockerfile`, `Dockerfile.*`, `Containerfile`, `(docker-)compose*.yml` | `FROM [--platform=…] image[:tag][@digest] [AS stage]`, `image: …` | image name (with registry) |
| PyPI | `requirements*.txt`, `constraints*.txt`, `requirements/*.txt\|in` | PEP 508 lines with a specifier; `--hash=` continuation lines are skipped | normalised name (PEP 503) |
| PyPI | `pyproject.toml`, `Pipfile` | PEP 621 / build-system strings (also several per line), Poetry and Pipenv `name = "spec"` and `name = { version = "…" }` | normalised name |
| PyPI | `setup.cfg` | PEP 508 lines, also `install_requires = …` | normalised name |
| any file | — | a value directly below a Renovate annotation comment `# renovate: datasource=X depName=Y` (comment lines may sit in between) | `renovate-annotated:<datasource>` / `depName` |

## Ignored

- **Lockfiles**: `package-lock.json`, `npm-shrinkwrap.json`, `yarn.lock`, `pnpm-lock.yaml`,
  `bun.lock(b)`, `packages.lock.json`, `poetry.lock`, `Pipfile.lock`, `uv.lock`, `pdm.lock`,
  `*.lockfile`, `composer.lock`, `Gemfile.lock`, `Cargo.lock`, `go.sum`, `pubspec.lock`,
  `mix.lock`, `flake.lock`. They are listed in `ignored_lockfiles` and play no part.
- Blank lines and comment-only lines (`#`, `//`, `;`, `<!--`).
- A pair of lines whose parsed value did not change (reformatting).

## Reasons a pull request becomes unevaluable

| Reason in `unevaluable_reasons` | Typical cause |
| --- | --- |
| `diff not available: …` | `gh pr diff` failed — most often the diff exceeds GitHub's size limit |
| `no dependency update found in the manifests …` | the PR changes only lockfiles (a transitive security update) |
| `<file>: cannot interpret '<line>' (unsupported file type)` | an ecosystem outside the table (Cargo, Go, Helm, Terraform, `.python-version`, …) |
| `<file>: cannot interpret '<line>' (<why>)` | a known file, but a line shape the parser does not cover — a version taken from a variable or build argument, `version.ref` in a catalog, a `<version>` whose `<artifactId>` is outside the hunk |
| `<file>: <name> is added or removed, not updated` | a dependency appears on only one side of the change |
| `<file>: file added / deleted / renamed …` | only in-place changes of existing manifests are evaluated |
| `<file>: binary file` | e.g. `gradle-wrapper.jar` |

An unevaluable PR is never proposed and never counts as cover for another PR. This is
deliberate: a PR is only closed when every one of its changes was understood.
