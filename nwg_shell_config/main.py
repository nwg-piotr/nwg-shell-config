#!/usr/bin/env python3

# Dependencies: python-geopy i3ipc

import argparse
import signal

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib

from nwg_shell_config.tools import *

from nwg_shell_config.__about__ import __version__

dir_name = os.path.dirname(__file__)

data_dir = ""
config_home = os.getenv('XDG_CONFIG_HOME') if os.getenv('XDG_CONFIG_HOME') else os.path.join(
    os.getenv("HOME"), ".config/")

outputs = []
settings = {}
preset = {}


def validate_workspaces(gtk_entry):
    valid_text = ""
    for char in gtk_entry.get_text():
        if char.isdigit() or char == " ":
            valid_text += char
    while '  ' in valid_text:
        valid_text = valid_text.replace('  ', ' ')
    gtk_entry.set_text(valid_text)


def handle_keyboard(window, event):
    if event.type == Gdk.EventType.KEY_RELEASE and event.keyval == Gdk.KEY_Escape:
        window.close()


class GUI(object):
    def __init__(self):
        builder = Gtk.Builder()
        builder.add_from_file(os.path.join(dir_name, "glade/main.glade"))

        self.window = builder.get_object("main-window")
        self.window.connect('destroy', Gtk.main_quit)
        self.window.connect("key-release-event", handle_keyboard)

        self.version = builder.get_object("version")

        self.keyboard_layout = builder.get_object("keyboard-layout")

        self.appindicator = builder.get_object("appindicator")

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
        self.launcher_css = builder.get_object("launcher-css")
        self.launcher_on = builder.get_object("launcher-on")

        self.exit_position = builder.get_object("exit-position")
        self.exit_full = builder.get_object("exit-full")
        self.exit_alignment = builder.get_object("exit-alignment")
        self.exit_margin = builder.get_object("exit-margin")
        self.exit_icon_size = builder.get_object("exit-icon-size")
        self.exit_css = builder.get_object("exit-css")
        self.exit_on = builder.get_object("exit-on")

        self.dock_position = builder.get_object("dock-position")

        self.dock_output = builder.get_object("dock-output")
        self.dock_output.append("Any", "Any")
        for output in outputs:
            self.dock_output.append(output, output)
        if not preset["dock-output"]:
            self.dock_output.set_active_id("Any")

        self.dock_full = builder.get_object("dock-full")
        self.dock_autohide = builder.get_object("dock-autohide")
        self.dock_alignment = builder.get_object("dock-alignment")
        self.dock_permanent = builder.get_object("dock-permanent")
        self.dock_exclusive = builder.get_object("dock-exclusive")
        self.dock_margin = builder.get_object("dock-margin")
        self.dock_icon_size = builder.get_object("dock-icon-size")
        self.dock_css = builder.get_object("dock-css")
        self.dock_on = builder.get_object("dock-on")

        self.panel_preset = builder.get_object("panel-preset")
        self.panel_preset.connect("changed", self.on_preset_changed)
        self.panel_custom = builder.get_object("panel-custom")
        self.panel_css = builder.get_object("panel-css")

        self.swaync_positionX = builder.get_object("swaync-positionX")
        self.swaync_positionY = builder.get_object("swaync-positionY")

        self.show_on_startup = builder.get_object("show-on-startup")
        self.show_help = builder.get_object("show-help")

        btn_close = builder.get_object("btn-close")
        btn_close.connect("clicked", Gtk.main_quit)
        btn_close.grab_focus()

        btn_save = builder.get_object("btn-save")
        btn_save.connect("clicked", self.on_save_btn)

        self.tz, self.lat, self.long = get_lat_lon()

        self.version.set_text("v{}".format(__version__))

        self.fill_in_from_settings(self)
        self.fill_in_missing_values(self)

    def on_preset_changed(self, combo):
        p = combo.get_active_text()
        settings["panel-preset"] = p
        self.panel_css.set_sensitive(p == "custom")
        self.panel_custom.set_visible(p == "custom")
        self.launcher_css.set_sensitive(p == "custom")
        self.exit_css.set_sensitive(p == "custom")
        self.dock_css.set_sensitive(p == "custom")

        load_preset()
        self.fill_in_from_settings()
        self.fill_in_missing_values()

    def set_chromium(self, *args):
        self.browser.set_text(
            "chromium --enable-features=UseOzonePlatform --ozone-platform=wayland")

    def set_firefox(self, *args):
        self.browser.set_text("MOZ_ENABLE_WAYLAND=1 firefox")

    def fill_in_from_settings(self, *args, skip_preset=False):
        self.keyboard_layout.set_text(settings["keyboard-layout"])
        self.autotiling_workspaces.set_text(settings["autotiling-workspaces"])
        self.autotiling_on.set_active(settings["autotiling-on"])

        self.appindicator.set_active(settings["appindicator"])

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
        adj = Gtk.Adjustment(lower=1000, upper=10001, step_increment=1, page_increment=10.0,
                             page_size=0.1)
        self.night_temp_low.configure(adj, 1, 0)
        self.night_temp_low.set_value(settings["night-temp-low"])

        self.night_temp_high.set_value(settings["night-temp-high"])
        adj = Gtk.Adjustment(lower=1000, upper=10001, step_increment=1, page_increment=10.0,
                             page_size=1)
        self.night_temp_high.configure(adj, 1, 0)
        self.night_temp_high.set_value(settings["night-temp-high"])

        self.night_gamma.set_value(settings["night-gamma"])
        adj = Gtk.Adjustment(lower=0.1, upper=10.1, step_increment=0.1, page_increment=1,
                             page_size=0.1)
        self.night_gamma.configure(adj, 0.1, 1)
        self.night_gamma.set_value(settings["night-gamma"])

        self.night_on.set_active(settings["night-on"])
        self.terminal.set_text(settings["terminal"])
        self.file_manager.set_text(settings["file-manager"])
        self.editor.set_text(settings["editor"])
        self.browser.set_text(settings["browser"])
        self.show_on_startup.set_active(settings["show-on-startup"])
        self.show_help.set_active(settings["show-help"])

        self.launcher_columns.set_value(preset["launcher-columns"])
        self.launcher_icon_size.set_value(preset["launcher-icon-size"])
        self.launcher_file_search_columns.set_value(preset["launcher-file-search-columns"])
        self.launcher_search_files.set_active(preset["launcher-search-files"])
        self.launcher_categories.set_active(preset["launcher-categories"])
        self.launcher_resident.set_active(preset["launcher-resident"])
        self.launcher_overlay.set_active(preset["launcher-overlay"])
        self.launcher_css.set_text(preset["launcher-css"])
        self.launcher_on.set_active(preset["launcher-on"])

        self.launcher_columns.set_numeric(True)
        adj = Gtk.Adjustment(lower=1, upper=10, step_increment=1, page_increment=1,
                             page_size=1)
        self.launcher_columns.configure(adj, 1, 0)
        self.launcher_columns.set_value(preset["launcher-columns"])

        self.launcher_icon_size.set_numeric(True)
        adj = Gtk.Adjustment(lower=8, upper=256, step_increment=1, page_increment=1,
                             page_size=1)
        self.launcher_icon_size.configure(adj, 1, 0)
        self.launcher_icon_size.set_value(preset["launcher-icon-size"])

        self.launcher_file_search_columns.set_numeric(True)
        adj = Gtk.Adjustment(lower=1, upper=12, step_increment=1, page_increment=1,
                             page_size=1)
        self.launcher_file_search_columns.configure(adj, 1, 0)
        self.launcher_file_search_columns.set_value(preset["launcher-file-search-columns"])

        self.exit_position.set_active_id(preset["exit-position"])
        self.exit_full.set_active(preset["exit-full"])
        self.exit_alignment.set_active_id(preset["exit-alignment"])

        self.exit_margin.set_numeric(True)
        adj = Gtk.Adjustment(lower=0, upper=256, step_increment=1, page_increment=10,
                             page_size=1)
        self.exit_margin.configure(adj, 1, 0)
        self.exit_margin.set_value(preset["exit-margin"])

        self.exit_icon_size.set_numeric(True)
        adj = Gtk.Adjustment(lower=8, upper=256, step_increment=1, page_increment=10,
                             page_size=1)
        self.exit_icon_size.configure(adj, 1, 0)
        self.exit_icon_size.set_value(preset["exit-icon-size"])
        self.exit_css.set_text(preset["exit-css"])
        self.exit_on.set_active(preset["exit-on"])

        self.dock_position.set_active_id(preset["dock-position"])
        if preset["dock-output"]:
            self.dock_output.set_active_id(preset["dock-output"])

        self.dock_full.set_active(preset["dock-full"])
        self.dock_autohide.set_active(preset["dock-autohide"])
        self.dock_permanent.set_active(preset["dock-permanent"])
        self.dock_exclusive.set_active(preset["dock-exclusive"])
        self.dock_alignment.set_active_id(preset["dock-alignment"])

        self.dock_margin.set_numeric(True)
        adj = Gtk.Adjustment(lower=0, upper=256, step_increment=1, page_increment=10,
                             page_size=1)
        self.dock_margin.configure(adj, 1, 0)
        self.dock_margin.set_value(preset["dock-margin"])

        self.dock_icon_size.set_numeric(True)
        adj = Gtk.Adjustment(lower=0, upper=256, step_increment=1, page_increment=10,
                             page_size=1)
        self.dock_icon_size.configure(adj, 1, 0)
        self.dock_icon_size.set_value(preset["dock-icon-size"])

        self.panel_preset.set_active_id(settings["panel-preset"])
        # this must be after the previous line or will get overridden by the `switch_dock` method
        self.dock_css.set_text(preset["dock-css"])
        self.dock_on.set_active(preset["dock-on"])

        self.panel_css.set_text(preset["panel-css"])
        self.panel_custom.set_text(settings["panel-custom"])

        self.swaync_positionX.set_active_id(preset["swaync-positionX"])
        self.swaync_positionY.set_active_id(preset["swaync-positionY"])

    def fill_in_missing_values(self, *args):
        if self.keyboard_layout.get_text() == "":
            self.keyboard_layout.set_text("us")

        if self.autotiling_workspaces.get_text() == "":
            self.autotiling_workspaces.set_text(settings["autotiling-workspaces"])

        if (self.night_lat.get_value() == -1.0 and self.night_long.get_value()) == -1.0 \
                or (self.night_lat.get_value() == 0 and self.night_long.get_value() == 0):
            self.night_lat.set_value(self.lat)
            self.night_long.set_value(self.long)

        if self.terminal.get_text() == "":
            self.terminal.set_text(get_terminal())

        if self.file_manager.get_text() == "":
            self.file_manager.set_text(get_file_manager())

        if self.editor.get_text() == "":
            self.editor.set_text(get_editor())

        if self.browser.get_text() == "":
            self.browser.set_text(get_browsers())

    def read_form(self):
        settings["keyboard-layout"] = self.keyboard_layout.get_text()
        settings["autotiling-workspaces"] = self.autotiling_workspaces.get_text()
        settings["autotiling-on"] = self.autotiling_on.get_active()
        settings["appindicator"] = self.appindicator.get_active()
        settings["night-lat"] = self.night_lat.get_value()
        settings["night-long"] = self.night_long.get_value()
        settings["night-temp-low"] = int(self.night_temp_low.get_value())
        settings["night-temp-high"] = int(self.night_temp_high.get_value())
        settings["night-gamma"] = round(self.night_gamma.get_value(), 2)
        settings["night-on"] = self.night_on.get_active()
        settings["terminal"] = self.terminal.get_text()
        settings["file-manager"] = self.file_manager.get_text()
        settings["editor"] = self.editor.get_text()
        settings["browser"] = self.browser.get_text()
        settings["panel-preset"] = self.panel_preset.get_active_text()
        settings["panel-custom"] = self.panel_custom.get_text()
        settings["show-on-startup"] = self.show_on_startup.get_active()
        settings["show-help"] = self.show_help.get_active()

        preset["launcher-columns"] = int(self.launcher_columns.get_value())
        preset["launcher-icon-size"] = int(self.launcher_icon_size.get_value())
        preset["launcher-file-search-columns"] = int(self.launcher_file_search_columns.get_value())
        preset["launcher-search-files"] = self.launcher_search_files.get_active()
        preset["launcher-categories"] = self.launcher_categories.get_active()
        preset["launcher-resident"] = self.launcher_resident.get_active()
        preset["launcher-overlay"] = self.launcher_overlay.get_active()
        preset["launcher-css"] = self.launcher_css.get_text()
        preset["launcher-on"] = self.launcher_on.get_active()
        preset["exit-position"] = self.exit_position.get_active_text()
        preset["exit-full"] = self.exit_full.get_active()
        preset["exit-alignment"] = self.exit_alignment.get_active_text()
        preset["exit-margin"] = int(self.exit_margin.get_value())
        preset["exit-icon-size"] = int(self.exit_icon_size.get_value())
        preset["exit-css"] = self.exit_css.get_text()
        preset["exit-on"] = self.exit_on.get_active()
        preset["dock-position"] = self.dock_position.get_active_text()
        if self.dock_output.get_active_text():
            preset["dock-output"] = self.dock_output.get_active_text()
        preset["dock-full"] = self.dock_full.get_active()
        preset["dock-autohide"] = self.dock_autohide.get_active()
        preset["dock-permanent"] = self.dock_permanent.get_active()
        preset["dock-exclusive"] = self.dock_exclusive.get_active()
        preset["dock-alignment"] = self.dock_alignment.get_active_text()
        preset["dock-margin"] = int(self.dock_margin.get_value())
        preset["dock-icon-size"] = int(self.dock_icon_size.get_value())
        preset["dock-css"] = self.dock_css.get_text()
        preset["dock-on"] = self.dock_on.get_active()
        preset["panel-css"] = self.panel_css.get_text()

        preset["swaync-positionX"] = self.swaync_positionX.get_active_id()
        preset["swaync-positionY"] = self.swaync_positionY.get_active_id()

    def on_save_btn(self, b):
        self.read_form()
        save_preset()
        update_swaync_config(preset["swaync-positionX"], preset["swaync-positionY"])

        save_includes()
        f = os.path.join(data_dir, "settings")
        print("Saving {}".format(f))
        save_json(settings, f)


def save_includes():
    cmd_launcher_autostart = ""

    # ~/.config/sway/variables
    variables = []
    if settings["keyboard-layout"]:
        variables.append("set $lang '{}'".format(settings["keyboard-layout"]))
    if settings["terminal"]:
        variables.append("set $term {}".format(settings["terminal"]))
    if settings["browser"]:
        variables.append("set $browser {}".format(settings["browser"]))
    if settings["file-manager"]:
        variables.append("set $filemanager {}".format(settings["file-manager"]))
    if settings["editor"]:
        variables.append("set $editor {}".format(settings["editor"]))

    cmd_launcher = "nwg-drawer"
    if preset["launcher-resident"]:
        cmd_launcher += " -r"
    if preset["launcher-columns"]:
        cmd_launcher += " -c {}".format(preset["launcher-columns"])
    if preset["launcher-icon-size"]:
        cmd_launcher += " -is {}".format(preset["launcher-icon-size"])
    if preset["launcher-file-search-columns"]:
        cmd_launcher += " -fscol {}".format(preset["launcher-file-search-columns"])
    if not preset["launcher-search-files"]:
        cmd_launcher += " -nofs"
    if not preset["launcher-categories"]:
        cmd_launcher += " -nocats"
    if preset["launcher-overlay"]:
        cmd_launcher += " -ovl"
    if preset["launcher-css"]:
        cmd_launcher += " -s {}".format(preset["launcher-css"])
    if settings["terminal"]:
        cmd_launcher += " -term {}".format(settings["terminal"])

    if preset["launcher-on"]:
        if preset["launcher-resident"]:
            cmd_launcher_autostart = "exec_always {}".format(cmd_launcher)
            variables.append("set $launcher nwg-drawer")
        else:
            variables.append("set $launcher {}".format(cmd_launcher))

    cmd_exit = "nwg-bar"
    if preset["exit-position"]:
        cmd_exit += " -p {}".format(preset["exit-position"])
    if preset["exit-full"]:
        cmd_exit += " -f"
    if preset["exit-alignment"]:
        cmd_exit += " -a {}".format(preset["exit-alignment"])
    if preset["exit-margin"]:
        cmd_exit += " -mb {} -ml {} -mr {} -mt {}".format(preset["exit-margin"], preset["exit-margin"],
                                                          preset["exit-margin"], preset["exit-margin"])
    if preset["exit-icon-size"]:
        cmd_exit += " -i {}".format(preset["exit-icon-size"])
    if preset["exit-css"]:
        cmd_exit += " -s {}".format(preset["exit-css"])

    variables.append("set $exit {}".format(cmd_exit))

    cmd_dock = "nwg-dock"
    if preset["dock-autohide"]:
        cmd_dock += " -d"
    elif preset["dock-permanent"]:
        cmd_dock += " -r"
    if preset["dock-position"]:
        cmd_dock += " -p {}".format(preset["dock-position"])
    if preset["dock-output"] and preset["dock-output"] != "Any":
        cmd_dock += " -o {}".format(preset["dock-output"])
    if preset["dock-full"]:
        cmd_dock += " -f"
    if preset["dock-alignment"]:
        cmd_dock += " -a {}".format(preset["dock-alignment"])
    if preset["dock-margin"]:
        cmd_dock += " -mb {} -ml {} -mr {} -mt {}".format(preset["dock-margin"], preset["dock-margin"],
                                                          preset["dock-margin"], preset["dock-margin"])
    if preset["dock-icon-size"]:
        cmd_dock += " -i {}".format(preset["dock-icon-size"])

    if preset["dock-exclusive"]:
        cmd_dock += " -x"

    if preset["dock-css"]:
        cmd_dock += " -s {}".format(preset["dock-css"])

    if preset["dock-on"] and not preset["dock-autohide"] and not preset["dock-permanent"]:
        variables.append("set $dock {}".format(cmd_dock))

    save_list_to_text_file(variables, os.path.join(config_home, "sway/variables"))

    # ~/.config/sway/autostart
    autostart = []
    if settings["night-on"]:
        cmd_night = "exec wlsunset"
        if settings["night-lat"]:
            cmd_night += " -l {}".format(settings["night-lat"])
        if settings["night-long"]:
            cmd_night += " -L {}".format(settings["night-long"])
        if settings["night-temp-low"]:
            cmd_night += " -t {}".format(settings["night-temp-low"])
        if settings["night-temp-high"]:
            cmd_night += " -T {}".format(settings["night-temp-high"])
        if settings["night-gamma"]:
            cmd_night += " -g {}".format(settings["night-gamma"])
        autostart.append(cmd_night)

    name = settings["panel-preset"] if not settings["panel-preset"] == "custom" else "style"
    p = os.path.join(config_home, "swaync")
    autostart.append("exec swaync -s {}/{}.css".format(p, name))

    if settings["appindicator"]:
        autostart.append("exec nm-applet --indicator")

    if settings["autotiling-on"]:
        cmd_autoiling = "exec_always autotiling"
        if settings["autotiling-workspaces"]:
            cmd_autoiling += " -w {}".format(settings["autotiling-workspaces"])
        autostart.append(cmd_autoiling)

    if cmd_launcher_autostart:
        autostart.append(cmd_launcher_autostart)

    if preset["dock-on"] and (preset["dock-autohide"] or preset["dock-permanent"]):
        autostart.append("exec_always {}".format(cmd_dock))

    cmd_panel = "exec_always nwg-panel"
    if settings["panel-preset"] != "custom":
        cmd_panel += " -c {}".format(settings["panel-preset"])
    elif settings["panel-custom"]:
        cmd_panel += " -c {}".format(settings["panel-custom"])
    if preset["panel-css"]:
        cmd_panel += " -s {}".format(preset["panel-css"])
    autostart.append(cmd_panel)

    autostart.append("exec_always nwg-shell-check-updates")

    if settings["show-help"]:
        autostart.append("exec_always nwg-wrapper -t help-sway.pango -c help-sway.css -p right -mr 50 -si -sq 14")

    if settings["show-on-startup"]:
        autostart.append("exec nwg-shell-config")

    save_list_to_text_file(autostart, os.path.join(config_home, "sway/autostart"))

    reload()


def reload():
    name = settings["panel-preset"] if not settings["panel-preset"] == "custom" else "style"
    p = os.path.join(config_home, "swaync")
    swaync_daemon = "swaync -s {}/{}.css &".format(p, name)

    for cmd in ["pkill -f autotiling",
                "pkill -f nwg-drawer",
                "pkill -f nwg-dock",
                "pkill -f nwg-bar",
                "pkill -f swaync",
                "pkill -f swaync",
                swaync_daemon,
                "swaync-client --reload-config",
                "swaymsg reload"]:
        subprocess.call(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    # kill running help window if any
    if not settings["show-help"]:
        subprocess.call("pkill -14 nwg-wrapper", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)


def load_settings():
    defaults = {
        "keyboard-layout": "us",
        "autotiling-workspaces": "1 2 3 4 5 6 7 8",
        "autotiling-on": True,
        "appindicator": True,
        "night-lat": -1,
        "night-long": -1,
        "night-temp-low": 4500,
        "night-temp-high": 6500,
        "night-gamma": 1.0,
        "night-on": True,
        "terminal": "",
        "file-manager": "",
        "editor": "",
        "browser": "",
        "panel-preset": "preset-0",
        "panel-custom": "",
        "show-on-startup": True,
        "show-help": False,
        "last-upgrade-check": 0
    }
    settings_file = os.path.join(data_dir, "settings")
    global settings
    if os.path.isfile(settings_file):
        print("Loading settings")
        settings = load_json(settings_file)
        for key in defaults:
            missing = 0
            if key not in settings:
                settings[key] = defaults[key]
                print("'{}' key missing from settings, adding '{}'".format(key, defaults[key]))
                missing += 1
            if missing > 0:
                print("Saving {}".format(settings_file))
                save_json(defaults, settings_file)
    else:
        print("ERROR: failed loading settings, creating {}".format(settings_file), file=sys.stderr)
        save_json(defaults, settings_file)


def load_preset():
    defaults = {
        "panel-css": "",
        "launcher-columns": 6,
        "launcher-icon-size": 64,
        "launcher-file-search-columns": 2,
        "launcher-search-files": True,
        "launcher-categories": True,
        "launcher-resident": False,
        "launcher-overlay": False,
        "launcher-css": "",
        "launcher-on": True,
        "exit-position": "center",
        "exit-full": False,
        "exit-alignment": "middle",
        "exit-margin": 0,
        "exit-icon-size": 48,
        "exit-css": "",
        "exit-on": True,
        "dock-position": "bottom",
        "dock-output": "",
        "dock-full": False,
        "dock-autohide": False,
        "dock-permanent": False,
        "dock-exclusive": False,
        "dock-alignment": "center",
        "dock-margin": 0,
        "dock-icon-size": 48,
        "dock-css": "",
        "dock-on": False,
        "swaync-positionX": "right",
        "swaync-positionY": "top"
    }
    global preset
    preset_file = os.path.join(data_dir, settings["panel-preset"])
    if os.path.isfile(preset_file):
        print("Loading preset from {}".format(preset_file))
        preset = load_json(preset_file)
        missing = 0
        for key in defaults:
            if key not in preset:
                preset[key] = defaults[key]
                print("'{}' key missing from preset, adding '{}'".format(key, defaults[key]))
                missing += 1
            if missing > 0:
                print("Saving {}".format(preset_file))
                save_json(defaults, preset_file)
    else:
        print("ERROR: failed loading preset, creating {}".format(preset_file), file=sys.stderr)
        save_json(defaults, preset_file)


def save_preset():
    f = os.path.join(data_dir, settings["panel-preset"])
    print("Saving {}".format(f))
    save_json(preset, f)


def update_swaync_config(pos_x, pos_y):
    settings_file = os.path.join(config_home, "swaync/config.json")
    if os.path.isfile(settings_file):
        print("Loading swaync settings from {}".format(settings_file))
        swaync_settings = load_json(settings_file)
        swaync_settings["positionX"] = pos_x
        swaync_settings["positionY"] = pos_y
    else:
        swaync_settings = {"positionX": pos_x, "positionY": pos_y}
    print("Saving swaync settings to {}".format(settings_file))
    save_json(swaync_settings, settings_file)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v",
                        "--version",
                        action="version",
                        version="%(prog)s version {}".format(__version__),
                        help="display version information")
    parser.parse_args()

    GLib.set_prgname('nwg-shell-config')

    global data_dir
    data_dir = get_data_dir()

    global outputs
    outputs = list_outputs()

    print("Outputs: {}".format(outputs))
    print("Data dir: {}".format(data_dir))
    print("Config home: {}".format(config_home))

    init_files(os.path.join(dir_name, "shell"), data_dir)

    load_settings()

    load_preset()
    ui = GUI()
    ui.window.show_all()
    if settings["panel-preset"] != "custom":
        ui.panel_custom.set_visible(False)
        ui.panel_css.set_sensitive(False)
        ui.launcher_css.set_sensitive(False)
        ui.exit_css.set_sensitive(False)
        ui.dock_css.set_sensitive(False)
    else:
        ui.panel_custom.set_sensitive(True)
        ui.panel_css.set_sensitive(True)
        ui.launcher_css.set_sensitive(True)
        ui.exit_css.set_sensitive(True)
        ui.dock_css.set_sensitive(True)

    Gtk.main()


if __name__ == '__main__':
    sys.exit(main())
