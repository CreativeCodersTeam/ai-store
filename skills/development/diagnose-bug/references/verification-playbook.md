# Verification playbook

How to turn an OPEN claim into VERIFIED or REFUTED. Pick the strongest source available;
record method and evidence in the ledger. A claim verified only by reading documentation or
from memory stays OPEN.

## Contents

1. Experiments
2. Repository code and history
3. Frameworks and libraries — installed version first
4. Verifying the bug report itself
5. Cheap checks that refute a lot

## 1. Experiments

The strongest evidence is a prediction that comes true.

- **Reproduction test first.** Narrow it until it fails for exactly one reason, and make it
  independent of test order and of other tests in the same file (fresh state per test, no shared
  fixtures that the bug itself can pollute). A test that fails for two reasons hides one of them;
  a test that only fails after another test ran proves the wrong thing, and for state-leak bugs
  the reproduction is exactly the kind of test that leaks into its neighbours.
- **Prediction check.** Before any change: "if hypothesis H is right, then change C makes the
  reproduction pass and changes nothing else". Apply C temporarily, run the reproduction and
  the surrounding test suite, capture C as a patch and both outcomes as text, then revert C. If the reproduction passes but
  other tests now fail, H may be right and C is just a bad fix — note that separately.
- **Differential runs.** Same code, different input / config / version / environment. One
  variable at a time; two variables changed at once prove nothing.
- **Instrumentation.** Temporary logging or asserts at the boundaries between components to see
  where a value first goes wrong. Log the value *and* its type. Remove afterwards.
- **Intermittent bugs.** Run in a loop with a count (`for i in $(seq 50); do …; done`,
  `--repeat`, `--count`), fix seeds, force scheduling with sleeps or barriers, run with a
  sanitizer or race detector where the ecosystem has one. Report the rate before and after.

## 2. Repository code and history

- **Read the whole path**, entry point to failure, not only the frame in the stack trace. Note
  every place where an error is caught, a default is substituted, or a value is coerced — those
  are where symptoms detach from causes.
- **Compare a passing and a failing case** through the same path; the first divergence is
  usually within one call of the cause.
- **History:**
  - `git log -S '<identifier>' --oneline -- <path>` — when a string was added or removed.
  - `git log -G '<regex>' -p -- <path>` — when matching lines changed.
  - `git blame -L <start>,<end> <path>` — who changed the failing lines and in which commit.
  - `git bisect start <bad> <good>` with the reproduction test as `git bisect run` — when a
    known-good commit exists. This is often the fastest route from "since when" to "why".
  - `git log --oneline -- <lockfile>` — dependency bumps around the regression date.
- **Configuration and data.** Check the config actually loaded at runtime (print it), not the
  file you think is loaded. Check environment-specific overrides and defaults applied in code.

## 3. Frameworks and libraries — installed version first

What you remember about a library is a hypothesis about a version you may not be using.

1. **Find the installed version** from the lockfile or resolved project file, not the manifest's
   range:

   | Ecosystem | Installed version | Source in dependency cache |
   |-----------|-------------------|----------------------------|
   | Node / npm, pnpm, yarn | `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`; `npm ls <pkg>` | `node_modules/<pkg>/` |
   | .NET | `packages.lock.json`, `Directory.Packages.props`, `dotnet list package`; `obj/project.assets.json` | `~/.nuget/packages/<pkg>/<version>/` (decompile with `ilspycmd` or read the `.xml` docs) |
   | Python | `poetry.lock`, `uv.lock`, `Pipfile.lock`, `pip freeze` / `pip show <pkg>` | `site-packages/<pkg>/` (`python -c "import pkg; print(pkg.__file__)"`) |
   | Java / Kotlin | `gradle dependencies`, `mvn dependency:tree` | `~/.gradle/caches/`, `~/.m2/repository/` (sources jars) |
   | Go | `go.sum`, `go list -m all` | `$(go env GOMODCACHE)/<module>@<version>/` |
   | Rust | `Cargo.lock` | `~/.cargo/registry/src/` |
   | Angular / TypeScript | as Node, plus the `typescript` version — compiler behavior changes matter | `node_modules/typescript/` |

   Also record the runtime version (`node --version`, `dotnet --version`, `python --version`,
   `java -version`): language runtimes change behavior too (e.g. sort stability, default
   timezone handling, hash seeds).

2. **Read the source at that version** in the dependency cache when the claim is about
   behavior ("does it throw or return null?", "is the comparator required to return a number?").
   Cite path and line.

3. **Read the changelog / release notes for that exact version** when the claim is about a
   change ("this used to work"). Look for the version range between last-known-good and
   current. Cite the entry.

4. **Check the issue tracker** for the symptom plus version when the behavior looks like a
   library bug — and treat an open issue as evidence, not proof; reproduce it locally with a
   minimal script.

5. **Write a micro-test** against the library alone when the claim is central. Ten lines that
   call the library with the suspicious input settle the question better than any document.

## 4. Verifying the bug report itself

- **Expected behavior:** find the spec, acceptance test, or documentation that defines it. If
  only the reporter defines it, mark the expectation OPEN and say so in the report; the "bug"
  may be intended behavior or a missing requirement.
- **Steps to reproduce:** run them literally before adapting them. If they do not reproduce,
  that is a finding — the reporter's environment differs from yours in a way that matters.
- **Error messages:** search the exact text in the repository and in dependencies. A message
  that does not exist in the code you are reading comes from somewhere else.
- **"Since when":** verify against history (deploy log, git log) rather than the reporter's
  memory.

## 5. Cheap checks that refute a lot

Run these early; each can eliminate several hypotheses in seconds.

- Does the bug reproduce on a clean checkout with fresh dependencies?
- Does it reproduce with the previous release / commit? (Regression vs. latent bug.)
- Does it reproduce with minimal input? (Data-dependent vs. logic bug.)
- Does it reproduce in a single run, or only across runs / requests? (State leaking between
  calls: caches, singletons, mutable defaults, static fields, test order.)
- Does it reproduce with the same runtime version the reporter used?
- Is the code you are reading the code that runs? (Stale build, wrong branch, cached bytecode,
  a second copy of the module on the path.)
