
# GuideOS Cinnamon-Sicherung
**Einfaches Backup‑ und Restore‑Tool für den Cinnamon‑Desktop (GTK4)**

## Entwickler:
evilware666 & Helga

## 📝 Überblick  
Der *GuideOS Cinnamon Backup & Restore* ist ein leicht verständliches Werkzeug, um **alle wichtigen Cinnamon‑Desktop‑Einstellungen** zu sichern und wiederherzustellen.  
Ideal vor Systemänderungen, nach Neuinstallationen oder zum Übertragen des eigenen Setups auf einen anderen Rechner.

## ✨ Funktionen  
- 🔧 **Backup des gesamten Cinnamon‑Desktops**
  - Cinnamon‑Einstellungen (`dconf`)
  - Themes, Icons, Applets, Desklets
  - Hintergrundbild + Pfad
  - Autostart‑Einträge
  - Benutzer‑Anwendungen (`.local/share/applications`)
- 🔄 **Wiederherstellung mit einem Klick**
  - Vollständiges Zurückspielen aller gesicherten Daten
  - Automatisches Wiederherstellen des Hintergrundbilds
  - Nutzung von `rsync` für zuverlässige Dateiübertragung
- 🧵 **Multithreading**
  - Backup/Restore läuft im Hintergrund
  - Fortschrittsdialog mit Spinner
  - Abbrechen jederzeit möglich
- 🛡️ **Sicher**
  - Arbeitet ausschließlich im Benutzerverzeichnis
  - Keine Systemdateien werden verändert
- 🖥️ **GTK4‑Oberfläche**
  - Modern, klar, einsteigerfreundlich

## ❗ Nicht enthalten  
- Angepinnte Programme in der Cinnamon‑Taskleiste (Panel‑Launcher)

## 📦 Gesicherte Inhalte  
Das Backup‑Archiv (`.tar.gz`) enthält:

```
.cinnamon/
.config/cinnamon/
.local/share/cinnamon/
.local/cinnamon/
.local/share/icons/
.icons/
.themes/
.config/autostart/
.local/share/applications/
cinnamon-configs.dconf
wallpaper/
```

## ▶️ Verwendung

### Backup erstellen
1. Programm starten  
2. **„Sichern“** klicken  
3. Speicherort wählen  
4. Backup wird erstellt → `.tar.gz`

### Wiederherstellen
1. Programm starten  
2. **„Wiederherstellen“** klicken  
3. Backup‑Datei auswählen  
4. Nach Abschluss: **einmal ab‑ und wieder anmelden**

## 🔧 Technische Details  
- Export der Cinnamon‑Einstellungen via  
  `dconf dump /org/cinnamon/`
- Wiederherstellung via  
  `dconf load /org/cinnamon/`
- Hintergrundbild wird kopiert und per `gsettings` gesetzt
- Dateien werden mit `rsync -a` übertragen
- Temporäre Arbeitsverzeichnisse werden automatisch gelöscht

## 📄 Lizenz  
MIT‑Lizenz

