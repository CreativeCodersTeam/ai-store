# Review der Skills unter `skills/dotnet`

**Datum:** 2026-08-02
**Scope:** Alle 11 Skills unter `skills/dotnet/` (SKILL.md + sämtliche `references/`-Dateien), inklusive Test-Artefakte unter `skills/dotnet/tests/`
**Prüfkriterien:** Qualität, Lücken, Redundanzen, Unklarheiten
**Schweregrade:** `Kritisch` (Workflow bricht / faktisch falsch mit Folgewirkung) · `Hoch` (führt Nutzer fehl oder lässt zentrale Fälle ungedeckt) · `Mittel` (reale Schwäche, begrenzte Wirkung) · `Niedrig` (Verbesserung / Kosmetik)

---

## 1. Gesamtbewertung

Die Skill-Suite ist überdurchschnittlich reif: konsistente Frontmatter-Descriptions mit expliziter Abgrenzung („use dotnet-fundamentals instead"), saubere Progressive Disclosure (schlanke SKILL.md, Details in `references/`), dokumentierte bewusste Abweichungen (z. B. `dotnet-sdk-builder` vs. `dotnet-fundamentals` beim Options-Pattern), ein nicht-interaktiver Modus im Reviewer und eigene Test-Artefakte unter `skills/dotnet/tests/` (26 Testprompts) sowie eine Shell-Testsuite für die Reviewer-Skripte. Die Beziehungspflege wurde nach einem früheren Review zentralisiert (Related-Skills-Blöcke verweisen auf den Router als Single Source of Truth).

Dem stehen ein kritischer Versionskonflikt im Kern-Workflow, einige falsche bzw. lückenhafte Querverweise und verstreute Einzelthemen gegenüber. Kein Finding erfordert eine Neustrukturierung — alle sind punktuell behebbar.

**Verteilung:** 1× Kritisch · 5× Hoch · 9× Mittel · 4× Niedrig

---

## 2. Findings

### Kritisch

#### K-1 — `dotnet-dev` erzwingt `dotnet-reviewer`, der auf .NET < 10 abbricht ✅ behoben (2026-08-03)

**Dateien:** `dotnet-dev/SKILL.md` (Skill Map: „Code review | dotnet-reviewer | always"; Phase 5), `dotnet-reviewer/SKILL.md` (Step 2: „Exit 4 (SDK < 10 or none): abort")

`dotnet-dev` deklariert `dotnet-reviewer` als unverzichtbare Pflicht-Bindung in Phase 5 („always") und verbietet zugleich jede eigenmächtige Abkürzung („Inline self-review does NOT satisfy this phase"). `dotnet-reviewer` bricht jedoch bei jedem Projekt unterhalb .NET 10 hart ab. Für ein .NET-8-Projekt (aktuelles LTS) oder .NET 9 ist der Workflow damit per Konstruktion nicht abschließbar: Phase 5 ist Pflicht, ihr einziges zugelassenes Mittel verweigert den Dienst, und ein `n/a`-Grund („Projekt ist net8.0") ist nach den strengen `n/a`-Kriterien nicht vorgesehen.

Der Konflikt zieht sich durch die Suite: `dotnet-sdk-builder` generiert im Template `net9.0`, `dotnet-nuget-manager` nennt „.NET 8.0 SDK or later" als Voraussetzung, `dotnet-fundamentals` behandelt .NET-8-Features (Keyed Services) — die Suite adressiert also ausdrücklich .NET 8/9, nur der verpflichtende Review-Schritt nicht.

**Empfehlung (eine der beiden):**
1. `dotnet-reviewer` auf .NET 8+ öffnen (Checklisten existieren bereits versionsneutral; nur `review-checklist-net10.md` ist versionsspezifisch — ein `review-checklist-net8.md`/`-net9.md` oder ein „General only"-Fallback genügt), **oder**
2. in `dotnet-dev` Phase 5 einen definierten Pfad für < .NET 10 ergänzen (z. B. dokumentierter Review-Fallback mit denselben Checklisten, als solcher im Report ausgewiesen).

**Behoben (2026-08-03)** — Empfehlung 1 umgesetzt, plus die zugrunde liegende Ursache: Die Suite hat jetzt **eine** Versionsregel, kanonisch in `dotnet-fundamentals/references/target-framework.md` (explizite User-Vorgabe → Repo-Vorgabe → aktuelles LTS, derzeit .NET 10). `detect-dotnet-version.sh` hat beide Versions-Gates verloren und liefert stattdessen `resolved_from`; Exit 4 bedeutet nur noch „kein .NET-Projekt gefunden" und führt zum LTS-Fallback statt zum Abbruch. `dotnet-reviewer` Step 2 nutzt die Version zur Checklisten-Auswahl, nicht als Eintrittsbedingung — Phase 5 ist damit auf jedem Ziel abschließbar. Die divergierenden Einzelangaben (`net9.0`-Template, „.NET 8.0 SDK or later", `net8.0`-Beispiel) sind auf Hooks reduziert; Feature-Marker heißen jetzt einheitlich `(since .NET 8)` und sind ausdrücklich keine Zielangabe. Nachweis: `skills/dotnet/tests/version-cascade-test.md`, `tests/dotnet-reviewer/unit/test-detect-version.sh`.

---

### Hoch

#### H-1 — Falscher Querverweis: DI/Configuration liegt nicht in `dotnet-aspnet` ✅ behoben (2026-08-02)

**Datei:** `dotnet-reviewer/references/review-checklist-architecture.md:25`
**Status:** Behoben — der Verweis zeigt jetzt auf `dotnet-fundamentals` (`references/dependency-injection.md`, `references/options-pattern.md`); der Reviewer-spezifische Hook blieb unverändert.

> "See the `dotnet-aspnet` skill (Dependency Injection + Configuration sections) for lifetime rules and the Options pattern."

`dotnet-aspnet` besitzt keine DI-/Configuration-Abschnitte — es delegiert diese Themen ausdrücklich an `dotnet-fundamentals` (sowohl in der Description als auch in SKILL.md: „This skill covers the HTTP / web layer only"). Ein Reviewer-Agent, der dem Verweis folgt, findet die Lifetime-Regeln und das Options-Pattern nicht. Korrektes Ziel: `dotnet-fundamentals` (`references/dependency-injection.md`, `references/options-pattern.md`).

#### H-2 — Router kennt `dotnet-dev` nicht; Vorrangregel Dev-Workflow vs. Wissens-Skills fehlt

**Dateien:** `dotnet/SKILL.md`, `dotnet-dev/SKILL.md`

Der Router beansprucht, alle .NET-Skills zu kartieren („Routes between …" listet 9 Skills), führt aber `dotnet-dev` — den zentralen Implementierungs-Workflow — weder in der Description noch in einer Routing-Tabelle. Wer den Router mit „implementiere Feature X" konsultiert, landet bei einem Wissens-Skill statt beim Workflow. Umgekehrt referenziert `dotnet-dev` den Router als „tie-breaker"; die Beziehung ist einseitig.

Damit bleibt auch die wichtigste Triggering-Ambiguität ungeregelt: `dotnet-dev` triggert auf „any task that produces or modifies C# production code" — dieselben Prompts, auf die auch `dotnet-aspnet`/`dotnet-ef-core`/`dotnet-fundamentals` matchen. Nirgends steht, dass bei einem Change-Request der Workflow-Skill führt und die Wissens-Skills als dessen Bindungen geladen werden.

**Empfehlung:** Im Router eine dritte Kategorie „Workflow-Orchestrierung" mit `dotnet-dev` ergänzen plus eine Vorrangregel („Change-Request → `dotnet-dev`; die Wissens-Skills werden von dort als Bindungen gezogen").

#### H-3 — `modern-patterns.md`: Abschnitt „Primary Constructors" ist ein Stub

**Datei:** `dotnet-fundamentals/references/modern-patterns.md:5-7`

Der Abschnitt „Primary Constructors (C# 12)" besteht aus einem einzigen Bullet — und der behandelt einen Spezialfall (Middleware, scoped Services via `InvokeAsync`), der zudem `dotnet-aspnet/references/middleware.md` dupliziert. Das eigentliche Pattern fehlt komplett: Syntax, Einsatz in Services/Controllern, Capturing-Semantik, Abgrenzung zu `record`-Primary-Constructors, wann klassischer Konstruktor + `readonly`-Feld vorzuziehen ist. Die Frontmatter-Description von `dotnet-fundamentals` bewirbt primary constructors ausdrücklich; die Reviewer-Checkliste net10 flagt sogar den Legacy-Stil („ctor + private readonly field") — die Wissensgrundlage dazu existiert aber nicht. Vermutlich ein Redaktionsverlust.

#### H-4 — `dotnet-inspect`: unbenannte Voraussetzung `dnx` (.NET 10 SDK), kein Fallback

**Dateien:** `dotnet-inspect/SKILL.md` (Installation), `references/command-reference.md`

Alle Kommandos laufen über `dnx dotnet-inspect -y -- …`. `dnx` (tool-exec) ist erst ab .NET 10 SDK verfügbar; der Skill nennt keine SDK-Anforderung und keinen Fallback (`dotnet tool install -g dotnet-inspect` / `dotnet tool run`). Das kollidiert mit dem Suite-Baseline-Anspruch „.NET 8 SDK" (`dotnet-nuget-manager`): Auf einer 8er/9er-Maschine schlägt jede Beispielzeile fehl — und `dotnet-dev` bindet `dotnet-inspect` in Phase 1/4 ein. Voraussetzungen-Abschnitt ergänzen (SDK ≥ 10 oder Fallback-Kommando dokumentieren).

#### H-5 — Lücke: ASP.NET-Core-Integrationstests haben keinen Ort

**Dateien:** `dotnet-tester/SKILL.md`, `dotnet-aspnet/SKILL.md`

`dotnet-tester` grenzt sich ab („Not for … integration tests that only exercise external systems") und behandelt ausschließlich Unit-Tests. `dotnet-aspnet` schweigt zu Tests vollständig. Der in der Praxis häufigste ASP.NET-Core-Testtyp — In-Memory-Integrationstests via `WebApplicationFactory<TEntryPoint>` / `Microsoft.AspNetCore.Mvc.Testing` (Endpoint + Pipeline + DI + Auth-Stubs) — wird von keinem Skill abgedeckt. Zum Vergleich: `dotnet-ef-core` löst dasselbe Problem für seine Domäne vorbildlich (SQLite in-memory, Testcontainers). Empfehlung: Abschnitt bzw. Reference in `dotnet-aspnet` („testing.md" mit WebApplicationFactory-Pattern) oder erweiterter Scope in `dotnet-tester`, plus wechselseitige Verweise.

---

### Mittel

#### M-1 — `middleware.md` zu dünn für den Anspruch „single canonical sequence" ✅ behoben (2026-08-02)

**Status:** Behoben — `middleware.md` vollständig ausgebaut: komplette annotierte Sequenz (inkl. `UseStaticFiles`, `UseRouting`, Endpoint-Mapping), „Why this order"-Begründungen, expliziter RateLimiter-vs.-Auth-Trade-off, Einordnungsregel für eigene Middleware. SKILL.md unangetastet (A-3-Invariante hält). Per Retrieval-Probe RED→GREEN→REFACTOR→Verify verifiziert, siehe `skills/dotnet/tests/aspnet-middleware-depth-test.md`.

**Dateien:** `dotnet-aspnet/SKILL.md:25`, `references/middleware.md`

SKILL.md erhebt die Datei zur einzigen kanonischen Quelle für die Pipeline-Reihenfolge („never order the pipeline from memory"). Die Sequenz nennt aber weder `UseRouting`/`UseStaticFiles`/`UseSwagger`(bzw. `MapOpenApi`) noch die Einordnung eigener Middleware, und sie begründet nichts — z. B. warum `UseRateLimiter` hier nach `UseAuthorization` steht (Effekt: unauthentifizierte Requests werden nicht limitiert; je nach Bedrohungsmodell gewollt oder falsch). Eine kanonische Referenz sollte die vollständige Reihenfolge plus die „Warum"-Begründungen enthalten, sonst muss der Anwender doch wieder aus dem Gedächtnis ordnen.

#### M-2 — `ConfigureAwait(false)`-Regel verstreut, fehlt am natürlichen Ort ✅ behoben (2026-08-02)

**Status:** Behoben — neuer Abschnitt „`ConfigureAwait(false)`" (Regel + Begründung + Beispiel) in `modern-patterns.md`; die drei Streustellen sind jetzt konsistente Kurz-Hooks mit Verweis auf fundamentals (inkl. Korrektur der „not in tests"-Verkürzung in `dotnet-dev`). Per Accuracy-Probe verifiziert, siehe `skills/dotnet/tests/fundamentals-configureawait-test.md`.

**Dateien:** `dotnet-dev/references/REFERENCE.md:123`, `dotnet-sdk-builder/references/http-client-patterns.md:77`, `dotnet-reviewer/references/review-checklist-performance.md:8`

Die Regel („in Library-Code ja, in Application-/Testcode nein") steht dreimal in leicht unterschiedlicher Formulierung in Workflow- und Review-Skills — aber nicht in `dotnet-fundamentals/references/modern-patterns.md`, dem designierten Ort für async-Idiome, wo bereits `CancellationToken`-Propagation und `OperationCanceledException` behandelt werden. Konsolidieren: Regel + Begründung in `modern-patterns.md`, die anderen Stellen verweisen.

#### M-3 — Redundanz: `AddXxx`-Extension-Pattern doppelt, mit divergierenden Validierungsansätzen ✅ behoben (2026-08-02)

**Status:** Behoben — Gegenverweis-Box in `dependency-injection.md` ergänzt; die Abweichung ist jetzt beidseitig dokumentiert und per Konsistenz-Probe gegen den sdk-builder-Text geprüft (eine REFACTOR-Runde: `BindConfiguration`-Attribution präzisiert), siehe `skills/dotnet/tests/fundamentals-configureawait-test.md`.

**Dateien:** `dotnet-fundamentals/references/dependency-injection.md:55-78`, `dotnet-sdk-builder/references/di-patterns.md`

Beide zeigen das Library-Registrierungs-Pattern; fundamentals mit `BindConfiguration` + `ValidateDataAnnotations`, sdk-builder mit `IValidateOptions<T>` + `Configure`. Die Options-Klassen-Abweichung (`required/init` vs. `get; set;`) ist in sdk-builder vorbildlich begründet — fundamentals kennt die Gegenrichtung aber nicht: Wer nur fundamentals liest, hält `required` + `BindConfiguration` für das einzige Muster. Ein Satz in `dependency-injection.md` („für SDK-Libraries mit `Action<T>`-Konfiguration siehe die dokumentierte Abweichung in `dotnet-sdk-builder`") schließt die Lücke.

#### M-4 — `dotnet-ef-core`: vage „Consider …"-Bullets ohne Handlungsanleitung

**Datei:** `dotnet-ef-core/SKILL.md`

Mehrere Bullets sind nicht aktionabel: „Consider using transactions for multiple operations" (wann? Wie verhält sich das zum eigenen „SaveChanges once per unit of work"?), „Consider database functions for complex operations", „Consider snapshot testing for model changes", „Consider data encryption for sensitive information". Andere Bullets im selben File zeigen, wie es geht (Pagination, Chunked-Save — mit Bedingung, Code, Begründung). Zudem doppelt „Use parameterized queries" (Security, Zeile 71) das präzisere Raw-SQL-Bullet zwei Zeilen darunter. Das Test-Artefakt `efcore-bullet-actionability-test.md` zeigt, dass das Problem bekannt ist — der Rest-Bestand sollte nachgezogen werden.

#### M-5 — `dotnet-dev` hat keinen nicht-interaktiven Modus

**Datei:** `dotnet-dev/SKILL.md`

Jede Phase endet in einem harten Gate („STOP … wait for confirmation"), Phase 2 verlangt bis zu 8 Einzel-Roundtrips. `dotnet-reviewer` definiert für dieselbe Situation (Sub-Agent, kein User erreichbar) explizite Defaults und Herkunfts-Protokollierung — `dotnet-dev` nicht. In Headless-/Automations-Kontexten (CI, geplante Agents, Sub-Agent-Dispatch) blockiert der Workflow ohne definiertes Verhalten. Entweder explizit dokumentieren „nur interaktiv verwendbar" oder einen Non-Interactive-Pfad analog zum Reviewer definieren.

#### M-6 — `dotnet-tester` Phase 3 setzt Subagents voraus, ohne Fallback

**Datei:** `dotnet-tester/SKILL.md:141`

„Start a **separate agent** …" — in Umgebungen ohne Subagent-Fähigkeit (Claude.ai, eingeschränkte Harnesses) ist Phase 3 nicht ausführbar; ein Inline-Fallback („führe die Analyse selbst mit demselben Prompt-Template aus, akzeptiere den Verlust der Unabhängigkeit") fehlt.

#### M-7 — Versionsspezifische Checkliste existiert nur für net10; `net<N>`-Mechanik undefiniert für künftige Versionen ✅ behoben (2026-08-03)

**Dateien:** `dotnet-reviewer/SKILL.md` (Step 6.1), `references/review-checklist-net10.md`

Step 6 verweist generisch auf `review-checklist-net<N>.md`, vorhanden ist nur `-net10`. Sobald `net11.0` als Target auftaucht, ist das Verhalten undefiniert (Datei fehlt; kein dokumentierter Fallback wie „nimm die höchste vorhandene ≤ N"). Ein Satz genügt.

**Behoben (2026-08-03)** — Step 6.1 definiert die Auswahl explizit: exakte Datei → sonst höchste vorhandene `net<M>` mit `M ≤ N` (Substitution im Report benannt) → sonst nur die versionsneutralen Checklisten (ebenfalls benannt). `review-checklist-net10.md` beschreibt seine Geltung jetzt als „höchster Major ≥ 10". Stillschweigende Substitution steht unter „Things This Skill Never Does".

#### M-8 — `error-handling.md`: defekter `type`-URI und fehlende `IProblemDetailsService`-Integration

**Datei:** `dotnet-aspnet/references/error-handling.md`

Das Beispiel setzt `Type = "https://httpstatuses.com/500"` — die Domain ist seit Jahren tot (Nachfolger httpstatuses.io); RFC 9457 sieht `about:blank` als Default vor, wenn kein eigener Problem-Type dokumentiert wird. Außerdem schreibt der `IExceptionHandler` die Response manuell (`WriteAsJsonAsync`), statt den registrierten `AddProblemDetails`-Customizer über `IProblemDetailsService.TryWriteAsync` zu nutzen — dadurch geht die im selben File konfigurierte `traceId`-Extension im Fehlerpfad verloren. Die beiden Beispiele wirken zusammengehörig, sind aber nicht integriert.

#### M-9 — Router: Kompositions-Notiz unvollständig

**Datei:** `dotnet/SKILL.md:47-48`

„`dotnet-sdk-builder` invokes `dotnet-xmldocs` and `dotnet-tester`" — laut sdk-builder Step 7 wird auch `dotnet-nuget-manager` invoked (und so steht es in dessen Related-Skills-Block: „Invoked in Step 7"). Da der Router nach dem C-7-Fix die einzige vollständige Beziehungsquelle sein soll, wiegt die Auslassung dort mehr als anderswo.

---

### Niedrig

#### N-1 — Router-Label „Knowledge skills (best practices, `references/` only)" trifft auf `dotnet-ef-core` nicht zu

`dotnet-ef-core` hält fast den gesamten Inhalt in der SKILL.md (nur Concurrency ist ausgelagert) — bei `dotnet-aspnet`/`dotnet-fundamentals` ist es umgekehrt. Entweder Label präzisieren oder ef-core strukturell angleichen. Rein kosmetisch, kann aber die Erwartung „Details stehen immer in references/" enttäuschen.

#### N-2 — `dotnet-fundamentals`-Description transportiert die Baseline-Rolle nicht ✅ behoben (2026-08-02)

**Status:** Behoben — Baseline-Klausel („Also use as the baseline whenever any C# production code is written or modified … load it alongside them, not instead of them") an die Description angehängt; per Selection-Probe (RED→GREEN) verifiziert, siehe `skills/dotnet/tests/description-selection-test.md`, Abschnitt „Re-Run 2026-08-02".

SKILL.md sagt: „Writing or modifying **any** C# production code — this is the baseline skill; … load this skill alongside them". Die Frontmatter-Description nennt nur die Einzelthemen (DI, Options, Config, Idiome). Da die Description der primäre Trigger ist, droht Undertriggering genau in dem Fall, für den die Baseline gedacht ist (allgemeiner C#-Code ohne DI/Options-Stichwort).

#### N-3 — `dotnet-tester` nennt `dotnet-fundamentals` nicht unter Related Skills ✅ behoben (2026-08-02)

**Status:** Behoben — Eintrag an erster Stelle des Related-Skills-Blocks ergänzt (neutrale Formulierung gemäß C-7-Konvention, keine Invoke-Behauptung).

Testcode profitiert unmittelbar von den fundamentals-Idiomen (CancellationToken in async-Tests, `required`/`init` in Test-Fixtures); aspnet/ef-core/sdk-builder verweisen alle auf fundamentals, tester nicht. Kleine Konsistenzlücke.

#### N-4 — `openapi-and-cross-cutting.md`: Legacy-Syntax im .NET-9+-Kontext ✅ behoben (2026-08-02)

**Status:** Behoben — beide `tags: new[] { "ready" }`-Vorkommen durch Collection Expressions (`tags: ["ready"]`) ersetzt; per Grep bestätigt, dass keine weiteren Legacy-Collection-Vorkommen in den Skill-Referenzen existieren.

`tags: new[] { "ready" }` statt Collection Expression (`["ready"]`) — genau das Muster, das `review-checklist-net10.md` flaggen würde. Die Referenzen sollten dem eigenen Review-Standard genügen.

---

## 3. Kurzbewertung pro Skill

| Skill | Qualität | Anmerkungen |
|---|---|---|
| `dotnet` (Router) | Gut | Klare Zwei-Kategorien-Struktur; Lücke: `dotnet-dev` fehlt (H-2), Kompositions-Notiz unvollständig (M-9) |
| `dotnet-fundamentals` | Gut | Starke Referenzen (DI, Options, Config); Primary-Constructors-Stub (H-3), Description zu eng (N-2) |
| `dotnet-aspnet` | Gut | Saubere Abgrenzung zum Fundamentals-Skill, starkes auth.md; middleware.md zu dünn (M-1), Integrationstests fehlen (H-5), error-handling nicht integriert (M-8) |
| `dotnet-ef-core` | Befriedigend | Fachlich korrekt, gute Testing-/Pagination-/Security-Teile; etliche vage Bullets (M-4), Strukturausreißer (N-1) |
| `dotnet-xmldocs` | Sehr gut | Präzise Microsoft-Formeln, kanonisches Beispiel mit Präzedenzregel — vorbildlich |
| `dotnet-sdk-builder` | Sehr gut | Klarer Workflow mit Nutzer-Entscheidungspunkten, dokumentierte Abweichung vom Fundamentals-Pattern, vollständige Codebeispiele |
| `dotnet-tester` | Gut | „Never Fake a Green Test" ist herausragend; Subagent-Abhängigkeit ohne Fallback (M-6) |
| `dotnet-reviewer` | Gut | Skripte, Exit-Code-Verträge, Non-Interactive-Modus, eigene Testsuite; .NET-10-Beschränkung (K-1) und fehlender net\<N\>-Fallback (M-7) ✅ behoben 2026-08-03, falscher Querverweis (H-1) ✅ behoben |
| `dotnet-inspect` | Gut | Exzellente Decision-Tree-Struktur; `dnx`-Voraussetzung undokumentiert (H-4) |
| `dotnet-nuget-manager` | Gut | Klare Core Rules mit begründetem Hand-Edit-Fallback, CPM/VersionOverride-Falle abgedeckt |
| `dotnet-dev` | Gut (mit Vorbehalt) | Konsequentes Anti-Rationalisierungs-Design (Waiver vs. n/a vs. silent skip ist stark); K-1, keine Non-Interactive-Fähigkeit (M-5). Die hohe MUST-/Gate-Dichte ist erkennbar bewusst gewählt, steht aber in Spannung zur Skill-Writing-Leitlinie „explain the why in lieu of heavy-handed MUSTs" — bei Kleinstaufgaben ist mit Nutzer-Reibung zu rechnen (8 Roundtrips vor der ersten Codezeile) |

## 4. Empfohlene Reihenfolge der Behebung

1. **K-1** — Versionskonflikt `dotnet-dev` ↔ `dotnet-reviewer` auflösen (blockiert den Kern-Workflow für .NET 8/9). ✅ erledigt (2026-08-03), zusammen mit **M-7**
2. **H-1** — Querverweis in der Architektur-Checkliste korrigieren (Ein-Zeilen-Fix, faktisch falsch). ✅ erledigt (2026-08-02)
3. **H-2, M-9** — Router vervollständigen (`dotnet-dev` + Vorrangregel; sdk-builder-Komposition).
4. **H-3** — Primary-Constructors-Inhalt in `modern-patterns.md` nachliefern.
5. **H-4** — `dnx`-Voraussetzung in `dotnet-inspect` dokumentieren.
6. **H-5** — Ort für ASP.NET-Core-Integrationstests schaffen.
7. **M-1 … M-8, N-1 … N-4** — in beliebiger Reihenfolge, jeweils lokal begrenzte Edits.

---

*Erstellt durch Skill-Review am 2026-08-02. Grundlage: vollständige Lektüre aller SKILL.md- und references/-Dateien unter `skills/dotnet/` im Stand von Commit `83c881d`.*
