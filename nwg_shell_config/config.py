#!/usr/bin/env python3

# Dependencies: python-geopy i3ipc

import argparse

import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk, GLib

from nwg_shell_config.tools import *
from nwg_shell_config.ui_components import *

from nwg_shell_config.__about__ import __version__

dir_name = os.path.dirname(__file__)

data_dir = ""
config_home = os.getenv('XDG_CONFIG_HOME') if os.getenv('XDG_CONFIG_HOME') else os.path.join(
    os.getenv("HOME"), ".config/")

outputs = []
settings = {}
# preset = {}
preset_0 = {}
preset_1 = {}
preset_2 = {}
preset_3 = {}
preset_custom = {}

content = Gtk.Frame()
submenus = []
current_submenu = None
btn_apply = Gtk.Button()
grid = Gtk.Grid()


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


def side_menu():
    list_box = Gtk.ListBox()
    list_box.set_property("margin-top", 6)

    row = Gtk.ListBoxRow()
    row.set_selectable(False)
    lbl = Gtk.Label()
    lbl.set_property("halign", Gtk.Align.START)
    lbl.set_markup("<b>Common</b>")
    lbl.set_property("margin-top", 3)
    lbl.set_property("margin-start", 3)
    row.add(lbl)
    list_box.add(row)

    row = SideMenuRow("Screen settings")
    row.eb.connect("button-press-event", set_up_screen_tab)
    list_box.add(row)

    row = SideMenuRow("Keyboard")
    row.eb.connect("button-press-event", set_up_keyboard_tab)
    list_box.add(row)

    row = SideMenuRow("Pointer device")
    row.eb.connect("button-press-event", set_up_pointer_tab)
    list_box.add(row)

    row = SideMenuRow("Touchpad")
    row.eb.connect("button-press-event", hide_submenus)
    list_box.add(row)

    row = SideMenuRow("Applications")
    row.eb.connect("button-press-event", set_up_applications_tab)
    list_box.add(row)

    row = Gtk.ListBoxRow()
    row.set_selectable(False)
    lbl = Gtk.Label()
    lbl.set_property("halign", Gtk.Align.START)
    lbl.set_property("margin-top", 6)
    lbl.set_markup("<b>Desktop styles</b>")
    lbl.set_property("margin-start", 3)
    row.add(lbl)
    list_box.add(row)

    row = SideMenuRow("Preset 0")
    list_box.add(row)

    submenu_0 = preset_menu(0)
    list_box.add(submenu_0)
    row.eb.connect("button-press-event", toggle_submenu, submenu_0)

    row = SideMenuRow("Preset 1")
    list_box.add(row)

    submenu_1 = preset_menu(1)
    list_box.add(submenu_1)
    row.eb.connect("button-press-event", toggle_submenu, submenu_1)

    row = SideMenuRow("Preset 2")
    list_box.add(row)

    submenu_2 = preset_menu(2)
    list_box.add(submenu_2)
    row.eb.connect("button-press-event", toggle_submenu, submenu_2)

    row = SideMenuRow("Preset 3")
    list_box.add(row)

    submenu_3 = preset_menu(3)
    list_box.add(submenu_3)
    row.eb.connect("button-press-event", toggle_submenu, submenu_3)

    row = SideMenuRow("Custom preset")
    list_box.add(row)

    submenu_c = preset_menu("c")
    list_box.add(submenu_c)
    row.eb.connect("button-press-event", toggle_submenu, submenu_c)

    list_box.set_selection_mode(Gtk.SelectionMode.NONE)
    return list_box


def preset_menu(preset_id):
    if preset_id == 0:
        preset = preset_0
        preset_name = "Preset 0"
    elif preset_id == 1:
        preset = preset_1
        preset_name = "Preset 1"
    elif preset_id == 2:
        preset = preset_2
        preset_name = "Preset 2"
    elif preset_id == 3:
        preset = preset_3
        preset_name = "Preset 3"
    else:
        preset = preset_custom
        preset_name = "Custom preset"

    list_box = Gtk.ListBox()

    row = SubMenuRow("App drawer")
    row.eb.connect("button-press-event", set_up_drawer_tab, preset, preset_name)
    list_box.add(row)

    row = SubMenuRow("Dock")
    row.eb.connect("button-press-event", set_up_dock_tab, preset, preset_name)
    list_box.add(row)

    row = SubMenuRow("Exit menu")
    row.eb.connect("button-press-event", set_up_bar_tab, preset, preset_name)
    list_box.add(row)

    row = SubMenuRow("Notifications")
    row.eb.connect("button-press-event", set_up_notification_tab, preset, preset_name)
    list_box.add(row)

    if preset_id == "c":
        row = SubMenuRow("Panel & css")
        row.eb.connect("button-press-event", set_up_panel_styling_tab, preset, preset_name)
        list_box.add(row)

    global submenus
    submenus.append(list_box)

    list_box.set_selection_mode(Gtk.SelectionMode.NONE)
    return list_box


def hide_submenus(*args):
    for item in submenus:
        if item != current_submenu:
            item.hide()


def toggle_submenu(event_box, event_button, listbox):
    global current_submenu
    current_submenu = listbox
    hide_submenus()
    if not listbox.is_visible():
        listbox.show_all()
        listbox.unselect_all()
    else:
        listbox.hide()


def set_up_screen_tab(*args):
    hide_submenus()
    global content
    content.destroy()
    content = screen_tab(settings)
    grid.attach(content, 1, 0, 1, 1)


def set_up_applications_tab(*args, warn=False):
    hide_submenus()
    global content
    content.destroy()
    content = applications_tab(settings, warn)
    grid.attach(content, 1, 0, 1, 1)


def set_up_keyboard_tab(*args):
    hide_submenus()
    global content
    content.destroy()
    content = keyboard_tab(settings)
    grid.attach(content, 1, 0, 1, 1)


def set_up_pointer_tab(*args):
    hide_submenus()
    global content
    content.destroy()
    content = pointer_tab(settings)
    grid.attach(content, 1, 0, 1, 1)


def set_up_drawer_tab(event_box, event_button, preset, preset_name):
    hide_submenus()
    global content
    content.destroy()
    content = drawer_tab(preset, preset_name)
    grid.attach(content, 1, 0, 1, 1)


def set_up_dock_tab(event_box, event_button, preset, preset_name):
    hide_submenus()
    global content
    content.destroy()
    content = dock_tab(preset, preset_name, outputs)
    grid.attach(content, 1, 0, 1, 1)


def set_up_bar_tab(event_box, event_button, preset, preset_name):
    hide_submenus()
    global content
    content.destroy()
    content = bar_tab(preset, preset_name)
    grid.attach(content, 1, 0, 1, 1)


def set_up_notification_tab(event_box, event_button, preset, preset_name):
    hide_submenus()
    global content
    content.destroy()
    content = notification_tab(preset, preset_name)
    grid.attach(content, 1, 0, 1, 1)


def set_up_panel_styling_tab(event_box, event_button, preset, preset_name):
    hide_submenus()
    global content
    content.destroy()
    content = panel_styling_tab(settings, preset, preset_name)
    grid.attach(content, 1, 0, 1, 1)


class GUI(object):
    def __init__(self):
        builder = Gtk.Builder()
        builder.add_from_file(os.path.join(dir_name, "glade/form.glade"))

        self.window = builder.get_object("window")
        self.window.connect('destroy', Gtk.main_quit)
        self.window.connect("key-release-event", handle_keyboard)

        global grid
        grid = builder.get_object("grid")

        self.menu = side_menu()
        grid.attach(self.menu, 0, 0, 1, 1)

        self.version = builder.get_object("version-label")
        self.version.set_text("v{}".format(__version__))

        github = builder.get_object("github")
        github.set_markup('<a href="https://github.com/nwg-piotr/nwg-shell-config">GitHub</a>')

        """
        self.fill_in_from_settings(self)
        self.fill_in_missing_values(self)
        """

        cb_show = builder.get_object("show-on-startup")
        cb_show.set_active(settings["show-on-startup"])
        cb_show.connect("toggled", set_from_checkbutton, settings, "show-on-startup")

        btn_close = builder.get_object("btn-close")
        btn_close.connect("clicked", Gtk.main_quit)
        btn_close.grab_focus()

        global btn_apply
        btn_apply = builder.get_object("btn-apply")
        btn_apply.connect("clicked", self.on_apply_btn)

        self.tz, self.lat, self.long = get_lat_lon()

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

    def on_apply_btn(self, b):
        save_presets()
        presets = {
            "preset-0": preset_0,
            "preset-1": preset_1,
            "preset-2": preset_2,
            "preset-3": preset_3,
            "custom": preset_custom
        }
        preset = presets[settings["panel-preset"]]
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

    if settings["panel-preset"] == "preset-0":
        preset = preset_0
    elif settings["panel-preset"] == "preset-1":
        preset = preset_1
    elif settings["panel-preset"] == "preset-2":
        preset = preset_2
    elif settings["panel-preset"] == "preset-3":
        preset = preset_3
    else:
        preset = preset_custom

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
        "autotiling-workspaces": "",
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
        "keyboard-use-settings": True,
        "keyboard-xkb-layout": "us",
        "keyboard-xkb-variant": "",
        "keyboard-repeat-delay": 300,
        "keyboard-repeat-rate": 40,
        "keyboard-xkb-capslock": "disabled",
        "keyboard-xkb-numlock": "disabled",
        "pointer-use-settings": True,
        "pointer-accel-profile": "flat",
        "pointer-pointer-accel": 0.0,
        "pointer-natural-scroll": "disabled",
        "pointer-scroll-factor": 1.0,
        "pointer-left-handed": "disabled",
        "last-upgrade-check": 0
    }
    settings_file = os.path.join(data_dir, "settings")
    global settings
    if os.path.isfile(settings_file):
        print("Loading settings")
        settings = load_json(settings_file)
        missing = 0
        for key in defaults:
            if key not in settings:
                settings[key] = defaults[key]
                print("'{}' key missing from settings, adding '{}'".format(key, defaults[key]))
                missing += 1
        if missing > 0:
            print("Saving {}".format(settings_file))
            save_json(settings, settings_file)
    else:
        print("ERROR: failed loading settings, creating {}".format(settings_file), file=sys.stderr)
        save_json(defaults, settings_file)


def load_presets():
    global preset_0
    preset_0 = load_preset("preset-0")
    global preset_1
    preset_1 = load_preset("preset-1")
    global preset_2
    preset_2 = load_preset("preset-2")
    global preset_3
    preset_3 = load_preset("preset-3")
    global preset_custom
    preset_custom = load_preset("custom")


def load_preset(file_name):
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
    preset_file = os.path.join(data_dir, file_name)
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

        return preset
    else:
        print("ERROR: failed loading preset, creating {}".format(preset_file), file=sys.stderr)
        save_json(defaults, preset_file)

        return {}


def save_presets():
    global preset_0, preset_1, preset_2, preset_3, preset_custom

    f = os.path.join(data_dir, "preset-0")
    print("Saving {}".format(f))
    save_json(preset_0, f)

    f = os.path.join(data_dir, "preset-1")
    print("Saving {}".format(f))
    save_json(preset_1, f)

    f = os.path.join(data_dir, "preset-2")
    print("Saving {}".format(f))
    save_json(preset_2, f)

    f = os.path.join(data_dir, "preset-3")
    print("Saving {}".format(f))
    save_json(preset_3, f)

    f = os.path.join(data_dir, "custom")
    print("Saving {}".format(f))
    save_json(preset_custom, f)


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

    # load_preset()
    load_presets()

    ui = GUI()

    screen = Gdk.Screen.get_default()
    provider = Gtk.CssProvider()
    style_context = Gtk.StyleContext()
    style_context.add_provider_for_screen(screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
    css = b"""
            button#app-btn { padding: 6px; border: none }
            * { outline: none }
            """
    provider.load_from_data(css)

    if not settings["terminal"] or not settings["file-manager"] or not settings["editor"] or not settings["browser"]:
        set_up_applications_tab(warn=True)
    else:
        set_up_screen_tab()

    ui.window.show_all()
    hide_submenus()
    """if settings["panel-preset"] != "custom":
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
        ui.dock_css.set_sensitive(True)"""

    Gtk.main()


if __name__ == '__main__':
    sys.exit(main())
