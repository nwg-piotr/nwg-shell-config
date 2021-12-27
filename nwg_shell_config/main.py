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

settings = {"keyboard-layout": "", "autotiling-workspaces": "1 2 3 4 5 6 7 8", "autotiling-on": True,
            "night-lat": -1.0, "night-long": -1.0, "night-temp-low": 4000, "night-temp-high": 6500, "night-gamma": 1.0,
            "night-on": True, "terminal": "foot", "file-manager": "", "editor": "", "browser": "",
            "launcher-columns": 3, "launcher-icon-size": 64, "launcher-file-search-columns": 2,
            "launcher-search-files": True, "launcher-categories": True, "launcher-overlay": False,
            "exit-position": "center", "exit-full": False, "exit-alignment": "middle", "exit-margin": 0,
            "exit-icon-size": 48, "exit-on": True, "dock-position": "bottom", "dock-full": False,
            "dock-alignment": "center", "dock-margin": 0, "dock-icon-size": 48, "dock-on": False}


class MainWindow(Gtk.Window):
    def __init__(self):
        builder = Gtk.Builder()
        builder.add_from_file(os.path.join(dir_name, "glade/main.glade"))

        self.window = builder.get_object("main-window")
        self.window.connect('destroy', Gtk.main_quit)
        self.keyboard_layout = builder.get_object("keyboard-layout")

        self.autotiling_workspaces = builder.get_object("autotiling-workspaces")
        self.autotiling_on = builder.get_object("autotiling-on")

        self.night_lat = builder.get_object("night-lat")
        self.night_long = builder.get_object("night-long")
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
        self.launcher_overlay = builder.get_object("launcher-overlay")

        self.exit_position = builder.get_object("exit-position")
        self.exit_full = builder.get_object("exit-full")
        self.exit_alignment = builder.get_object("exit-alignment")
        self.exit_margin = builder.get_object("exit-margin")
        self.exit_icon_size = builder.get_object("exit-icon-size")
        self.exit_on = builder.get_object("exit-on")

        self.dock_position = builder.get_object("dock-position")
        self.dock_full = builder.get_object("dock-full")
        self.dock_alignment = builder.get_object("dock-alignment")
        self.dock_margin = builder.get_object("dock-margin")
        self.dock_icon_size = builder.get_object("dock-icon-size")
        self.dock_on = builder.get_object("dock-on")

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
        adj = Gtk.Adjustment(value=0.0, lower=-90.0, upper=90.1, step_increment=0.1, page_increment=10.0,
                             page_size=0.1)
        self.night_lat.configure(adj, 0.1, 4)
        self.night_lat.set_value(settings["night-lat"])

        self.night_long.set_value(settings["night-long"])
        adj = Gtk.Adjustment(value=0.0, lower=-180.0, upper=180.1, step_increment=0.1, page_increment=10.0,
                             page_size=0.1)
        self.night_long.configure(adj, 0.1, 4)
        self.night_long.set_value(settings["night-long"])

        self.night_temp_low.set_value(settings["night-temp-low"])
        adj = Gtk.Adjustment(value=0.0, lower=1000, upper=6500, step_increment=1, page_increment=10.0,
                             page_size=0.1)
        self.night_temp_low.configure(adj, 1, 0)
        self.night_temp_low.set_value(settings["night-temp-low"])

        self.night_temp_high.set_value(settings["night-temp-high"])
        adj = Gtk.Adjustment(value=0.0, lower=1000, upper=6500, step_increment=1, page_increment=10.0,
                             page_size=0.1)
        self.night_temp_high.configure(adj, 1, 0)
        self.night_temp_high.set_value(settings["night-temp-high"])

        self.night_gamma.set_value(settings["night-gamma"])
        adj = Gtk.Adjustment(value=0.0, lower=0.1, upper=1.1, step_increment=0.1, page_increment=1,
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
        self.launcher_overlay.set_active(settings["launcher-overlay"])

    def fill_in_missing_values(self, *args):
        if self.keyboard_layout.get_text() == "":
            lang = locale.getlocale()[0].split("_")[0]
            if lang:
                self.keyboard_layout.set_text(lang)

        if self.autotiling_workspaces.get_text() == "":
            self.autotiling_workspaces.set_text(settings["autotiling-workspaces"])

        if self.night_lat.get_value() == -1.0 and self.night_long.get_value() == -1:
            tz, lat, long = get_lat_lon()
            self.night_lat.set_value(lat)
            self.night_long.set_value(long)
            print("Coordinates {}, {} auto-set from configured location: {}".format(lat, long, tz))

        if self.terminal.get_text() == "":
            self.terminal.set_text(get_terminal())

        if self.file_manager.get_text() == "":
            self.file_manager.set_text(get_file_manager())

        if self.editor.get_text() == "":
            self.editor.set_text(get_editor())

        if self.browser.get_text() == "":
            self.browser.set_text(get_browser_command())


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
