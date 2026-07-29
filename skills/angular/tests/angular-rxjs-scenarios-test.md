# angular-rxjs — Testszenarien (TDD für Skills)

Alle Szenarien werden als general-purpose Subagents ausgeführt.
Baseline (RED): Prompt ohne Skill. GREEN: identischer Prompt, davor der komplette SKILL.md-Inhalt mit der Anweisung, ihn als geladenen Skill zu befolgen.

Gemeinsamer Prompt-Rahmen: "You are working in an Angular 21 application (standalone components, zoneless, default new-project setup). Do NOT read or explore any repository — answer entirely from your own knowledge, producing code directly in your final message. Your final message is raw output for analysis, not a user-facing message."

## S1 — Typeahead (Operatorwahl + Lifecycle)

Task: Implement a typeahead search box component. As the user types into an input, call `SearchService.search(term: string): Observable<Result[]>` (already injectable) and show the results in the template. Requirements: don't hammer the API on every keystroke, and stale responses must never overwrite newer ones.
Produce the complete component (TypeScript + inline template). Briefly explain your choices (2-3 sentences).

Prüfkriterien: switchMap (nicht mergeMap/concatMap), debounceTime + distinctUntilChanged, kein manuelles subscribe (toSignal oder async pipe), kein destroy$-Boilerplate, Fehlerbehandlung im inneren Stream.

## S2 — Memory-Leak-Fix (Subscription-Lifecycle)

Gegebener Code: OrdersComponent mit verschachtelten subscribes (getOrders → forEach → getCustomer), kein Unsubscribe, orders-Array wird gepusht.
Task: Fix it following current Angular best practices. Produce the fixed component and briefly explain what was wrong (2-3 sentences).

Prüfkriterien: verschachtelte subscribes durch Higher-Order-Operator (switchMap + forkJoin) ersetzt, takeUntilDestroyed statt destroy$-Subject (oder deklarativ via toSignal/async pipe ohne subscribe), keine ngOnDestroy-Boilerplate, moderne Template-Syntax (@for) akzeptabel aber nicht Pflicht.

## S3 — Observable → Template (Signals-Interop, zoneless)

Gegeben: `AuthService.currentUser$: Observable<User | null>` (Shared Library, nicht änderbar).
Task: Header-Komponente: Name anzeigen wenn eingeloggt, "Admin"-Badge wenn `user.roles` 'admin' enthält. Idiomatisch für diese Angular-Version.

Prüfkriterien: toSignal(...) + computed für abgeleiteten Zustand (async pipe mehrfach im Template oder subscribe + Property sind Baseline-Fehler), initialValue/undefined-Handling korrekt, keine doppelte Subscription des kalten Streams.

## S4 — RxJS testen (Vitest, zoneless)

Gegeben: ProductSearchFacade mit query$-Subject, debounceTime(300), distinctUntilChanged, switchMap auf HttpClient, catchError → of([]).
Task: Unit tests covering debouncing, switchMap cancellation, error fallback. Complete spec file + testing approach (2-3 sentences).

Prüfkriterien: kein fakeAsync/tick (zone.js fehlt in zoneless-Projekten!), stattdessen TestScheduler/Marbles oder Vitest fake timers, provideHttpClientTesting + HttpTestingController korrekt, keine done-Callback-Race-Patterns, flush von Requests nach Ablauf des Debounce.

## Baseline-Ergebnisse (RED)

### S1 Typeahead — BESTANDEN (überraschend gut)
signal + toObservable → debounceTime(300) + distinctUntilChanged + switchMap → toSignal(initialValue). Kein subscribe, kein destroy$-Boilerplate, leerer Term kurzgeschlossen mit of([]). OnPush, @if/@for.
Einzige Lücke: **keine Fehlerbehandlung im inneren Stream** — ein HTTP-Fehler beendet den Typeahead-Stream dauerhaft (kein catchError am inneren Observable). Das erwähnte der Agent nicht einmal.

### S2 Leak-Fix — BESTANDEN
Verschachtelte subscribes → switchMap + forkJoin, Kunden dedupliziert, toSignal statt manueller Subscription, @for mit track, zoneless-Begründung korrekt.
Lücke: auch hier **kein catchError** — ein einziger fehlgeschlagener getCustomer-Call lässt forkJoin und damit den ganzen Stream fehlschlagen; orders bleibt leer, kein Hinweis darauf.

### S3 Interop — BESTANDEN
toSignal(initialValue: null) + computed für isAdmin, @if mit as-Aliasing, korrekte zoneless-Begründung. Keine nennenswerten Lücken (Erstausgabe enthielt einen Tippfehler im Template, selbst korrigiert).

### S4 Testing — BESTANDEN (stark)
Vitest fake timers (vi.useFakeTimers/advanceTimersByTime) statt fakeAsync — mit expliziter zoneless-Begründung. provideHttpClientTesting + HttpTestingController, req.cancelled-Assertion für switchMap-Cancellation, Test dass der Stream nach Fehler weiterlebt, httpMock.verify() in afterEach. Keine nennenswerten Lücken.

### S5 Resource-API-Versionswissen — TEILWEISE
Angular-21-Status korrekt gewusst (developer preview seit v20, v19→v20-Breaking-Changes request→params, ResourceStatus-Union). Angular 22 aber: "post-cutoff … likely-but-unverified" — konnte die Stabilisierung in v22 nicht bestätigen. → Skill soll den verifizierten Fakt pinnen: resource/rxResource/httpResource stabil ab Angular 22 (Mai 2026), developer preview in 21.

### Muster über alle Baselines
Moderne Interop-Patterns (toSignal/computed/takeUntilDestroyed-Ära) sind bereits Baseline-Wissen. Die tatsächliche Lücke: **Fehlerbehandlung wird systematisch weggelassen** (Stream-Termination durch unbehandelte Fehler in switchMap/forkJoin). Skill-Fokus entsprechend schärfen.

## Ergebnisse mit Skill (GREEN)

### S1 Typeahead — BESTANDEN
Inneres catchError innerhalb von switchMap vorhanden, Begründung nennt explizit das Outer-Placement-Problem ("permanently complete the outer stream and silently kill the feature"). Alle Baseline-Stärken erhalten (switchMap, debounce, toSignal, initialValue).

### S2 Leak-Fix — BESTANDEN
Per-Source-catchError in forkJoin mit Fallback-Wert ('Unknown customer') + äußeres catchError für getOrders — beide Baseline-Lücken geschlossen. Agent referenziert die Skill-Regeln explizit ("forkJoin (dedupe inputs first)", "template-feeding stream must survive errors"). Alle Baseline-Stärken erhalten.

### S5 Resource-API — BESTANDEN
Benennt sicher: developer preview in 21, stabil ab Angular 22 (Mai 2026). Empfehlung (httpResource heute, Risiko explizit pinnen, Mutationen klassisch) deckungsgleich mit Skill. Übernimmt die Common-Mistake-Regel wörtlich.

### Fazit
Alle drei zuvor lückenhaften Szenarien bestehen mit Skill; keine neuen Fehlinterpretationen beobachtet → REFACTOR ohne Befund. S3/S4 bestanden bereits die Baseline; die Skill-Inhalte zu Interop/Testing decken sich mit deren Baseline-Verhalten (kein Degradationsrisiko erkennbar), daher nicht erneut gelaufen.
