#!/usr/bin/env python3

"""
nwg-shell config utility
Repository: https://github.com/nwg-piotr/nwg-shell-config
Project site: https://nwg-piotr.github.io/nwg-shell
Author's email: nwg.piotr@gmail.com
Copyright (c) 2021-2024 Piotr Miller & Contributors
License: MIT
"""

import argparse
import os.path
import signal
import time

from nwg_shell_config.tools import *
from nwg_shell_config.ui_components import *
from nwg_shell_config.__about__ import __version__, __need_update__
import gi

gi.require_version('Gdk', '3.0')
from gi.repository import Gdk, GLib

gi.require_version('Gtk', '3.0')

dir_name = os.path.dirname(__file__)

shell_data = load_shell_data()
pending_updates = 0
update_btn = Gtk.Button()

data_dir = ""
config_home = get_config_home()

data_home = get_data_home()

voc = {}
ui = None

outputs = []
settings = {}
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

backup_configs = ["azote", "foot", "gtklock", "hypr", "nwg-bar", "nwg-displays", "nwg-dock", "nwg-dock-hyprland",
                  "nwg-drawer", "nwg-look", "nwg-panel", "sway", "swaync"]

backup_data = ["nwg-look", "nwg-panel", "nwg-shell-config"]


def check_updates():
    global shell_data
    shell_data = load_shell_data()
    global pending_updates
    pending_updates = 0
    for v in __need_update__:
        if v not in shell_data["updates"] and is_newer(v, shell_data["installed-version"]):
            pending_updates += 1
    global update_btn
    if pending_updates > 0:
        img = Gtk.Image.new_from_icon_name("nwg-shell-update", Gtk.IconSize.DIALOG)

        update_btn.set_label("Updates ({})".format(pending_updates))
    else:
        img = Gtk.Image.new_from_icon_name("nwg-shell", Gtk.IconSize.DIALOG)
        update_btn.set_label("Updates")
    update_btn.set_image(img)


def signal_handler(sig, frame):
    if sig == 2 or sig == 15:
        desc = {2: "SIGINT", 15: "SIGTERM"}
        print("terminated with {}".format(desc[sig]))
        Gtk.main_quit()
    elif sig == 10:
        print("SIGUSR1 received, checking updates")
        check_updates()
    elif sig != 17:
        print("signal {} received".format(sig))


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
    lbl.set_markup("<b>{}</b>".format(voc["common"]))
    lbl.set_property("margin-top", 3)
    lbl.set_property("margin-start", 3)
    row.add(lbl)
    list_box.add(row)

    row = SideMenuRow(voc["screen-settings"])
    row.eb.connect("button-press-event", set_up_screen_tab)
    list_box.add(row)

    row = SideMenuRow(voc["general-settings"])
    row.eb.connect("button-press-event", h_set_up_general_tab)
    list_box.add(row)

    row = SideMenuRow(voc["dwindle-layout"])
    row.eb.connect("button-press-event", h_set_up_dwindle_tab)
    list_box.add(row)

    row = SideMenuRow(voc["master-layout"])
    row.eb.connect("button-press-event", h_set_up_master_tab)
    list_box.add(row)

    row = SideMenuRow(voc["input-devices"])
    row.eb.connect("button-press-event", h_set_up_input_tab)
    list_box.add(row)

    row = SideMenuRow("  {}".format(voc["touchpad"]))
    row.eb.connect("button-press-event", set_up_touchpad_tab)
    list_box.add(row)

    row = SideMenuRow(voc["miscellaneous"])
    row.eb.connect("button-press-event", h_set_up_misc_tab)
    list_box.add(row)

    row = SideMenuRow(voc["idle-lock-screen"])
    row.eb.connect("button-press-event", set_up_lockscreen_tab)
    list_box.add(row)

    # currently gtklock does not work on Hyprland
    # row = SideMenuRow(voc["gtklock"])
    # row.eb.connect("button-press-event", set_up_gtklock_tab)
    # list_box.add(row)

    row = SideMenuRow(voc["applications"])
    row.eb.connect("button-press-event", set_up_applications_tab)
    list_box.add(row)

    row = SideMenuRow(voc["backup"])
    row.eb.connect("button-press-event", set_up_backup_tab, config_home, data_home, backup_configs, backup_data)
    list_box.add(row)

    row = SideMenuRow(voc["system-info"])
    row.eb.connect("button-press-event", set_up_sys_info_tab)
    list_box.add(row)

    row = Gtk.ListBoxRow()
    row.set_selectable(False)
    lbl = Gtk.Label()
    lbl.set_property("halign", Gtk.Align.START)
    lbl.set_property("margin-top", 6)
    lbl.set_markup("<b>{}</b>".format(voc["desktop-styles"]))
    lbl.set_property("margin-start", 3)
    row.add(lbl)
    list_box.add(row)

    row = SideMenuRow("{} 0".format("hyprland-"))
    list_box.add(row)

    submenu_0 = preset_menu(0)
    list_box.add(submenu_0)
    row.eb.connect("button-press-event", toggle_submenu, submenu_0)

    row = SideMenuRow("{} 1".format("hyprland-"))
    list_box.add(row)

    submenu_1 = preset_menu(1)
    list_box.add(submenu_1)
    row.eb.connect("button-press-event", toggle_submenu, submenu_1)

    row = SideMenuRow("{} 2".format("hyprland-"))
    list_box.add(row)

    submenu_2 = preset_menu(2)
    list_box.add(submenu_2)
    row.eb.connect("button-press-event", toggle_submenu, submenu_2)

    row = SideMenuRow("{} 3".format("hyprland-"))
    list_box.add(row)

    submenu_3 = preset_menu(3)
    list_box.add(submenu_3)
    row.eb.connect("button-press-event", toggle_submenu, submenu_3)

    row = SideMenuRow("custom-hyprland")
    list_box.add(row)

    submenu_c = preset_menu("c")
    list_box.add(submenu_c)
    row.eb.connect("button-press-event", toggle_submenu, submenu_c)

    list_box.set_selection_mode(Gtk.SelectionMode.NONE)
    return list_box


def preset_menu(preset_id):
    if preset_id == 0:
        preset = preset_0
        preset_name = "{} 0".format(voc["preset"])
    elif preset_id == 1:
        preset = preset_1
        preset_name = "{} 1".format(voc["preset"])
    elif preset_id == 2:
        preset = preset_2
        preset_name = "{} 2".format(voc["preset"])
    elif preset_id == 3:
        preset = preset_3
        preset_name = "{} 3".format(voc["preset"])
    else:
        preset = preset_custom
        preset_name = "Custom preset"

    list_box = Gtk.ListBox()

    row = SideMenuRow(voc["app-drawer"], margin_start=18)
    row.eb.connect("button-press-event", set_up_drawer_tab, preset, preset_name)
    list_box.add(row)

    row = SideMenuRow(voc["dock"], margin_start=18)
    row.eb.connect("button-press-event", set_up_dock_tab, preset, preset_name)
    list_box.add(row)

    row = SideMenuRow(voc["exit-menu"], margin_start=18)
    row.eb.connect("button-press-event", set_up_bar_tab, preset, preset_name)
    list_box.add(row)

    row = SideMenuRow(voc["notifications"], margin_start=18)
    row.eb.connect("button-press-event", set_up_notification_tab, preset, preset_name)
    list_box.add(row)

    row = SideMenuRow(voc["gtklock"], margin_start=18)
    row.eb.connect("button-press-event", set_up_gtklock_preset_tab, preset, preset_name)
    list_box.add(row)

    if preset_id == "c":
        row = SideMenuRow(voc["panel-css"], margin_start=18)
        row.eb.connect("button-press-event", set_up_panel_styling_tab, preset, preset_name)
        list_box.add(row)

    global submenus
    submenus.append(list_box)

    list_box.set_selection_mode(Gtk.SelectionMode.NONE)
    return list_box


def hide_submenus():
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
    global update_btn
    content, update_btn = screen_tab(settings, voc, pending_updates)
    grid.attach(content, 1, 0, 1, 1)


def set_up_applications_tab(*args, warn=False):
    hide_submenus()
    global content
    content.destroy()
    content = applications_tab(settings, voc, warn)
    grid.attach(content, 1, 0, 1, 1)


def set_up_backup_tab(btn, event, config_home, data_home, backup_configs, backup_data):
    hide_submenus()
    global content
    content.destroy()
    content = backup_tab(config_home, data_home, backup_configs, backup_data, voc)
    grid.attach(content, 1, 0, 1, 1)


def h_set_up_general_tab(*args):
    hide_submenus()
    global content
    content.destroy()
    content = h_general_tab(settings, voc)
    grid.attach(content, 1, 0, 1, 1)


def h_set_up_dwindle_tab(*args):
    hide_submenus()
    global content
    content.destroy()
    content = h_dwindle_tab(settings, voc)
    grid.attach(content, 1, 0, 1, 1)


def h_set_up_master_tab(*args):
    hide_submenus()
    global content
    content.destroy()
    content = h_master_tab(settings, voc)
    grid.attach(content, 1, 0, 1, 1)


def h_set_up_input_tab(*args):
    hide_submenus()
    global content
    content.destroy()
    content = h_input_tab(settings, voc)
    grid.attach(content, 1, 0, 1, 1)


def set_up_touchpad_tab(*args):
    hide_submenus()
    global content
    content.destroy()
    content = h_touchpad_tab(settings, voc)
    grid.attach(content, 1, 0, 1, 1)


def h_set_up_misc_tab(*args):
    hide_submenus()
    global content
    content.destroy()
    content = h_misc_tab(settings, voc)
    grid.attach(content, 1, 0, 1, 1)


def set_up_lockscreen_tab(*args):
    hide_submenus()
    global content
    content.destroy()
    content = lockscreen_tab(settings, voc)
    grid.attach(content, 1, 0, 1, 1)


def set_up_gtklock_tab(*args):
    hide_submenus()
    global content
    content.destroy()
    content = gtklock_tab(settings, voc)
    grid.attach(content, 1, 0, 1, 1)


def set_up_drawer_tab(event_box, event_button, preset, preset_name):
    hide_submenus()
    global content
    content.destroy()
    content = drawer_tab(preset, preset_name, outputs, voc)
    grid.attach(content, 1, 0, 1, 1)


def set_up_dock_tab(event_box, event_button, preset, preset_name):
    hide_submenus()
    global content
    content.destroy()
    content = dock_tab(preset, preset_name, outputs, voc)
    grid.attach(content, 1, 0, 1, 1)


def set_up_bar_tab(event_box, event_button, preset, preset_name):
    hide_submenus()
    global content
    content.destroy()
    content = bar_tab(preset, preset_name, voc)
    grid.attach(content, 1, 0, 1, 1)


def set_up_notification_tab(event_box, event_button, preset, preset_name):
    hide_submenus()
    global content
    content.destroy()
    content = notification_tab(preset, preset_name, voc)
    grid.attach(content, 1, 0, 1, 1)


def set_up_gtklock_preset_tab(event_box, event_button, preset, preset_name):
    hide_submenus()
    global content
    content.destroy()
    content = gtklock_preset_tab(preset, preset_name, voc)
    grid.attach(content, 1, 0, 1, 1)


def set_up_panel_styling_tab(event_box, event_button, preset, preset_name):
    hide_submenus()
    global content
    content.destroy()
    content = panel_styling_tab(settings, preset, preset_name, voc)
    grid.attach(content, 1, 0, 1, 1)


def set_up_sys_info_tab(event_box, event_button):
    hide_submenus()
    global content
    content.destroy()
    content = sys_info_tab(voc)
    grid.attach(content, 1, 0, 1, 1)


def on_apply_btn(b):
    f = os.path.join(data_dir, "settings-hyprland")
    print("Saving {}".format(f))
    save_json(settings, f)

    save_presets()
    presets = {
        "hyprland-0": preset_0,
        "hyprland-1": preset_1,
        "hyprland-2": preset_2,
        "hyprland-3": preset_3,
        "custom-hyprland": preset_custom
    }
    preset = presets[settings["panel-preset"]]
    update_swaync_config(preset["swaync-positionX"],
                         preset["swaync-positionY"],
                         preset["swaync-control-center-width"],
                         preset["swaync-notification-window-width"],
                         preset["swaync-mpris"])

    save_includes()


class GUI(object):
    def __init__(self):
        self.label_interface_locale = None
        self.scrolled_window = None
        self.menu = None
        builder = Gtk.Builder()
        builder.add_from_file(os.path.join(dir_name, "glade/form.glade"))

        self.window = builder.get_object("window")
        self.window.connect('destroy', Gtk.main_quit)
        self.window.connect("key-release-event", handle_keyboard)

        global grid
        grid = builder.get_object("grid")

        self.build_side_menu()

        self.version = builder.get_object("version-label")
        self.version.set_text("v{}".format(__version__))

        github = builder.get_object("github")
        github.set_markup('<a href="https://github.com/nwg-piotr/nwg-shell-config">GitHub</a>')

        self.cb_show = builder.get_object("show-on-startup")
        self.cb_show.set_active(settings["show-on-startup"])
        self.cb_show.set_label(voc["show-on-startup"])
        self.cb_show.set_tooltip_text(voc["show-on-startup-tooltip"])
        self.cb_show.connect("toggled", set_from_checkbutton, settings, "show-on-startup")

        self.label_interface_locale = builder.get_object("interface-locale")
        self.label_interface_locale.set_text("{}:".format(voc["interface-locale"]))

        self.combo_interface_locale = builder.get_object("combo-interface-locale")
        self.combo_interface_locale.append("auto", "auto")
        self.combo_interface_locale.set_tooltip_text(voc["interface-locale-tooltip"])
        locale_dir = os.path.join(dir_name, "langs")
        entries = os.listdir(locale_dir)
        entries.sort()
        for entry in entries:
            if entry.endswith(".json"):
                loc = entry.split(".")[0]
                self.combo_interface_locale.append(loc, loc)
        if shell_data["interface-locale"]:
            self.combo_interface_locale.set_active_id(shell_data["interface-locale"])
        else:
            self.combo_interface_locale.set_active_id("auto")
        self.combo_interface_locale.connect("changed", set_interface_locale)

        btn_translate = builder.get_object("button-translate")
        icon = Gtk.Image.new_from_icon_name("nwg-shell-translate", Gtk.IconSize.BUTTON)
        btn_translate.set_image(icon)
        btn_translate.set_tooltip_text("Would you like to help with translations?")
        btn_translate.connect("clicked", on_button_translate)

        self.btn_close = builder.get_object("btn-close")
        self.btn_close.set_label(voc["close"])
        self.btn_close.set_tooltip_text(voc["close-tooltip"])
        self.btn_close.connect("clicked", Gtk.main_quit)
        self.btn_close.grab_focus()

        global btn_apply
        btn_apply = builder.get_object("btn-apply")
        btn_apply.set_label(voc["apply"])
        btn_apply.set_tooltip_text(voc["apply-tooltip"])
        btn_apply.connect("clicked", on_apply_btn)

        if settings["night-lat"] == -1 or settings["night-long"] == -1:
            self.tz, self.lat, self.long = get_lat_lon()

    def refresh_bottom_menu_locale(self):
        self.label_interface_locale.set_text("{}:".format(voc["interface-locale"]))
        self.cb_show.set_label(voc["show-on-startup"])
        self.cb_show.set_tooltip_text(voc["show-on-startup-tooltip"])
        self.combo_interface_locale.set_tooltip_text(voc["interface-locale-tooltip"])
        btn_apply.set_label(voc["apply"])
        btn_apply.set_tooltip_text(voc["apply-tooltip"])

        self.btn_close.set_label(voc["close"])
        self.btn_close.set_tooltip_text(voc["close-tooltip"])

    def build_side_menu(self):
        if self.scrolled_window:
            self.scrolled_window.destroy()
        self.scrolled_window = Gtk.ScrolledWindow.new(None, None)
        self.scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scrolled_window.set_propagate_natural_height(True)
        grid.attach(self.scrolled_window, 0, 0, 1, 1)

        self.menu = side_menu()
        self.scrolled_window.add(self.menu)
        self.scrolled_window.show_all()


def set_interface_locale(combo):
    # selected locale will affect all the nwg-shell components... one day. Let's save it globally.
    if combo.get_active_id() and combo.get_active_id() != "auto":
        shell_data["interface-locale"] = combo.get_active_id()
    else:
        shell_data["interface-locale"] = ""
    save_json(shell_data, os.path.join(get_shell_data_dir(), "data"))

    load_vocabulary()

    # refresh UI on language changed
    global ui
    if ui:
        ui.build_side_menu()
        ui.refresh_bottom_menu_locale()
    # kinda shortcut, but let's just get to the screen tab, instead of remembering which one we were in
    set_up_screen_tab()


def on_button_translate(btn):
    launch(btn, "nwg-shell-translate")


def save_includes():
    # ~/.config/hypr/includes.conf
    cmd_launcher_autostart = ""

    includes = ["# This content was generated by nwg-shell-config. Do not modify it manually.", "\n# VARIABLES"]
    if settings["terminal"]:
        includes.append("$term = {}".format(settings["terminal"]))
    if settings["browser"]:
        includes.append("$browser = {}".format(settings["browser"]))
    if settings["file-manager"]:
        includes.append("$filemanager = {}".format(settings["file-manager"]))
    if settings["editor"]:
        includes.append("$editor = {}".format(settings["editor"]))

    if settings["panel-preset"] == "hyprland-0":
        preset = preset_0
    elif settings["panel-preset"] == "hyprland-1":
        preset = preset_1
    elif settings["panel-preset"] == "hyprland-2":
        preset = preset_2
    elif settings["panel-preset"] == "hyprland-3":
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
    if preset["launcher-gtk-theme"]:
        cmd_launcher += " -g {}".format(preset["launcher-gtk-theme"])
    if preset["launcher-gtk-icon-theme"]:
        # dict: {"theme_name": "folder_name"}
        theme_names = get_icon_themes()
        cmd_launcher += " -i {}".format(theme_names[preset["launcher-gtk-icon-theme"]])

    if "hyprland-" in settings["panel-preset"]:
        cmd_launcher += " -s {}.css".format(settings["panel-preset"])
    elif preset["launcher-css"]:
        cmd_launcher += " -s {}".format(preset["launcher-css"])

    if settings["terminal"]:
        cmd_launcher += " -term {}".format(settings["terminal"])

    if preset["launcher-force-theme"]:
        cmd_launcher += " -ft"

    if preset["launcher-run-through-compositor"]:
        cmd_launcher += " -wm hyprland"

    if preset["launcher-output"] and preset["launcher-output"] != "Any":
        cmd_launcher += " -o {}".format(preset["launcher-output"])

    if preset["powerbar-on"]:
        if settings["pb-exit"]:
            cmd_launcher += f' -pbexit \'{settings["pb-exit"]}\''
        if settings["pb-lock"]:
            cmd_launcher += f' -pblock \'{settings["pb-lock"]}\''
        if settings["pb-poweroff"]:
            cmd_launcher += f' -pbpoweroff \'{settings["pb-poweroff"]}\''
        if settings["pb-reboot"]:
            cmd_launcher += f' -pbreboot \'{settings["pb-reboot"]}\''
        if settings["pb-sleep"]:
            cmd_launcher += f' -pbsleep \'{settings["pb-sleep"]}\''
        if preset["pb-size"] >= 8:
            cmd_launcher += f' -pbsize {preset["pb-size"]}'

    if preset["launcher-on"]:
        if preset["launcher-resident"]:
            cmd_launcher_autostart = "exec = {}".format(cmd_launcher)
            includes.append("$launcher = nwg-drawer")
        else:
            includes.append("$launcher = {}".format(cmd_launcher))

    if preset["exit-on"]:
        cmd_exit = "nwg-bar -t hyprland.json"
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

        if "hyprland-" in settings["panel-preset"]:
            cmd_exit += " -s {}.css".format(settings["panel-preset"])
        elif preset["exit-css"]:
            cmd_exit += " -s {}".format(preset["exit-css"])
    else:
        cmd_exit = "$launcher"

    includes.append("$exit = {}".format(cmd_exit))

    # For vertical dock not to collide with horizontal panels, we need to start it w/ some delay
    if preset["dock-startup-delay"] > 0:
        cmd_dock = "exec = killall nwg-dock-hyprland\nexec = sleep {} && nwg-dock-hyprland".format(
            preset["dock-startup-delay"])
    else:
        cmd_dock = "exec = nwg-dock-hyprland"
    if preset["dock-autohide"]:
        cmd_dock += " -d"
    elif preset["dock-permanent"]:
        cmd_dock += " -r"
    if preset["dock-position"]:
        cmd_dock += " -p {}".format(preset["dock-position"])
    if preset["dock-output"] and preset["dock-output"] != "Any":
        cmd_dock += " -o {}".format(preset["dock-output"])
    if preset["dock-layer"]:
        cmd_dock += " -l {}".format(preset["dock-layer"])
    if preset["dock-full"]:
        cmd_dock += " -f"
    if preset["dock-alignment"]:
        cmd_dock += " -a {}".format(preset["dock-alignment"])
    if preset["dock-margin"]:
        cmd_dock += " -mb {} -ml {} -mr {} -mt {}".format(preset["dock-margin"], preset["dock-margin"],
                                                          preset["dock-margin"], preset["dock-margin"])
    if preset["dock-icon-size"]:
        cmd_dock += " -i {}".format(preset["dock-icon-size"])

    cmd_dock += " -hd {}".format(preset["dock-hotspot-delay"])

    if preset["dock-exclusive"]:
        cmd_dock += " -x"

    if "preset-" in settings["panel-preset"]:
        cmd_dock += " -s {}.css".format(settings["panel-preset"])
    elif preset["dock-css"]:
        cmd_dock += " -s {}".format(preset["dock-css"])

    if preset["dock-on"] and not preset["dock-autohide"] and not preset["dock-permanent"]:
        includes.append("$dock = {}".format(cmd_dock))

    includes.append("\n# AUTOSTART")
    includes.append("exec-once = rm {}".format(os.path.join(temp_dir(), "nwg-shell-check-update.lock")))

    # Kill wlsunset. We will need either to restart it or turn it off
    subprocess.call("pkill -f wlsunset", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    time.sleep(0.5)

    if settings["night-on"]:
        cmd = "wlsunset -t {} -T {} -l {} -L {} -g {}".format(settings["night-temp-low"],
                                                              settings["night-temp-high"],
                                                              settings["night-lat"],
                                                              settings["night-long"],
                                                              settings["night-gamma"])
        try:
            subprocess.Popen(cmd, shell=True)
        except Exception as e:
            eprint(e)

        includes.append("exec-once = {}".format(cmd))

    name = settings["panel-preset"] if not settings["panel-preset"] == "custom" else "style"
    p = os.path.join(config_home, "swaync")
    includes.append("exec-once = swaync -c {}/hyprland.json -s {}/{}.css".format(p, p, name))

    if settings["appindicator"]:
        includes.append("exec-once = nm-applet --indicator")

    if settings["cliphist"]:
        includes.append("exec-once = wl-paste --type text --watch cliphist store")
        includes.append("exec-once = wl-paste --type image --watch cliphist store")

    if cmd_launcher_autostart:
        includes.append(cmd_launcher_autostart)

    cmd_panel = "exec = nwg-panel"
    if settings["panel-preset"] != "custom":
        cmd_panel += " -c {}".format(settings["panel-preset"])
    elif settings["panel-custom"]:
        cmd_panel += " -c {}".format(settings["panel-custom"])
    if preset["panel-css"]:
        cmd_panel += " -s {}".format(preset["panel-css"])
    includes.append(cmd_panel)

    if preset["dock-on"] and (preset["dock-autohide"] or preset["dock-permanent"]):
        includes.append(cmd_dock)

    includes.append("exec = nwg-shell-check-updates")

    if settings["lockscreen-use-settings"]:
        c_sleep = "timeout {} '{}'".format(settings["sleep-timeout"], settings["sleep-cmd"]) if settings[
            "sleep-cmd"] else ""

        c_resume = "resume '{}'".format(settings["resume-cmd"]) if settings["resume-cmd"] else ""
        # Let's make it a bit idiot-proof
        if c_sleep and "dpms off" in settings["sleep-cmd"] and "dpms on" not in settings["resume-cmd"]:
            c_resume = "swaymsg \"output * dpms on\""

        c_after_resume = "after-resume '{}'".format(settings["after-resume"]) if settings["after-resume"] else ""

        c_before_sleep = "before-sleep {}".format(settings["before-sleep"]) if settings[
            "before-sleep"] else ""

        cmd_idle = "exec = swayidle timeout {} nwg-lock {} {} {} {}".format(settings["lockscreen-timeout"],
                                                                         c_sleep, c_resume, c_after_resume, c_before_sleep)
        includes.append(cmd_idle)
        # We can't `exec-once = swayidle`, as it would create multiple instances. Let's restart it here.
        subprocess.call("killall swayidle", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        subprocess.Popen("swayidle timeout {} nwg-lock {} {} {}".format(settings["lockscreen-timeout"],
                                                                        c_sleep, c_resume, c_before_sleep), shell=True)

    if settings["update-indicator-on"]:
        includes.append("exec-once = nwg-update-indicator")

    if settings["screenshot"]:
        includes.append("exec = nwg-screenshot-applet")

    if settings["show-on-startup"]:
        includes.append("exec-once = nwg-shell-config")

    # Export general devices settings
    if settings["gen-use-settings"]:
        includes.append("\n# GENERAL SETTINGS\ngeneral {")
        includes.append('    border_size = {}'.format(settings["gen-border_size"]))
        includes.append('    no_border_on_floating = {}'.format(bool2lower(settings["gen-no_border_on_floating"])))
        includes.append('    gaps_in = {}'.format(settings["gen-gaps_in"]))
        includes.append('    gaps_out = {}'.format(settings["gen-gaps_out"]))
        if settings["gen-col-active_border-start"]:
            line = "    col.active_border = rgba({})".format(settings["gen-col-active_border-start"])
            if settings["gen-col-active_border-end"]:
                line += " rgba({})".format(settings["gen-col-active_border-end"])
            if settings["gen-col-active_border-end"] and settings["gen-col-active_border-deg"]:
                line += " {}deg".format(settings["gen-col-active_border-deg"])
            includes.append(line)
        if settings["gen-col-inactive_border-start"]:
            line = "    col.inactive_border = rgba({})".format(settings["gen-col-inactive_border-start"])
            if settings["gen-col-inactive_border-end"]:
                line += " rgba({})".format(settings["gen-col-inactive_border-end"])
            if settings["gen-col-inactive_border-end"] and settings["gen-col-inactive_border-deg"]:
                line += " {}deg".format(settings["gen-col-inactive_border-deg"])
            includes.append(line)

        if settings["gen-cursor_inactive_timeout"]:
            includes.append('    cursor_inactive_timeout = {}'.format(settings["gen-cursor_inactive_timeout"]))
        includes.append('    layout = {}'.format(settings["gen-layout"]))
        if settings["gen-no_cursor_warps"]:
            includes.append('    no_cursor_warps = {}'.format(bool2lower(settings["gen-no_cursor_warps"])))
        if settings["gen-no_focus_fallback"]:
            includes.append('    no_focus_fallback = {}'.format(bool2lower(settings["gen-no_focus_fallback"])))
        if settings["gen-resize_on_border"]:
            includes.append('    resize_on_border = {}'.format(bool2lower(settings["gen-resize_on_border"])))
        if settings["gen-extend_border_grab_area"]:
            includes.append(
                '    extend_border_grab_area = {}'.format(bool2lower(settings["gen-extend_border_grab_area"])))
        if settings["gen-hover_icon_on_border"]:
            includes.append('    hover_icon_on_border = {}'.format(bool2lower(settings["gen-hover_icon_on_border"])))
        includes.append('}')

    # Export dwindle layout settings
    if settings["dwindle-use-settings"]:
        includes.append("\n# DWINDLE LAYOUT \ndwindle {")
        includes.append('    pseudotile = {}'.format(bool2lower(settings["dwindle-pseudotile"])))
        includes.append('    force_split = {}'.format(settings["dwindle-force_split"]))
        includes.append('    preserve_split = {}'.format(bool2lower(settings["dwindle-preserve_split"])))
        includes.append('    smart_split = {}'.format(bool2lower(settings["dwindle-smart_split"])))
        includes.append('    smart_resizing = {}'.format(bool2lower(settings["dwindle-smart_resizing"])))
        includes.append('    special_scale_factor = {}'.format(settings["dwindle-special_scale_factor"]))
        includes.append('    split_width_multiplier = {}'.format(settings["dwindle-split_width_multiplier"]))
        includes.append('    no_gaps_when_only = {}'.format(bool2lower(settings["dwindle-no_gaps_when_only"])))
        includes.append('    use_active_for_splits = {}'.format(bool2lower(settings["dwindle-use_active_for_splits"])))
        includes.append('    default_split_ratio = {}'.format(settings["dwindle-default_split_ratio"]))
        includes.append('}')

    # Export master layout settings
    if settings["master-use-settings"]:
        includes.append("\n# MASTER LAYOUT \nmaster {")
        includes.append('    allow_small_split = {}'.format(bool2lower(settings["master-allow_small_split"])))
        includes.append('    special_scale_factor = {}'.format(settings["master-special_scale_factor"]))
        includes.append('    mfact = {}'.format(settings["master-mfact"]))
        includes.append('    new_is_master = {}'.format(bool2lower(settings["master-new_is_master"])))
        includes.append('    new_on_top = {}'.format(bool2lower(settings["master-new_on_top"])))
        includes.append('    no_gaps_when_only = {}'.format(bool2lower(settings["master-no_gaps_when_only"])))
        includes.append('    orientation = {}'.format(settings["master-orientation"]))
        includes.append('    inherit_fullscreen = {}'.format(bool2lower(settings["master-inherit_fullscreen"])))
        includes.append('    always_center_master = {}'.format(bool2lower(settings["master-always_center_master"])))
        includes.append('}')

    # Export input devices settings
    if settings["input-use-settings"]:
        includes.append("\n# INPUT DEVICES\ninput {")
        if settings["input-kb_layout"]:
            includes.append('    kb_layout = {}'.format(settings["input-kb_layout"]))
        if settings["input-kb_model"]:
            includes.append('    kb_model = {}'.format(settings["input-kb_model"]))
        if settings["input-kb_variant"]:
            includes.append('    kb_variant = {}'.format(settings["input-kb_variant"]))
        if settings["input-kb_options"]:
            includes.append('    kb_options = {}'.format(settings["input-kb_options"]))
        if settings["input-kb_rules"]:
            includes.append('    kb_rules = {}'.format(settings["input-kb_rules"]))
        if settings["input-numlock_by_default"]:
            includes.append('    numlock_by_default = {}'.format(bool2lower(settings["input-numlock_by_default"])))
        if settings["input-repeat_rate"]:
            includes.append('    repeat_rate = {}'.format(settings["input-repeat_rate"]))
        if settings["input-repeat_delay"]:
            includes.append('    repeat_delay = {}'.format(settings["input-repeat_delay"]))
        if settings["input-sensitivity"]:
            includes.append('    sensitivity = {}'.format(settings["input-sensitivity"]))
        if settings["input-accel_profile"]:
            includes.append('    accel_profile = {}'.format(settings["input-accel_profile"]))
        if settings["input-left_handed"]:
            includes.append('    left_handed = {}'.format(bool2lower(settings["input-left_handed"])))
        if settings["input-scroll_method"]:
            includes.append('    scroll_method = {}'.format(settings["input-scroll_method"]))
        if settings["input-scroll_button"]:
            includes.append('    scroll_button = {}'.format(settings["input-scroll_button"]))
        if settings["input-natural_scroll"]:
            includes.append('    natural_scroll = {}'.format(bool2lower(settings["input-natural_scroll"])))
        includes.append('    follow_mouse = {}'.format(settings["input-follow_mouse"]))
        includes.append('    mouse_refocus = {}'.format(bool2lower(settings["input-mouse_refocus"])))
        if settings["input-float_switch_override_focus"]:
            includes.append(
                '    float_switch_override_focus = {}'.format(settings["input-float_switch_override_focus"]))

        if settings["touchpad-use-settings"]:
            includes.append("    touchpad {")
            if settings["touchpad-disable_while_typing"]:
                includes.append(
                    '        disable_while_typing = {}'.format(bool2lower(settings["touchpad-disable_while_typing"])))
            if settings["touchpad-natural_scroll"]:
                includes.append('        natural_scroll = {}'.format(bool2lower(settings["touchpad-natural_scroll"])))
            if settings["touchpad-scroll_factor"]:
                includes.append('        scroll_factor = {}'.format(settings["touchpad-scroll_factor"]))
            if settings["touchpad-middle_button_emulation"]:
                includes.append(
                    '        middle_button_emulation = {}'.format(
                        bool2lower(settings["touchpad-middle_button_emulation"])))
            if settings["touchpad-tap_button_map"]:
                includes.append('        tap_button_map = {}'.format(settings["touchpad-tap_button_map"]))
            if settings["touchpad-clickfinger_behavior"]:
                includes.append(
                    '        clickfinger_behavior = {}'.format(bool2lower(settings["touchpad-clickfinger_behavior"])))
            if settings["touchpad-tap-to-click"]:
                includes.append('        tap-to-click = {}'.format(bool2lower(settings["touchpad-tap-to-click"])))
            if settings["touchpad-drag_lock"]:
                includes.append('        drag_lock = {}'.format(bool2lower(settings["touchpad-drag_lock"])))
            if settings["touchpad-tap-and-drag"]:
                includes.append('        tap-and-drag = {}'.format(bool2lower(settings["touchpad-tap-and-drag"])))
            includes.append("    }")
        includes.append('}')

    # Export misc settings
    if settings["misc-use-settings"]:
        includes.append("\n# MISC SETTINGS\nmisc {")
        includes.append('    disable_hyprland_logo = {}'.format(bool2lower(settings["misc-disable_hyprland_logo"])))
        includes.append('    disable_splash_rendering = {}'.format(bool2lower(settings["misc-disable_splash_rendering"])))
        includes.append('    vrr = {}'.format(settings["misc-vrr"]))
        includes.append('    mouse_move_enables_dpms = {}'.format(bool2lower(settings["misc-mouse_move_enables_dpms"])))
        includes.append('    key_press_enables_dpms = {}'.format(bool2lower(settings["misc-key_press_enables_dpms"])))
        includes.append('    layers_hog_keyboard_focus = {}'.format(bool2lower(settings["misc-layers_hog_keyboard_focus"])))
        includes.append('    focus_on_activate = {}'.format(bool2lower(settings["misc-focus_on_activate"])))
        includes.append('    mouse_move_focuses_monitor = {}'.format(bool2lower(settings["misc-mouse_move_focuses_monitor"])))
        includes.append('}')

    if preset["launcher-super-key"]:  # add more keys when necessary, for now we have one
        includes.append('\n# KEY BINDINGS')

    if preset["launcher-super-key"]:
        includes.append('bindr = SUPER, SUPER_L, exec, $launcher')

    p = os.path.join(config_home, "hypr/includes.conf")
    print("Saving includes to {}".format(p))
    save_list_to_text_file(includes, p)

    reload()


def reload():
    name = settings["panel-preset"] if not settings["panel-preset"] == "custom" else "style"
    p = os.path.join(config_home, "swaync")
    swaync_daemon = "swaync -c {}/hyprland.json -s {}/{}.css".format(p, p, name)
    for cmd in ["pkill -f nwg-drawer",
                "pkill -f nwg-dock",
                "pkill -f nwg-bar",
                "pkill -f swaync",]:
        subprocess.call(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    subprocess.Popen(swaync_daemon, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    if settings["update-indicator-on"]:
        launch(None, "nwg-update-indicator")
    else:
        subprocess.call("pkill -f nwg-update-indicator", shell=True, stdout=subprocess.DEVNULL,
                        stderr=subprocess.STDOUT)

    if not settings["screenshot"]:
        subprocess.call("pkill -f nwg-screenshot", shell=True, stdout=subprocess.DEVNULL,
                        stderr=subprocess.STDOUT)


def load_settings():
    settings_file = os.path.join(data_dir, "settings-hyprland")
    defaults = {
        "appindicator": True,
        "cliphist": True,
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
        "panel-preset": "hyprland-0",
        "panel-custom": "",
        "screenshot": True,
        "show-on-startup": True,

        "pb-exit": "hyprctl dispatch exit",
        "pb-lock": "nwg-lock",
        "pb-poweroff": "systemctl -i poweroff",
        "pb-reboot": "systemctl reboot",
        "pb-sleep": "systemctl suspend",

        "gen-use-settings": True,
        "gen-border_size": 1,
        "gen-no_border_on_floating": False,
        "gen-gaps_in": 5,
        "gen-gaps_out": 20,
        "gen-col-active_border-start": "33ccffee",
        "gen-col-active_border-end": "00ff99ee",
        "gen-col-active_border-deg": 45,
        "gen-col-inactive_border-start": "595959aa",
        "gen-col-inactive_border-end": "",
        "gen-col-inactive_border-deg": 0,
        "gen-cursor_inactive_timeout": 0,
        "gen-layout": "dwindle",
        "gen-no_cursor_warps": False,
        "gen-no_focus_fallback": False,
        "gen-resize_on_border": False,
        "gen-extend_border_grab_area": 15,
        "gen-hover_icon_on_border": True,

        "dwindle-use-settings": True,
        "dwindle-pseudotile": False,
        "dwindle-force_split": 0,
        "dwindle-preserve_split": True,
        "dwindle-smart_split": False,
        "dwindle-smart_resizing": True,
        "dwindle-permanent_direction_override": False,
        "dwindle-special_scale_factor": 0.8,
        "dwindle-split_width_multiplier": 1.0,
        "dwindle-no_gaps_when_only": False,
        "dwindle-use_active_for_splits": True,
        "dwindle-default_split_ratio": 1.0,

        "master-use-settings": True,
        "master-allow_small_split": False,
        "master-special_scale_factor": 0.8,
        "master-mfact": 0.55,
        "master-new_is_master": True,
        "master-new_on_top": False,
        "master-no_gaps_when_only": False,
        "master-orientation": "left",
        "master-inherit_fullscreen": True,
        "master-always_center_master": False,

        "input-use-settings": True,
        "input-kb_layout": "us",
        "input-kb_model": "",
        "input-kb_variant": "",
        "input-kb_options": "",
        "input-kb_rules": "",
        "input-kb_file": "",
        "input-numlock_by_default": False,
        "input-repeat_rate": 25,
        "input-repeat_delay": 600,
        "input-sensitivity": 0.0,
        "input-accel_profile": "",
        "input-left_handed": False,
        "input-scroll_method": "",
        "input-scroll_button": 0,
        "input-natural_scroll": False,
        "input-follow_mouse": 1,
        "input-mouse_refocus": True,
        "input-float_switch_override_focus": 1,

        "touchpad-use-settings": True,
        "touchpad-disable_while_typing": True,
        "touchpad-natural_scroll": False,
        "touchpad-scroll_factor": 1.0,
        "touchpad-middle_button_emulation": False,
        "touchpad-tap_button_map": "",
        "touchpad-clickfinger_behavior": "",
        "touchpad-tap-to-click": True,
        "touchpad-drag_lock": False,
        "touchpad-tap-and-drag": False,

        "misc-use-settings": True,
        "misc-disable_hyprland_logo": True,
        "misc-disable_splash_rendering": True,
        "misc-vrr": 0,
        "misc-mouse_move_enables_dpms": False,
        "misc-key_press_enables_dpms": False,
        "misc-layers_hog_keyboard_focus": True,
        "misc-focus_on_activate": False,
        "misc-mouse_move_focuses_monitor": True,

        "lockscreen-use-settings": True,
        "lockscreen-locker": "gtklock",  # swaylock | gtklock
        "lockscreen-background-source": "local",  # unsplash | local
        "lockscreen-custom-cmd": "",
        "lockscreen-timeout": 1200,
        "sleep-cmd": "systemctl suspend",
        "sleep-timeout": 1800,
        "resume-cmd": "",
        "after-resume": "",
        "before-sleep": "",
        "backgrounds-custom-path": "",
        "backgrounds-use-custom-path": False,
        "background-dirs": ["/usr/share/backgrounds/nwg-shell"],
        "background-dirs-once-set": False,
        "unsplash-width": 1920,
        "unsplash-height": 1080,
        "unsplash-keywords": ["nature", "water", "landscape"],
        "help-font-size": 12,
        "help-layer-shell": True,
        "help-keyboard": False,
        "gtklock-disable-input-inhibitor": False,
        "gtklock-idle-timeout": 10,
        "gtklock-logout-command": "swaymsg exit",
        "gtklock-playerctl": False,
        "gtklock-powerbar": False,
        "gtklock-poweroff-command": "systemctl -i poweroff",
        "gtklock-reboot-command": "systemctl reboot",
        "gtklock-suspend-command": "systemctl suspend",
        "gtklock-time-format": "%H:%M:%S",
        "gtklock-userinfo": False,
        "gtklock-userswitch-command": "",
        "update-indicator-on": False,
        "update-indicator-interval": 30,
        "update-command": "nwg-system-update"
    }
    global settings
    if os.path.isfile(settings_file):
        print("Loading settings from {}".format(settings_file))
        settings = load_json(settings_file)
        missing = 0
        for key in defaults:
            if key not in settings:
                settings[key] = defaults[key]
                print("'{}' key missing from settings, adding '{}'".format(key, defaults[key]))
                missing += 1
        if missing > 0:
            print("{} missing config key(s) substituted. Saving {}".format(missing, settings_file))
            save_json(settings, settings_file)
    else:
        print("ERROR: failed loading settings, creating {}".format(settings_file), file=sys.stderr)
        save_json(defaults, settings_file)


def load_presets():
    global preset_0
    preset_0 = load_preset("hyprland-0")
    global preset_1
    preset_1 = load_preset("hyprland-1")
    global preset_2
    preset_2 = load_preset("hyprland-2")
    global preset_3
    preset_3 = load_preset("hyprland-3")
    global preset_custom
    preset_custom = load_preset("custom-hyprland")


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
        "launcher-gtk-theme": "",
        "launcher-gtk-icon-theme": "",
        "launcher-force-theme": False,
        "launcher-run-through-compositor": False,
        "launcher-super-key": False,
        "launcher-output": "Any",
        "exit-position": "center",
        "exit-full": False,
        "exit-alignment": "middle",
        "exit-margin": 0,
        "exit-icon-size": 48,
        "exit-css": "",
        "exit-on": True,
        "dock-position": "bottom",
        "dock-output": "Any",
        "dock-full": False,
        "dock-autohide": False,
        "dock-permanent": False,
        "dock-exclusive": False,
        "dock-alignment": "center",
        "dock-layer": "overlay",
        "dock-margin": 0,
        "dock-icon-size": 48,
        "dock-hotspot-delay": 20,
        "dock-startup-delay": 0,
        "dock-css": "",
        "dock-on": False,
        "swaync-positionX": "right",
        "swaync-positionY": "top",
        "swaync-control-center-width": 500,
        "swaync-notification-window-width": 500,
        "swaync-mpris": False,
        "gtklock-userinfo-round-image": True,
        "gtklock-userinfo-vertical-layout": True,
        "gtklock-userinfo-under-clock": False,
        "gtklock-powerbar-show-labels": True,
        "gtklock-powerbar-linked-buttons": False,
        "gtklock-playerctl-art-size": 64,
        "gtklock-playerctl-position": "top-right",
        "gtklock-playerctl-show-hidden": True,
        "powerbar-on": True,
        "pb-size": 48
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
            save_json(preset, preset_file)

        return preset
    else:
        print("ERROR: failed loading preset, creating {}".format(preset_file), file=sys.stderr)
        save_json(defaults, preset_file)

        return {}


def save_presets():
    global preset_0, preset_1, preset_2, preset_3, preset_custom

    f = os.path.join(data_dir, "hyprland-0")
    print("Saving {}".format(f))
    save_json(preset_0, f)

    f = os.path.join(data_dir, "hyprland-1")
    print("Saving {}".format(f))
    save_json(preset_1, f)

    f = os.path.join(data_dir, "hyprland-2")
    print("Saving {}".format(f))
    save_json(preset_2, f)

    f = os.path.join(data_dir, "hyprland-3")
    print("Saving {}".format(f))
    save_json(preset_3, f)

    f = os.path.join(data_dir, "custom-hyprland")
    print("Saving {}".format(f))
    save_json(preset_custom, f)


def update_swaync_config(pos_x, pos_y, cc_width, window_width, mpris):
    settings_file = os.path.join(config_home, "swaync/hyprland.json")
    if os.path.isfile(settings_file):
        print("Loading swaync settings from {}".format(settings_file))
        swaync_settings = load_json(settings_file)
    else:
        swaync_settings = {}

    # Check if some new keys appeared
    defaults = load_json("/etc/xdg/swaync/config.json")

    for key in defaults:
        if key not in swaync_settings:
            swaync_settings[key] = defaults[key]

    swaync_settings["positionX"] = pos_x
    swaync_settings["positionY"] = pos_y
    swaync_settings["control-center-width"] = cc_width
    swaync_settings["notification-window-width"] = window_width

    if mpris:
        if "mpris" not in swaync_settings["widgets"]:
            swaync_settings["widgets"].append("mpris")
    else:
        if "mpris" in swaync_settings["widgets"]:
            swaync_settings["widgets"].remove("mpris")

    print("Saving swaync settings to {}".format(settings_file))
    save_json(swaync_settings, settings_file)


def load_vocabulary():
    global voc
    # basic vocabulary (for en_US)
    voc = load_json(os.path.join(dir_name, "langs", "en_US.json"))
    if not voc:
        eprint("Failed loading vocabulary")
        sys.exit(1)

    lang = os.getenv("LANG").split(".")[0] if not shell_data["interface-locale"] else shell_data["interface-locale"]
    # translate if necessary
    if lang != "en_US":
        loc_file = os.path.join(dir_name, "langs", "{}.json".format(lang))
        if os.path.isfile(loc_file):
            # localized vocabulary
            loc = load_json(loc_file)
            if not loc:
                eprint("Failed loading translation into '{}'".format(lang))
            else:
                for key in loc:
                    voc[key] = loc[key]


def load_settings_save_includes():
    global data_dir
    data_dir = get_data_dir()
    load_presets()
    load_settings()
    save_includes()
    sys.exit(0)


def restore_backup(b_path, voc):
    if b_path.startswith("~/"):
        b_path = os.path.join(os.getenv("HOME"), b_path[2:])
    unpack_from_path(b_path)
    restore_from_tmp(None, None, voc)


def main():
    global data_dir
    data_dir = get_data_dir()

    parser = argparse.ArgumentParser()
    parser.add_argument("-v",
                        "--version",
                        action="version",
                        version="%(prog)s version {}".format(__version__),
                        help="display version information")

    parser.add_argument("-r",
                        "--restore",
                        action="store_true",
                        help="restore default presets")

    parser.add_argument("-b",
                        "--restore_backup",
                        type=str,
                        default="",
                        help="restore all configs from a backup file (given path)")

    parser.add_argument("-s",
                        "--save",
                        action="store_true",
                        help="load settings & Save includes (for use w/ external scripts)")

    parser.parse_args()
    args = parser.parse_args()

    if args.save:
        init_files(os.path.join(dir_name, "shell"), data_dir)
        load_settings_save_includes()

    GLib.set_prgname('nwg-shell-config')

    his = os.getenv("HYPRLAND_INSTANCE_SIGNATURE")
    if his:
        print("HYPRLAND_INSTANCE_SIGNATURE={}".format(his))
    else:
        eprint("HYPRLAND_INSTANCE_SIGNATURE not found, terminating")
        sys.exit(1)

    global outputs
    outputs = h_list_monitors()

    print("Outputs: {}".format(outputs))
    print("Data dir: {}".format(data_dir))
    print("Config home: {}".format(config_home))

    load_vocabulary()

    if args.restore:
        if input("\nRestore default presets? y/N ").upper() == "Y":
            init_files(os.path.join(dir_name, "shell"), data_dir, overwrite=True)
            sys.exit(0)
    elif args.restore_backup:
        restore_backup(args.restore_backup, voc)
        sys.exit(0)
    else:
        # initialize missing own data files
        init_files(os.path.join(dir_name, "shell"), data_dir)

    check_updates()

    for folder in ["nwg-look", "nwg-shell", "nwg-shell-config"]:
        src = os.path.join("/etc/skel/.local/share", folder)
        dst = os.path.join(data_home, folder)
        if os.path.exists(src) and not os.path.exists(dst):
            os.mkdir(dst)
            print(dst, "missing, initializing")
            init_files(src, dst)

    load_settings()

    load_presets()

    global ui
    ui = GUI()

    screen = Gdk.Screen.get_default()
    provider = Gtk.CssProvider()
    style_context = Gtk.StyleContext()
    style_context.add_provider_for_screen(screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
    css = b"""
            button#app-btn { padding: 6px 2px 6px 2px; border: none }
            * { outline: none }
            """
    provider.load_from_data(css)

    if not settings["terminal"] or not settings["file-manager"] or not settings["editor"] or not settings["browser"]:
        set_up_applications_tab(warn=True)
    else:
        set_up_screen_tab()

    ui.window.show_all()
    hide_submenus()

    catchable_sigs = set(signal.Signals) - {signal.SIGKILL, signal.SIGSTOP}
    for sig in catchable_sigs:
        signal.signal(sig, signal_handler)

    Gtk.main()


if __name__ == '__main__':
    sys.exit(main())
