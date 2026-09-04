
Es soll ein neuer Skill implement-feature im Ordner skills/development zusammen mit dem User erstellt werden.
Der Skill soll zusammen mit dem User verfeinert werden, um die Anforderungen des Users bestmöglich zu erfüllen.

Der Skill soll aus einem Plan und einer Spec eine Implementierung erstellen.

Never Commit Changes: Der Skill soll die Änderungen nicht direkt commiten, sondern dem Benutzer die Möglichkeit geben, die Änderungen zu prüfen und zu entscheiden, ob er sie übernehmen möchte.

Grobes Vorgehen zur Orientierung:
1. Prüfe, ob sowohl Plan als auch Spec vorhanden sind. Wenn nicht, informiere den Benutzer, dass beide Dokumente benötigt werden und beende deine Arbeit hier.
2. Prüfe den Plan und die Spec auf Konsistenz. Wenn Inkonsistenzen gefunden werden, informiere den Benutzer und frage den user, wie er fortfahren möchte (z.B. Abbruch, Korrektur der Dokumente, Ignorieren der Inkonsistenzen).
3. Lies eine Übersicht aller zur Verfügung stehender Skills ein und suche die heraus, die für die Implementierung der Anforderungen im Plan und in der Spec relevant sind (z.b. Skills für bestimmte Frameworks, Patterns, Tech Stack). Informiere den Benutzer über die gefundenen Skills und frage, ob er diese verwenden möchte oder eigene Skills einbringen will. Der User kann über Multiselect Tool Skills wieder abwählen, die er nicht verwenden möchte und zusätzlich neue hinzufügen.
4. Ordne die ausgewählten Skills den einzelenen Tasks im Plan zu. Informiere den Benutzer über die Zuordnung und frage, ob er diese so übernehmen möchte oder Änderungen vornehmen möchte.
5. Frage den User, ob er die Implementierung direkt in diesem Context umsetzen soll oder mit Subagents arbeiten soll (6.1 oder 6.2).

6.1 Umsetzung direkt in diesem Context:
- Erstelle für jeden Task im Plan eine Implementierung unter Verwendung der zugeordneten Skills.
- Informiere den Benutzer über den Fortschritt und die Ergebnisse der Implementierung.
- Weiter zu 7.

6.2 Umsetzung mit Subagents: (Bringe hier gerne noch eigene Ideen ein, wie man die Subagents noch besser nutzen kann und robustere Ergebnisse erzielen kann und die Qualität der Implementierung verbessern kann)
- Erstelle für jeden Task im Plan einen Subagenten, der die Implementierung unter Verwendung der zugeordneten Skills übernimmt. Der Subagent muss alle für seinen Task notwendigen Infos bekommen (Plan, Spec, zugeordnete Skills). Anweisung, an den Subagent, dass er die Skills zwingend laden muss, bevor er mit der Implementierung beginnt. Er darf nur mit sehr guten Gründen vom Plan abweichen. Die Abweichung darf nicht die zu erzielende Funktionialität verändern. Er muss alle geladenen Skills, sein Ergebnis, Abweichungen vom Plan mit Begründung an den Hauptagenten zurückmelden.  
- Informiere den Benutzer über die Erstellung der Subagenten und deren Fortschritt bei der Implementierung.
- Prüfe nach Abschluss eines jeden Subagents die Ergebnisse auf Konsistenz mit dem Plan und der Spec. Wenn Inkonsistenzen gefunden werden, informiere den Benutzer und frage, wie er fortfahren möchte (z.B. Abbruch, Korrektur der Dokumente, Ignorieren der Inkonsistenzen).


7. Starte einen Subagent für ein komplettes Review der uncommitted Changes. Nutze hier die Skills für Code Review, Refactoring und Testing für diesen konkreten Tech Stack. Der Subagent soll die Änderungen prüfen, Verbesserungsvorschläge machen und einen Review Report erstellen. 
8. Warte auf das Review Ergebnis und informiere den Benutzer über die Ergebnisse. Frage, ob er die Änderungen übernehmen möchte Schlage hier nur die wichtigsten Punkte zur Änderung vor. Wenn der Benutzer Änderungen wünscht, gehe zurück zu Schritt 6 und wiederhole den Prozess.
9. Schreibe einen abschließenden Bericht über die durchgeführten Arbeiten. Erfasse dort auch die Entscheidungen des Benutzers, die verwendeten Skills, die Ergebnisse der Implementierung und des Reviews sowie eventuelle Abweichungen vom ursprünglichen Plan.