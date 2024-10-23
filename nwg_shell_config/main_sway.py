#!/usr/bin/env python3

"""
nwg-shell config utility
Repository: https://github.com/nwg-piotr/nwg-shell-config
Project site: https://nwg-piotr.github.io/nwg-shell
Author's email: nwg.piotr@gmail.com
Copyright (c) 2021-2022 Piotr Miller & Contributors
License: MIT
"""

import argparse
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

    row = SideMenuRow(voc["autotiling"])
    row.eb.connect("button-press-event", set_up_autotiling_tab)
    list_box.add(row)

    row = SideMenuRow(voc["keyboard"])
    row.eb.connect("button-press-event", set_up_keyboard_tab)
    list_box.add(row)

    row = SideMenuRow(voc["pointer-device"])
    row.eb.connect("button-press-event", set_up_pointer_tab)
    list_box.add(row)

    row = SideMenuRow(voc["touchpad"])
    row.eb.connect("button-press-event", set_up_touchpad_tab)
    list_box.add(row)

    row = SideMenuRow(voc["idle-lock-screen"])
    row.eb.connect("button-press-event", set_up_lockscreen_tab)
    list_box.add(row)

    row = SideMenuRow(voc["gtklock"])
    row.eb.connect("button-press-event", set_up_gtklock_tab)
    list_box.add(row)

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

    row = SideMenuRow("{} 0".format(voc["preset"]))
    list_box.add(row)

    submenu_0 = preset_menu(0)
    list_box.add(submenu_0)
    row.eb.connect("button-press-event", toggle_submenu, submenu_0)

    row = SideMenuRow("{} 1".format(voc["preset"]))
    list_box.add(row)

    submenu_1 = preset_menu(1)
    list_box.add(submenu_1)
    row.eb.connect("button-press-event", toggle_submenu, submenu_1)

    row = SideMenuRow("{} 2".format(voc["preset"]))
    list_box.add(row)

    submenu_2 = preset_menu(2)
    list_box.add(submenu_2)
    row.eb.connect("button-press-event", toggle_submenu, submenu_2)

    row = SideMenuRow("{} 3".format(voc["preset"]))
    list_box.add(row)

    submenu_3 = preset_menu(3)
    list_box.add(submenu_3)
    row.eb.connect("button-press-event", toggle_submenu, submenu_3)

    row = SideMenuRow(voc["custom-preset"])
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

    # row = SideMenuRow(voc["exit-menu"], margin_start=18)
    # row.eb.connect("button-press-event", set_up_bar_tab, preset, preset_name)
    # list_box.add(row)

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
    content = screen_tab(settings, voc)
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


def set_up_autotiling_tab(*args):
    hide_submenus()
    global content
    content.destroy()
    content = autotiling_tab(settings, outputs, voc)
    grid.attach(content, 1, 0, 1, 1)


def set_up_keyboard_tab(*args):
    hide_submenus()
    global content
    content.destroy()
    content = keyboard_tab(settings, voc)
    grid.attach(content, 1, 0, 1, 1)


def set_up_pointer_tab(*args):
    hide_submenus()
    global content
    content.destroy()
    content = pointer_tab(settings, voc)
    grid.attach(content, 1, 0, 1, 1)


def set_up_touchpad_tab(*args):
    hide_submenus()
    global content
    content.destroy()
    content = touchpad_tab(settings, voc)
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


# def set_up_bar_tab(event_box, event_button, preset, preset_name):
#     hide_submenus()
#     global content
#     content.destroy()
#     content = bar_tab(preset, preset_name, voc)
#     grid.attach(content, 1, 0, 1, 1)


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
    f = os.path.join(data_dir, "settings")
    print("Saving {}".format(f))
    save_json(settings, f)

    save_presets()
    presets = {
        "preset-0": preset_0,
        "preset-1": preset_1,
        "preset-2": preset_2,
        "preset-3": preset_3,
        "custom": preset_custom
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
    cmd_launcher_autostart = ""

    # ~/.config/sway/variables
    variables = []
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
    if preset["launcher-gtk-theme"]:
        cmd_launcher += " -g {}".format(preset["launcher-gtk-theme"])
    if preset["launcher-gtk-icon-theme"]:
        # dict: {"theme_name": "folder_name"}
        theme_names = get_icon_themes()
        cmd_launcher += " -i {}".format(theme_names[preset["launcher-gtk-icon-theme"]])

    if "preset-" in settings["panel-preset"]:
        cmd_launcher += " -s {}.css".format(settings["panel-preset"])
    elif preset["launcher-css"]:
        cmd_launcher += " -s {}".format(preset["launcher-css"])

    if settings["terminal"]:
        cmd_launcher += " -term {}".format(settings["terminal"])

    if preset["launcher-force-theme"]:
        cmd_launcher += " -ft"

    if preset["launcher-run-through-compositor"]:
        cmd_launcher += " -wm sway"

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
        if preset["pb-icon-theme"]:
            cmd_launcher += ' -pbuseicontheme'

    if preset["launcher-on"]:
        if preset["launcher-resident"]:
            cmd_launcher_autostart = "exec_always {}".format(cmd_launcher)
            variables.append("set $launcher nwg-drawer")
        else:
            variables.append("set $launcher {}".format(cmd_launcher))

    if preset["exit-on"]:
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

        if "preset-" in settings["panel-preset"]:
            cmd_exit += " -s {}.css".format(settings["panel-preset"])
        elif preset["exit-css"]:
            cmd_exit += " -s {}".format(preset["exit-css"])
    else:
        cmd_exit = "$launcher"

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

    if preset["launcher-at-start"]:
        cmd_dock += " -lp start"

    if "preset-" in settings["panel-preset"]:
        cmd_dock += " -s {}.css".format(settings["panel-preset"])
    elif preset["dock-css"]:
        cmd_dock += " -s {}".format(preset["dock-css"])

    if preset["dock-on"] and not preset["dock-autohide"] and not preset["dock-permanent"]:
        variables.append("set $dock {}".format(cmd_dock))

    save_list_to_text_file(variables, os.path.join(config_home, "sway/variables"))

    # ~/.config/sway/autostart
    autostart = ["# This content was generated by nwg-shell-config. Do not modify it manually.\n"]

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

        autostart.append("exec {}".format(cmd))

    name = settings["panel-preset"] if not settings["panel-preset"] == "custom" else "style"
    p = os.path.join(config_home, "swaync")
    autostart.append("exec swaync -s {}/{}.css".format(p, name))

    if settings["appindicator"]:
        autostart.append("exec nm-applet --indicator")

    if settings["cliphist"]:
        autostart.append("exec wl-paste --type text --watch cliphist store")
        autostart.append("exec wl-paste --type image --watch cliphist store")

    if settings["autotiling-on"]:
        cmd_autotiling = "exec_always nwg-autotiling"

        if settings["autotiling-workspaces"]:
            cmd_autotiling += " -w {}".format(settings["autotiling-workspaces"])

        autostart.append(cmd_autotiling)

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

        cmd_idle = "exec swayidle timeout {} nwg-lock {} {} {} {}".format(settings["lockscreen-timeout"],
                                                                       c_sleep, c_resume, c_after_resume, c_before_sleep)
        autostart.append(cmd_idle)
        # We can't `exec_always swayidle`, as it would create multiple instances. Let's restart it here.
        subprocess.call("killall swayidle", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        subprocess.Popen(cmd_idle, shell=True)

    if settings["update-indicator-on"]:
        autostart.append("exec nwg-update-indicator")

    if settings["screenshot"]:
        autostart.append("exec_always nwg-screenshot-applet")

    if settings["show-on-startup"]:
        autostart.append("exec nwg-shell-config")

    save_list_to_text_file(autostart, os.path.join(config_home, "sway/autostart"))

    # Export keyboard settings
    if settings["keyboard-use-settings"]:
        lines = ['input "type:keyboard" {'] if not settings["keyboard-identifier"] else [
            'input "%s" {' % settings["keyboard-identifier"]]
        if settings["keyboard-xkb-layout"]:
            lines.append('  xkb_layout {}'.format(settings["keyboard-xkb-layout"]))
        if settings["keyboard-xkb-variant"]:
            lines.append('  xkb_variant {}'.format(settings["keyboard-xkb-variant"]))
        lines.append('  repeat_delay {}'.format(settings["keyboard-repeat-delay"]))
        lines.append('  repeat_rate {}'.format(settings["keyboard-repeat-rate"]))
        lines.append('  xkb_capslock {}'.format(settings["keyboard-xkb-capslock"]))
        lines.append('  xkb_numlock {}'.format(settings["keyboard-xkb-numlock"]))
        if settings["keyboard-custom-name"] and settings["keyboard-custom-value"]:
            lines.append('  {} {}'.format(settings["keyboard-custom-name"], settings["keyboard-custom-value"]))
        lines.append('}')

        if preset["launcher-super-key"]:
            lines.append('bindsym --release Super_L exec $launcher')

        save_list_to_text_file(lines, os.path.join(config_home, "sway/keyboard"))
    else:
        save_list_to_text_file([""], os.path.join(config_home, "sway/keyboard"))

    # Export pointer device settings
    if settings["pointer-use-settings"]:
        lines = ['input "type:pointer" {'] if not settings["pointer-identifier"] else [
            'input "%s" {' % settings["pointer-identifier"]]
        lines.append('  natural_scroll {}'.format(settings["pointer-natural-scroll"]))
        lines.append('  scroll_factor {}'.format(settings["pointer-scroll-factor"]))
        lines.append('  left_handed {}'.format(settings["pointer-left-handed"]))
        if settings["pointer-custom-name"] and settings["pointer-custom-value"]:
            lines.append('  {} {}'.format(settings["keyboard-custom-name"], settings["keyboard-custom-value"]))
        lines.append('}')

        save_list_to_text_file(lines, os.path.join(config_home, "sway/pointer"))
    else:
        save_list_to_text_file([""], os.path.join(config_home, "sway/pointer"))

    # Export touchpad settings
    if settings["touchpad-use-settings"]:
        lines = ['input "type:touchpad" {'] if not settings["touchpad-identifier"] else [
            'input "%s" {' % settings["touchpad-identifier"]]
        lines.append('  pointer_accel {}'.format(settings["touchpad-pointer-accel"]))
        lines.append('  natural_scroll {}'.format(settings["touchpad-natural-scroll"]))
        lines.append('  scroll_factor {}'.format(settings["touchpad-scroll-factor"]))
        lines.append('  scroll_method {}'.format(settings["touchpad-scroll-method"]))
        lines.append('  click_method {}'.format(settings["touchpad-click-method"]))
        lines.append('  left_handed {}'.format(settings["touchpad-left-handed"]))
        lines.append('  tap {}'.format(settings["touchpad-tap"]))
        lines.append('  tap_button_map {}'.format(settings["touchpad-tap-button-map"]))
        lines.append('  drag {}'.format(settings["touchpad-drag"]))
        lines.append('  drag_lock {}'.format(settings["touchpad-drag-lock"]))
        lines.append('  dwt {}'.format(settings["touchpad-dwt"]))
        lines.append('  middle_emulation {}'.format(settings["touchpad-middle-emulation"]))
        if settings["touchpad-custom-name"] and settings["touchpad-custom-value"]:
            lines.append('  {} {}'.format(settings["touchpad-custom-name"], settings["touchpad-custom-value"]))
        lines.append('}')

        save_list_to_text_file(lines, os.path.join(config_home, "sway/touchpad"))
    else:
        save_list_to_text_file([""], os.path.join(config_home, "sway/touchpad"))

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
                swaync_daemon,
                "swaync-client --reload-config",
                "swaymsg reload"]:
        subprocess.call(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    if settings["update-indicator-on"]:
        launch(None, "nwg-update-indicator")
    else:
        subprocess.call("pkill -f nwg-update-indicator", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    if not settings["screenshot"]:
        subprocess.call("pkill -f nwg-screenshot", shell=True, stdout=subprocess.DEVNULL,
                        stderr=subprocess.STDOUT)


def load_settings():
    settings_file = os.path.join(data_dir, "settings")
    defaults = {
        "keyboard-layout": "us",
        "autotiling-workspaces": "",
        "autotiling-on": True,
        "autotiling-limit": False,
        "autotiling-output-limits": {},
        "autotiling-output-splitwidths": {},
        "autotiling-output-splitheights": {},
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

        "pb-exit": "swaymsg exit",
        "pb-lock": "nwg-lock",
        "pb-poweroff": "systemctl -i poweroff",
        "pb-reboot": "systemctl reboot",
        "pb-sleep": "systemctl suspend",

        "panel-preset": "preset-0",
        "panel-custom": "",
        "screenshot": True,
        "show-on-startup": True,
        "keyboard-use-settings": True,
        "keyboard-identifier": "",
        "keyboard-xkb-layout": "us",
        "keyboard-xkb-variant": "",
        "keyboard-repeat-delay": 300,
        "keyboard-repeat-rate": 40,
        "keyboard-xkb-capslock": "disabled",
        "keyboard-xkb-numlock": "disabled",
        "keyboard-custom-name": "",
        "keyboard-custom-value": "",
        "pointer-use-settings": True,
        "pointer-identifier": "",
        "pointer-accel-profile": "flat",
        "pointer-pointer-accel": 0.0,
        "pointer-natural-scroll": "disabled",
        "pointer-scroll-factor": 1.0,
        "pointer-left-handed": "disabled",
        "pointer-custom-name": "",
        "pointer-custom-value": "",
        "touchpad-use-settings": True,
        "touchpad-identifier": "",
        "touchpad-accel-profile": "flat",
        "touchpad-pointer-accel": 0.0,
        "touchpad-natural-scroll": "disabled",
        "touchpad-scroll-factor": 1.0,
        "touchpad-scroll-method": "two_finger",
        "touchpad-left-handed": "disabled",
        "touchpad-tap": "enabled",
        "touchpad-tap-button-map": "lrm",
        "touchpad-drag": "enabled",
        "touchpad-drag-lock": "disabled",
        "touchpad-dwt": "enabled",
        "touchpad-middle-emulation": "enabled",
        "touchpad-click-method": "button_areas",
        "touchpad-custom-name": "",
        "touchpad-custom-value": "",
        "lockscreen-use-settings": True,
        "lockscreen-locker": "gtklock",  # swaylock | gtklock
        "lockscreen-background-source": "local",  # unsplash | local
        "lockscreen-custom-cmd": "",
        "lockscreen-timeout": 1200,
        "sleep-cmd": 'swaymsg "output * dpms off"',
        "sleep-timeout": 1800,
        "resume-cmd": 'swaymsg "output * dpms on"',
        "after-resume": 'swaymsg "output * enable"',
        "before-sleep": "",
        "backgrounds-custom-path": "",
        "backgrounds-use-custom-path": False,
        "background-dirs": ["/usr/share/backgrounds/nwg-shell"],
        "background-dirs-once-set": False,
        "unsplash-width": 1920,
        "unsplash-height": 1080,
        "unsplash-keywords": ["nature", "water", "landscape"],
        "wallhaven-ratio": "16x9,16x10",
        "wallhaven-atleast": "1920x1080",
        "wallhaven-api-key": "",
        "wallhaven-tags": ["nature", "landscape"],
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
        "launcher-at-start": False,
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
        "pb-icon-theme": False,
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


def update_swaync_config(pos_x, pos_y, cc_width, window_width, mpris):
    settings_file = os.path.join(config_home, "swaync/config.json")
    if os.path.isfile(settings_file):
        print("Loading swaync settings from {}".format(settings_file))
        swaync_settings = load_json(settings_file)

        # Check if some new keys appeared
        defaults = load_json("/etc/xdg/swaync/config.json")

        for key in defaults:
            if key not in swaync_settings:
                swaync_settings[key] = defaults[key]

        swaync_settings["positionX"] = pos_x
        swaync_settings["positionY"] = pos_y
        swaync_settings["control-center-width"] = cc_width
        swaync_settings["notification-window-width"] = window_width
    else:
        swaync_settings = {
            "positionX": pos_x,
            "positionY": pos_y,
            "control-center-width": cc_width,
            "notification-window-width": window_width
        }

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

    if not os.getenv("SWAYSOCK"):
        eprint("SWAYSOCK not found, terminating")
        sys.exit(1)

    GLib.set_prgname('nwg-shell-config')

    global outputs
    outputs = list_outputs()

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
