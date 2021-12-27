#!/usr/bin/env python3

# Dependencies: python-geopy

import locale
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib

from nwg_shell_config.tools import *

dir_name = os.path.dirname(__file__)

config_home = os.getenv('XDG_CONFIG_HOME') if os.getenv('XDG_CONFIG_HOME') else os.path.join(
    os.getenv("HOME"), ".config/")

settings = {"keyboard-layout": "",
            "autotiling-workspaces": "1 2 3 4 5 6 7 8", "autotiling-on": True,
            "night-lat": -1.0, "night-long": -1.0, "night-temp-low": 4000, "night-temp-high": 6500,
            "night-gamma": 1.0, "night-on": True,
            "terminal": "", "file-manager": "", "editor": "", "browser": "",
            "launcher-columns": 6, "launcher-icon-size": 64, "launcher-file-search-columns": 2,
            "launcher-search-files": True, "launcher-categories": True, "launcher-resident": True,
            "launcher-overlay": False, "launcher-on": True,
            "exit-position": "center", "exit-full": False, "exit-alignment": "middle", "exit-margin": 0,
            "exit-icon-size": 48, "exit-on": True,
            "dock-position": "bottom", "dock-full": False, "dock-autohide": True,
            "dock-alignment": "center", "dock-margin": 0, "dock-icon-size": 48, "dock-on": False}


def validate_workspaces(gtk_entry):
    valid_text = ""
    for char in gtk_entry.get_text():
        if char.isdigit() or char == " ":
            valid_text += char
    while '  ' in valid_text:
        valid_text = valid_text.replace('  ', ' ')
    gtk_entry.set_text(valid_text)


class MainWindow(Gtk.Window):
    def __init__(self):
        builder = Gtk.Builder()
        builder.add_from_file(os.path.join(dir_name, "glade/main.glade"))

        self.window = builder.get_object("main-window")
        self.window.connect('destroy', Gtk.main_quit)
        self.keyboard_layout = builder.get_object("keyboard-layout")

        self.autotiling_workspaces = builder.get_object("autotiling-workspaces")
        self.autotiling_workspaces.connect("changed", validate_workspaces)
        self.autotiling_on = builder.get_object("autotiling-on")

        self.night_lat = builder.get_object("night-lat")
        self.night_lat_info = builder.get_object("night-lat-info")
        self.night_long = builder.get_object("night-long")
        self.night_long_info = builder.get_object("night-long-info")
        self.night_temp_low = builder.get_object("night-temp-low")
        self.night_temp_high = builder.get_object("night-temp-high")
        self.night_gamma = builder.get_object("night-gamma")
        self.night_on = builder.get_object("night-on")

        self.terminal = builder.get_object("terminal")
        self.file_manager = builder.get_object("file-manager")
        self.editor = builder.get_object("editor")

        self.browser = builder.get_object("browser")
        self.browser_chromium = builder.get_object("browser-chromium")
        self.browser_chromium.connect("clicked", self.set_chromium)
        self.browser_firefox = builder.get_object("browser-firefox")
        self.browser_firefox.connect("clicked", self.set_firefox)

        self.launcher_columns = builder.get_object("launcher-columns")
        self.launcher_icon_size = builder.get_object("launcher-icon-size")
        self.launcher_file_search_columns = builder.get_object("launcher-file-search-columns")
        self.launcher_search_files = builder.get_object("launcher-search-files")
        self.launcher_categories = builder.get_object("launcher-categories")
        self.launcher_resident = builder.get_object("launcher-resident")
        self.launcher_overlay = builder.get_object("launcher-overlay")
        self.launcher_on = builder.get_object("launcher-on")

        self.exit_position = builder.get_object("exit-position")
        self.exit_full = builder.get_object("exit-full")
        self.exit_alignment = builder.get_object("exit-alignment")
        self.exit_margin = builder.get_object("exit-margin")
        self.exit_icon_size = builder.get_object("exit-icon-size")
        self.exit_on = builder.get_object("exit-on")

        self.dock_position = builder.get_object("dock-position")
        self.dock_full = builder.get_object("dock-full")
        self.dock_autohide = builder.get_object("dock-autohide")
        self.dock_alignment = builder.get_object("dock-alignment")
        self.dock_margin = builder.get_object("dock-margin")
        self.dock_icon_size = builder.get_object("dock-icon-size")
        self.dock_on = builder.get_object("dock-on")

        self.btn_close = builder.get_object("btn-close")
        self.btn_save = builder.get_object("btn-save")
        self.btn_save.connect("clicked", self.on_save_btn)

        self.tz, self.lat, self.long = get_lat_lon()

        self.fill_in_from_settings(self)
        self.fill_in_missing_values(self)

        self.window.show_all()

    def set_chromium(self, *args):
        self.browser.set_text("chromium --disable-gpu-memory-buffer-video-frames --enable-features=UseOzonePlatform --ozone-platform=wayland")

    def set_firefox(self, *args):
        self.browser.set_text("MOZ_ENABLE_WAYLAND=1 firefox")

    def fill_in_from_settings(self, *args):
        print(settings)
        self.keyboard_layout.set_text(settings["keyboard-layout"])
        self.autotiling_workspaces.set_text(settings["autotiling-workspaces"])
        self.autotiling_on.set_active(settings["autotiling-on"])

        self.night_lat.set_numeric(True)
        adj = Gtk.Adjustment(lower=-90.0, upper=90.1, step_increment=0.1, page_increment=10.0,
                             page_size=0.1)
        self.night_lat.configure(adj, 0.1, 4)
        self.night_lat.set_value(settings["night-lat"])
        self.night_lat_info.set_tooltip_text("When undefined, the value for '{}' will be used.".format(self.tz))

        self.night_long.set_value(settings["night-long"])
        adj = Gtk.Adjustment(lower=-180.0, upper=180.1, step_increment=0.1, page_increment=10.0,
                             page_size=0.1)
        self.night_long.configure(adj, 0.1, 4)
        self.night_long.set_value(settings["night-long"])
        self.night_long_info.set_tooltip_text("When undefined, the value for '{}' will be used.".format(self.tz))

        self.night_temp_low.set_value(settings["night-temp-low"])
        adj = Gtk.Adjustment(lower=1000, upper=6500, step_increment=1, page_increment=10.0,
                             page_size=0.1)
        self.night_temp_low.configure(adj, 1, 0)
        self.night_temp_low.set_value(settings["night-temp-low"])

        self.night_temp_high.set_value(settings["night-temp-high"])
        adj = Gtk.Adjustment(lower=1000, upper=6501, step_increment=1, page_increment=10.0,
                             page_size=1)
        self.night_temp_high.configure(adj, 1, 0)
        self.night_temp_high.set_value(settings["night-temp-high"])

        self.night_gamma.set_value(settings["night-gamma"])
        adj = Gtk.Adjustment(lower=0.1, upper=1.1, step_increment=0.1, page_increment=1,
                             page_size=0.1)
        self.night_gamma.configure(adj, 0.1, 1)
        self.night_gamma.set_value(settings["night-gamma"])

        self.night_on.set_active(settings["night-on"])
        self.terminal.set_text(settings["terminal"])
        self.file_manager.set_text(settings["file-manager"])
        self.editor.set_text(settings["editor"])
        self.browser.set_text(settings["browser"])
        self.launcher_columns.set_value(settings["launcher-columns"])
        self.launcher_icon_size.set_value(settings["launcher-icon-size"])
        self.launcher_file_search_columns.set_value(settings["launcher-file-search-columns"])
        self.launcher_search_files.set_active(settings["launcher-search-files"])
        self.launcher_categories.set_active(settings["launcher-categories"])
        self.launcher_resident.set_active(settings["launcher-resident"])
        self.launcher_overlay.set_active(settings["launcher-overlay"])
        self.launcher_on.set_active(settings["launcher-on"])

        self.launcher_columns.set_numeric(True)
        adj = Gtk.Adjustment(lower=1, upper=10, step_increment=1, page_increment=1,
                             page_size=1)
        self.launcher_columns.configure(adj, 1, 0)
        self.launcher_columns.set_value(settings["launcher-columns"])

        self.launcher_icon_size.set_numeric(True)
        adj = Gtk.Adjustment(lower=8, upper=256, step_increment=1, page_increment=1,
                             page_size=1)
        self.launcher_icon_size.configure(adj, 1, 0)
        self.launcher_icon_size.set_value(settings["launcher-icon-size"])

        self.launcher_file_search_columns.set_numeric(True)
        adj = Gtk.Adjustment(lower=1, upper=12, step_increment=1, page_increment=1,
                             page_size=1)
        self.launcher_file_search_columns.configure(adj, 1, 0)
        self.launcher_file_search_columns.set_value(settings["launcher-file-search-columns"])

        self.exit_position.set_active_id(settings["exit-position"])
        self.exit_full.set_active(settings["exit-full"])
        self.exit_alignment.set_active_id(settings["exit-alignment"])

        self.exit_margin.set_numeric(True)
        adj = Gtk.Adjustment(lower=0, upper=256, step_increment=1, page_increment=10,
                             page_size=1)
        self.exit_margin.configure(adj, 1, 0)
        self.exit_margin.set_value(settings["exit-margin"])

        self.exit_icon_size.set_numeric(True)
        adj = Gtk.Adjustment(lower=8, upper=256, step_increment=1, page_increment=10,
                             page_size=1)
        self.exit_icon_size.configure(adj, 1, 0)
        self.exit_icon_size.set_value(settings["exit-icon-size"])

        self.dock_position.set_active_id(settings["dock-position"])
        self.dock_full.set_active(settings["dock-full"])
        self.dock_autohide.set_active(settings["dock-autohide"])
        self.dock_alignment.set_active_id(settings["dock-alignment"])

        self.dock_margin.set_numeric(True)
        adj = Gtk.Adjustment(lower=0, upper=256, step_increment=1, page_increment=10,
                             page_size=1)
        self.dock_margin.configure(adj, 1, 0)
        self.dock_margin.set_value(settings["dock-margin"])

        self.dock_icon_size.set_numeric(True)
        adj = Gtk.Adjustment(lower=0, upper=256, step_increment=1, page_increment=10,
                             page_size=1)
        self.dock_icon_size.configure(adj, 1, 0)
        self.dock_icon_size.set_value(settings["dock-icon-size"])

    def fill_in_missing_values(self, *args):
        if self.keyboard_layout.get_text() == "":
            lang = locale.getlocale()[0].split("_")[0]
            if lang:
                self.keyboard_layout.set_text(lang)

        if self.autotiling_workspaces.get_text() == "":
            self.autotiling_workspaces.set_text(settings["autotiling-workspaces"])

        if self.night_lat.get_value() == -1.0 and self.night_long.get_value() == -1:
            self.night_lat.set_value(self.lat)
            self.night_long.set_value(self.long)
            print("Coordinates {}, {} auto-set from configured location: {}".format(self.lat, self.long, self.tz))

        if self.terminal.get_text() == "":
            self.terminal.set_text(get_terminal())

        if self.file_manager.get_text() == "":
            self.file_manager.set_text(get_file_manager())

        if self.editor.get_text() == "":
            self.editor.set_text(get_editor())

        if self.browser.get_text() == "":
            self.browser.set_text(get_browser_command())

    def read_form(self):
        settings["keyboard-layout"] = self.keyboard_layout.get_text()
        settings["autotiling-workspaces"] = self.autotiling_workspaces.get_text()
        settings["night-lat"] = self.night_lat.get_value()
        settings["night-long"] = self.night_long.get_value()
        settings["night-temp-low"] = int(self.night_temp_low.get_value())
        settings["night-temp-high"] = int(self.night_temp_high.get_value())
        settings["night-gamma"] = self.night_gamma.get_value()
        settings["night-on"] = self.night_on.get_active()
        settings["terminal"] = self.terminal.get_text()
        settings["file-manager"] = self.file_manager.get_text()
        settings["editor"] = self.editor.get_text()
        settings["browser"] = self.browser.get_text()
        settings["launcher-columns"] = int(self.launcher_columns.get_value())
        settings["launcher-icon-size"] = int(self.launcher_icon_size.get_value())
        settings["launcher-file-search-columns"] = int(self.launcher_file_search_columns.get_value())
        settings["launcher-search-files"] = self.launcher_search_files.get_active()
        settings["launcher-categories"] = self.launcher_categories.get_active()
        settings["launcher-resident"] = self.launcher_resident.get_active()
        settings["launcher-overlay"] = self.launcher_overlay.get_active()
        settings["launcher-on"] = self.launcher_on.get_active()
        settings["exit-position"] = self.exit_position.get_active_text()
        settings["exit-full"] = self.exit_full.get_active()
        settings["exit-alignment"] = self.exit_alignment.get_active_text()
        settings["exit-margin"] = int(self.exit_margin.get_value())
        settings["exit-icon-size"] = int(self.exit_icon_size.get_value())
        settings["exit-on"] = self.exit_on.get_active()
        settings["dock-position"] = self.dock_position.get_active_text()
        settings["dock-full"] = self.dock_full.get_active()
        settings["dock-autohide"] = self.dock_autohide.get_active()
        settings["dock-alignment"] = self.dock_alignment.get_active_text()
        settings["dock-margin"] = int(self.dock_margin.get_value())
        settings["dock-icon-size"] = int(self.dock_icon_size.get_value())
        settings["dock-on"] = self.dock_on.get_active()

    def on_save_btn(self, b):
        self.read_form()
        print(settings)


def main():
    GLib.set_prgname('nwg-shell')

    data_dir = get_data_dir()
    settings_file = os.path.join(data_dir, "settings")
    global settings
    if os.path.isfile(settings_file):
        settings = load_json(settings_file)
        print("Settings loaded from {}".format(settings_file))
    else:
        save_json(settings, settings_file)
        print("Created initial settings in {}".format(settings_file))

    win = MainWindow()

    print(get_lat_lon())
    print(data_dir)
    print(config_home)
    print(check_deps())

    Gtk.main()


if __name__ == '__main__':
    sys.exit(main())
