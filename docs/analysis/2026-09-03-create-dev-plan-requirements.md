Lege einen Skill create-dev-plan unter skills/development an. Der Skill soll zusammen mit dem User aus einer Anfordeung einen Plan für die Entwicklung erstellen. Prüfe meine folgenden Vorschläge für das Vorgehen auf Lücken, Fallstricke und Fehler. Ignoriere alle anderen Skills und Dokument in diesem Repo bei der Erstellung, außer den Skill create-dev-spec.

Input des Users muss entweder ein Spec Dokument aus dem create-dev-spec ein, oder eine Anforderung in Form von direktem Text, Issue Url oder einem anderen Anforderungsdokument.

Ist der Input kein komplettes Spec Dokument, dann frage den User, ob er zuerst mit Hilfe des create-dev-spec ein Spec Dokument erstellt werden soll, mit dem dann hier weitergearbeitet wird.

Vorgehen:
1. Spec-Review vor dem Planen. Die Spec einmal komplett lesen und jede Anforderung markieren, die unklar, widersprüchlich oder unvollständig ist. Offene Fragen klären, bevor der Plan entsteht. Ein Plan auf Basis von Annahmen ist der häufigste Grund für Nacharbeit.

2. Scope prüfen und schneiden. Deckt die Spec mehrere unabhängige Teilsysteme ab, gehört sie in mehrere Pläne. Jeder Plan sollte für sich lauffähige, testbare Software liefern.

3. Globale Constraints herausziehen. Versionsuntergrenzen, erlaubte Abhängigkeiten, Namenskonventionen, Plattformvorgaben. Diese stehen wörtlich am Anfang des Plans, weil sie implizit für jede Aufgabe gelten.

4. Bestehenden Code verstehen. Welche Module, Muster und Konventionen gibt es schon? Der Plan muss sich an das Vorhandene anlehnen, nicht dagegen arbeiten.

5. Dateistruktur festlegen. Vor der Aufgabenliste festhalten, welche Dateien neu entstehen oder geändert werden und wofür jede verantwortlich ist. Hier werden die Zerlegungsentscheidungen fixiert: eine Verantwortung pro Datei, zusammen ändernde Dinge liegen zusammen.

6. Schnittstellen zwischen Aufgaben definieren. Für jede Aufgabe: Was konsumiert sie von vorherigen Aufgaben, was liefert sie für spätere? Exakte Namen, Signaturen, Typen. Wer nur eine Aufgabe bearbeitet, erfährt sonst nicht, wie die Nachbarn heißen.

7. Aufgaben richtig dimensionieren. Eine Aufgabe ist die kleinste Einheit mit eigenem Testzyklus, die ein Reviewer separat abnehmen oder ablehnen könnte. Setup, Konfiguration und Doku gehören in die Aufgabe, deren Ergebnis sie braucht. Bilde die Anhängigkeit zwischen den Aufgaben explizit ab.

8. Erstelle eine detaillierte Task Liste der Aufgaben als Markdown zur späteren Abarbeitung. Jeder einzele Punkt ist eine Checkbox zum abhaken.

Zusatzinfo für Ableitung von Tests aus der Spec zur Übertragung in den Plan:
## Ableitung der Tests aus den Anforderungen (Traceability)

### Zweck

Der Plan verbindet jede Anforderung mit dem Test, der sie später beweist. Die
Verbindung entsteht beim Übergang von Spec zu Plan, nicht erst bei der Umsetzung.
Damit ist beim Freigeben des Plans prüfbar, ob jede Anforderung verifiziert wird,
und am Ende der Umsetzung, ob sie verifiziert wurde.

### Eingang

- Der Skill akzeptiert eine fertige Spec mit nummerierten Anforderungen oder eine
  rohe Anforderung ohne Nummerierung.
- Vorhandene IDs (z. B. `AC-n`, `FR-n`, `NFR-n`) werden unverändert übernommen.
  Fehlen IDs, vergibt der Skill sie selbst und weist sie im Plan aus, damit die
  Spec nachgezogen werden kann.
- Jedes Akzeptanzkriterium muss mindestens einen Fehler- oder Randfall enthalten.
  Ein Kriterium, das nur den Erfolgsfall beschreibt, wird als Lücke gemeldet.

### Anforderungen an den Plan

1. **Verifies-Block pro Task.** Jeder Task nennt die Anforderungs-IDs, die er
   beweist, und pro ID die Testart sowie den geplanten Testnamen. Der Test ist das
   erste Arbeitsergebnis des Tasks, nicht das letzte.

   ```
   Task #N: <Gegenstand>
     Verifies:
       AC-3  → Akzeptanz/Integration  <Testname>
       FR-2  → Unit                   <Testname>
       NFR-1 → manuell                <Prüfschritt, Verantwortlicher>
   ```

2. **Feste Zuordnung Anforderungsart → Testart.** Die Zuordnung ist Teil des
   Skills und wird nicht pro Task neu entschieden:

   | Anforderungsart | Testart | Bemerkung |
      |---|---|---|
   | Akzeptanzkriterium (Given/When/Then, von außen beobachtbar) | Akzeptanz- oder Integrationstest an der Systemgrenze | ein Test pro Kriterium, ID im Testnamen oder als Markierung |
   | Funktionale Anforderung (Geschäftsregel, Validierung, Berechtigung) | Unit-Test der betroffenen Logik | Regeltabellen als parametrisierte Tests |
   | Schnittstellen- oder Datenvertrag | Contract-Test | Schema, Statuscodes je Fehlerfall, Migration gegen leeren Datenbestand |
   | Nicht-funktionale Anforderung | automatisiert **oder** manuell, immer explizit | automatisiert: Analyzer, Budget, Lasttest-Schwelle; sonst benannter manueller Prüfschritt |

   Konkrete Frameworks und Werkzeuge bestimmt der Skill nicht; sie kommen aus
   dem Zielprojekt oder den nachgelagerten Implementierungs-Skills.

3. **Vollständigkeit.** Jedes Akzeptanzkriterium erscheint in genau einem
   Verifies-Block. Ein Kriterium ohne Task blockiert die Freigabe des Plans.

4. **Keine verwaisten Tests.** Ein geplanter Test, den keine Anforderungs-ID
   erreicht, wird entweder als Implementierungsdetail gekennzeichnet und nicht im
   Verifies-Block geführt, oder als Hinweis auf eine fehlende Anforderung gemeldet.

5. **Rückkopplung zur Spec.** Ein Kriterium, das sich nicht in einen Test
   übersetzen lässt, ist nicht konkret genug. Der Skill schreibt keinen vagen
   Test, sondern meldet das Kriterium als offene Frage an die Spec zurück.

6. **Mock-Grenzen aus dem Code.** Wo zwischen echter und ersetzter Abhängigkeit
   getrennt wird, entscheidet der Plan anhand des Zielprojekts, nicht anhand der
   Formulierung in der Spec.

7. **Traceability-Matrix.** Der Plan enthält eine Tabelle Anforderungs-ID →
   Task → Test. Für nicht-funktionale Anforderungen steht dort, ob die Prüfung
   automatisiert oder manuell erfolgt.

8. **Todos aus dem Verifies-Block.** Die Todo-Liste eines Tasks leitet sich aus
   dem Verifies-Block ab: zuerst der Test je ID, dann die Umsetzung, dann
   Dokumentation. Die Reihenfolge ist Teil des Plans.

9. **Stabilität nach Freigabe.** Die im Plan genannten Testnamen sind nach der
   Freigabe fest. Eine Umbenennung während der Umsetzung ist eine Planänderung
   und wird als solche ausgewiesen.

### Nicht Ziel dieses Abschnitts

- Der Skill schreibt keine Tests und keinen Produktionscode.
- Der Skill ändert die Spec nicht; Rückmeldungen an die Spec werden als offene
  Fragen im Plan geführt.
- Der Skill legt keine Testframeworks, Namenskonventionen oder Verzeichnisse fest.

### Akzeptanzkriterien für den Skill

- Gegeben eine Spec mit fünf Akzeptanzkriterien, wenn der Plan erzeugt wird,
  dann erscheint jede der fünf IDs in genau einem Verifies-Block und in der Matrix.
- Gegeben eine Spec mit einem Kriterium ohne Fehlerfall, wenn der Plan erzeugt
  wird, dann wird das Kriterium als Lücke gemeldet und nicht still übernommen.
- Gegeben eine rohe Anforderung ohne IDs, wenn der Plan erzeugt wird, dann
  vergibt der Skill IDs und listet sie als Rückmeldung an die Spec.
- Gegeben eine nicht-funktionale Anforderung ohne messbares Ziel, wenn der Plan
  erzeugt wird, dann steht in der Matrix `manuell` mit Prüfschritt, nie eine
  leere Zelle.
- Gegeben ein Kriterium, das sich nicht in einen Test übersetzen lässt, wenn der
  Plan erzeugt wird, dann erscheint es unter offenen Fragen und der Plan enthält
  dafür keinen Testnamen.

---

## Bezug zu bestehenden Skills

- **Eingang:** `skills/development/create-dev-spec/` liefert Specs nach `references/spec-template.md` mit `FR-n`, `NFR-n` und `AC-n`. Die IDs sind dort bereits definiert; Abschnitt 7 der Vorlage fordert, dass jedes AC die FRs nennt, die es verifiziert.
- **Ausgang:** Die Implementierungs-Workflows (`dotnet-dev`, `angular-dev`, `implementer`) konsumieren den Plan. Sie binden die Testart an ihre Tester-Skills; die Zuordnung Anforderungsart → Testart aus Punkt 2 ist dafür die Schnittstelle.
- **Prüfung:** Die Reviewer-Skills können die Traceability-Matrix am Ende der Umsetzung gegen die vorhandenen Tests prüfen. Das ist kein Bestandteil dieses Dokuments, aber der Grund, warum die Testnamen nach Freigabe fest sind (Punkt 9).