#!/usr/bin/env python3
# ==============================================================================
# GuideOS Cinnamon Backup & Restore - GTK4/libadwaita Version
# ------------------------------------------------------------------------------
# Beschreibung:
# Dieses Tool ermöglicht es, den aktuellen Cinnamon-Desktop schnell und einfach
# zu sichern oder wiederherzustellen. Gesichert werden unter anderem:
#   - Cinnamon-Einstellungen (über dconf)
#   - Benutzeranpassungen im Cinnamon- und Konfigurationsverzeichnis
#   - Das aktuelle Hintergrundbild und Autostart-Einträge
#
# Damit können Benutzer ihren Desktop-Zustand bequem speichern und bei Bedarf
# vollständig wiederherstellen – ideal für Tests, Neuinstallationen oder 
# Systemanpassungen unter GuideOS.
#
# Autor: evilware666 & Helga
# Version: 3.4
# Datum: 2025-10-14
# ==============================================================================

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio, GLib
import subprocess
import os
import tempfile
import shutil
from datetime import datetime
import threading

class CinnamonBackupRestore(Gtk.Application):
    def __init__(self):
        super().__init__(application_id='com.guideos.cinnamon-backup',
                         flags=Gio.ApplicationFlags.FLAGS_NONE)
        
    def do_activate(self):
        # Hauptfenster
        self.window = Gtk.ApplicationWindow(application=self)
        self.window.set_title("GuideOS Cinnamon Desktop Tool")
        self.window.set_default_size(500, 400)
        self.window.set_resizable(True)
        
        # Haupt-Box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_margin_top(30)
        main_box.set_margin_bottom(30)
        main_box.set_margin_start(30)
        main_box.set_margin_end(30)
        
        # Einfache Erklärung
        info_label = Gtk.Label()
        info_label.set_markup("""
<span size="large" weight="bold">🔧 Cinnamon Desktop Tool</span>

<span weight="bold">Was macht das Tool?</span>
Sichert oder stellt deinen gesamten Cinnamon-Desktop wieder her
(Einstellungen, Hintergrundbild, Design, Autostart)

<span weight="bold">Wann brauchst du das?</span>
• Vor großen Änderungen am System
• Nach einer Neuinstallation von GuideOS
• Zum Übertragen auf einen anderen Computer

<span foreground="red" weight="bold">❌ NICHT gesichert:</span>
Angepinnte Programme in der Taskleiste

<span weight="bold">Einfach ausprobieren - du kannst nichts kaputt machen!</span>
        """)
        info_label.set_wrap(True)
        info_label.set_halign(Gtk.Align.CENTER)
        main_box.append(info_label)
        
        # Button-Box
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        button_box.set_halign(Gtk.Align.CENTER)
        button_box.set_margin_top(20)
        button_box.set_margin_bottom(20)
        
        # Sichern-Button
        backup_button = Gtk.Button(label="💾 Sichern")
        backup_button.get_style_context().add_class("suggested-action")
        backup_button.set_size_request(150, 45)
        backup_button.connect("clicked", self.on_backup_clicked)
        button_box.append(backup_button)
        
        # Wiederherstellen-Button
        restore_button = Gtk.Button(label="🔄 Wiederherstellen")
        restore_button.get_style_context().add_class("destructive-action")
        restore_button.set_size_request(150, 45)
        restore_button.connect("clicked", self.on_restore_clicked)
        button_box.append(restore_button)
        
        main_box.append(button_box)
        
        # Beenden-Button
        quit_button = Gtk.Button(label="❌ Beenden")
        quit_button.set_halign(Gtk.Align.CENTER)
        quit_button.set_size_request(100, 30)
        quit_button.connect("clicked", lambda x: self.quit())
        main_box.append(quit_button)
        
        self.window.set_child(main_box)
        self.window.present()
    
    def show_message_dialog(self, title, text, is_error=False, is_question=False):
        """Einheitlichen GTK-Dialog anzeigen"""
        dialog = Gtk.MessageDialog(
            transient_for=self.window,
            modal=True,
            text=title,
            secondary_text=text
        )
        
        if is_question:
            dialog.add_button("Abbrechen", Gtk.ResponseType.CANCEL)
            dialog.add_button("Ja", Gtk.ResponseType.OK)
            dialog.get_widget_for_response(Gtk.ResponseType.OK).get_style_context().add_class("destructive-action")
            return dialog
        
        dialog.add_button("OK", Gtk.ResponseType.OK)
        if is_error:
            dialog.get_widget_for_response(Gtk.ResponseType.OK).get_style_context().add_class("destructive-action")
        else:
            dialog.get_widget_for_response(Gtk.ResponseType.OK).get_style_context().add_class("suggested-action")
        
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.show()
        return None
    
    def show_progress(self, title, callback, *args):
        """Fortschrittsdialog anzeigen"""
        dialog = Gtk.MessageDialog(
            transient_for=self.window,
            modal=True,
            text=title,
            secondary_text="Bitte warten..."
        )
        
        spinner = Gtk.Spinner()
        spinner.start()
        spinner.set_margin_top(10)
        
        # Spinner in den Dialog einfügen
        content_area = dialog.get_content_area()
        content_area.append(spinner)
        
        dialog.add_button("Abbrechen", Gtk.ResponseType.CANCEL)
        dialog.show()
        
        cancel_flag = threading.Event()
        
        def on_response(dialog, response):
            if response == Gtk.ResponseType.CANCEL:
                cancel_flag.set()
                dialog.destroy()
        
        dialog.connect("response", on_response)
        
        def run_task():
            result = callback(*args, cancel_flag)
            GLib.idle_add(lambda: self.on_progress_done(dialog, result))
        
        thread = threading.Thread(target=run_task, daemon=True)
        thread.start()
    
    def on_progress_done(self, dialog, result):
        dialog.destroy()
        if result["success"]:
            self.show_message_dialog(result["title"], result["text"])
        else:
            self.show_message_dialog("Fehler", result["text"], is_error=True)
    
    def on_backup_clicked(self, button):
        """Backup starten"""
        dialog = self.show_message_dialog(
            "Desktop sichern?",
            "Möchtest du jetzt ein Backup deines Desktops erstellen?",
            is_question=True
        )
        dialog.connect("response", self.on_backup_confirm)
        dialog.show()
    
    def on_backup_confirm(self, dialog, response):
        dialog.destroy()
        if response == Gtk.ResponseType.OK:
            # Datei speichern Dialog
            file_dialog = Gtk.FileDialog.new()
            file_dialog.set_title("Backup speichern unter...")
            
            default_name = f"Cinnamon-Desktop_{datetime.now().strftime('%Y-%m-%d')}.tar.gz"
            gfile = Gio.File.new_for_path(os.path.join(os.path.expanduser("~"), default_name))
            file_dialog.set_initial_file(gfile)
            
            file_dialog.save(self.window, None, self.on_backup_file_selected)
    
    def on_backup_file_selected(self, dialog, result):
        try:
            file = dialog.save_finish(result)
            if file:
                self.show_progress("Backup wird erstellt...", self.do_backup, file.get_path())
        except GLib.GError:
            pass  # Benutzer hat abgebrochen
    
    def do_backup(self, speicherort, cancel_flag=None):
        """Backup durchführen - GENAU die Original-Befehle"""
        try:
            if cancel_flag and cancel_flag.is_set():
                return {"success": False, "title": "Abgebrochen", "text": "Die Sicherung wurde abgebrochen."}
            
            tmpdir = tempfile.mkdtemp()
            
            # Cinnamon-Einstellungen sichern
            with open(f"{tmpdir}/cinnamon-configs.dconf", 'w') as f:
                subprocess.run(['dconf', 'dump', '/org/cinnamon/'], stdout=f)
            
            if cancel_flag and cancel_flag.is_set():
                shutil.rmtree(tmpdir)
                return {"success": False, "title": "Abgebrochen", "text": "Die Sicherung wurde abgebrochen."}
            
            # Hintergrundbild sichern
            result = subprocess.run(['gsettings', 'get', 'org.cinnamon.desktop.background', 'picture-uri'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                wallpaper = result.stdout.strip().strip("'").replace('file://', '')
                if os.path.exists(wallpaper):
                    os.makedirs(f"{tmpdir}/wallpaper", exist_ok=True)
                    shutil.copy(wallpaper, f"{tmpdir}/wallpaper/")
                    with open(f"{tmpdir}/wallpaper/path.txt", 'w') as f:
                        f.write(wallpaper)
            
            # Backup erstellen
            home = os.path.expanduser("~")
            os.chdir(home)
            
            include_dirs = [".cinnamon", ".config/cinnamon", ".local/share/cinnamon", 
                          ".local/cinnamon", ".local/share/icons", ".icons", ".themes", 
                          ".config/autostart", ".local/share/applications"]
            
            tar_args = ['tar', '-czf', speicherort]
            for dir_name in include_dirs:
                if os.path.exists(dir_name):
                    tar_args.append(dir_name)
            
            tar_args.extend(['-C', tmpdir, 'cinnamon-configs.dconf'])
            if os.path.exists(f"{tmpdir}/wallpaper"):
                tar_args.append('wallpaper')
            
            subprocess.run(tar_args, stderr=subprocess.DEVNULL)
            shutil.rmtree(tmpdir)
            
            return {"success": True, "title": "✅ Fertig!", "text": f"Backup gespeichert unter:\n{speicherort}"}
        except Exception as e:
            return {"success": False, "title": "Fehler", "text": f"Backup fehlgeschlagen:\n{str(e)}"}
    
    def on_restore_clicked(self, button):
        """Wiederherstellung starten"""
        dialog = self.show_message_dialog(
            "⚠️ Achtung!",
            "Die Wiederherstellung überschreibt deine aktuellen Desktop-Einstellungen.\n\nMöchtest du wirklich fortfahren?",
            is_question=True
        )
        dialog.connect("response", self.on_restore_confirm)
        dialog.show()
    
    def on_restore_confirm(self, dialog, response):
        dialog.destroy()
        if response == Gtk.ResponseType.OK:
            # Datei öffnen Dialog
            file_dialog = Gtk.FileDialog.new()
            file_dialog.set_title("Backup-Datei auswählen")
            file_dialog.open(self.window, None, self.on_restore_file_selected)
    
    def on_restore_file_selected(self, dialog, result):
        try:
            file = dialog.open_finish(result)
            if file:
                self.show_progress("Wiederherstellung läuft...", self.do_restore, file.get_path())
        except GLib.GError:
            pass  # Benutzer hat abgebrochen
    
    def do_restore(self, backup_file, cancel_flag=None):
        """Wiederherstellung durchführen - GENAU die Original-Befehle"""
        try:
            if cancel_flag and cancel_flag.is_set():
                return {"success": False, "title": "Abgebrochen", "text": "Die Wiederherstellung wurde abgebrochen."}
            
            tmpdir = tempfile.mkdtemp()
            
            # Backup entpacken
            subprocess.run(['tar', '-xzf', backup_file, '-C', tmpdir])
            
            if cancel_flag and cancel_flag.is_set():
                shutil.rmtree(tmpdir)
                return {"success": False, "title": "Abgebrochen", "text": "Die Wiederherstellung wurde abgebrochen."}
            
            home = os.path.expanduser("~")
            
            # Verzeichnisse wiederherstellen
            restore_dirs = [
                (".cinnamon", ".cinnamon"),
                (".config/cinnamon", ".config/cinnamon"),
                (".local/share/cinnamon", ".local/share/cinnamon"),
                (".local/cinnamon", ".local/cinnamon"),
                (".local/share/icons", ".local/share/icons"),
                (".icons", ".icons"),
                (".themes", ".themes"),
                (".config/autostart", ".config/autostart"),
                (".local/share/applications", ".local/share/applications")
            ]
            
            for src, dst in restore_dirs:
                src_path = os.path.join(tmpdir, src)
                dst_path = os.path.join(home, dst)
                if os.path.exists(src_path):
                    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                    subprocess.run(['rsync', '-a', f"{src_path}/", f"{dst_path}/"], stderr=subprocess.DEVNULL)
            
            if cancel_flag and cancel_flag.is_set():
                shutil.rmtree(tmpdir)
                return {"success": False, "title": "Abgebrochen", "text": "Die Wiederherstellung wurde abgebrochen."}
            
            # Cinnamon-Einstellungen wiederherstellen
            dconf_file = os.path.join(tmpdir, "cinnamon-configs.dconf")
            if os.path.exists(dconf_file):
                with open(dconf_file, 'r') as f:
                    subprocess.run(['dconf', 'load', '/org/cinnamon/'], stdin=f)
            
            # Hintergrundbild wiederherstellen
            path_file = os.path.join(tmpdir, "wallpaper/path.txt")
            if os.path.exists(path_file):
                with open(path_file, 'r') as f:
                    wall_path = f.read().strip()
                wall_file = os.path.basename(wall_path)
                bilder_dir = os.path.join(home, "Bilder")
                os.makedirs(bilder_dir, exist_ok=True)
                
                wallpaper_src = os.path.join(tmpdir, "wallpaper", wall_file)
                if os.path.exists(wallpaper_src):
                    shutil.copy(wallpaper_src, os.path.join(bilder_dir, wall_file))
                    subprocess.run(['gsettings', 'set', 'org.cinnamon.desktop.background', 
                                  'picture-uri', f"file://{bilder_dir}/{wall_file}"])
            
            shutil.rmtree(tmpdir)
            
            return {"success": True, "title": "✅ Fertig!", 
                   "text": "Desktop wurde wiederhergestellt!\n\nTipp: Logge dich einmal aus und wieder ein."}
        except Exception as e:
            return {"success": False, "title": "Fehler", "text": f"Wiederherstellung fehlgeschlagen:\n{str(e)}"}

def main():
    app = CinnamonBackupRestore()
    app.run(None)

if __name__ == "__main__":
    main()
