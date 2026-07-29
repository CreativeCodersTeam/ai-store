# angular-reviewer (Reactivity-Checkliste) — Testszenarien (TDD für Skills)

Alle Szenarien werden als general-purpose Subagents ausgeführt und simulieren Step 6 (Review) des angular-reviewer-Workflows.
Baseline (RED): Prompt mit den **fünf bestehenden Checklisten** + Severity-Taxonomie. GREEN: identischer Prompt, zusätzlich `review-checklist-reactivity.md` als sechste Checkliste.

Gemeinsamer Prompt-Rahmen (englisch, wörtlich):

> You are performing Step 6 (Review) of a structured Angular code review on an Angular 20 project (standalone components, signals available). First read ONLY these checklist files (they are your complete review criteria): `<Liste der Checklisten-Pfade>`. Do not read or explore anything else — the diff below is complete and self-contained. Review the diff strictly against those checklists. Report every finding as `[Severity][Area] path:line` (line numbers approximate is fine) with a one-sentence description and a `typescript`-fenced fix suggestion. Order findings by severity. Your final message is raw output for analysis, not a user-facing message.

Checklisten-Pfade: die fünf bestehenden `references/review-checklist-*.md` + `severity-taxonomy.md` (RED); GREEN zusätzlich `review-checklist-reactivity.md`. Danach im Prompt: der Fixture-Diff (als neue Dateien).

Bewertung pro Seed: **gefunden** (Kernproblem korrekt benannt) / **teilweise** (Stelle geflaggt, aber falsches/oberflächliches Problem) / **verfehlt**. Zusätzlich: False Positives auf den Decoys (korrekter Code, der NICHT geflaggt werden darf).

## R1 — Component-Fixture (Leaks, Races, Side Effects in Komponenten)

Der Diff fügt drei neue Dateien hinzu:

### `src/app/search/customer-search.component.ts`

```typescript
import { Component, ChangeDetectionStrategy, OnInit, inject, signal } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { AsyncPipe } from '@angular/common';
import { Subject, mergeMap, debounceTime, distinctUntilChanged, map } from 'rxjs';
import { CustomerApi, Customer } from '../api/customer-api';

@Component({
  selector: 'app-customer-search',
  standalone: true,
  imports: [AsyncPipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <input #box (input)="term$.next(box.value)" placeholder="Search customers" />
    <p>Searches so far: {{ searchCount }}</p>
    @if (results$ | async; as results) {
      <ul>
        @for (c of results; track c.id) {
          <li>{{ c.name }}</li>
        }
      </ul>
    }
  `,
})
export class CustomerSearchComponent implements OnInit {
  private readonly api = inject(CustomerApi);
  private readonly route = inject(ActivatedRoute);

  protected searchCount = 0;
  protected readonly term$ = new Subject<string>();

  protected readonly results$ = this.term$.pipe(
    debounceTime(300),
    distinctUntilChanged(),
    map(term => {
      this.searchCount++;
      return term.trim();
    }),
    mergeMap(term => this.api.search(term)),
  );

  ngOnInit(): void {
    this.route.queryParams.subscribe(params => {
      if (params['q']) {
        this.term$.next(params['q']);
      }
    });
  }
}
```

### `src/app/dashboard/dashboard.component.ts`

```typescript
import { Component, ChangeDetectionStrategy, OnInit, OnDestroy, inject, signal, computed } from '@angular/core';
import { Subject, takeUntil } from 'rxjs';
import { DashboardApi, Summary, Widget } from '../api/dashboard-api';
import { SummaryCache } from '../api/summary-cache';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <h2>Dashboard ({{ totalWidgets() }} widgets)</h2>
    <p>{{ summary?.headline }}</p>
  `,
})
export class DashboardComponent implements OnInit, OnDestroy {
  private readonly api = inject(DashboardApi);
  private readonly cache = inject(SummaryCache);
  private readonly destroy$ = new Subject<void>();

  protected summary: Summary | undefined;
  protected readonly widgets = signal<Widget[]>([]);
  private readonly lastComputedAt = signal(0);

  protected readonly totalWidgets = computed(() => {
    this.lastComputedAt.set(Date.now());
    return this.widgets().length;
  });

  ngOnInit(): void {
    this.cache.summary$
      .pipe(takeUntil(this.destroy$))
      .subscribe(s => (this.summary = s));

    this.api.loadSummary()
      .pipe(takeUntil(this.destroy$))
      .subscribe(s => (this.summary = s));

    this.api.loadWidgets()
      .pipe(takeUntil(this.destroy$))
      .subscribe(w => this.widgets.set(w));

    window.addEventListener('resize', this.onResize);

    setInterval(() => {
      this.api.loadWidgets().subscribe(w => this.widgets.set(w));
    }, 30_000);
  }

  ngOnDestroy(): void {
    this.widgets.set([]);
  }

  private readonly onResize = () => {
    this.lastComputedAt.set(Date.now());
  };
}
```

### `src/app/settings/settings-form.component.ts`

```typescript
import { Component, ChangeDetectionStrategy, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule } from '@angular/forms';
import { toSignal, takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { Subject, exhaustMap } from 'rxjs';
import { SettingsApi, Profile } from '../api/settings-api';
import { ToastService } from '../ui/toast.service';

@Component({
  selector: 'app-settings-form',
  standalone: true,
  imports: [ReactiveFormsModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <form [formGroup]="form">
      <input formControlName="displayName" />
      <button type="button" (click)="save()">Save</button>
      <button type="button" (click)="export$.next()">Export</button>
    </form>
    <p>Plan: {{ profile()?.plan }}</p>
  `,
})
export class SettingsFormComponent {
  private readonly api = inject(SettingsApi);
  private readonly toast = inject(ToastService);
  private readonly fb = inject(FormBuilder);

  protected readonly form = this.fb.group({ displayName: [''] });

  protected readonly profile = toSignal(this.api.profile$, { initialValue: undefined });

  protected readonly export$ = new Subject<void>();

  constructor() {
    this.export$
      .pipe(
        exhaustMap(() => this.api.exportSettings()),
        takeUntilDestroyed(),
      )
      .subscribe(() => this.toast.show('Export ready'));
  }

  save(): void {
    this.api.saveSettings(this.form.getRawValue()).subscribe(() => {
      this.toast.show('Saved');
    });
  }
}
```

### Prüfkriterien R1 (Seeds)

| Seed | Stelle | Erwarteter Befund |
|---|---|---|
| A1 | customer-search `ngOnInit` | `route.queryParams.subscribe` ohne Teardown → Subscription-Leak |
| A2 | dashboard `destroy$`/`ngOnDestroy` | `takeUntil(this.destroy$)`, aber `destroy$` feuert nie (`ngOnDestroy` ohne `next()`/`complete()`) → alle drei Streams leaken trotz sichtbarem "Teardown" |
| B1 | dashboard `ngOnInit` | `window.addEventListener('resize', …)` ohne `removeEventListener` → Memory-Leak, Komponente bleibt referenziert |
| B2 | dashboard `ngOnInit` | `setInterval` ohne `clearInterval` → Timer + innere Subscription leben ewig; innere `subscribe` zusätzlich ohne Teardown |
| C1 | customer-search `results$` | `mergeMap` im Typeahead → veraltete Response kann neuere überschreiben; `switchMap` nötig |
| C2 | settings-form `save()` | Subscribe pro Klick ohne `exhaustMap`/Busy-Guard → Doppel-Submit-Race; zusätzlich Subscription ohne Teardown |
| C3 | dashboard `ngOnInit` | `cache.summary$` und `api.loadSummary()` schreiben beide `this.summary` → Last-write-wins-Race |
| D1 | customer-search `results$` | Zustandsmutation (`this.searchCount++`) in `map` → Side Effect in purem Operator |
| D2 | dashboard `totalWidgets` | Signal-Write (`lastComputedAt.set`) innerhalb `computed()` → Side Effect in Derivation |

Decoys (dürfen NICHT geflaggt werden): `export$`-Stream in settings-form (korrekt: `exhaustMap` + `takeUntilDestroyed`), `toSignal(…, { initialValue })` für `profile`.

## R2 — Service/Stream-Fixture (shareReplay, Cache, kalte Observables, effect)

Der Diff fügt zwei neue Dateien hinzu:

### `src/app/live/live-data.service.ts`

```typescript
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, shareReplay } from 'rxjs';
import { WebsocketClient, Tick } from './websocket-client';
import { CustomerDetail } from '../api/customer-api';

@Injectable({ providedIn: 'root' })
export class LiveDataService {
  private readonly http = inject(HttpClient);
  private readonly ws = inject(WebsocketClient);

  private readonly detailCache = new Map<string, CustomerDetail>();

  readonly ticks$: Observable<Tick> = this.ws.stream('ticks').pipe(
    shareReplay(1),
  );

  readonly config$ = this.http.get<Record<string, string>>('/api/config').pipe(
    shareReplay({ bufferSize: 1, refCount: true }),
  );

  customerDetail(id: string): Observable<CustomerDetail> {
    return new Observable<CustomerDetail>(subscriber => {
      const cached = this.detailCache.get(id);
      if (cached) {
        subscriber.next(cached);
        subscriber.complete();
        return;
      }
      this.http.get<CustomerDetail>(`/api/customers/${id}`).subscribe(detail => {
        this.detailCache.set(id, detail);
        subscriber.next(detail);
        subscriber.complete();
      });
    });
  }
}
```

### `src/app/orders/orders-widget.component.ts`

```typescript
import { Component, ChangeDetectionStrategy, OnInit, inject, signal, effect } from '@angular/core';
import { AsyncPipe } from '@angular/common';
import { OrdersApi, Order, CustomerRef } from '../api/orders-api';
import { WebsocketClient } from '../live/websocket-client';

@Component({
  selector: 'app-orders-widget',
  standalone: true,
  imports: [AsyncPipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <h3>Orders ({{ (orders$ | async)?.length ?? 0 }})</h3>
    @if (orders$ | async; as orders) {
      <ul>
        @for (o of orders; track o.id) {
          <li>{{ o.title }}</li>
        }
      </ul>
    }
    <p>Customers loaded: {{ customers.length }}</p>
  `,
})
export class OrdersWidgetComponent implements OnInit {
  private readonly api = inject(OrdersApi);
  private readonly ws = inject(WebsocketClient);

  protected readonly orders$ = this.api.getOrders();
  protected readonly customers: CustomerRef[] = [];
  protected readonly channel = signal('orders-default');

  constructor() {
    effect(() => {
      const id = this.channel();
      this.ws.on(id, message => this.handleMessage(message));
    });
  }

  ngOnInit(): void {
    this.api.getOrders().subscribe(orders => {
      orders.forEach(order => {
        this.api.getCustomer(order.customerId).subscribe(customer => {
          this.customers.push(customer);
        });
      });
    });
  }

  private handleMessage(message: unknown): void {
    this.channel.set(String(message));
  }
}
```

### Prüfkriterien R2 (Seeds)

| Seed | Stelle | Erwarteter Befund |
|---|---|---|
| A3 | live-data `ticks$` | `shareReplay(1)` (refCount false) auf endlosem WS-Stream → Quelle lebt nach letztem Abonnenten ewig weiter (Leak) |
| B3 | live-data `detailCache` | Unbegrenzte `Map` in root-Service → wächst unbeschränkt, keine Eviction |
| C4 | orders-widget `ngOnInit` | Verschachtelte `subscribe`s + `push` in geteiltes Array → nichtdeterministische Reihenfolge, kein Teardown; `forkJoin`/Higher-Order-Operator nötig |
| D3 | orders-widget Template + `orders$` | Kaltes HTTP-Observable zweimal per `async` gebunden **plus** drittes `getOrders()` in `ngOnInit` → drei separate HTTP-Requests (Side Effect pro Subscription); sharen oder `toSignal` |
| D5 | orders-widget `effect()` | `effect` registriert WS-Listener ohne Cleanup-Callback → bei jedem `channel`-Wechsel zusätzlicher Listener, alte bleiben aktiv |

Decoy (darf NICHT geflaggt werden): `config$` (`shareReplay({ bufferSize: 1, refCount: true })` auf komplettierendem HTTP-GET).

## Baseline-Ergebnisse (RED)

### R1 Component — DETEKTION BESTANDEN, SEVERITY-KALIBRIERUNG NICHT

| Seed | Ergebnis |
|---|---|
| A1 `queryParams.subscribe` ohne Teardown | **gefunden** — [Major] |
| A2 `destroy$` feuert nie | **gefunden** — [Major], "declared but ngOnDestroy never calls next()/complete() … all three subscriptions leak" |
| B1 resize-Listener | **gefunden** — [Major], `DestroyRef.onDestroy`-Fix |
| B2 `setInterval` ohne clear | **gefunden** — [Major], `timer` + `takeUntilDestroyed`-Fix |
| C1 `mergeMap`-Typeahead | **gefunden** — [Major], switchMap-Fix |
| C2 Doppel-Submit `save()` | **teilweise** — nur [Suggestion][Performance]; die Race (doppelter Schreib-Request) wird als Stil-Empfehlung eingestuft, nicht als Fehler |
| C3 Last-write-wins auf `summary` | **gefunden, unterbewertet** — [Minor][Architecture]; nichtdeterministisches UI als Minor |
| D1 `searchCount++` in `map` | **gefunden** — [Minor], tap+signal-Fix |
| D2 Signal-Write in `computed()` | **gefunden** — [Critical] (NG0600) |

Decoys: `export$` (exhaustMap+takeUntilDestroyed) nicht geflaggt ✓; `toSignal(…, { initialValue: undefined })` als [Nitpick] "redundant" geflaggt — kosmetisch, kein inhaltlicher False Positive, aber notiert.

### R2 Service/Stream — WEITGEHEND BESTANDEN

| Seed | Ergebnis |
|---|---|
| A3 `shareReplay` ohne refCount | **gefunden** — [Major][Performance], Fix exakt `shareReplay({ bufferSize: 1, refCount: true })` |
| B3 unbegrenzter Cache | **teilweise** — nur [Suggestion][Performance] als Invalidierungs-Thema ("grows unboundedly … stale details"), nicht als Memory-Leak mit Major-Gewicht |
| C4 verschachtelte subscribes | **gefunden** — [Major], forkJoin + Dedup + `takeUntilDestroyed`; Race-Aspekt (Reihenfolge) implizit über "unbounded N+1 fan-out", Mutation-unter-OnPush separat als [Major][Angular-Idioms] |
| D3 kaltes Observable, 3 Subscriptions | **gefunden** — [Major], "three identical HTTP requests", Fix `shareReplay`/`toSignal` |
| D5 `effect()` ohne Cleanup | **gefunden** — [Critical], `onCleanup`-Fix inkl. Erkennung der Selbsttrigger-Schleife |

Decoy `config$`: nicht geflaggt, sogar explizit als korrekt gelobt. Darüber hinaus wertvolle Zusatzbefunde (fehlende Teardown-Funktion im handgerollten Observable, verschluckte HTTP-Fehler, fehlende Request-Dedupe).

Fazit R2: Die bestehenden Checklisten (Performance: shareReplay/nested subscribes; Code-Quality: Teardown & Resources) tragen bereits weit. Echte Lücke nur: **unbegrenzte Caches werden nicht als Memory-Leak klassifiziert** (Severity/Framing).

### R1 Component, Zweitmodell Haiku 4.5 — DURCHGEFALLEN (3 von 9 Seeds verfehlt)

| Seed | Ergebnis |
|---|---|
| A1 | **gefunden** [Major] (Fix leicht fehlerhaft: `takeUntilDestroyed()` in `ngOnInit` ohne DestroyRef) |
| A2 `destroy$` feuert nie | **VERFEHLT** — die drei `takeUntil`-Streams wurden als korrekt behandelt |
| B1 | **gefunden** [Major] |
| B2 | **gefunden** [Major] |
| C1 `mergeMap`-Typeahead | **VERFEHLT** — obwohl in der Performance-Checkliste ("switchMap … typeahead") explizit steht; der eigene Fix-Vorschlag zu D1 behielt `mergeMap` sogar bei |
| C2 Doppel-Submit | **VERFEHLT** — `save()` nur als "lacks teardown" geflaggt (mit unbrauchbarem `takeUntilDestroyed`-Fix), Race nicht erkannt |
| C3 | **gefunden** [Major][Architecture] ("race condition where the last one wins"), Fix-Code allerdings schwach |
| D1 | **gefunden** [Major] |
| D2 | **gefunden** [Major] |

Decoys: beide sauber (kein False Positive).

### R2 Service/Stream, Zweitmodell Haiku 4.5 — DURCHGEFALLEN (2 von 5 Seeds verfehlt)

| Seed | Ergebnis |
|---|---|
| A3 `shareReplay` ohne refCount | **gefunden** [Major] — aber primär als "Inkonsistenz" zum korrekten `config$` geframt (Fund verdankt sich dem Decoy-Kontrast), Leak nur in Klammern |
| B3 unbegrenzter Cache | **VERFEHLT** — mit keinem Wort erwähnt |
| C4 verschachtelte subscribes | **gefunden** [Critical] — Teardown/N+1/OnPush benannt, Reihenfolge-Race implizit über `concatMap`+`toArray`-Fix |
| D3 kaltes Observable, 3 Subscriptions | **VERFEHLT** — doppelte HTTP-Requests nirgends erkannt (nur generischer toSignal-Refactor-Vorschlag) |
| D5 `effect()` ohne Cleanup | **gefunden** [Major] |

Decoy `config$`: sauber ✓.

### Muster über alle Baselines (RED-Fazit)

1. **Detektion hängt am Modellwissen, nicht an den Checklisten**: Fable 5 fand alle 14 Seeds, aber A2 (kaputtes `destroy$`-Wiring), B3 (unbegrenzter Cache), C3 (Multi-Writer-Race), D1 (Side Effect in `map`), D2 (Signal-Write in `computed`), D3 (kaltes Observable mehrfach subscribed) und D5 (`effect` ohne Cleanup) stehen in **keiner** Checkliste — Haiku 4.5 verfehlte prompt 5 von 14 Seeds (A2, C1, C2, B3, D3), obwohl C1 (`mergeMap`-Typeahead) sogar explizit in der Performance-Checkliste steht. Race Conditions sind die schwächste Kategorie.
2. **Severity-Kalibrierung fehlt**: Selbst bei Fund werden Races/Leaks herabgestuft — C2 als [Suggestion], C3 als [Minor], B3 (unbegrenzter Cache) als [Suggestion]-Invalidierungsthema statt Memory-Leak.
3. **Kein passender Area-Tag**: Leaks/Races/Side-Effects verteilen sich auf Performance/Code-Quality/Architecture; die vier Zielkategorien sind im Report nicht identifizierbar.

→ GREEN-Checkliste adressiert genau: explizite Flag-Regeln für A2/C1–C4/D1–D5-Muster, Severity-Vorgaben (Leaks/Races default Major), Reactivity-Area-Tag.

## Ergebnisse mit Skill (GREEN)

_(wird nach den GREEN-Läufen ausgefüllt)_
