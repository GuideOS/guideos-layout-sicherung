# GuideOS Cinnamon-Sicherung

Autor: evilware666 & Helga\
Version: 1.1

Dieses Tool ermöglicht das komfortable Sichern und Wiederherstellen des
Cinnamon-Layouts unter GuideOS.\
Es speichert unter anderem Panel-Positionen, Applets, Desklets, Themes,
Fenster-Einstellungen sowie optional den Status des Plank-Docks.

## Funktionen

### 1. Layout sichern

Beim Sichern werden alle relevanten Cinnamon-Konfigurationsdateien in
ein Sicherungsverzeichnis kopiert.\
Der Benutzer kann beim Start die Sicherungs-Location selbst auswählen.

**Plank-Logik beim Sichern:**\
- Wenn Plank zum Zeitpunkt der Sicherung aktiv ist, wird dies erkannt
und gespeichert.\
- Wenn Plank nicht aktiv ist, wird dies ebenfalls korrekt gespeichert.

Es erfolgt keine wiederkehrende OK-Abfrage -- nur eine einzige
Bestätigung nach Abschluss.

### 2. Layout wiederherstellen

Beim Wiederherstellen werden die gesicherten Dateien in das System
zurückkopiert.

**Plank-Verhalten beim Wiederherstellen:**\
- Wenn Plank beim Sichern aktiv war → Plank wird automatisch wieder
aktiviert.\
- Wenn Plank beim Sichern nicht aktiv war → Plank wird deaktiviert bzw.
nicht gestartet.

Nach dem Wiederherstellen erscheint ein Hinweis, dass der Benutzer sich
ab- und wieder anmelden muss.

Es erfolgt nur eine OK-Meldung nach Abschluss -- ohne unnötige
Zwischenbestätigungen.

### 3. Hauptmenü

Das Skript zeigt ein einfaches Menü mit folgenden Auswahlmöglichkeiten:

-   Layout sichern\
-   Layout wiederherstellen\
-   Beenden

Die Option *Beenden* schließt das Programm vollständig.

## Speicherort der Sicherungen

Der Benutzer kann beim Start frei wählen, wohin die Sicherung
gespeichert wird.\
Dies ermöglicht z. B. Sicherungen auf USB-Datenträgern oder in eigene
Ordnerstrukturen.

## Technische Hinweise

-   Alle Funktionen sind robust ausgelegt.\
-   Die Plank-Erkennung stellt sicher, dass kein falscher Autostart
    erfolgt.\
-   Es werden ausschließlich Nutzerkonfigurationsdateien verändert.
