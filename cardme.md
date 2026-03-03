# Projekt: CardMe – Windows Flashcard App (One-Shot)

**Rolle:** Du bist ein erfahrener Senior Windows App-Entwickler. 
**Ziel:** Schreibe den kompletten, fehlerfreien Code für eine Windows-Desktop-Anwendung in einem einzigen "One-Shot"-Durchlauf. Der User hat keine Programmiererfahrung, daher muss der Code out-of-the-box funktionieren.

## Konzept: "CardMe"
Eine minimalistische, moderne Karteikarten-App (Flashcards) speziell für Power-User, die nachts lernen. 
* **Design:** Deep Dark Mode (dunkelgraue/schwarze Hintergründe, subtile Neon-Akzente z.B. in Blau oder Violett). Clean und ohne ablenkende UI-Elemente.
* **Technologie-Stack:** Python. Nutze die Bibliothek `customtkinter` für ein modernes, natives Dark-Mode-Aussehen und `json` für die Datenspeicherung.

## Kernfunktionen (Aktualisiert)
1.  **Lokale Speicherung & Flexibler Pfad:** Die Daten werden lokal gespeichert. Die App soll beim ersten Start einen Ordner (z.B. "CardMe_Data") erstellen. Der User soll in den Einstellungen der App den Pfad zu diesem Ordner ändern können (z.B. in einen OneDrive/Dropbox-Ordner, um von überall via Texteditor am Handy Karten hinzufügen zu können).
2.  **Multi-Deck Management:** * Der User kann beliebig viele, voneinander unabhängige Decks erstellen (z.B. "Englisch", "Programmieren", "Allgemeinwissen").
    * Jedes Deck wird als eigene `.json`-Datei im Datenordner gespeichert.
    * Ein Dropdown-Menü oder eine Seitenleiste (Sidebar) auf der Startseite, um zwischen den Decks zu wechseln oder neue zu erstellen.
3.  **Karten hinzufügen:** Ein simples Menü mit zwei Eingabefeldern ("Vorderseite" und "Rückseite") und einem "Speichern"-Button, das die Karte direkt in das aktuell ausgewählte Deck einfügt.
4.  **Lern-Modus:** * Zeigt eine zufällige oder die nächste Karte des *aktuell ausgewählten Decks* an.
    * Ein Button "Antwort aufdecken", der die Rückseite anzeigt.
    * Danach ein Button für "Nächste Karte".

## Technische Vorgaben für den Output
* Schreibe den gesamten Code in eine einzige `main.py` Datei.
* Kommentiere die wichtigsten Funktionen kurz auf Deutsch.
* Füge am Anfang deiner Antwort eine extrem kurze, simple Schritt-für-Schritt-Anleitung hinzu, wie der User den Code unter Windows ausführt (z.B. Python installieren, `pip install customtkinter` ausführen, Datei starten).
* WICHTIG: Implementiere keine versteckten Terminal-Aufrufe oder Systemeingriffe. Die App soll rein lokal, sicher und isoliert in ihrer eigenen GUI laufen.