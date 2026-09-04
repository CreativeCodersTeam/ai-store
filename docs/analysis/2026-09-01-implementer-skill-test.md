# Test des `implementer`-Skills: Vollständigkeit und Verbindlichkeit der Skill-Bindung

**Datum:** 2026-09-01
**Prüfling:** `skills/general/implementer/` (`SKILL.md` + `references/REFERENCE.md`)
**Stand:** Branch `feature/compactandrefactor`, Commit `2d75407`, Arbeitsbaum sauber
**Testfrage:** Zieht `implementer` beim **Erstellen einer .NET-Anwendung** alle beim Nutzer verfügbaren `dotnet-*`-Skills heran, und ordnet er sie den Umsetzungs-Tasks **zwingend** zu?
**Prüfkriterien:** Vollständigkeit der Skill-Erfassung · Verbindlichkeit der Zuordnung · Durchsetzbarkeit des Mechanismus · Verhalten im Greenfield-Fall
**Schweregrade:** `Kritisch` (Workflow bricht / faktisch falsch mit Folgewirkung) · `Hoch` (führt Nutzer fehl oder lässt zentrale Fälle ungedeckt) · `Mittel` (reale Schwäche, begrenzte Wirkung) · `Niedrig` (Verbesserung / Kosmetik)

---

## 1. Verdikt

**Verbindlichkeit der Zuordnung: bestanden.** Für jeden Skill, den `implementer` einem Capability-Slot zuordnet, funktioniert die Durchsetzung wie konstruiert. Beide Verhaltensproben erzeugten unaufgefordert formatkorrekte Per-Task-Checklisten, füllten `language-implementation` korrekt mehrfach, kollabierten keine Invocations und reproduzierten die Nicht-Übertragbarkeit zwischen Tasks von sich aus (Probe A, Task #2: `build-deps — filled by "dotnet-nuget-manager" (re-invoked; no carryover from Task 1)`).

**Vollständigkeit der Erfassung: nicht bestanden.** Von 12 im Test angebotenen .NET-relevanten Skills erreichen nur **7** tatsächlich eine Task-Checkliste. Zwei fachlich einschlägige Skills (`dotnet-inspect`, `migrate-nullable-references`) sind über den Mechanismus **prinzipiell unerreichbar**, weil das Slot-Taxonom keine passende Kategorie besitzt. Ein dritter (`dotnet-reviewer`) wird zwar geslottet, entgeht aber der Durchsetzungsmaschine vollständig.

**Übergeordnet:** Der gesamte Zwangsmechanismus beruht auf `Skill(...)`-Aufrufen, die die eigene Frontmatter des Skills nicht erlaubt (Finding K-1). Für den konkret gefragten Fall — *Erstellen* einer Anwendung — ist zusätzlich das gesamte Stack-Erkennungsverfahren nicht anwendbar (Finding H-3).

**Verteilung:** 1× Kritisch · 3× Hoch · 3× Mittel · 3× Niedrig

**Empfehlung für den gefragten Anwendungsfall:** Für „neue .NET-Anwendung erstellen" ist `dotnet-dev` heute die belastbarere Wahl — es bindet `dotnet-inspect` explizit, hat harte Gates und ein vollständiges Invocation-Log. `implementer` ist konzeptionell überlegen (namensfrei, überlebt neue und fremde Skills), scheitert aber an K-1 im Kern und an H-1/H-3 im gefragten Szenario.

---

## 2. Prüfling

| Datei | Zeilen | SHA-256 |
|---|---|---|
| `skills/general/implementer/SKILL.md` | 255 | `1321541624e84210fe6291d599b608ec104d3e2ba3b218f2697a0ee809bf35cf` |
| `skills/general/implementer/references/REFERENCE.md` | 326 | `128539310053784486da695d42b672da1b55fbba52eb2b37373f9ec0d8fbdaa1` |

Der zu prüfende Mechanismus ist die **Capability-Slot-Discovery**: `implementer` nennt bewusst keine konkreten Skill-Namen, sondern listet zur Laufzeit die verfügbaren Skills, klassifiziert sie **nach ihrer `description`** und füllt fünf Slots (`SKILL.md:57–63`):

| Slot | Filled by a skill whose description covers… | Used in |
|------|---------------------------------------------|---------|
| `language-implementation` | writing code for the detected stack | Phase 3 |
| `language-testing` | the stack's test framework / test conventions | Phase 3 |
| `language-docs` | the stack's documentation conventions | Phase 3 |
| `language-review` | reviewing code for the detected stack | Phase 4 |
| `build-deps` | builds / package & dependency management | Phase 3 |

Die Verbindlichkeit stammt aus vier Textstellen in `SKILL.md`:

- `:71–72` — „**Slot fulfillment is by invocation, not by listing.** A capability slot counts as fulfilled only when its skill has been invoked via the `Skill` tool **in this conversation, for this task**."
- `:112–125` — Phase 2: jede Task publiziert eine Skill-Prerequisite-Checkliste
- `:137–142` — Phase 3, Step 0: „call the `Skill` tool **once per capability slot**… before any `Write`, `Edit`, or code-producing `Bash` call"
- `:217–228` — Phase 5: Invocation-Log mit den drei Zuständen `[x]` / `[n/a]` / `[!]`

---

## 3. Testaufbau

Zweistufig, nach der Repo-Konvention aus `CLAUDE.md` („Testing skill behavior"): statische Belegsammlung (RED-Baseline) plus Verifikations-Proben durch frische Subagents, die nur die Passage unter Test sehen.

### 3.1 Statische Prüfungen

Alle Kommandos aus dem Repository-Root, Commit `2d75407`.

#### T-S1 — Vollständigkeit des Slot-Inventars

```bash
for s in language-implementation language-testing language-docs language-review build-deps; do
  printf "%-24s %s\n" "$s" \
    "$(grep -o "$s" skills/general/implementer/SKILL.md \
        skills/general/implementer/references/REFERENCE.md | wc -l | tr -d ' ')"
done
```

**Ist-Ausgabe:**

```
language-implementation  10
language-testing         9
language-docs            9
language-review          5
build-deps               6
```

**Bewertung:** Genau fünf Slot-IDs existieren, keine weitere. `language-review` ist mit 5 Nennungen am schwächsten verankert — Vorbefund zu H-2.

#### T-S2 — Existiert ein Slot für Recherche / API-Surface / Migration?

```bash
grep -in "api surface\|lookup\|inspect\|research\|migration\|analyz" \
  skills/general/implementer/SKILL.md \
  skills/general/implementer/references/REFERENCE.md
```

**Ist-Ausgabe (vollständig):**

```
SKILL.md:88:Analyze the requirement before any code is written:
SKILL.md:146:  - Delegate to sub-agents (explore for research, task for builds/tests, general-purpose
SKILL.md:195:1. Launch a code-review sub-agent to analyze all changes made. If the `language-review` slot
references/REFERENCE.md:37:#### 1.4 Analyze the Codebase
references/REFERENCE.md:157:   - `explore` — For codebase research and analysis
references/REFERENCE.md:295:- Use `explore` agents for research, `task` agents for builds/tests, `general-purpose` for complex changes
```

**Bewertung:** Kein Treffer beschreibt einen **Slot**. „Research" erscheint ausschließlich als Subagent-Typ, nie als Capability. Beleg für H-1.

#### T-S3 — Greenfield-Behandlung

```bash
grep -in "greenfield\|empty repo\|new project\|from scratch\|scaffold\|does not exist yet\|no existing" \
  skills/general/implementer/SKILL.md \
  skills/general/implementer/references/REFERENCE.md
```

**Ist-Ausgabe:** *(leer — kein einziger Treffer)*

**Bewertung:** Beleg für H-3.

#### T-S4 — Erscheint `language-review` in einer Task-Checkliste?

```bash
awk 'NR>=110 && NR<=115 {print NR": "$0}' skills/general/implementer/references/REFERENCE.md
```

**Ist-Ausgabe:**

```
110: 3. **Documentation:** What documentation needs updating? (can be "none" if truly not applicable)
111:
112: Each task MUST also record its **capability slots** (from Phase 1.5), e.g.
113: `language-implementation`, `language-testing`, `language-docs`, `build-deps`. If a needed
114: slot is empty, mark it as "generic fallback" so the gap is visible in the plan.
115:
```

**Bewertung:** Die Task-Slot-Aufzählung listet vier von fünf Slots — `language-review` fehlt. Beleg für H-2.

#### T-S5 — Frontmatter gegen Repo-Konvention

```bash
grep -n "allowed-tools" skills/general/implementer/SKILL.md
grep -rl "allowed-tools" skills/ --include=SKILL.md
grep -n "Frontmatter is" CLAUDE.md
```

**Ist-Ausgabe:**

```
skills/general/implementer/SKILL.md:9:allowed-tools: Read Grep Glob Edit Create Task
--
skills/general/implementer/SKILL.md
--
CLAUDE.md:43:Frontmatter is `name` + `description` only. The **description is load-bearing** — it is the sole
```

**Bewertung:** Einziger Skill von 36 mit `allowed-tools`; verletzt die eigene Konvention. Beleg für K-1.

#### T-S6 — Fordert der Skill Tools, die er selbst nicht erlaubt?

```bash
grep -n 'Skill(skill=\|`Skill` tool' skills/general/implementer/SKILL.md
grep -n "ask_user" skills/general/implementer/SKILL.md \
                   skills/general/implementer/references/REFERENCE.md
```

**Ist-Ausgabe:**

```
SKILL.md:72:only when its skill has been invoked via the `Skill` tool **in this conversation, for this
SKILL.md:139:    code-producing `Bash` call for this task, call the `Skill` tool **once per capability
SKILL.md:173:Skill(skill="<skill filling language-implementation>")   ← MUST fire before production-code Write/Edit
SKILL.md:174:Skill(skill="<skill filling language-testing>")          ← MUST fire before test-code Write/Edit
SKILL.md:175:Skill(skill="<skill filling language-docs>")             ← MUST fire before doc Write/Edit
SKILL.md:222:    as "turn N", "before Write of `<file>`", or the exact `Skill(skill="…")` call. Generic
SKILL.md:248:| "I already listed the slot in the plan" | A listed slot is not an invoked skill. The slot is only fulfilled when the `Skill` tool has fired in this conversation for this task. |
--
SKILL.md:92:3. Clarify ambiguities — ask the user targeted questions using the ask_user tool
references/REFERENCE.md:29:- If anything is unclear, use the `ask_user` tool to ask targeted questions
```

**Bewertung:** Sieben Forderungen nach `Skill`, zwei nach `ask_user` — keines der beiden steht in `allowed-tools`. Beleg für K-1.

#### T-S7 — Divergenz der beiden Slot-Tabellen

```bash
sed -n '57,63p'  skills/general/implementer/SKILL.md
awk 'NR>=317 && NR<=323 {print NR": "$0}' skills/general/implementer/references/REFERENCE.md
```

**Ist-Ausgabe (nebeneinandergestellt):**

| Slot | `SKILL.md:57–63` | `REFERENCE.md:317–323` |
|---|---|---|
| `language-implementation` | writing code for the detected stack · Phase 3 | writing code for the detected stack · 3.2 |
| `language-testing` | the stack's test framework / **test** conventions · Phase 3 | the stack's test framework / conventions · 3.3 |
| `language-docs` | the stack's documentation conventions · Phase 3 | the stack's documentation conventions · 3.4 |
| `language-review` | **reviewing code for the detected stack** · Phase 4 | **stack-specific code review** · 4 |
| `build-deps` | **builds / package & dependency management** · Phase 3 | **build, package & dependency management** · 3.5 |

**Bewertung:** Beleg für N-2.

#### T-S8 — Existieren Test-Artefakte für `implementer`?

```bash
find skills -type d -name tests
grep -rl "implementer" skills/*/tests/ 2>/dev/null || echo "keine"
```

**Ist-Ausgabe:**

```
skills/angular/tests
skills/dotnet/tests
keine
```

**Bewertung:** `skills/general/tests/` existiert nicht. Beleg für N-3.

### 3.2 Verhaltensproben — Design

**Methode** (nach `CLAUDE.md`, „Testing skill behavior"): Zwei frische `general-purpose`-Subagents, Modell Sonnet, ohne Repo-Zugriff. Beide bekommen ausschließlich

1. Kopien der zwei Prüflingsdateien im Scratchpad — **keine** anderen Repo-Dateien, insbesondere keine `dotnet-*`-Skills, keine bestehenden Test-Artefakte, keine `CLAUDE.md`;
2. eine **simulierte Runtime-Skill-Liste** (Abschnitt 3.3) als vollständiges Ergebnis des „skill-listing mechanism" aus Phase 1.5, Schritt 2;
3. ein Anforderungsszenario (Abschnitt 3.4);
4. ein festes Ausgabeschema (Abschnitt 3.5).

**Isolationsauflagen im Prompt (wörtlich):**

```
- Read ONLY these two files, nothing else. Do not read any other file, do not grep,
  do not glob, do not list directories.
- Do NOT call the Skill tool. Do NOT write any files. Do NOT write any code.
- Ignore any skills listed in your own system prompt. Use ONLY the simulated skill
  listing given below as "the available skills at runtime".
```

**Warum zwei Szenarien:** Szenario A prüft den Normalfall (Web-API, viele passende Skills). Szenario B ist gezielt so konstruiert, dass es die vermutete Strukturlücke trifft — es *erzwingt* fachlich einen API-Surface-Lookup (Stripe-Paketinhalt) und eine Nullable-Reference-Types-Anforderung, für die je ein einschlägiger Skill in der Liste steht.

**Verifikation der Ergebnisse:** Alle von den Proben behaupteten Textstellen wurden nachträglich gegen die Originaldateien geprüft (T-S5, T-S6, T-S7 entstanden aus dieser Nachprüfung). Keine Probe-Behauptung wurde ungeprüft übernommen.

### 3.3 Testdaten — simulierte Runtime-Skill-Liste

Identisch für beide Proben. 19 Einträge: 12 .NET-relevante (die real beim Nutzer installierten Skills mitsamt ihren echten `description`-Texten) plus 7 Distraktoren zur Prüfung der Trennschärfe.

```
- dotnet: Use when a task involves .NET or C# and the right specialized skill is not obvious, or when an overview of the available .NET skills is needed. Routes between dotnet-fundamentals, dotnet-aspnet, dotnet-ef-core, dotnet-xmldocs, dotnet-sdk-builder, dotnet-tester, dotnet-reviewer, dotnet-inspect, and dotnet-nuget-manager. When the matching skill is already clear, invoke that skill directly instead.
- dotnet-aspnet: Use when building or changing ASP.NET Core Web/REST APIs — controllers, minimal APIs, middleware pipeline, routing, model binding, validation, authentication, authorization, error handling with ProblemDetails, OpenAPI/Swagger, health checks, CORS, or rate limiting. For DI, Options pattern, and configuration common to all .NET hosts, use dotnet-fundamentals instead.
- dotnet-dev: Use when asked to implement, extend, or change a feature, user story, requirement, or bug fix in a .NET / C# project — any task that produces or modifies C# production code, tests, or documentation. Use when a .NET change request arrives, before writing any code.
- dotnet-ef-core: Use when designing a DbContext, entities, or relationships, writing LINQ queries against EF Core, creating or reviewing migrations, implementing concurrency control or repository patterns, setting up EF Core tests, or troubleshooting N+1 and other query performance issues.
- dotnet-fundamentals: Use when registering services in any .NET host (ASP.NET Core, Worker Service, Console, MAUI), choosing DI lifetimes, binding configuration to IOptions<T>, setting up appsettings.json / User Secrets / environment variables, or applying modern C# idioms such as primary constructors, required properties, nullable reference types, and CancellationToken propagation. Also use as the baseline whenever any C# production code is written or modified — dotnet-aspnet, dotnet-ef-core, and dotnet-sdk-builder build on it; load it alongside them, not instead of them.
- dotnet-inspect: Use when answering questions about .NET library contents — which types or members a NuGet package, platform library (System.*, Microsoft.AspNetCore.*), or local .dll/.nupkg file exposes, what changed between two versions, which extension methods or interface implementors exist, or where the source of an API lives.
- dotnet-nuget-manager: Use when adding, removing, or updating NuGet package references or versions in a .NET project or solution, listing outdated packages, verifying that a package version exists, or working in a solution with Directory.Packages.props central package management — including requests phrased as dotnet add/remove package or dotnet list package --outdated.
- dotnet-reviewer: Use only when explicitly requested by name — "dotnet-reviewer", "dotnet code review", or "dotnet review" — or when invoked by the dotnet-dev workflow (Phase 5), for a structured code review of a .NET / C# project (uncommitted working-tree changes or current feature branch vs. main). Must NOT activate on generic "review my code" requests; other-language reviewers must not be hijacked.
- dotnet-sdk-builder: Use when asked to create a .NET SDK or client library, wrap a REST API in a typed C# client, generate a typed HTTP client with IHttpClientFactory, or produce a library with DI registration (AddXxx), Options pattern, and typed exceptions.
- dotnet-tester: Use when creating unit tests, adding tests, or improving test coverage for C#/.NET code, when new production code lacks tests, or when an existing suite is missing edge cases or error paths — projects using xUnit, FakeItEasy, AwesomeAssertions, FluentAssertions, NUnit, MSTest, or Moq. Also for in-process ASP.NET Core integration tests (WebApplicationFactory).
- dotnet-xmldocs: Use when writing or reviewing C# XML documentation comments (///) — public APIs without docs, insufficient or non-Microsoft-style <summary>, <param>, <returns>, or <exception> tags, or documentation that feeds OpenAPI/Swagger or NuGet symbol output.
- migrate-nullable-references: Enable nullable reference types in a C# project and systematically resolve all warnings. USE FOR: adopting NRTs in existing codebases, file-by-file or project-wide migration, fixing CS8602/CS8618/CS86xx warnings, annotating APIs for nullability.
- jest: Use when writing or configuring Jest tests for TypeScript/JavaScript projects.
- rxjs: Use when working with RxJS observables, operators, and reactive patterns in TypeScript.
- java-junit: Use when writing JUnit tests for Java projects.
- refactoring: Use when restructuring existing code without changing its behavior.
- code-review: Use when reviewing code changes for quality, correctness and maintainability in any language.
- create-readme: Use when creating or updating a README file for a project.
```

### 3.4 Testdaten — Szenarien

**Szenario A (Probe A) — Web-API, greenfield:**

> „Erstelle mir eine neue .NET Anwendung: eine ASP.NET Core Web API zur Verwaltung von Kunden (CRUD), mit EF Core auf SQL Server als Persistenz und Serilog für strukturiertes Logging. Das Repository ist leer."

**Szenario B (Probe B) — SDK/Konsole, greenfield:**

> „Erstelle mir eine neue .NET Anwendung: eine Konsolen-App plus eine wiederverwendbare Client-Library, die die Stripe REST API als typisierten C#-Client kapselt. Nullable Reference Types sollen aktiviert sein. Das Repository ist leer."

### 3.5 Testdaten — Ausgabeschema

Beide Proben mussten exakt fünf Sektionen liefern:

```
SECTION 1 — PHASE 1 OUTPUT
  Phase-1-Ausgabe inkl. erkanntem Stack und gefüllter Capability-Slot-Map
  im vom Skill vorgeschriebenen Format. Leere Slots ausweisen.

SECTION 2 — PHASE 2 OUTPUT
  Task-Liste. Jede Task trägt ihre Skill-Prerequisite-Checkliste im
  vom Skill vorgeschriebenen Format.

SECTION 3 — SKILL COVERAGE TABLE
  Für JEDEN der 12 .NET-Skills eine Zeile:
  <skill> | SLOT: <slot-id oder NONE> | ASSIGNED TO TASKS: <Nummern oder NONE> | WHY
  "Be honest. If the skill's five slots gave you nowhere to put a skill, write NONE."

SECTION 4 — (A) Stack-Erkennung bei leerem Repo / (B) zwei gezielte Fragen:
  (a) Welcher Slot deckt "look up an external library's API surface"?
  (b) Welcher Slot deckt "nullable reference types aktivieren"?

SECTION 5 — HONEST GAPS
  "Do not be diplomatic; this is a defect hunt."
```

---

## 4. Rohergebnisse

### 4.1 Probe A — Web-API-Szenario

**Erkannter Stack:** .NET/C#, ASP.NET Core Web API, EF Core (SQL Server), Serilog — „detected from the request text, not from repo signals (repo is empty)".

**Capability-Slot-Map:**

| Slot | Filled by | Anmerkung der Probe |
|---|---|---|
| `language-implementation` | `dotnet-aspnet`, `dotnet-ef-core`, `dotnet-fundamentals` | „three skills share the slot for different sub-areas" |
| `language-testing` | `dotnet-tester` | unit + WebApplicationFactory |
| `language-docs` | `dotnet-xmldocs` | |
| `language-review` | `dotnet-reviewer` (flagged) + generisches `code-review` | „activation-gating tension noted" |
| `build-deps` | `dotnet-nuget-manager` | |

Zusatzbefund der Probe: „**no discovered skill mentions logging/Serilog by name** — the Serilog work falls to `dotnet-fundamentals`'s generic DI/config coverage only."

**Task-Liste mit Checklisten (wörtlich):**

```
Task #1: Solution & Project Scaffolding
  Skill prerequisites (Step 0 of Phase 3):
    [ ] language-implementation   — filled by "dotnet-fundamentals"
    [ ] build-deps                — filled by "dotnet-nuget-manager"

Task #2: Customer Entity, DbContext & EF Core Migrations
  Skill prerequisites (Step 0 of Phase 3):
    [ ] language-implementation   — filled by "dotnet-ef-core"
    [ ] language-implementation   — filled by "dotnet-fundamentals"   (DI registration of DbContext)
    [ ] language-testing          — filled by "dotnet-tester"
    [ ] language-docs             — filled by "dotnet-xmldocs"
    [ ] build-deps                — filled by "dotnet-nuget-manager"   (re-invoked; no carryover from Task 1)

Task #3: CRUD API Endpoints for Customers
  Skill prerequisites (Step 0 of Phase 3):
    [ ] language-implementation   — filled by "dotnet-aspnet"
    [ ] language-implementation   — filled by "dotnet-fundamentals"   (DI/config baseline)
    [ ] language-testing          — filled by "dotnet-tester"
    [ ] language-docs             — filled by "dotnet-xmldocs"

Task #4: Serilog Structured Logging Integration
  Skill prerequisites (Step 0 of Phase 3):
    [ ] language-implementation   — filled by "dotnet-fundamentals"   (generic DI/config only — no skill covers Serilog specifics)
    [ ] language-testing          — filled by "dotnet-tester"
    [ ] language-docs             — EMPTY (no matching skill; generic fallback)
    [ ] build-deps                — filled by "dotnet-nuget-manager"

Task #5: Build & Full-Solution Verification
  Skill prerequisites (Step 0 of Phase 3):
    [ ] build-deps                — filled by "dotnet-nuget-manager"
```

**Coverage-Tabelle (Sektion 3, gekürzt auf Slot/Tasks):**

```
dotnet                      | SLOT: NONE                    | TASKS: NONE
dotnet-aspnet               | SLOT: language-implementation | TASKS: 1,3
dotnet-dev                  | SLOT: NONE                    | TASKS: NONE
dotnet-ef-core              | SLOT: language-implementation | TASKS: 2
dotnet-fundamentals         | SLOT: language-implementation | TASKS: 1,2,3,4
dotnet-inspect              | SLOT: NONE                    | TASKS: NONE
dotnet-nuget-manager        | SLOT: build-deps              | TASKS: 1,2,4,5
dotnet-reviewer             | SLOT: language-review (flagged) | TASKS: NONE (Phase 4, not a numbered Phase-2 task)
dotnet-sdk-builder          | SLOT: NONE                    | TASKS: NONE
dotnet-tester               | SLOT: language-testing        | TASKS: 2,3,4
dotnet-xmldocs              | SLOT: language-docs           | TASKS: 2,3
migrate-nullable-references | SLOT: NONE                    | TASKS: NONE
```

**Gaps-Liste der Probe A (10 Punkte, gekürzt):** fehlendes `ask_user` in `allowed-tools` · fehlendes `Skill` in `allowed-tools` · hartkodierte Subagent-Typen · `dotnet-reviewer`-Aktivierungskonflikt · `dotnet-dev`/`implementer`-Trigger-Kollision · kein Slot für README-Dokumentation · Phase-1.5-Schritt 5 (Instruction-Files lesen) nicht ausführbar · kein Fallback für leeres Repository · „per affected file/module" setzt Bestandscode voraus · Gates im Papiertest nicht durchsetzbar.

### 4.2 Probe B — SDK/Konsolen-Szenario

**Erkannter Stack:** .NET/C# (Console-Host + Class Library) — „No manifest/source signals exist yet (empty repo), so the stack was inferred directly from the request text itself".

**Capability-Slot-Map:**

| Slot | Filled by | Anmerkung der Probe |
|---|---|---|
| `language-implementation` | `dotnet-fundamentals`, `dotnet-sdk-builder` | sdk-builder „matches the Stripe-client ask almost verbatim" |
| `language-testing` | `dotnet-tester` | |
| `language-docs` | `dotnet-xmldocs` | „does not cover README/usage prose (gap)" |
| `language-review` | `dotnet-reviewer` | „its own activation gate names a different workflow" |
| `build-deps` | `dotnet-nuget-manager` (**partial**) | „no skill covers project scaffolding or build/test execution" |

**Task-Liste mit Checklisten (wörtlich, gekürzt auf die Checklisten):**

```
Task #1: Solution & project scaffolding
    [ ] language-implementation — filled by "dotnet-fundamentals"
    [ ] language-testing        — filled by "dotnet-tester"
    [ ] build-deps              — EMPTY (no matching skill covers project/solution scaffolding; generic fallback via `dotnet` CLI)

Task #2: Stripe core typed client
    [ ] language-implementation — filled by "dotnet-fundamentals"
    [ ] language-implementation — filled by "dotnet-sdk-builder"
    [ ] language-testing        — filled by "dotnet-tester"
    [ ] language-docs           — filled by "dotnet-xmldocs"
    [ ] build-deps              — filled by "dotnet-nuget-manager"

Task #3: Stripe resource endpoints
    [ ] language-implementation — filled by "dotnet-sdk-builder"
    [ ] language-testing        — filled by "dotnet-tester"
    [ ] language-docs           — filled by "dotnet-xmldocs"
    [ ] build-deps              — EMPTY (no new package changes expected this task; generic fallback)

Task #4: Console app wiring/demo
    [ ] language-implementation — filled by "dotnet-fundamentals"
    [ ] language-docs           — filled by "dotnet-xmldocs" (covers only XML-comment conventions; README prose has no matching skill)

Task #5: Solution-wide build & test verification
    [ ] build-deps — filled by "dotnet-nuget-manager" (package-management portion only; "run dotnet build/dotnet test" portion has no matching skill — generic fallback)
```

**Coverage-Tabelle (Sektion 3, gekürzt):**

```
dotnet                      | SLOT: NONE                    | TASKS: NONE
dotnet-aspnet               | SLOT: NONE                    | TASKS: NONE   (korrekt — kein Web-API-Host)
dotnet-dev                  | SLOT: NONE                    | TASKS: NONE
dotnet-ef-core              | SLOT: NONE                    | TASKS: NONE   (korrekt — keine Persistenz)
dotnet-fundamentals         | SLOT: language-implementation | TASKS: 1,2,4
dotnet-inspect              | SLOT: NONE                    | TASKS: NONE
dotnet-nuget-manager        | SLOT: build-deps              | TASKS: 2 (partiell 1,5)
dotnet-reviewer             | SLOT: language-review         | TASKS: Phase 4
dotnet-sdk-builder          | SLOT: language-implementation | TASKS: 2,3
dotnet-tester               | SLOT: language-testing        | TASKS: 1,2,3
dotnet-xmldocs              | SLOT: language-docs           | TASKS: 2,3 (partiell 4)
migrate-nullable-references | SLOT: NONE                    | TASKS: NONE
```

**Antworten auf die zwei gezielten Fragen (Sektion 4, wörtlich):**

> (a) **„Look up an external library's API surface":** None of the five capability slots covers this. `dotnet-inspect` in the listing is a precise textual match for the need, but the slot taxonomy … has no category for "inspect a third-party package's contents." Because Phase 3's Step 0 only invokes skills that are attached to an assigned slot on a task, `dotnet-inspect` would never be pulled in through the formal mechanism — it could only be used ad hoc, outside the slot machinery, which the skill text neither authorizes nor forbids.

> (b) **Nullable reference types:** Covered by `language-implementation`, filled by `dotnet-fundamentals` … `migrate-nullable-references`, despite the more obvious name match, does not apply — it targets fixing warnings in already-existing code, and this repo is empty.

### 4.3 Übereinstimmung der beiden Proben

Beide Proben liefen unabhängig, ohne Kenntnis voneinander, mit unterschiedlichem Szenario.

| Befund | Probe A | Probe B | Übereinstimmung |
|---|---|---|---|
| Checklisten-Format korrekt reproduziert | ja | ja | ✅ |
| Mehrfachbelegung `language-implementation` | ja (3 Skills) | ja (2 Skills) | ✅ |
| Keine Invocation-Übertragung zwischen Tasks | explizit vermerkt | implizit befolgt | ✅ |
| `dotnet-inspect` ohne Slot | ja | ja + ausdrücklich als *strukturell* benannt | ✅ |
| `migrate-nullable-references` ohne Slot | ja | ja | ✅ |
| `dotnet-reviewer` erreicht keine Task | ja (`TASKS: NONE`) | ja (`Phase 4`) | ✅ |
| `dotnet-reviewer`-Description schließt `implementer` aus | erkannt, „flagged" | erkannt, als Improvisation deklariert | ✅ |
| `dotnet-dev` vs. `implementer` unarbitriert | erkannt | erkannt | ✅ |
| Stack aus Anforderungstext statt aus Signalen erraten | ja | ja | ✅ |
| Slot-Taxonom deckt README/Prosa nicht | ja | ja | ✅ |
| `build-deps` deckt Build-/Test-Ausführung ab? | **ja** (Task 5) | **nein**, ausdrücklich „partial" | ❌ **Divergenz** |

**Zur Divergenz:** Probe A ordnete Task #5 („Build & Full-Solution Verification") `build-deps` zu und begründete, `dotnet-nuget-manager` „covers build/test commands". Das ist eine Überdehnung — die Description dieses Skills nennt ausschließlich Paket-Operationen (`dotnet add/remove package`, `dotnet list package --outdated`), keine Build- oder Testausführung. Probe B las korrekt und markierte den Slot als nur teilweise gedeckt. Die Divergenz ist selbst ein Befund: weil das Slot-Modell keinen Zustand „teilweise gefüllt" kennt, wird die Lücke je nach Agent entweder sichtbar gemacht oder wegdefiniert (Finding M-1).

### 4.4 Konsolidierte Coverage-Matrix

| Skill | Probe A | Probe B | Erreicht eine Task-Checkliste? |
|---|---|---|---|
| `dotnet-fundamentals` | impl · 1,2,3,4 | impl · 1,2,4 | ✅ |
| `dotnet-aspnet` | impl · 1,3 | — *(szenariokorrekt)* | ✅ |
| `dotnet-ef-core` | impl · 2 | — *(szenariokorrekt)* | ✅ |
| `dotnet-sdk-builder` | — *(szenariokorrekt)* | impl · 2,3 | ✅ |
| `dotnet-tester` | testing · 2,3,4 | testing · 1,2,3 | ✅ |
| `dotnet-xmldocs` | docs · 2,3 | docs · 2,3 | ✅ |
| `dotnet-nuget-manager` | build-deps · 1,2,4,5 | build-deps · 2 | ✅ |
| `dotnet-reviewer` | Slot gefüllt, **Tasks: keine** | Slot gefüllt, **Tasks: keine** | ❌ H-2 |
| `dotnet-inspect` | **kein Slot** | **kein Slot** | ❌ H-1 |
| `migrate-nullable-references` | **kein Slot** | **kein Slot** | ❌ H-1 |
| `dotnet` (Router) | kein Slot | kein Slot | ⚪ vertretbar |
| `dotnet-dev` | kein Slot | kein Slot | ⚠️ M-3, unarbitriert |

**Ergebnis: 7 von 12 Skills erreichen eine Task-Checkliste.**

---

## 5. Findings

### Kritisch

#### K-1 — `allowed-tools` sperrt genau das Tool aus, auf dem der gesamte Zwangsmechanismus beruht

**Dateien:** `skills/general/implementer/SKILL.md:9` (Frontmatter); Forderungsstellen `:72`, `:139`, `:173–175`, `:222`, `:248`; `references/REFERENCE.md:29`

**Testdaten:**

Ist-Frontmatter (`SKILL.md:1–10`):

```yaml
---
name: implementer
description: >
  Iterative implementation workflow for requirements. …
allowed-tools: Read Grep Glob Edit Create Task
---
```

Gegenüberstellung geforderter vs. erlaubter Tools:

| Vom Skill gefordert | Fundstelle | In `allowed-tools`? |
|---|---|---|
| `Skill` | `:72`, `:139`, `:173`, `:174`, `:175`, `:222`, `:248` (7×) | ❌ |
| `ask_user` | `SKILL.md:92`, `REFERENCE.md:29` | ❌ |
| `Write` | `:139` („before any `Write`, `Edit`, or code-producing `Bash` call") | ❌ |
| `Bash` | `:139` | ❌ |
| `Edit` | `:139` | ✅ |
| `Read`, `Grep`, `Glob` | Phase 1 | ✅ |
| `Create`, `Task` | — | ⚠️ keine realen Claude-Code-Tool-Namen |

Repo-Konvention (`CLAUDE.md:43`): „Frontmatter is `name` + `description` only."
Verbreitung (T-S5): `implementer` ist der **einzige** von 36 Skills mit `allowed-tools`.

**Erwartung:** Ein Skill, dessen zentrale Regel `Skill(...)`-Aufrufe verlangt, erlaubt dieses Tool.
**Ist:** Er verbietet es implizit über eine Allow-Liste, die er selbst nicht braucht.

**Wirkung:** In einem Harness, das `allowed-tools` restriktiv auslegt, ist die Kernregel „Slot fulfillment is by invocation, not by listing" **nicht ausführbar** — jeder Slot müsste als `[!]` enden. Der Skill schreibt zudem `Write`/`Bash` vor, ohne sie zu erlauben, und nennt zwei Tool-Namen (`Create`, `Task`), die es nicht gibt. Probe A benannte beide Hälften eigenständig: „*The skill cannot fulfill its own mandatory Step 0 without a tool its own frontmatter never grants.*"

**Empfehlung:** Zeile 9 ersatzlos löschen. Einzeiler, höchster Hebel, stellt zugleich die Repo-Konvention wieder her.

---

### Hoch

#### H-1 — Das geschlossene Fünf-Slot-Taxonom lässt fachlich einschlägige Skills strukturell fallen

**Dateien:** `SKILL.md:57–63`, `references/REFERENCE.md:65–68`, `:317–323`

**Testdaten:**
- T-S2 zeigt: kein Slot beschreibt Recherche, API-Surface-Lookup oder Migration.
- Beide Proben: `dotnet-inspect` → `SLOT: NONE`, `migrate-nullable-references` → `SLOT: NONE`.
- Szenario B war so konstruiert, dass ein API-Surface-Lookup fachlich zwingend ist (Stripe-Paketinhalt). Probe B wörtlich:

  > „`dotnet-inspect` exists and is on-point, but the five-slot taxonomy has no home for it, so the workflow's own invocation mechanism (Step 0, slot-driven) can never trigger it for a task like this one — a real capability the workflow can't reach through its own rules."

**Erwartung:** Ein in der Liste verfügbarer, fachlich passender Skill wird gebunden.
**Ist:** Er wird stillschweigend verworfen, weil er in keinen der fünf Slots fällt. Da Step 0 ausschließlich slot-zugeordnete Skills aufruft, ist er über den Mechanismus **prinzipiell unerreichbar**.

**Vergleich:** `dotnet-dev` bindet denselben Skill explizit — Skill Map, Zeile „External / platform / NuGet API surface lookup | `dotnet-inspect` | Phase 1, 4 | when an external/platform API is involved". `implementer` ist hier also strikt schwächer als der Workflow, dessen generische Variante er sein soll.

**Empfehlung:** Zwei Ergänzungen:
1. Slot `api-surface-lookup` („looking up the contents/API surface of an external library or package", Phase 1 + 3) in beide Slot-Tabellen aufnehmen.
2. Auffangregel in Phase 1.5 ergänzen: *„Ein entdeckter Skill, der zur Aufgabe passt, aber in keinen definierten Slot fällt, eröffnet einen Ad-hoc-Slot mit sprechendem Namen; er unterliegt denselben Step-0- und Log-Pflichten."* Damit trägt der Mechanismus auch Skills, die es heute noch nicht gibt — was der erklärten Absicht des Skills entspricht.

#### H-2 — `language-review` entgeht der Durchsetzungsmaschine vollständig

**Dateien:** `references/REFERENCE.md:112–114`; `SKILL.md:112–125` (Phase 2), `:137–142` (Step 0), `:195–196` (Phase 4), `:217–228` (Phase-5-Log)

**Testdaten:**
- T-S1: `language-review` ist mit 5 Nennungen der am schwächsten verankerte Slot.
- T-S4: Die Task-Slot-Aufzählung in `REFERENCE.md:113` nennt `language-implementation`, `language-testing`, `language-docs`, `build-deps` — **`language-review` fehlt**.
- Phase 4 formuliert nur weich (`SKILL.md:195`): „If the `language-review` slot is filled, use that skill" — nicht „invocation, not listing".
- Probe A, Coverage-Tabelle: `dotnet-reviewer | SLOT: language-review (flagged) | ASSIGNED TO TASKS: NONE (Phase 4, not a numbered Phase-2 task)`.
- Probe B: `ASSIGNED TO TASKS: Phase 4` — ebenfalls keine Task-Nummer.
- In keiner der insgesamt **10 erzeugten Task-Checklisten** beider Proben erscheint eine `language-review`-Zeile.

**Erwartung:** Der Review-Slot unterliegt derselben Beweispflicht wie die übrigen vier.
**Ist:** Step 0 und das Phase-5-Log hängen ausschließlich an **Task**-Checklisten. Review ist eine Phase, kein Task — der Slot bekommt daher nie ein `[x]`, `[n/a]` oder `[!]` und erscheint in keinem Audit-Trail.

**Wirkung:** Ausgerechnet der Slot, der die Qualität aller anderen absichert, ist der einzige ohne Nachweis. Ein Agent, der Phase 4 überspringt, hinterlässt keine Spur im Log.

**Empfehlung:** Eine der beiden Varianten:
1. `language-review` in die Aufzählung `REFERENCE.md:113` aufnehmen und Phase 4 als regulären Abschluss-Task modellieren, oder
2. das Phase-5-Log (`SKILL.md:217–228`) um eine verpflichtende, task-unabhängige Zeile für den Review-Slot erweitern, mit denselben drei Zuständen.

#### H-3 — Für das Erstellen einer neuen Anwendung existiert kein Erkennungsverfahren

**Dateien:** `references/REFERENCE.md:37–43` (Phase 1.4), `:45–71` (Phase 1.5); `SKILL.md:95–101`

**Testdaten:**
- T-S3: Grep nach `greenfield|empty repo|new project|from scratch|scaffold|does not exist yet|no existing` über beide Dateien → **null Treffer**.
- Phase 1.4 setzt durchgehend Bestandscode voraus: „Identify files, modules, and components **affected**", „Understand the **existing** architecture and patterns", „Look for **existing** tests that cover the affected area".
- Alle vier Detektionssignale in Phase 1.5 sind Artefakte eines existierenden Repos: Manifest-/Build-Files, Source-Extensions, Lockfiles/Toolchain-/CI-Configs, Framework-Marker in Manifests.
- Beide Szenarien enthielten den Satz „Das Repository ist leer." Beide Proben mussten identisch improvisieren.

Probe A wörtlich:

> „None of these signals exist — no `*.csproj`, no `.cs` files, no lockfile, no CI config. **The skill's detection procedure gave no applicable signal.** I inferred the stack directly from the request text instead … The skill text is silent on this greenfield case."

Probe B wörtlich:

> „Signal detection assumed a non-empty repo. … I had to substitute 'parse the natural-language request' as the sole signal source. The reference document never addresses the greenfield case."

Zusatzbefund Probe A: auch die Formulierung „per affected file/module" in Phase 1.5 „presupposes an existing codebase being modified, not a greenfield build where the 'affected' codebase doesn't exist yet."

**Erwartung:** Für „erstelle eine neue .NET-Anwendung" — den in der Testfrage genannten Fall — existiert ein definierter Pfad.
**Ist:** Das dokumentierte Verfahren liefert null Signale; der Agent muss raten. Beide Proben rieten richtig, aber beide deklarierten es als ungedeckte Improvisation.

**Wirkung:** Der Skill ist ausgerechnet in dem Fall undefiniert, in dem die Slot-Map am folgenreichsten ist — bei Greenfield gibt es keine Bestandskonventionen, die einen Fehlgriff später korrigieren würden.

**Empfehlung:** Phase 1.5 um ein fünftes, ausdrücklich nachrangiges Signal erweitern: *„Nennt die Anforderung selbst Sprache, Framework oder Laufzeit explizit, ist das ein gültiges Signal — verbindlich nur, wenn keine Datei-Signale existieren (Greenfield)."* Zusätzlich in Phase 1.4 einen Greenfield-Zweig ergänzen, der die Bestandsanalyse durch die Zielstruktur ersetzt (geplantes Solution-Layout, geplante Projekte).

---

### Mittel

#### M-1 — Nur teilweise gedeckte Slots melden „filled" und machen die Lücke unsichtbar

**Dateien:** `SKILL.md:57–63` (Slot-Definitionen), `:63` (`build-deps`), `:61` (`language-docs`), `references/REFERENCE.md:73` („Record empty slots explicitly")

**Testdaten:**

| Slot | Definition | Tatsächlich vom gefüllten Skill gedeckt | Ungedeckt |
|---|---|---|---|
| `build-deps` | „builds / package & dependency management" | `dotnet-nuget-manager`: Paket-/Versionsverwaltung | `dotnet new`-Scaffolding, `dotnet build`, `dotnet test` |
| `language-docs` | „the stack's documentation conventions" | `dotnet-xmldocs`: `///`-Kommentare | README/Usage-Prosa (`create-readme` existiert, hat aber keinen Slot) |

Probe B wörtlich:

> „The slot's own definition is 'builds / package & dependency management,' but the only matching skill (`dotnet-nuget-manager`) covers exclusively package/version references — nothing in the listing covers `dotnet new`/solution scaffolding or running `dotnet build`/`dotnet test`. Tasks 1 and 5 had to fall back to unbacked generic knowledge for that half, even though the slot table nominally shows `build-deps` as 'filled.'"

**Divergenz als Beleg (vgl. 4.3):** Probe A ordnete Task #5 `build-deps` zu und behauptete, `dotnet-nuget-manager` decke Build-/Test-Kommandos — eine Überdehnung gegenüber dessen Description. Probe B markierte denselben Slot in Task #1 als `EMPTY` und in Task #5 als „partial". Dasselbe Modell, dieselben Daten, entgegengesetzte Sichtbarkeit der Lücke.

**Erwartung:** Die Regel „Record empty slots explicitly — they mean 'use the generic fallback'" macht Lücken sichtbar.
**Ist:** Das binäre Modell `filled` / `EMPTY` kennt keinen Zwischenzustand. Ein zur Hälfte gedeckter Slot erscheint als voll gedeckt, und die Hälfte ohne Skill wird ohne Vermerk generisch erledigt.

**Empfehlung:** Dritten Zustand `partially filled — <gedeckter Teil> / gap: <ungedeckter Teil>` einführen, in der Slot-Map wie in der Task-Checkliste, und im Phase-5-Log als eigenen Zustand führen.

#### M-2 — Die Description von `dotnet-reviewer` schließt `implementer` als Aufrufer aus

**Dateien:** `skills/dotnet/dotnet-reviewer/SKILL.md` (Frontmatter-Description); `skills/general/implementer/SKILL.md:54–55`, `references/REFERENCE.md:66–68`

**Testdaten:**

Klassifikationsregel des Prüflings (`SKILL.md:54–55`): „**Classify each skill by its `description`** — match purpose and technology from the text, **never from the name**".

Description von `dotnet-reviewer` (Testdatum, wörtlich): „Use **only** when explicitly requested by name — 'dotnet-reviewer', 'dotnet code review', or 'dotnet review' — or when invoked by the **dotnet-dev** workflow (Phase 5) … **Must NOT activate** on generic 'review my code' requests."

Beide Proben erkannten den Widerspruch unabhängig. Probe B wörtlich:

> „The implementer skill gives no rule for what wins when a candidate skill's own trigger text appears to exclude the calling context. I resolved it by letting purpose/technology classification override the activation-gate prose … but that rule is about slot classification, not about resolving a skill's self-declared trigger conditions, so this is an improvisation."

**Erwartung:** Description-basierte Klassifikation ist entscheidbar.
**Ist:** Buchstabengetreu darf `implementer` den Slot `language-review` nicht mit `dotnet-reviewer` füllen — `implementer` ist weder „explicitly requested by name" noch „the dotnet-dev workflow". Beide Proben füllten dennoch, beide unter ausdrücklichem Vorbehalt.

**Wirkung:** Nichtdeterminismus an der einzigen Stelle, die Codequalität absichert. Ein strenger Agent lässt den Slot leer und reviewt generisch; ein pragmatischer füllt ihn.

**Empfehlung:** Die Description von `dotnet-reviewer` um den Aufrufer erweitern, z. B. „… or when invoked by a workflow skill that dispatches a code review (`dotnet-dev` Phase 5, `implementer` Phase 4)". Das hält die Regel „Must NOT activate on generic 'review my code'" intakt und macht den legitimen Aufrufer explizit. Familien-Parität beachten: `angular-reviewer` und `gherkin-bdd-reviewer` prüfen und ggf. gleich behandeln.

#### M-3 — `dotnet-dev` und `implementer` triggern auf dieselbe Anfrage; nichts arbitriert

**Dateien:** `skills/dotnet/dotnet-dev/SKILL.md` (Description), `skills/general/implementer/SKILL.md` (Description)

**Testdaten:**

| Skill | Description-Auslöser |
|---|---|
| `dotnet-dev` | „Use when asked to implement, extend, or change a feature, user story, requirement, or bug fix in a .NET / C# project … Use when a .NET change request arrives, before writing any code." |
| `implementer` | „Use this skill when asked to implement a feature, user story, requirement, or change request." |

Beide Descriptions werden von beiden Testszenarien erfüllt. Zusätzlich gilt: `dotnet-dev`s Description („any task that produces or modifies C# production code, tests, or documentation") passt bei reiner Description-Klassifikation auch auf den Slot `language-implementation` — dann würde `implementer` einen phasengegateten Workflow **innerhalb** seines eigenen Workflows invoken (Gates in Gates).

Beide Proben schlossen `dotnet-dev` aus, beide nannten es eine ungedeckte Ermessensentscheidung. Probe B wörtlich:

> „Neither `implementer-SKILL.md` nor `implementer-REFERENCE.md` says what to do when a discovered skill is itself another phase-gated workflow — nest it, defer entirely to it, or exclude it. I excluded it; the text doesn't confirm or contradict that choice."

**Empfehlung:** Zwei Ergänzungen:
1. Ausschlussregel in Phase 1.5: *„Skills, deren Description selbst einen phasengegateten Workflow beschreibt, füllen keine Slots — sie sind Alternativen zu diesem Workflow, keine Bausteine darin."*
2. Abgrenzung in beiden Descriptions nach dem Muster, das die `dotnet-*`-Familie bereits verwendet (`dotnet-aspnet`: „For DI … use dotnet-fundamentals instead"). Beispiel für `implementer`: „Für .NET-/C#-Projekte mit installierter `dotnet-*`-Familie ist `dotnet-dev` vorzuziehen; dieser Skill greift, wenn kein stack-spezifischer Workflow existiert."

---

### Niedrig

#### N-1 — Hartkodierte Subagent-Typen widersprechen der eigenen „keine feste Liste"-Philosophie

**Datei:** `references/REFERENCE.md:156–158`, `:295`; `SKILL.md:146`

**Testdaten:**

```
156:   - `explore` — For codebase research and analysis
157:   - `task` — For running builds, tests, linters (returns brief summary on success, full output on failure)
158:   - `general-purpose` — For complex multi-step code changes
```

Dem steht die Kernaussage aus Phase 1.5, Schritt 2 gegenüber: „List the available skills using your runtime's own skill-listing mechanism. **Do NOT assume a fixed directory** — the location varies across platforms."

Probe A wörtlich: „The skill assumes a fixed three-type roster it never guarantees exists." Im Testlauf existierte kein Agent namens `task`.

**Empfehlung:** Analog zur Skill-Discovery formulieren — Rollen beschreiben („ein Agent für Recherche", „ein Agent für Build-/Testläufe"), konkrete Namen als Beispiele kennzeichnen.

#### N-2 — Zwei divergierende Slot-Tabellen verletzen das Single-Sourcing-Prinzip

**Dateien:** `SKILL.md:57–63` und `references/REFERENCE.md:317–323`

**Testdaten:** siehe T-S7. Abweichungen bei `language-review` („reviewing code for the detected stack" vs. „stack-specific code review"), `build-deps` („builds / package & dependency management" vs. „build, package & dependency management") und `language-testing` („test framework / **test** conventions" vs. „test framework / conventions"). Zusätzlich unterschiedliche Phasenangaben (`Phase 3` vs. `3.2`/`3.3`/`3.4`/`3.5`).

`CLAUDE.md` benennt genau das als wiederkehrende Defektklasse: „A rule lives in exactly one canonical home … Divergent restatements of the same rule are the defect class this repo has repeatedly fixed."

**Empfehlung:** Die Tabelle in `SKILL.md` als kanonisch festlegen; die Quick-Reference in `REFERENCE.md` auf einen Verweis reduzieren oder wortgleich spiegeln.

#### N-3 — `implementer` besitzt kein einziges Test-Artefakt

**Testdaten (T-S8):** `skills/general/tests/` existiert nicht. Zum Vergleich: `skills/dotnet/tests/` enthält 20 `*-test.md`, `skills/angular/tests/` weitere. `implementer` ist ein Workflow-Archetyp mit derselben Enforcement-Maschinerie wie `dotnet-dev` (Step 0, Prerequisite-Checklisten, `[x]`/`[n/a]`/`[!]`-Log) — und ungetestet.

**Empfehlung:** `skills/general/tests/` anlegen und dieses Dokument als RED-Baseline für zwei Artefakte verwenden:
- `implementer-slot-coverage-test.md` (H-1, H-2, M-1)
- `implementer-greenfield-detection-test.md` (H-3)

Die Prompts aus Abschnitt 3.3–3.5 sind unverändert als Verifikations-Probe wiederverwendbar.

---

## 6. Empfohlene Reihenfolge der Behebung

| # | Finding | Aufwand | Wirkung |
|---|---|---|---|
| 1 | **K-1** — `allowed-tools`-Zeile löschen | 1 Zeile | Macht den Zwangsmechanismus überhaupt ausführbar; stellt die Repo-Konvention wieder her |
| 2 | **H-3** — Greenfield-Signal + Phase-1.4-Zweig | ~10 Zeilen | Deckt den in der Testfrage gestellten Fall |
| 3 | **H-1** — Slot `api-surface-lookup` + Auffangregel | ~8 Zeilen, 2 Tabellen | Macht `dotnet-inspect` erreichbar; zukunftsfest für unbekannte Skills |
| 4 | **H-2** — Review-Slot in Log/Checkliste aufnehmen | ~5 Zeilen | Schließt das Loch im Audit-Trail |
| 5 | **M-1** — Zustand `partially filled` | ~6 Zeilen | Beseitigt die beobachtete Nichtdeterminismus-Divergenz |
| 6 | **M-2**, **M-3** — Description-Abgrenzungen | je 1 Satz, familienweit spiegeln | Beseitigt zwei Ermessensentscheidungen |
| 7 | **N-1**, **N-2**, **N-3** | Kosmetik + Testartefakte | Konsistenz und Regressionsschutz |

Nach Schritt 1–4 wären beide Testszenarien vollständig gedeckt.

---

## 7. Reproduktion

```bash
# 1. Stand herstellen
git checkout 2d75407

# 2. Statische Prüfungen T-S1 bis T-S8 aus Abschnitt 3.1 ausführen
#    (alle Kommandos sind dort vollständig abgedruckt)

# 3. Prüfling isolieren
mkdir -p /tmp/probe
cp skills/general/implementer/SKILL.md            /tmp/probe/implementer-SKILL.md
cp skills/general/implementer/references/REFERENCE.md /tmp/probe/implementer-REFERENCE.md
```

Anschließend zwei frische `general-purpose`-Subagents starten. Prompt-Bausteine: Isolationsauflagen (3.2) + Szenario A bzw. B (3.4) + vollständige Skill-Liste (3.3) + Ausgabeschema (3.5). Die Subagents dürfen **nur** die beiden Dateien unter `/tmp/probe/` lesen und **kein** `Skill`-Tool aufrufen.

**Nachprüfung ist Pflicht:** Jede von einer Probe behauptete Textstelle gegen die Originaldatei verifizieren. In diesem Durchlauf ergab die Nachprüfung eine Überdehnung (Probe A zu `build-deps`/Task 5, siehe 4.3) — Probe-Aussagen sind Hinweise, keine Belege.

**Erwartete Regression nach den Fixes:** Nach Behebung von H-1 und H-2 muss die Coverage-Matrix (4.4) für Szenario B `dotnet-inspect` mit einem Slot und mindestens einer Task-Nummer ausweisen, und `dotnet-reviewer` muss in beiden Szenarien eine Log-Zeile mit einem der drei Zustände erhalten.

---

## 8. Grenzen dieses Tests

- **Nur Phase 1 und 2 wurden verhaltensmäßig geprüft.** Die Proben durften kein `Skill`-Tool aufrufen und keinen Code schreiben, also blieben Phase 3 (Step 0 in der Praxis), Phase 4 und das Phase-5-Log ungetestet. Geprüft wurde, ob die Zuordnung **entsteht** — nicht, ob sie unter Zeitdruck **hält**. Für `dotnet-dev` existieren dafür bereits Druck-Tests unter `skills/dotnet/tests/`; für `implementer` fehlen sie (N-3).
- **Die Gates wurden nicht durchgesetzt.** Beide Proben mussten Phase 1 und 2 in einem Zug liefern, obwohl der Skill nach jeder Phase auf Nutzerbestätigung wartet. Beide vermerkten das von sich aus.
- **Phase 1.5, Schritt 5** („Review instruction files: CLAUDE.md, AGENTS.md …") war durch die Isolationsauflage nicht ausführbar. Probe A wies das explizit aus, statt es stillschweigend zu überspringen.
- **Stichprobengröße n = 2**, ein Modell (Sonnet), zwei Szenarien. Die Übereinstimmung liegt bei 10 von 11 Prüfpunkten (4.3); die eine Divergenz ist selbst als Finding erfasst (M-1). Für die strukturellen Befunde (H-1, H-2, H-3, K-1) ist die Stichprobe unkritisch — sie sind statisch aus dem Skill-Text belegt und hängen nicht vom Modellverhalten ab.
- **Nicht geprüft:** ob `implementer` bei einer .NET-Anfrage überhaupt vor `dotnet-dev` anspringt (Trigger-Verhalten, vgl. M-3). Das erfordert einen Aktivierungstest nach dem Muster von `skills/dotnet/tests/reviewer-activation-test.md`.
