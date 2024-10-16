import json
import subprocess
import gi
import os

from datetime import datetime
from i3ipc import Connection

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from nwg_shell_config.tools import is_command, get_lat_lon, list_background_dirs, load_text_file, \
    list_inputs_by_type, h_list_devices_by_type, gtklock_module_path, do_backup, unpack_to_tmp, restore_from_tmp, \
    get_theme_names, get_icon_themes, get_command_output, hyprctl


def set_from_checkbutton(cb, settings, key):
    settings[key] = cb.get_active()


def set_idle_use_from_checkbutton(cb, settings):
    settings["lockscreen-use-settings"] = cb.get_active()
    if not settings["lockscreen-use-settings"]:
        subprocess.call("killall swayidle", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)


def set_from_spinbutton(cb, settings, key, ndigits):
    settings[key] = round(cb.get_value(), ndigits)


def set_int_from_spinbutton(cb, settings, key):
    settings[key] = int(cb.get_value())


def set_limit_per_output(cb, settings, output_name):
    settings["autotiling-output-limits"][output_name] = int(cb.get_value())


def set_split_per_output(cb, settings, key, output_name):
    settings[key][output_name] = round(cb.get_value(), 2)


def reset_autotiling(btn, l_spin_boxes, w_spin_boxes, h_spin_boxes):
    for sb in l_spin_boxes:
        sb.set_value(0)
    for sb in w_spin_boxes:
        sb.set_value(1.0)
    for sb in h_spin_boxes:
        sb.set_value(1.0)


def set_keywords_from_entry(entry, settings):
    txt = entry.get_text()
    # Sanitize
    if " " in txt:
        txt = txt.replace(" ", "")
        entry.set_text(txt)
    if ",," in txt:
        txt = txt.replace(",,", ",")
        entry.set_text(txt)
    for c in txt:
        if ord(c) > 128:
            txt = txt.replace(c, "")
            entry.set_text(txt)
    txt = txt.strip(",")

    settings["unsplash-keywords"] = txt.split(",")


def validate_update_cmd(entry, cb, sb, settings):
    text = entry.get_text()
    if text and is_command(text):
        cb.set_active(True)
        cb.set_sensitive(True)
        sb.set_sensitive(True)
        settings["update-command"] = text
    else:
        cb.set_active(False)
        cb.set_sensitive(False)
        sb.set_sensitive(False)


def set_timeouts(cb, cb1, settings, key):
    settings[key] = int(cb.get_value())
    if int(cb1.get_value() < settings[key] + 5):
        cb1.set_value(settings[key] + 5)


def set_sleep_timeout(sb, lock_timeout_sb, settings, key):
    timeout = sb.get_value()
    lock_timeout = lock_timeout_sb.get_value()
    if timeout <= lock_timeout + 5:
        sb.set_value(lock_timeout + 5)
    settings[key] = int(sb.get_value())


def update_lat_lon(btn, sb_lat, sb_lon):
    tz, lat, lon = get_lat_lon()
    sb_lat.set_value(lat)
    sb_lat.set_tooltip_text(tz)
    sb_lon.set_value(lon)
    sb_lon.set_tooltip_text(tz)


def set_from_workspaces(entry, settings):
    valid_text = ""
    for char in entry.get_text():
        if char.isdigit() or char == " ":
            valid_text += char
    while '  ' in valid_text:
        valid_text = valid_text.replace('  ', ' ')
    entry.set_text(valid_text)
    settings["autotiling-workspaces"] = valid_text.strip()
    print(settings["autotiling-workspaces"])


def set_from_entry(entry, settings, key):
    settings[key] = entry.get_text()


def restore_defaults(btn, entry_dict):
    for key in entry_dict:
        key.set_text(entry_dict[key])


def set_custom_cmd_from_entry(entry, settings, key, widgets_to_lock):
    text = entry.get_text()
    for widget in widgets_to_lock:
        if text:
            widget.set_sensitive(False)
        else:
            widget.set_sensitive(True)
    settings[key] = text


def set_browser_from_combo(combo, entry, browsers_dict):
    entry.set_text(browsers_dict[combo.get_active_id()])


def set_dict_key_from_combo(combo, settings, key):
    settings[key] = combo.get_active_id()


def set_int_dict_key_from_combo(combo, settings, key):
    settings[key] = int(combo.get_active_id())

# def set_icon_theme_from_combo(combo, settings, key, theme_names):
#     settings[key] = theme_names[combo.get_active_id()]


def on_custom_folder_selected(fcb, cb_custom_path, settings):
    settings["backgrounds-custom-path"] = fcb.get_filename()
    cb_custom_path.set_sensitive(True)


def set_key_from_checkbox(cb, settings, key):
    settings[key] = cb.get_active()


def on_folder_btn_toggled(btn, settings):
    p = btn.get_label()
    if btn.get_active():
        if p not in settings["background-dirs"]:
            settings["background-dirs"].append(p)
    else:
        if p in settings["background-dirs"]:
            settings["background-dirs"].remove(p)


def launch(widget, cmd):
    print("Executing '{}'".format(cmd))
    subprocess.Popen('exec {}'.format(cmd), shell=True)


class SideMenuRow(Gtk.ListBoxRow):
    def __init__(self, label, margin_start=9):
        super().__init__()
        self.eb = Gtk.EventBox()
        self.add(self.eb)
        lbl = Gtk.Label.new(label)
        lbl.set_property("halign", Gtk.Align.START)
        lbl.set_property("margin-start", margin_start)
        lbl.set_property("margin-end", 9)
        self.eb.add(lbl)


def screen_tab(settings, voc):
    frame = Gtk.Frame()
    frame.set_label("  {}: {}  ".format(voc["common"], voc["screen-settings"]))
    frame.set_label_align(0.5, 0.5)
    frame.set_property("hexpand", True)
    grid = Gtk.Grid()
    frame.add(grid)
    grid.set_property("margin", 6)
    grid.set_column_spacing(6)
    grid.set_row_spacing(6)

    box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 6)
    box.set_homogeneous(True)
    box.set_property("margin-left", 0)
    box.set_property("margin-bottom", 4)
    grid.attach(box, 0, 0, 6, 1)

    btn = Gtk.Button()
    btn.set_property("name", "app-btn")
    btn.set_always_show_image(True)
    btn.set_image_position(Gtk.PositionType.TOP)
    img = Gtk.Image.new_from_icon_name("nwg-displays", Gtk.IconSize.DIALOG)
    btn.set_image(img)
    btn.set_label(voc["displays"])
    btn.connect("clicked", launch, "nwg-displays")
    box.pack_start(btn, False, True, 0)

    btn = Gtk.Button()
    btn.set_property("name", "app-btn")
    btn.set_always_show_image(True)
    btn.set_image_position(Gtk.PositionType.TOP)
    img = Gtk.Image.new_from_icon_name("azote", Gtk.IconSize.DIALOG)
    btn.set_image(img)
    btn.set_label(voc["wallpapers"])
    btn.connect("clicked", launch, "azote")
    box.pack_start(btn, False, True, 0)

    btn = Gtk.Button()
    btn.set_property("name", "app-btn")
    btn.set_always_show_image(True)
    btn.set_image_position(Gtk.PositionType.TOP)
    img = Gtk.Image.new_from_icon_name("nwg-look", Gtk.IconSize.DIALOG)
    btn.set_image(img)
    btn.set_label(voc["look-feel"])
    btn.connect("clicked", launch, "nwg-look")
    box.pack_start(btn, False, True, 0)

    btn = Gtk.Button()
    btn.set_property("name", "app-btn")
    btn.set_always_show_image(True)
    btn.set_image_position(Gtk.PositionType.TOP)
    img = Gtk.Image.new_from_icon_name("nwg-panel", Gtk.IconSize.DIALOG)
    btn.set_image(img)
    btn.set_label(voc["panel-settings"])
    btn.connect("clicked", launch, "nwg-panel-config")
    box.pack_start(btn, False, True, 0)

    # update_btn = Gtk.Button()
    # update_btn.set_property("name", "app-btn")
    # update_btn.set_always_show_image(True)
    # update_btn.set_image_position(Gtk.PositionType.TOP)
    # if pending_updates == 0:
    #     update_btn.set_label(voc["updates"])
    #     img = Gtk.Image.new_from_icon_name("nwg-shell", Gtk.IconSize.DIALOG)
    # else:
    #     update_btn.set_label("Updates ({})".format(pending_updates))
    #     img = Gtk.Image.new_from_icon_name("nwg-shell-update", Gtk.IconSize.DIALOG)
    # update_btn.set_image(img)
    # update_btn.connect("clicked", launch, "nwg-shell-updater")
    # box.pack_start(update_btn, False, True, 0)

    lbl = Gtk.Label()
    lbl.set_markup("<b>{}</b>".format(voc["desktop-style"]))
    lbl.set_property("halign", Gtk.Align.START)
    grid.attach(lbl, 0, 1, 1, 1)

    combo = Gtk.ComboBoxText()
    # combo.set_property("halign", Gtk.Align.START)
    grid.attach(combo, 1, 1, 3, 1)
    if os.getenv("SWAYSOCK"):
        for p in ["preset-0", "preset-1", "preset-2", "preset-3", "custom"]:
            combo.append(p, p)
    elif os.getenv("HYPRLAND_INSTANCE_SIGNATURE"):
        for p in ["hyprland-0", "hyprland-1", "hyprland-2", "hyprland-3", "custom-hyprland"]:
            combo.append(p, p)
    combo.set_active_id(settings["panel-preset"])
    combo.connect("changed", set_dict_key_from_combo, settings, "panel-preset")
    combo.set_tooltip_text(voc["preset-tooltip"])

    lbl = Gtk.Label()
    lbl.set_markup("<b>{}</b>".format(voc["night-light"]))
    lbl.set_property("margin-top", 6)
    lbl.set_property("margin-bottom", 6)
    lbl.set_property("halign", Gtk.Align.START)
    grid.attach(lbl, 0, 2, 1, 1)

    cb_night_light_on = Gtk.CheckButton.new_with_label(voc["on"])
    cb_night_light_on.set_active(settings["night-on"])
    cb_night_light_on.connect("toggled", set_from_checkbutton, settings, "night-on")
    cb_night_light_on.set_tooltip_text(voc["night-light-tooltip"])
    grid.attach(cb_night_light_on, 1, 2, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["latitude"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 2, 3, 1, 1)

    sb_lat = Gtk.SpinButton.new_with_range(-90.0, 90.0, 0.1)
    sb_lat.set_tooltip_text(voc["latitude-tooltip"])
    sb_lat.set_digits(4)
    sb_lat.set_value(settings["night-lat"])
    sb_lat.connect("value-changed", set_from_spinbutton, settings, "night-lat", 4)
    grid.attach(sb_lat, 3, 3, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["temp-night"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 3, 1, 1)

    sb_temp_low = Gtk.SpinButton.new_with_range(1000, 10000, 100)
    sb_temp_low.set_tooltip_text(voc["night-light-night-tooltip"])
    sb_temp_low.set_value(settings["night-temp-low"])
    sb_temp_low.connect("value-changed", set_int_from_spinbutton, settings, "night-temp-low")
    grid.attach(sb_temp_low, 1, 3, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["longitude"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 2, 4, 1, 1)

    sb_lon = Gtk.SpinButton.new_with_range(-180, 180, 0.1)
    sb_lon.set_tooltip_text(voc["longitude-tooltip"])
    sb_lon.set_value(settings["night-long"])
    sb_lon.connect("value-changed", set_from_spinbutton, settings, "night-long", 4)
    sb_lon.set_digits(4)
    grid.attach(sb_lon, 3, 4, 1, 1)

    if (sb_lat.get_value() == -1.0 and sb_lon.get_value()) == -1.0 \
            or (sb_lat.get_value() == 0.0 and sb_lon.get_value() == 0.0):
        update_lat_lon(None, sb_lat, sb_lon)

    lbl = Gtk.Label.new("{}:".format(voc["temp-day"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 4, 1, 1)

    sb_temp_high = Gtk.SpinButton.new_with_range(1000, 10000, 100)
    sb_temp_high.set_tooltip_text(voc["night-light-day-tooltip"])
    sb_temp_high.set_value(settings["night-temp-high"])
    sb_temp_high.connect("value-changed", set_int_from_spinbutton, settings, "night-temp-high")
    grid.attach(sb_temp_high, 1, 4, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["gamma"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 5, 1, 1)

    btn = Gtk.Button.new_with_label(voc["calculate-lat-long"])
    btn.set_tooltip_text(voc["calculate-lat-long-tooltip"])
    btn.connect("clicked", update_lat_lon, sb_lat, sb_lon)
    grid.attach(btn, 3, 5, 1, 1)

    sb_gamma = Gtk.SpinButton.new_with_range(0.1, 10.0, 0.1)
    sb_gamma.set_value(settings["night-gamma"])
    sb_gamma.connect("value-changed", set_from_spinbutton, settings, "night-gamma", 1)
    sb_gamma.set_tooltip_text(voc["gamma-tooltip"])
    grid.attach(sb_gamma, 1, 5, 1, 1)

    lbl = Gtk.Label()
    lbl.set_markup("<b>{}</b>".format(voc["help-window"]))
    lbl.set_property("halign", Gtk.Align.START)
    grid.attach(lbl, 0, 6, 1, 1)

    box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
    grid.attach(box, 1, 6, 3, 1)

    cb_help_overlay = Gtk.CheckButton.new_with_label(voc["on-layer"])
    cb_help_overlay.set_active(settings["help-layer-shell"])
    cb_help_overlay.connect("toggled", set_from_checkbutton, settings, "help-layer-shell")
    cb_help_overlay.set_tooltip_text(voc["overlay-tooltip"])
    box.pack_start(cb_help_overlay, False, False, 0)

    cb_help_keyboard = Gtk.CheckButton.new_with_label(voc["keyboard"])
    cb_help_keyboard.set_active(settings["help-keyboard"])
    cb_help_keyboard.connect("toggled", set_from_checkbutton, settings, "help-keyboard")
    cb_help_keyboard.set_tooltip_text(voc["keyboard-tooltip"])
    box.pack_start(cb_help_keyboard, False, False, 0)

    lbl = Gtk.Label.new("{}:".format(voc["font-size"]))
    lbl.set_property("halign", Gtk.Align.END)
    box.pack_start(lbl, False, False, 6)

    sb_help_font_size = Gtk.SpinButton.new_with_range(6, 48, 1)
    sb_help_font_size.set_value(settings["help-font-size"])
    sb_help_font_size.connect("value-changed", set_int_from_spinbutton, settings, "help-font-size")
    box.pack_start(sb_help_font_size, True, True, 0)

    # The way to turn the update-indicator section in the form off, is not to provide the 'nwg-system-update' script.
    if is_command("nwg-system-update"):
        lbl = Gtk.Label()
        lbl.set_markup("<b>{}</b>".format(voc["update-tray-icon"]))
        lbl.set_property("halign", Gtk.Align.START)
        grid.attach(lbl, 0, 7, 1, 1)

        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 6)
        grid.attach(box, 1, 7, 3, 1)
        cb_update_indicator_on = Gtk.CheckButton.new_with_label(voc["on"])
        cb_update_indicator_on.set_active(settings["update-indicator-on"])
        cb_update_indicator_on.connect("toggled", set_from_checkbutton, settings, "update-indicator-on")
        cb_update_indicator_on.set_tooltip_text(voc["update-tray-icon-tooltip"])
        box.pack_start(cb_update_indicator_on, False, False, 0)

        lbl = Gtk.Label.new("{}:".format(voc["interval"]))
        lbl.set_property("halign", Gtk.Align.END)
        box.pack_start(lbl, False, False, 0)

        sb_update_indicator_interval = Gtk.SpinButton.new_with_range(1, 1440, 1)
        sb_update_indicator_interval.set_tooltip_text(voc["update-indicator-interval-tooltip"])
        sb_update_indicator_interval.set_value(settings["update-indicator-interval"])
        sb_update_indicator_interval.connect("value-changed", set_int_from_spinbutton, settings,
                                             "update-indicator-interval")
        box.pack_start(sb_update_indicator_interval, False, False, 0)

        lbl = Gtk.Label.new("{}:".format(voc["command"]))
        lbl.set_property("halign", Gtk.Align.END)
        box.pack_start(lbl, False, False, 0)

        entry_update_cmd = Gtk.Entry()
        entry_update_cmd.set_placeholder_text("nwg-system-update")
        entry_update_cmd.set_tooltip_text(voc["update-command-tooltip"])
        entry_update_cmd.set_text(settings["update-command"])
        entry_update_cmd.connect("changed", validate_update_cmd, cb_update_indicator_on, sb_update_indicator_interval,
                                 settings)
        box.pack_start(entry_update_cmd, False, False, 0)
    else:
        settings["update-indicator-on"] = False

    cb_cliphist = Gtk.CheckButton.new_with_label(voc["clipboard-history"])
    cb_cliphist.set_active(settings["cliphist"])
    cb_cliphist.connect("toggled", set_from_checkbutton, settings, "cliphist")
    cb_cliphist.set_tooltip_text(voc["clipboard-history-tooltip"])
    grid.attach(cb_cliphist, 0, 8, 1, 1)

    cb_nm_applet = Gtk.CheckButton.new_with_label(voc["nm-applet"])
    cb_nm_applet.set_active(settings["appindicator"])
    cb_nm_applet.connect("toggled", set_from_checkbutton, settings, "appindicator")
    cb_nm_applet.set_tooltip_text(voc["nm-applet-tooltip"])
    grid.attach(cb_nm_applet, 1, 8, 1, 1)

    cb_screenshot = Gtk.CheckButton.new_with_label(voc["screenshot-applet"])
    cb_screenshot.set_active(settings["screenshot"])
    cb_screenshot.connect("toggled", set_from_checkbutton, settings, "screenshot")
    cb_screenshot.set_tooltip_text(voc["screenshot-applet-tooltip"])
    grid.attach(cb_screenshot, 2, 8, 1, 1)

    frame.show_all()

    return frame


def applications_tab(settings, voc, warn):
    frame = Gtk.Frame()
    frame.set_label("  {}: {}  ".format(voc["common"], voc["applications"]))
    frame.set_label_align(0.5, 0.5)
    frame.set_property("hexpand", True)
    grid = Gtk.Grid()
    frame.add(grid)
    grid.set_property("margin", 12)
    grid.set_column_spacing(6)
    grid.set_row_spacing(6)

    lbl = Gtk.Label()
    lbl.set_markup("<b>{}</b>".format(voc["default-applications"]))
    lbl.set_property("halign", Gtk.Align.START)
    grid.attach(lbl, 0, 0, 2, 1)

    lbl = Gtk.Label.new("{}:".format(voc["terminal"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 1, 1, 1)

    entry_terminal = Gtk.Entry.new()
    entry_terminal.set_tooltip_text(voc["terminal-tooltip"])
    entry_terminal.set_property("halign", Gtk.Align.START)
    entry_terminal.connect("changed", set_from_entry, settings, "terminal")
    if not settings["terminal"]:
        for cmd in ["foot", "alacritty", "kitty", "gnome-terminal", "sakura", "wterm"]:
            if is_command(cmd):
                entry_terminal.set_text(cmd)
                break
    else:
        entry_terminal.set_text(settings["terminal"])
    set_from_entry(entry_terminal, settings, "terminal")

    grid.attach(entry_terminal, 1, 1, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["file-manager"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 2, 1, 1)

    entry_fm = Gtk.Entry()
    entry_fm.set_tooltip_text(voc["file-manager-tooltip"])
    entry_fm.set_property("halign", Gtk.Align.START)

    entry_fm.connect("changed", set_from_entry, settings, "file-manager")
    if not settings["file-manager"]:
        for cmd in ["thunar", "pcmanfm", "nautilus", "caja"]:
            if is_command(cmd):
                entry_fm.set_text(cmd)
                break
    else:
        entry_fm.set_text(settings["file-manager"])

    grid.attach(entry_fm, 1, 2, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["text-editor"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 3, 1, 1)

    entry_te = Gtk.Entry()
    entry_te.set_tooltip_text(voc["text-editor-tooltip"])
    entry_te.set_property("halign", Gtk.Align.START)

    entry_te.connect("changed", set_from_entry, settings, "editor")
    if not settings["editor"]:
        for cmd in ["mousepad", "geany", "atom", "emacs", "gedit"]:
            if is_command(cmd):
                entry_te.set_text(cmd)
                break
    else:
        entry_te.set_text(settings["editor"])

    grid.attach(entry_te, 1, 3, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["web-browser"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 4, 1, 1)

    entry_browser = Gtk.Entry.new()
    entry_browser.set_tooltip_text(voc["web-browser-tooltip"])
    entry_browser.set_property("hexpand", True)

    entry_browser.set_text(settings["browser"])
    set_from_entry(entry_browser, settings, "browser")
    entry_browser.connect("changed", set_from_entry, settings, "browser")
    grid.attach(entry_browser, 1, 4, 2, 1)

    combo = Gtk.ComboBoxText()
    combo.set_property("halign", Gtk.Align.START)
    combo.set_tooltip_text(voc["web-browser-combo-tooltip"])
    grid.attach(combo, 1, 5, 1, 1)
    browsers = get_browsers()
    for key in browsers:
        combo.append(key, key)
        if key in settings["browser"]:
            combo.set_active_id(key)

    if entry_browser.get_text():
        for key in ["chromium", "google-chrome-stable", "firefox", "qutebrowser", "epiphany", "microsoft-edge-stable", "surf"]:
            if entry_browser.get_text() == key:
                combo.set_active_id(key)

    combo.connect("changed", set_browser_from_combo, entry_browser, browsers)

    lbl = Gtk.Label()
    lbl.set_markup("<b>{}</b>".format(voc["powerbar-commands"]))
    lbl.set_property("halign", Gtk.Align.START)
    grid.attach(lbl, 0, 6, 2, 1)

    lbl = Gtk.Label.new(f'{voc["pb-lock-screen"]}:')
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 7, 1, 1)

    entry_pb_lock = Gtk.Entry.new()
    entry_pb_lock.set_text(settings["pb-lock"])
    entry_pb_lock.set_tooltip_text(voc["leave-blank-btn-tooltip"])
    entry_pb_lock.set_property("halign", Gtk.Align.START)
    set_from_entry(entry_pb_lock, settings, "pb-lock")
    entry_pb_lock.connect("changed", set_from_entry, settings, "pb-lock")
    grid.attach(entry_pb_lock, 1, 7, 1, 1)

    lbl = Gtk.Label.new(f'{voc["exit"]}:')
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 8, 1, 1)

    entry_pb_exit = Gtk.Entry.new()
    entry_pb_exit.set_text(settings["pb-exit"])
    entry_pb_exit.set_tooltip_text(voc["leave-blank-btn-tooltip"])
    entry_pb_exit.set_property("halign", Gtk.Align.START)
    set_from_entry(entry_pb_exit, settings, "pb-exit")
    entry_pb_exit.connect("changed", set_from_entry, settings, "pb-exit")
    grid.attach(entry_pb_exit, 1, 8, 1, 1)

    lbl = Gtk.Label.new(f'{voc["reboot"]}:')
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 9, 1, 1)

    entry_pb_reboot = Gtk.Entry.new()
    entry_pb_reboot.set_text(settings["pb-reboot"])
    entry_pb_reboot.set_tooltip_text(voc["leave-blank-btn-tooltip"])
    entry_pb_reboot.set_property("halign", Gtk.Align.START)
    set_from_entry(entry_pb_reboot, settings, "pb-reboot")
    entry_pb_reboot.connect("changed", set_from_entry, settings, "pb-reboot")
    grid.attach(entry_pb_reboot, 1, 9, 1, 1)

    lbl = Gtk.Label.new(f'{voc["sleep"]}:')
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 10, 1, 1)

    entry_pb_sleep = Gtk.Entry.new()
    entry_pb_sleep.set_text(settings["pb-sleep"])
    entry_pb_sleep.set_tooltip_text(voc["leave-blank-btn-tooltip"])
    entry_pb_sleep.set_property("halign", Gtk.Align.START)
    set_from_entry(entry_pb_sleep, settings, "pb-sleep")
    entry_pb_sleep.connect("changed", set_from_entry, settings, "pb-sleep")
    grid.attach(entry_pb_sleep, 1, 10, 1, 1)

    lbl = Gtk.Label.new(f'{voc["power-off"]}:')
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 11, 1, 1)

    entry_pb_poweroff = Gtk.Entry.new()
    entry_pb_poweroff.set_text(settings["pb-poweroff"])
    entry_pb_poweroff.set_property("halign", Gtk.Align.START)
    set_from_entry(entry_pb_poweroff, settings, "pb-poweroff")
    entry_pb_poweroff.connect("changed", set_from_entry, settings, "pb-poweroff")
    grid.attach(entry_pb_poweroff, 1, 11, 1, 1)

    if warn:
        lbl = Gtk.Label.new("If you see this warning on startup, some of the fields above\n"
                            "have not yet been saved. Adjust these settings to your needs,\n"
                            "and press the 'Apply' button, for your key bindings to work.")
        lbl.set_property("halign", Gtk.Align.CENTER)
        lbl.set_justify(Gtk.Justification.CENTER)
        lbl.set_property("margin-top", 18)
        lbl.set_line_wrap(True)
        grid.attach(lbl, 0, 8, 3, 2)

    frame.show_all()

    return frame


def get_browsers():
    result = {}
    browsers = {
        "brave": "brave --enable-features=UseOzonePlatform --ozone-platform=wayland",
        "chromium": "chromium --enable-features=UseOzonePlatform --ozone-platform=wayland",
        "google-chrome-stable": "google-chrome-stable --enable-features=UseOzonePlatform --ozone-platform=wayland",
        "epiphany": "epiphany",
        "falkon": "falkon",
        "firefox": "MOZ_ENABLE_WAYLAND=1 firefox",
        "konqueror": "konqueror",
        "microsoft-edge-stable": "microsoft-edge-stable --enable-features=UseOzonePlatform --ozone-platform=wayland",
        "midori": "midori",
        "opera": "opera",
        "qutebrowser": "qutebrowser",
        "seamonkey": "seamonkey",
        "surf": "surf",
        "vivaldi-stable": "vivaldi-stable --enable-features=UseOzonePlatform --ozone-platform=wayland",
    }
    for key in browsers:
        if is_command(key):
            result[key] = browsers[key]

    return result


def backup_tab(config_home, data_home, backup_configs, backup_data, voc):
    frame = Gtk.Frame()
    frame.set_label("  {}: {}  ".format(voc["common"], voc["backup"]))
    frame.set_label_align(0.5, 0.5)
    frame.set_property("hexpand", True)
    grid = Gtk.Grid()
    frame.add(grid)
    grid.set_property("margin", 12)
    grid.set_column_spacing(6)
    grid.set_row_spacing(6)

    lbl = Gtk.Label()
    lbl.set_property("halign", Gtk.Align.START)
    lbl.set_markup("<b>{}</b>".format(voc["backup-desc"]))
    grid.attach(lbl, 0, 0, 3, 1)

    entry_backup = Gtk.Entry()
    entry_backup.set_width_chars(45)
    entry_backup.set_placeholder_text(voc["backup-path"])
    time = datetime.now()
    entry_backup.set_text(
        os.path.join("{}".format(os.getenv("HOME")), time.strftime("nwg-shell-backup-%Y%m%d-%H%M%S")))
    grid.attach(entry_backup, 0, 1, 2, 1)

    btn = Gtk.Button()
    btn.set_label(voc["create"])
    btn.connect("clicked", do_backup, config_home, data_home, backup_configs, backup_data, entry_backup, voc)
    grid.attach(btn, 2, 1, 1, 1)

    lbl = Gtk.Label()
    lbl.set_property("halign", Gtk.Align.START)
    lbl.set_property("margin-top", 12)
    lbl.set_markup("<b>{}</b>".format(voc["backup-restore-desc"]))
    grid.attach(lbl, 0, 2, 3, 1)

    restore_warning = Gtk.Label()
    restore_warning.set_markup('<b>{}</b>'.format(voc["backup-restore-warning"]))
    grid.attach(restore_warning, 0, 4, 2, 1)

    restore_btn = Gtk.Button()

    fcb = Gtk.FileChooserButton.new("Select file", Gtk.FileChooserAction.OPEN)
    fcb.set_current_folder(os.getenv("HOME"))
    f_filter = Gtk.FileFilter()
    f_filter.set_name(".tar.gz files")
    f_filter.add_pattern("*.tar.gz")
    fcb.add_filter(f_filter)
    fcb.connect("file-set", unpack_to_tmp, restore_btn, restore_warning, voc)
    grid.attach(fcb, 0, 3, 3, 1)

    restore_btn.set_label(voc["backup-restore"])
    restore_btn.connect("clicked", restore_from_tmp, restore_warning, voc)
    grid.attach(restore_btn, 2, 4, 1, 1)

    frame.show_all()
    restore_btn.hide()
    restore_warning.hide()

    return frame


def autotiling_tab(settings, outputs, voc):
    frame = Gtk.Frame()
    frame.set_label("  {}: {}  ".format(voc["common"], voc["autotiling"]))
    frame.set_label_align(0.5, 0.5)
    frame.set_property("hexpand", True)
    grid = Gtk.Grid()
    frame.add(grid)
    grid.set_property("margin", 12)
    grid.set_column_spacing(6)
    grid.set_row_spacing(6)

    cb_autotiling_use_settings = Gtk.CheckButton.new_with_label(voc["use-these-settings"])
    cb_autotiling_use_settings.set_property("halign", Gtk.Align.START)
    cb_autotiling_use_settings.set_property("margin-bottom", 6)
    cb_autotiling_use_settings.set_tooltip_text(voc["autotiling-tooltip"])
    cb_autotiling_use_settings.set_active(settings["autotiling-on"])
    cb_autotiling_use_settings.connect("toggled", set_from_checkbutton, settings, "autotiling-on")
    grid.attach(cb_autotiling_use_settings, 0, 0, 2, 1)

    lbl = Gtk.Label()
    lbl.set_markup(
        '<a href="https://nwg-piotr.github.io/nwg-shell/utilities-and-scripts#workflow-autotiling">{}</a>'.format(
            voc["more-info"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 3, 0, 2, 1)

    lbl = Gtk.Label()
    lbl.set_markup("<b>{}</b>".format(voc["workspaces"]))
    lbl.set_property("halign", Gtk.Align.START)
    grid.attach(lbl, 0, 1, 1, 1)

    entry = Gtk.Entry()
    entry.set_placeholder_text("1 2 3 4 5 6 7 8")
    entry.set_property("halign", Gtk.Align.START)
    entry.set_text(settings["autotiling-workspaces"])
    entry.set_tooltip_text(voc["workspaces-tooltip"])
    entry.set_property("margin-bottom", 6)
    entry.connect("changed", set_from_workspaces, settings)
    grid.attach(entry, 1, 1, 2, 1)

    lbl = Gtk.Label()
    lbl.set_markup("<b>{}</b>".format(voc["workspaces"]))
    lbl.set_property("halign", Gtk.Align.START)
    grid.attach(lbl, 0, 1, 1, 1)

    lbl = Gtk.Label()
    lbl.set_markup("<b>{}</b>".format(voc["per-output"]))
    lbl.set_property("halign", Gtk.Align.START)
    grid.attach(lbl, 0, 2, 1, 1)

    lbl = Gtk.Label.new(voc["autotiling-depth-limit"])
    lbl.set_property("halign", Gtk.Align.START)
    grid.attach(lbl, 1, 2, 1, 1)

    lbl = Gtk.Label.new(voc["autotiling-split-width"])
    lbl.set_property("halign", Gtk.Align.START)
    grid.attach(lbl, 2, 2, 1, 1)

    lbl = Gtk.Label.new(voc["autotiling-split-height"])
    lbl.set_property("halign", Gtk.Align.START)
    grid.attach(lbl, 3, 2, 1, 1)

    l_spin_boxes = []
    w_spin_boxes = []
    h_spin_boxes = []
    i = 0
    for i in range(len(outputs)):
        o_name = outputs[i]
        lbl = Gtk.Label.new("{}:".format(o_name))
        lbl.set_property("halign", Gtk.Align.END)
        grid.attach(lbl, 0, 3 + i, 1, 1)

        limit = settings["autotiling-output-limits"][o_name] if o_name in settings["autotiling-output-limits"] else 0
        sb = Gtk.SpinButton.new_with_range(0, 256, 1)
        sb.set_property("halign", Gtk.Align.START)
        sb.set_value(limit)
        sb.set_tooltip_text(voc["autotiling-depth-limit-tooltip"])
        sb.connect("value-changed", set_limit_per_output, settings, o_name)
        l_spin_boxes.append(sb)
        grid.attach(sb, 1, 3 + i, 1, 1)

        split_width = settings["autotiling-output-splitwidths"][o_name] if o_name in settings[
            "autotiling-output-splitwidths"] else 1.0
        sb = Gtk.SpinButton.new_with_range(0.2, 1.9, 0.01)
        sb.set_property("halign", Gtk.Align.START)
        sb.set_value(split_width)
        sb.set_tooltip_text(voc["autotiling-split-tooltip"])
        sb.connect("value-changed", set_split_per_output, settings, "autotiling-output-splitwidths", o_name)
        w_spin_boxes.append(sb)
        grid.attach(sb, 2, 3 + i, 1, 1)

        split_height = settings["autotiling-output-splitheights"][o_name] if o_name in settings[
            "autotiling-output-splitheights"] else 1.0
        sb = Gtk.SpinButton.new_with_range(0.2, 1.9, 0.01)
        sb.set_property("halign", Gtk.Align.START)
        sb.set_value(split_height)
        sb.set_tooltip_text(voc["autotiling-split-tooltip"])
        sb.connect("value-changed", set_split_per_output, settings, "autotiling-output-splitheights", o_name)
        h_spin_boxes.append(sb)
        grid.attach(sb, 3, 3 + i, 1, 1)

    btn = Gtk.Button()
    btn.set_label(voc["restore-defaults"])
    btn.connect("clicked", reset_autotiling, l_spin_boxes, w_spin_boxes, h_spin_boxes)
    grid.attach(btn, 1, 3 + i + 1, 3, 1)

    frame.show_all()

    return frame


def keyboard_tab(settings, voc):
    frame = Gtk.Frame()
    frame.set_label("  {}: {}  ".format(voc["common"], voc["keyboard"]))
    frame.set_label_align(0.5, 0.5)
    frame.set_property("hexpand", True)
    grid = Gtk.Grid()
    frame.add(grid)
    grid.set_property("margin", 12)
    grid.set_column_spacing(6)
    grid.set_row_spacing(6)

    cb_keyboard_use_settings = Gtk.CheckButton.new_with_label(voc["use-these-settings"])
    cb_keyboard_use_settings.set_property("halign", Gtk.Align.START)
    cb_keyboard_use_settings.set_property("margin-bottom", 6)
    cb_keyboard_use_settings.set_tooltip_text(voc["keyboard-include-tooltip"])
    cb_keyboard_use_settings.set_active(settings["keyboard-use-settings"])
    cb_keyboard_use_settings.connect("toggled", set_from_checkbutton, settings, "keyboard-use-settings")
    grid.attach(cb_keyboard_use_settings, 0, 0, 2, 1)

    lbl = Gtk.Label.new("{}:".format(voc["device"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 1, 1, 1)

    combo_device = Gtk.ComboBoxText()
    combo_device.set_property("halign", Gtk.Align.START)
    combo_device.set_tooltip_text(voc["device-tooltip"])
    combo_device.append("", voc["all-of-type"])
    keyboards = list_inputs_by_type(input_type="keyboard")
    for item in keyboards:
        combo_device.append(item, item)
    combo_device.set_active_id(settings["keyboard-identifier"])
    combo_device.connect("changed", set_dict_key_from_combo, settings, "keyboard-identifier")
    grid.attach(combo_device, 1, 1, 2, 1)

    lbl = Gtk.Label.new("{}:".format(voc["keyboard-layout"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 2, 1, 1)

    entry_layout = Gtk.Entry()
    entry_layout.set_tooltip_text(voc["keyboard-layout-tooltip"])
    entry_layout.set_text(settings["keyboard-xkb-layout"])
    entry_layout.connect("changed", set_from_entry, settings, "keyboard-xkb-layout")
    grid.attach(entry_layout, 1, 2, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["keyboard-variant"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 3, 1, 1)

    entry_variant = Gtk.Entry()
    entry_variant.set_tooltip_text(voc["keyboard-variant-tooltip"])
    entry_variant.set_text(settings["keyboard-xkb-variant"])
    entry_variant.connect("changed", set_from_entry, settings, "keyboard-xkb-variant")
    grid.attach(entry_variant, 1, 3, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["keyboard-repeat-delay"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 4, 1, 1)

    sb_repeat_delay = Gtk.SpinButton.new_with_range(1, 6000, 1)
    sb_repeat_delay.set_value(settings["keyboard-repeat-delay"])
    sb_repeat_delay.connect("value-changed", set_int_from_spinbutton, settings, "keyboard-repeat-delay")
    sb_repeat_delay.set_tooltip_text(voc["keyboard-repeat-delay-tooltip"])
    grid.attach(sb_repeat_delay, 1, 4, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["keyboard-repeat-rate"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 5, 1, 1)

    sb_repeat_rate = Gtk.SpinButton.new_with_range(1, 4000, 1)
    sb_repeat_rate.set_value(settings["keyboard-repeat-rate"])
    sb_repeat_rate.connect("value-changed", set_int_from_spinbutton, settings, "keyboard-repeat-rate")
    sb_repeat_rate.set_tooltip_text(voc["keyboard-repeat-rate-tooltip"])
    grid.attach(sb_repeat_rate, 1, 5, 1, 1)

    lbl = Gtk.Label.new("CapsLock:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 6, 1, 1)

    combo_caps = Gtk.ComboBoxText()
    combo_caps.set_property("halign", Gtk.Align.START)
    combo_caps.set_tooltip_text(voc["capslock-tooltip"])
    for item in ["disabled", "enabled"]:
        combo_caps.append(item, voc[item])
    combo_caps.set_active_id(settings["keyboard-xkb-capslock"])
    combo_caps.connect("changed", set_dict_key_from_combo, settings, "keyboard-xkb-capslock")
    grid.attach(combo_caps, 1, 6, 1, 1)

    lbl = Gtk.Label.new("NumLock:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 7, 1, 1)

    combo_num = Gtk.ComboBoxText()
    combo_num.set_property("halign", Gtk.Align.START)
    combo_num.set_tooltip_text(voc["numlock-tooltip"])
    for item in ["disabled", "enabled"]:
        combo_num.append(item, voc[item])
    combo_num.set_active_id(settings["keyboard-xkb-numlock"])
    combo_num.connect("changed", set_dict_key_from_combo, settings, "keyboard-xkb-numlock")
    grid.attach(combo_num, 1, 7, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["custom-field"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 8, 1, 1)

    entry_cname = Gtk.Entry()
    entry_cname.set_tooltip_text(voc["custom-field-name-tooltip"])
    entry_cname.set_placeholder_text(voc["name"])
    entry_cname.set_text(settings["keyboard-custom-name"])
    entry_cname.connect("changed", set_from_entry, settings, "keyboard-custom-name")
    grid.attach(entry_cname, 1, 8, 1, 1)

    entry_cname = Gtk.Entry()
    entry_cname.set_tooltip_text(voc["custom-field-value-tooltip"])
    entry_cname.set_placeholder_text(voc["value"])
    entry_cname.set_text(settings["keyboard-custom-value"])
    entry_cname.connect("changed", set_from_entry, settings, "keyboard-custom-value")
    grid.attach(entry_cname, 2, 8, 1, 1)

    frame.show_all()

    return frame


def h_general_tab(settings, voc):
    frame = Gtk.Frame()
    frame.set_label("  {}: {}  ".format(voc["common"], voc["general-settings"]))
    frame.set_label_align(0.5, 0.5)
    frame.set_property("hexpand", True)
    grid = Gtk.Grid()
    frame.add(grid)
    grid.set_property("margin", 12)
    grid.set_column_spacing(6)
    grid.set_row_spacing(6)

    cb_gen_use_settings = Gtk.CheckButton.new_with_label(voc["use-these-settings"])
    cb_gen_use_settings.set_property("halign", Gtk.Align.START)
    cb_gen_use_settings.set_property("margin-bottom", 6)
    cb_gen_use_settings.set_tooltip_text(voc["hyprland-include-tooltip"])
    cb_gen_use_settings.set_active(settings["gen-use-settings"])
    cb_gen_use_settings.connect("toggled", set_from_checkbutton, settings, "gen-use-settings")
    grid.attach(cb_gen_use_settings, 0, 0, 2, 1)

    lbl = Gtk.Label.new("{}:".format(voc["layout"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 1, 1, 1)

    combo_layout = Gtk.ComboBoxText()
    for item in ["dwindle", "master"]:
        combo_layout.append(item, item)
    combo_layout.set_active_id(settings["gen-layout"])
    combo_layout.connect("changed", set_dict_key_from_combo, settings, "gen-layout")
    grid.attach(combo_layout, 1, 1, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["window-border-size"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 2, 1, 1)

    sb_border_size = Gtk.SpinButton.new_with_range(0, 256, 1)
    sb_border_size.set_property("halign", Gtk.Align.START)
    sb_border_size.set_value(settings["gen-border_size"])
    sb_border_size.connect("value-changed", set_int_from_spinbutton, settings, "gen-border_size")
    grid.attach(sb_border_size, 1, 2, 1, 1)

    cb_no_boarder = Gtk.CheckButton.new_with_label(voc["no-border-on-floating"])
    cb_no_boarder.set_property("halign", Gtk.Align.START)
    cb_no_boarder.set_property("margin-bottom", 6)
    cb_no_boarder.set_active(settings["gen-no_border_on_floating"])
    cb_no_boarder.connect("toggled", set_from_checkbutton, settings, "gen-no_border_on_floating")
    grid.attach(cb_no_boarder, 2, 2, 2, 1)

    lbl = Gtk.Label.new("{}:".format(voc["gaps-in"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 3, 1, 1)

    sb_gaps_in = Gtk.SpinButton.new_with_range(0, 256, 1)
    sb_gaps_in.set_property("halign", Gtk.Align.START)
    sb_gaps_in.set_value(settings["gen-gaps_in"])
    sb_gaps_in.connect("value-changed", set_int_from_spinbutton, settings, "gen-gaps_in")
    grid.attach(sb_gaps_in, 1, 3, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["gaps-out"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 2, 3, 1, 1)

    sb_gaps_out = Gtk.SpinButton.new_with_range(0, 256, 1)
    sb_gaps_out.set_property("halign", Gtk.Align.START)
    sb_gaps_out.set_value(settings["gen-gaps_out"])
    sb_gaps_out.connect("value-changed", set_int_from_spinbutton, settings, "gen-gaps_out")
    grid.attach(sb_gaps_out, 3, 3, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["color-active-border-start"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 4, 1, 1)

    entry_cab_start = Gtk.Entry()
    entry_cab_start.set_width_chars(8)
    entry_cab_start.set_tooltip_text(voc["color-border-start-tooltip"])
    entry_cab_start.set_text(settings["gen-col-active_border-start"])
    entry_cab_start.connect("changed", set_from_entry, settings, "gen-col-active_border-start")
    grid.attach(entry_cab_start, 1, 4, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["end"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 2, 4, 1, 1)

    entry_cab_end = Gtk.Entry()
    entry_cab_end.set_width_chars(8)
    entry_cab_end.set_tooltip_text(voc["color-border-end-tooltip"])
    entry_cab_end.set_text(settings["gen-col-active_border-end"])
    entry_cab_end.connect("changed", set_from_entry, settings, "gen-col-active_border-end")
    grid.attach(entry_cab_end, 3, 4, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["angle"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 4, 4, 1, 1)

    sb_cab_angle = Gtk.SpinButton.new_with_range(0, 365, 1)
    sb_cab_angle.set_property("halign", Gtk.Align.START)
    sb_cab_angle.set_tooltip_text(voc["color-gradient-angle"])
    sb_cab_angle.set_value(settings["gen-col-active_border-deg"])
    sb_cab_angle.connect("value-changed", set_int_from_spinbutton, settings, "gen-col-active_border-deg")
    grid.attach(sb_cab_angle, 5, 4, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["color-inactive-border-start"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 5, 1, 1)

    entry_cib_start = Gtk.Entry()
    entry_cib_start.set_width_chars(8)
    entry_cib_start.set_tooltip_text(voc["color-border-start-tooltip"])
    entry_cib_start.set_text(settings["gen-col-inactive_border-start"])
    entry_cib_start.connect("changed", set_from_entry, settings, "gen-col-inactive_border-start")
    grid.attach(entry_cib_start, 1, 5, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["end"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 2, 5, 1, 1)

    entry_cib_end = Gtk.Entry()
    entry_cib_end.set_width_chars(8)
    entry_cib_end.set_tooltip_text(voc["color-border-end-tooltip"])
    entry_cib_end.set_text(settings["gen-col-inactive_border-end"])
    entry_cib_end.connect("changed", set_from_entry, settings, "gen-col-inactive_border-end")
    grid.attach(entry_cib_end, 3, 5, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["angle"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 4, 5, 1, 1)

    sb_cib_angle = Gtk.SpinButton.new_with_range(0, 365, 1)
    sb_cib_angle.set_property("halign", Gtk.Align.START)
    sb_cib_angle.set_tooltip_text(voc["color-gradient-angle"])
    sb_cib_angle.set_value(settings["gen-col-inactive_border-deg"])
    sb_cib_angle.connect("value-changed", set_int_from_spinbutton, settings, "gen-col-inactive_border-deg")
    grid.attach(sb_cib_angle, 5, 5, 1, 1)

    cb_no_cursor_warps = Gtk.CheckButton.new_with_label(voc["no-cursor-warps"])
    cb_no_cursor_warps.set_tooltip_text(voc["no-cursor-warps-tooltip"])
    cb_no_cursor_warps.set_property("halign", Gtk.Align.START)
    cb_no_cursor_warps.set_active(settings["gen-no_cursor_warps"])
    cb_no_cursor_warps.connect("toggled", set_from_checkbutton, settings, "gen-no_cursor_warps")
    grid.attach(cb_no_cursor_warps, 0, 6, 1, 1)

    cb_no_focus_fallback = Gtk.CheckButton.new_with_label(voc["no-focus-fallback"])
    cb_no_focus_fallback.set_tooltip_text(voc["no-focus-fallback-tooltip"])
    cb_no_focus_fallback.set_property("halign", Gtk.Align.START)
    cb_no_focus_fallback.set_active(settings["gen-no_focus_fallback"])
    cb_no_focus_fallback.connect("toggled", set_from_checkbutton, settings, "gen-no_focus_fallback")
    grid.attach(cb_no_focus_fallback, 1, 6, 1, 1)

    cb_allow_tearing = Gtk.CheckButton.new_with_label(voc["allow-tearing"])
    cb_allow_tearing.set_tooltip_text(voc["allow-tearing-tooltip"])
    cb_allow_tearing.set_property("halign", Gtk.Align.START)
    cb_allow_tearing.set_active(settings["gen-allow_tearing"])
    cb_allow_tearing.connect("toggled", set_from_checkbutton, settings, "gen-allow_tearing")
    grid.attach(cb_allow_tearing, 1, 7, 1, 1)

    cb_resize_on_border = Gtk.CheckButton.new_with_label(voc["resize-on-border"])
    cb_resize_on_border.set_tooltip_text(voc["resize-on-border"])
    cb_resize_on_border.set_property("halign", Gtk.Align.START)
    cb_resize_on_border.set_active(settings["gen-resize_on_border"])
    cb_resize_on_border.connect("toggled", set_from_checkbutton, settings, "gen-resize_on_border")
    grid.attach(cb_resize_on_border, 0, 7, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["extend-border-grab-area"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 1, 8, 2, 1)

    sb_extend_grab_area = Gtk.SpinButton.new_with_range(0, 365, 1)
    sb_extend_grab_area.set_property("halign", Gtk.Align.START)
    sb_extend_grab_area.set_tooltip_text(voc["extend-border-grab-area-tooltip"])
    sb_extend_grab_area.set_value(settings["gen-extend_border_grab_area"])
    sb_extend_grab_area.connect("value-changed", set_int_from_spinbutton, settings, "gen-extend_border_grab_area")
    grid.attach(sb_extend_grab_area, 3, 8, 1, 1)

    cb_hover = Gtk.CheckButton.new_with_label(voc["hover-icon-on-border"])
    cb_hover.set_tooltip_text(voc["hover-icon-on-border-tooltip"])
    cb_hover.set_property("halign", Gtk.Align.START)
    cb_hover.set_active(settings["gen-hover_icon_on_border"])
    cb_hover.connect("toggled", set_from_checkbutton, settings, "gen-hover_icon_on_border")
    grid.attach(cb_hover, 0, 8, 1, 1)

    frame.show_all()

    return frame


def h_dwindle_tab(settings, voc):
    frame = Gtk.Frame()
    frame.set_label("  {}: {}  ".format(voc["common"], voc["dwindle-layout"]))
    frame.set_label_align(0.5, 0.5)
    frame.set_property("hexpand", True)
    grid = Gtk.Grid()
    frame.add(grid)
    grid.set_property("margin", 12)
    grid.set_column_spacing(6)
    grid.set_row_spacing(6)

    cb_use_settings = Gtk.CheckButton.new_with_label(voc["use-these-settings"])
    cb_use_settings.set_property("halign", Gtk.Align.START)
    cb_use_settings.set_property("margin-bottom", 6)
    cb_use_settings.set_tooltip_text(voc["hyprland-include-tooltip"])
    cb_use_settings.set_active(settings["dwindle-use-settings"])
    cb_use_settings.connect("toggled", set_from_checkbutton, settings, "dwindle-use-settings")
    grid.attach(cb_use_settings, 0, 0, 2, 1)

    cb_pseudotiling = Gtk.CheckButton.new_with_label(voc["pseudotiling"])
    cb_pseudotiling.set_property("halign", Gtk.Align.START)
    cb_pseudotiling.set_tooltip_text(voc["pseudotiling-tooltip"])
    cb_pseudotiling.set_active(settings["dwindle-pseudotile"])
    cb_pseudotiling.connect("toggled", set_from_checkbutton, settings, "dwindle-pseudotile")
    grid.attach(cb_pseudotiling, 0, 1, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["force-split"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 2, 1, 1, 1)

    combo_force_split = Gtk.ComboBoxText()
    combo_force_split.set_tooltip_text(voc["force-split-tooltip"])
    d = {"0": voc["force-split-0"], "1": voc["force-split-1"], "2": voc["force-split-2"]}
    for item in ["0", "1", "2"]:
        combo_force_split.append(item, d[item])
    combo_force_split.set_active_id(str(settings["dwindle-force_split"]))
    combo_force_split.connect("changed", set_int_dict_key_from_combo, settings, "dwindle-force_split")
    grid.attach(combo_force_split, 3, 1, 1, 1)

    cb_preserve_split = Gtk.CheckButton.new_with_label(voc["preserve-split"])
    cb_preserve_split.set_property("halign", Gtk.Align.START)
    cb_preserve_split.set_tooltip_text(voc["preserve-split-tooltip"])
    cb_preserve_split.set_active(settings["dwindle-preserve_split"])
    cb_preserve_split.connect("toggled", set_from_checkbutton, settings, "dwindle-preserve_split")
    grid.attach(cb_preserve_split, 1, 1, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["special-scale-factor"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 2, 1, 1)

    sb_ssf = Gtk.SpinButton.new_with_range(0.0, 1.0, 0.1)
    sb_ssf.set_value(settings["dwindle-special_scale_factor"])
    sb_ssf.set_tooltip_text(voc["special-scale-factor-tooltip"])
    sb_ssf.connect("value-changed", set_from_spinbutton, settings, "dwindle-special_scale_factor", 2)
    grid.attach(sb_ssf, 1, 2, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["split-width-multiplier"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 2, 2, 1, 1)

    sb_swm = Gtk.SpinButton.new_with_range(0.1, 2.0, 0.1)
    sb_swm.set_value(settings["dwindle-split_width_multiplier"])
    sb_swm.set_tooltip_text(voc["split-width-multiplier-tooltip"])
    sb_swm.connect("value-changed", set_from_spinbutton, settings, "dwindle-split_width_multiplier", 2)
    grid.attach(sb_swm, 3, 2, 1, 1)

    cb_ngwo = Gtk.CheckButton.new_with_label(voc["no-gaps-when-only"])
    cb_ngwo.set_property("halign", Gtk.Align.START)
    cb_ngwo.set_tooltip_text(voc["no-gaps-when-only-tooltip"])
    cb_ngwo.set_active(settings["dwindle-no_gaps_when_only"])
    cb_ngwo.connect("toggled", set_from_checkbutton, settings, "dwindle-no_gaps_when_only")
    grid.attach(cb_ngwo, 0, 3, 2, 1)

    cb_uafs = Gtk.CheckButton.new_with_label(voc["use-active-for-splits"])
    cb_uafs.set_property("halign", Gtk.Align.START)
    cb_uafs.set_tooltip_text(voc["use-active-for-splits-tooltip"])
    cb_uafs.set_active(settings["dwindle-use_active_for_splits"])
    cb_uafs.connect("toggled", set_from_checkbutton, settings, "dwindle-use_active_for_splits")
    grid.attach(cb_uafs, 2, 3, 2, 1)

    lbl = Gtk.Label.new("{}:".format(voc["default-split-ratio"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 4, 1, 1)

    sb_dsr = Gtk.SpinButton.new_with_range(0.1, 1.9, 0.01)
    sb_dsr.set_value(settings["dwindle-default_split_ratio"])
    sb_dsr.set_tooltip_text(voc["default-split-ratio-tooltip"])
    sb_dsr.connect("value-changed", set_from_spinbutton, settings, "dwindle-default_split_ratio", 3)
    grid.attach(sb_dsr, 1, 4, 1, 1)

    cb_smart_split = Gtk.CheckButton.new_with_label(voc["smart-split"])
    cb_smart_split.set_property("halign", Gtk.Align.START)
    cb_smart_split.set_tooltip_text(voc["smart-split-tooltip"])
    cb_smart_split.set_active(settings["dwindle-smart_split"])
    cb_smart_split.connect("toggled", set_from_checkbutton, settings, "dwindle-smart_split")
    grid.attach(cb_smart_split, 2, 4, 1, 1)

    cb_smart_resizing = Gtk.CheckButton.new_with_label(voc["smart-resizing"])
    cb_smart_resizing.set_property("halign", Gtk.Align.START)
    cb_smart_resizing.set_tooltip_text(voc["smart-resizing-tooltip"])
    cb_smart_resizing.set_active(settings["dwindle-smart_resizing"])
    cb_smart_resizing.connect("toggled", set_from_checkbutton, settings, "dwindle-smart_resizing")
    grid.attach(cb_smart_resizing, 3, 4, 1, 1)

    frame.show_all()

    return frame


def h_master_tab(settings, voc):
    frame = Gtk.Frame()
    frame.set_label("  {}: {}  ".format(voc["common"], voc["master-layout"]))
    frame.set_label_align(0.5, 0.5)
    frame.set_property("hexpand", True)
    grid = Gtk.Grid()
    frame.add(grid)
    grid.set_property("margin", 12)
    grid.set_column_spacing(6)
    grid.set_row_spacing(6)

    cb_use_settings = Gtk.CheckButton.new_with_label(voc["use-these-settings"])
    cb_use_settings.set_property("halign", Gtk.Align.START)
    cb_use_settings.set_property("margin-bottom", 6)
    cb_use_settings.set_tooltip_text(voc["hyprland-include-tooltip"])
    cb_use_settings.set_active(settings["master-use-settings"])
    cb_use_settings.connect("toggled", set_from_checkbutton, settings, "master-use-settings")
    grid.attach(cb_use_settings, 0, 0, 2, 1)

    cb_assp = Gtk.CheckButton.new_with_label(voc["allow-small-split"])
    cb_assp.set_property("halign", Gtk.Align.START)
    cb_assp.set_tooltip_text(voc["allow-small-split-tooltip"])
    cb_assp.set_active(settings["master-allow_small_split"])
    cb_assp.connect("toggled", set_from_checkbutton, settings, "master-allow_small_split")
    grid.attach(cb_assp, 0, 1, 1, 1)

    cb_nis = Gtk.CheckButton.new_with_label(voc["new-is-master"])
    cb_nis.set_property("halign", Gtk.Align.START)
    cb_nis.set_tooltip_text(voc["new-is-master-tooltip"])
    cb_nis.set_active(settings["master-new_is_master"])
    cb_nis.connect("toggled", set_from_checkbutton, settings, "master-new_is_master")
    grid.attach(cb_nis, 1, 1, 1, 1)

    cb_not = Gtk.CheckButton.new_with_label(voc["new-on-top"])
    cb_not.set_property("halign", Gtk.Align.START)
    cb_not.set_tooltip_text(voc["new-on-top-tooltip"])
    cb_not.set_active(settings["master-new_on_top"])
    cb_not.connect("toggled", set_from_checkbutton, settings, "master-new_on_top")
    grid.attach(cb_not, 2, 1, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["master-split-factor"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 2, 1, 1)

    sb_msf = Gtk.SpinButton.new_with_range(0.0, 1.0, 0.01)
    sb_msf.set_value(settings["master-mfact"])
    sb_msf.set_tooltip_text(voc["master-split-factor-tooltip"])
    sb_msf.connect("value-changed", set_from_spinbutton, settings, "master-mfact", 3)
    grid.attach(sb_msf, 1, 2, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["special-scale-factor"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 2, 2, 1, 1)

    sb_ssf = Gtk.SpinButton.new_with_range(0.0, 1.0, 0.01)
    sb_ssf.set_value(settings["master-special_scale_factor"])
    sb_ssf.set_tooltip_text(voc["special-scale-factor-tooltip"])
    sb_ssf.connect("value-changed", set_from_spinbutton, settings, "master-special_scale_factor", 3)
    grid.attach(sb_ssf, 3, 2, 1, 1)

    cb_ngwo = Gtk.CheckButton.new_with_label(voc["no-gaps-when-only"])
    cb_ngwo.set_property("halign", Gtk.Align.START)
    cb_ngwo.set_tooltip_text(voc["no-gaps-when-only-tooltip"])
    cb_ngwo.set_active(settings["master-no_gaps_when_only"])
    cb_ngwo.connect("toggled", set_from_checkbutton, settings, "master-no_gaps_when_only")
    grid.attach(cb_ngwo, 0, 3, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["master-orientation"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 2, 3, 1, 1)

    combo_orientation = Gtk.ComboBoxText()
    combo_orientation.set_property("halign", Gtk.Align.START)
    combo_orientation.set_tooltip_text(voc["master-orientation-tooltip"])
    d = {"left": voc["left"], "right": voc["right"], "top": voc["top"], "bottom": voc["bottom"],
         "center": voc["center"]}
    for item in ["left", "right", "top", "bottom", "center"]:
        combo_orientation.append(item, d[item])
    combo_orientation.set_active_id(settings["master-orientation"])
    combo_orientation.connect("changed", set_dict_key_from_combo, settings, "master-orientation")
    grid.attach(combo_orientation, 3, 3, 1, 1)

    cb_inherit = Gtk.CheckButton.new_with_label(voc["inherit-fullscreen"])
    cb_inherit.set_property("halign", Gtk.Align.START)
    cb_inherit.set_tooltip_text(voc["inherit-fullscreen-tooltip"])
    cb_inherit.set_active(settings["master-inherit_fullscreen"])
    cb_inherit.connect("toggled", set_from_checkbutton, settings, "master-inherit_fullscreen")
    grid.attach(cb_inherit, 0, 4, 1, 1)

    cb_acenter = Gtk.CheckButton.new_with_label(voc["always-center-master"])
    cb_acenter.set_property("halign", Gtk.Align.START)
    cb_acenter.set_tooltip_text(voc["always-center-master-tooltip"])
    cb_acenter.set_active(settings["master-always_center_master"])
    cb_acenter.connect("toggled", set_from_checkbutton, settings, "master-always_center_master")
    grid.attach(cb_acenter, 1, 4, 2, 1)

    frame.show_all()

    return frame


def h_misc_tab(settings, voc):
    frame = Gtk.Frame()
    frame.set_label("  {}: {}  ".format(voc["common"], voc["miscellaneous"]))
    frame.set_label_align(0.5, 0.5)
    frame.set_property("hexpand", True)
    grid = Gtk.Grid()
    frame.add(grid)
    grid.set_property("margin", 12)
    grid.set_column_spacing(6)
    grid.set_row_spacing(6)

    cb_use_settings = Gtk.CheckButton.new_with_label(voc["use-these-settings"])
    cb_use_settings.set_property("halign", Gtk.Align.START)
    cb_use_settings.set_property("margin-bottom", 6)
    cb_use_settings.set_tooltip_text(voc["hyprland-include-tooltip"])
    cb_use_settings.set_active(settings["misc-use-settings"])
    cb_use_settings.connect("toggled", set_from_checkbutton, settings, "misc-use-settings")
    grid.attach(cb_use_settings, 0, 0, 2, 1)

    cb_logo = Gtk.CheckButton.new_with_label(voc["disable-hyprland-logo"])
    cb_logo.set_property("halign", Gtk.Align.START)
    cb_logo.set_tooltip_text(voc["disable-hyprland-logo-tooltip"])
    cb_logo.set_active(settings["misc-disable_hyprland_logo"])
    cb_logo.connect("toggled", set_from_checkbutton, settings, "misc-disable_hyprland_logo")
    grid.attach(cb_logo, 0, 1, 1, 1)

    cb_splash = Gtk.CheckButton.new_with_label(voc["disable-splash-rendering"])
    cb_splash.set_property("halign", Gtk.Align.START)
    cb_splash.set_active(settings["misc-disable_splash_rendering"])
    cb_splash.connect("toggled", set_from_checkbutton, settings, "misc-disable_splash_rendering")
    grid.attach(cb_splash, 1, 1, 1, 1)

    cb_dpms_mouse = Gtk.CheckButton.new_with_label(voc["mouse-move-enables-dpms"])
    cb_dpms_mouse.set_property("halign", Gtk.Align.START)
    cb_dpms_mouse.set_tooltip_text(voc["mouse-move-enables-dpms-tooltip"])
    cb_dpms_mouse.set_active(settings["misc-mouse_move_enables_dpms"])
    cb_dpms_mouse.connect("toggled", set_from_checkbutton, settings, "misc-mouse_move_enables_dpms")
    grid.attach(cb_dpms_mouse, 0, 2, 1, 1)

    cb_dpms_key = Gtk.CheckButton.new_with_label(voc["key-press-enables-dpms"])
    cb_dpms_key.set_property("halign", Gtk.Align.START)
    cb_dpms_key.set_tooltip_text(voc["key-press-enables-dpms-tooltip"])
    cb_dpms_key.set_active(settings["misc-key_press_enables_dpms"])
    cb_dpms_key.connect("toggled", set_from_checkbutton, settings, "misc-key_press_enables_dpms")
    grid.attach(cb_dpms_key, 1, 2, 2, 1)

    cb_layers_hog = Gtk.CheckButton.new_with_label(voc["layers-hog-keyboard-focus"])
    cb_layers_hog.set_property("halign", Gtk.Align.START)
    cb_layers_hog.set_tooltip_text(voc["layers-hog-keyboard-focus-tooltip"])
    cb_layers_hog.set_active(settings["misc-layers_hog_keyboard_focus"])
    cb_layers_hog.connect("toggled", set_from_checkbutton, settings, "misc-layers_hog_keyboard_focus")
    grid.attach(cb_layers_hog, 0, 3, 1, 1)

    cb_focus_on_activate = Gtk.CheckButton.new_with_label(voc["focus-on-activate"])
    cb_focus_on_activate.set_property("halign", Gtk.Align.START)
    cb_focus_on_activate.set_tooltip_text(voc["focus-on-activate-tooltip"])
    cb_focus_on_activate.set_active(settings["misc-focus_on_activate"])
    cb_focus_on_activate.connect("toggled", set_from_checkbutton, settings, "misc-focus_on_activate")
    grid.attach(cb_focus_on_activate, 1, 3, 2, 1)

    cb_mouse_mon = Gtk.CheckButton.new_with_label(voc["mouse-move-focuses-monitor"])
    cb_mouse_mon.set_property("halign", Gtk.Align.START)
    cb_mouse_mon.set_tooltip_text(voc["mouse-move-focuses-monitor-tooltip"])
    cb_mouse_mon.set_active(settings["misc-mouse_move_focuses_monitor"])
    cb_mouse_mon.connect("toggled", set_from_checkbutton, settings, "misc-mouse_move_focuses_monitor")
    grid.attach(cb_mouse_mon, 1, 4, 2, 1)

    lbl = Gtk.Label.new("{}:".format(voc["vrr"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 5, 1, 1)

    combo_vrr = Gtk.ComboBoxText()
    combo_vrr.set_property("halign", Gtk.Align.START)
    combo_vrr.set_tooltip_text(voc["vrr-tooltip"])
    d = {0: voc["off"], 1: voc["on"], 2: voc["fullscreen-only"]}
    for item in [0, 1, 2]:
        combo_vrr.append(str(item), d[item])
    combo_vrr.set_active_id(str(settings["misc-vrr"]))
    combo_vrr.connect("changed", set_int_dict_key_from_combo, settings, "misc-vrr")
    grid.attach(combo_vrr, 1, 5, 1, 1)

    frame.show_all()

    return frame


def h_input_tab(settings, voc):
    frame = Gtk.Frame()
    frame.set_label("  {}: {}  ".format(voc["common"], voc["input-devices"]))
    frame.set_label_align(0.5, 0.5)
    frame.set_property("hexpand", True)
    grid = Gtk.Grid()
    frame.add(grid)
    grid.set_property("margin", 12)
    grid.set_column_spacing(6)
    grid.set_row_spacing(6)

    cb_keyboard_use_settings = Gtk.CheckButton.new_with_label(voc["use-these-settings"])
    cb_keyboard_use_settings.set_property("halign", Gtk.Align.START)
    cb_keyboard_use_settings.set_property("margin-bottom", 6)
    cb_keyboard_use_settings.set_tooltip_text(voc["hyprland-include-tooltip"])
    cb_keyboard_use_settings.set_active(settings["input-use-settings"])
    cb_keyboard_use_settings.connect("toggled", set_from_checkbutton, settings, "input-use-settings")
    grid.attach(cb_keyboard_use_settings, 0, 0, 2, 1)

    lbl = Gtk.Label.new("{}:".format(voc["kb-layout"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 1, 1, 1)

    entry_layout = Gtk.Entry()
    entry_layout.set_tooltip_text(voc["keyboard-layout-tooltip"])
    entry_layout.set_text(settings["input-kb_layout"])
    entry_layout.connect("changed", set_from_entry, settings, "input-kb_layout")
    grid.attach(entry_layout, 1, 1, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["kb-variant"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 2, 1, 1, 1)

    entry_variant = Gtk.Entry()
    entry_variant.set_tooltip_text(voc["keyboard-variant-tooltip"])
    entry_variant.set_text(settings["input-kb_variant"])
    entry_variant.connect("changed", set_from_entry, settings, "input-kb_variant")
    grid.attach(entry_variant, 3, 1, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["kb-model"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 2, 1, 1)

    entry_model = Gtk.Entry()
    entry_model.set_tooltip_text(voc["xkb-kb-model-tooltip"])
    entry_model.set_text(settings["input-kb_model"])
    entry_model.connect("changed", set_from_entry, settings, "input-kb_model")
    grid.attach(entry_model, 1, 2, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["kb-options"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 2, 2, 1, 1)

    entry_options = Gtk.Entry()
    entry_options.set_tooltip_text(voc["xkb-kb-options-tooltip"])
    entry_options.set_text(settings["input-kb_options"])
    entry_options.connect("changed", set_from_entry, settings, "input-kb_options")
    grid.attach(entry_options, 3, 2, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["kb-rules"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 4, 1, 1)

    entry_rules = Gtk.Entry()
    entry_rules.set_tooltip_text(voc["xkb-kb-rules-tooltip"])
    entry_rules.set_text(settings["input-kb_rules"])
    entry_rules.connect("changed", set_from_entry, settings, "input-kb_rules")
    grid.attach(entry_rules, 1, 4, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["kb-file"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 2, 4, 1, 1)

    entry_file = Gtk.Entry()
    entry_file.set_tooltip_text(voc["xkb-kb-file-tooltip"])
    entry_file.set_text(settings["input-kb_file"])
    entry_file.connect("changed", set_from_entry, settings, "input-kb_file")
    grid.attach(entry_file, 3, 4, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["keyboard-repeat-delay"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 5, 1, 1)

    sb_repeat_delay = Gtk.SpinButton.new_with_range(1, 6000, 1)
    sb_repeat_delay.set_value(settings["input-repeat_delay"])
    sb_repeat_delay.connect("value-changed", set_int_from_spinbutton, settings, "input-repeat_delay")
    sb_repeat_delay.set_tooltip_text(voc["keyboard-repeat-delay-tooltip"])
    grid.attach(sb_repeat_delay, 1, 5, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["keyboard-repeat-rate"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 2, 5, 1, 1)

    sb_repeat_rate = Gtk.SpinButton.new_with_range(1, 4000, 1)
    sb_repeat_rate.set_value(settings["input-repeat_rate"])
    sb_repeat_rate.connect("value-changed", set_int_from_spinbutton, settings, "input-repeat_rate")
    sb_repeat_rate.set_tooltip_text(voc["keyboard-repeat-rate-tooltip"])
    grid.attach(sb_repeat_rate, 3, 5, 1, 1)

    cb_numlock = Gtk.CheckButton.new_with_label(voc["numlock-by-default"])
    cb_numlock.set_property("halign", Gtk.Align.START)
    cb_numlock.set_property("margin-bottom", 6)
    cb_numlock.set_active(settings["input-numlock_by_default"])
    cb_numlock.connect("toggled", set_from_checkbutton, settings, "input-numlock_by_default")
    grid.attach(cb_numlock, 1, 7, 2, 1)

    lbl = Gtk.Label.new("{}:".format(voc["mouse-sensitivity"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 8, 1, 1)

    sb_m_sensitivity = Gtk.SpinButton.new_with_range(-1.0, 1.0, 0.1)
    sb_m_sensitivity.set_value(settings["input-sensitivity"])
    sb_m_sensitivity.connect("value-changed", set_from_spinbutton, settings, "input-sensitivity", 1)
    sb_m_sensitivity.set_tooltip_text(voc["scroll-factor-tooltip"])
    grid.attach(sb_m_sensitivity, 1, 8, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["acceleration-profile"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 2, 8, 1, 1)

    combo_aprofile = Gtk.ComboBoxText()
    combo_aprofile.set_tooltip_text(voc["acceleration-profile-tooltip"])
    combo_aprofile.append("", voc["default"])
    for item in ["flat", "adaptive"]:
        combo_aprofile.append(item, voc[item])
    combo_aprofile.set_active_id(settings["input-accel_profile"])
    combo_aprofile.connect("changed", set_dict_key_from_combo, settings, "input-accel_profile")
    grid.attach(combo_aprofile, 3, 8, 1, 1)

    cb_left_handed = Gtk.CheckButton.new_with_label(voc["left-handed"])
    cb_left_handed.set_tooltip_text(voc["left-handed-tooltip"])
    cb_left_handed.set_property("halign", Gtk.Align.START)
    cb_left_handed.set_active(settings["input-left_handed"])
    cb_left_handed.connect("toggled", set_from_checkbutton, settings, "input-left_handed")
    grid.attach(cb_left_handed, 1, 9, 1, 1)

    cb_left_handed = Gtk.CheckButton.new_with_label(voc["natural-scroll"])
    cb_left_handed.set_tooltip_text(voc["natural-scroll-tooltip"])
    cb_left_handed.set_property("halign", Gtk.Align.START)
    cb_left_handed.set_active(settings["input-natural_scroll"])
    cb_left_handed.connect("toggled", set_from_checkbutton, settings, "input-natural_scroll")
    grid.attach(cb_left_handed, 2, 9, 1, 1)

    cb_mouse_refocus = Gtk.CheckButton.new_with_label(voc["mouse-refocus"])
    cb_mouse_refocus.set_tooltip_text(voc["mouse-refocus-tooltip"])
    cb_mouse_refocus.set_property("halign", Gtk.Align.START)
    cb_mouse_refocus.set_active(settings["input-mouse_refocus"])
    cb_mouse_refocus.connect("toggled", set_from_checkbutton, settings, "input-mouse_refocus")
    grid.attach(cb_mouse_refocus, 3, 9, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["scroll-method"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 10, 1, 1)

    combo_scroll_method = Gtk.ComboBoxText()
    combo_scroll_method.set_tooltip_text(voc["scroll-method-tooltip"])
    for item in [("2fg", voc["two_finger"]), ("edge", voc["edge"]), ("on_button_down", voc["on_button_down"]),
                 ("no_scroll", voc["none"])]:
        combo_scroll_method.append(item[0], item[1])
    combo_scroll_method.set_active_id(settings["input-scroll_method"])
    combo_scroll_method.connect("changed", set_dict_key_from_combo, settings, "input-scroll_method")
    grid.attach(combo_scroll_method, 1, 10, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["scroll-button"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 2, 10, 1, 1)

    sb_scroll_button = Gtk.SpinButton.new_with_range(0, 512, 1)
    sb_scroll_button.set_value(settings["input-scroll_button"])
    sb_scroll_button.connect("value-changed", set_int_from_spinbutton, settings, "input-scroll_button")
    sb_scroll_button.set_tooltip_text(voc["scroll-button-tooltip"])
    grid.attach(sb_scroll_button, 3, 10, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["focus-follow-mouse"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 11, 1, 1)

    combo_focus = Gtk.ComboBoxText()
    # combo_focus.set_property("halign", Gtk.Align.START)
    combo_focus.set_tooltip_text(voc["focus-follow-mouse-tooltip"])
    for item in ["0", "1", "2", "3"]:
        combo_focus.append(item, item)
    combo_focus.set_active_id(str(settings["input-follow_mouse"]))
    combo_focus.connect("changed", set_int_dict_key_from_combo, settings, "input-follow_mouse")
    grid.attach(combo_focus, 1, 11, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["float-switch-override-focus"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 2, 11, 1, 1)

    combo_float_switch = Gtk.ComboBoxText()
    # combo_float_switch.set_property("halign", Gtk.Align.START)
    combo_float_switch.set_tooltip_text(voc["float-switch-override-focus-tooltip"])
    combo_float_switch.append("0", voc["disabled"])
    for item in ["1", "2"]:
        combo_float_switch.append(item, item)
    combo_float_switch.set_active_id(str(settings["input-float_switch_override_focus"]))
    combo_float_switch.connect("changed", set_int_dict_key_from_combo, settings, "input-float_switch_override_focus")
    grid.attach(combo_float_switch, 3, 11, 1, 1)

    frame.show_all()

    return frame


def pointer_tab(settings, voc):
    frame = Gtk.Frame()
    frame.set_label("  {}: {}  ".format(voc["common"], voc["pointer-device"]))
    frame.set_label_align(0.5, 0.5)
    frame.set_property("hexpand", True)
    grid = Gtk.Grid()
    frame.add(grid)
    grid.set_property("margin", 12)
    grid.set_column_spacing(6)
    grid.set_row_spacing(6)

    cb_pointer_use_settings = Gtk.CheckButton.new_with_label(voc["use-these-settings"])
    cb_pointer_use_settings.set_property("halign", Gtk.Align.START)
    cb_pointer_use_settings.set_property("margin-bottom", 6)
    cb_pointer_use_settings.set_tooltip_text(voc["pointer-device-include-tooltip"])
    cb_pointer_use_settings.set_active(settings["pointer-use-settings"])
    cb_pointer_use_settings.connect("toggled", set_from_checkbutton, settings, "pointer-use-settings")
    grid.attach(cb_pointer_use_settings, 0, 0, 2, 1)

    lbl = Gtk.Label.new("{}:".format(voc["device"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 1, 1, 1)

    combo_device = Gtk.ComboBoxText()
    combo_device.set_property("halign", Gtk.Align.START)
    combo_device.set_tooltip_text(voc["device-tooltip"])
    combo_device.append("", voc["all-of-type"])
    keyboards = list_inputs_by_type(input_type="pointer")
    for item in keyboards:
        combo_device.append(item, item)
    combo_device.set_active_id(settings["pointer-identifier"])
    combo_device.connect("changed", set_dict_key_from_combo, settings, "pointer-identifier")
    grid.attach(combo_device, 1, 1, 2, 1)

    lbl = Gtk.Label.new("{}:".format(voc["acceleration-profile"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 2, 1, 1)

    combo_aprofile = Gtk.ComboBoxText()
    combo_aprofile.set_property("halign", Gtk.Align.START)
    combo_aprofile.set_tooltip_text(voc["acceleration-profile-tooltip"])
    for item in ["flat", "adaptive"]:
        combo_aprofile.append(item, voc[item])
    combo_aprofile.set_active_id(settings["pointer-accel-profile"])
    combo_aprofile.connect("changed", set_dict_key_from_combo, settings, "pointer-accel-profile")
    grid.attach(combo_aprofile, 1, 2, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["acceleration"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 3, 1, 1)

    sb_acceleration = Gtk.SpinButton.new_with_range(-1, 1, 0.1)
    sb_acceleration.set_value(settings["pointer-pointer-accel"])
    sb_acceleration.connect("value-changed", set_from_spinbutton, settings, "pointer-pointer-accel", 1)
    sb_acceleration.set_tooltip_text(voc["acceleration-tooltip"])
    grid.attach(sb_acceleration, 1, 3, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["natural-scroll"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 4, 1, 1)

    combo_nscroll = Gtk.ComboBoxText()
    combo_nscroll.set_property("halign", Gtk.Align.START)
    combo_nscroll.set_tooltip_text(voc["natural-scroll-tooltip"])
    for item in ["disabled", "enabled"]:
        combo_nscroll.append(item, voc[item])
    combo_nscroll.set_active_id(settings["pointer-natural-scroll"])
    combo_nscroll.connect("changed", set_dict_key_from_combo, settings, "pointer-natural-scroll")
    grid.attach(combo_nscroll, 1, 4, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["scroll-factor"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 5, 1, 1)

    sb_sfactor = Gtk.SpinButton.new_with_range(0.1, 10, 0.1)
    sb_sfactor.set_value(settings["pointer-scroll-factor"])
    sb_sfactor.connect("value-changed", set_from_spinbutton, settings, "pointer-scroll-factor", 1)
    sb_sfactor.set_tooltip_text(voc["scroll-factor-tooltip"])
    grid.attach(sb_sfactor, 1, 5, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["left-handed"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 6, 1, 1)

    combo_left_handed = Gtk.ComboBoxText()
    combo_left_handed.set_property("halign", Gtk.Align.START)
    combo_left_handed.set_tooltip_text(voc["left-handed-tooltip"])
    for item in ["disabled", "enabled"]:
        combo_left_handed.append(item, voc[item])
    combo_left_handed.set_active_id(settings["pointer-left-handed"])
    combo_left_handed.connect("changed", set_dict_key_from_combo, settings, "pointer-left-handed")
    grid.attach(combo_left_handed, 1, 6, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["custom-field"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 7, 1, 1)

    entry_cname = Gtk.Entry()
    entry_cname.set_tooltip_text(voc["custom-field-name-tooltip"])
    entry_cname.set_placeholder_text(voc["name"])
    entry_cname.set_text(settings["pointer-custom-name"])
    entry_cname.connect("changed", set_from_entry, settings, "pointer-custom-name")
    grid.attach(entry_cname, 1, 7, 1, 1)

    entry_cname = Gtk.Entry()
    entry_cname.set_tooltip_text(voc["custom-field-value-tooltip"])
    entry_cname.set_placeholder_text(voc["value"])
    entry_cname.set_text(settings["pointer-custom-value"])
    entry_cname.connect("changed", set_from_entry, settings, "pointer-custom-value")
    grid.attach(entry_cname, 2, 7, 1, 1)

    frame.show_all()

    return frame


def touchpad_tab(settings, voc):
    frame = Gtk.Frame()
    frame.set_label("  {}: {}  ".format(voc["common"], voc["touchpad"]))
    frame.set_label_align(0.5, 0.5)
    frame.set_property("hexpand", True)
    grid = Gtk.Grid()
    frame.add(grid)
    grid.set_property("margin", 12)
    grid.set_column_spacing(6)
    grid.set_row_spacing(6)

    cb_touchpad_use_settings = Gtk.CheckButton.new_with_label(voc["use-these-settings"])
    cb_touchpad_use_settings.set_property("halign", Gtk.Align.START)
    cb_touchpad_use_settings.set_property("margin-bottom", 6)
    cb_touchpad_use_settings.set_tooltip_text(voc["touchpad-device-include-tooltip"])
    cb_touchpad_use_settings.set_active(settings["touchpad-use-settings"])
    cb_touchpad_use_settings.connect("toggled", set_from_checkbutton, settings, "touchpad-use-settings")
    grid.attach(cb_touchpad_use_settings, 0, 0, 2, 1)

    lbl = Gtk.Label.new("{}:".format(voc["device"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 1, 1, 1)

    combo_device = Gtk.ComboBoxText()
    combo_device.set_property("halign", Gtk.Align.START)
    combo_device.set_tooltip_text(voc["device-tooltip"])
    combo_device.append("", voc["all-of-type"])
    keyboards = list_inputs_by_type(input_type="touchpad")
    for item in keyboards:
        combo_device.append(item, item)
    combo_device.set_active_id(settings["touchpad-identifier"])
    combo_device.connect("changed", set_dict_key_from_combo, settings, "touchpad-identifier")
    grid.attach(combo_device, 1, 1, 3, 1)

    lbl = Gtk.Label.new("{}:".format(voc["acceleration-profile"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 2, 1, 1)

    combo_aprofile = Gtk.ComboBoxText()
    combo_aprofile.set_property("halign", Gtk.Align.START)
    combo_aprofile.set_tooltip_text(voc["acceleration-profile-tooltip"])
    for item in ["flat", "adaptive"]:
        combo_aprofile.append(item, voc[item])
    combo_aprofile.set_active_id(settings["touchpad-accel-profile"])
    combo_aprofile.connect("changed", set_dict_key_from_combo, settings, "touchpad-accel-profile")
    grid.attach(combo_aprofile, 1, 2, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["acceleration"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 3, 1, 1)

    sb_acceleration = Gtk.SpinButton.new_with_range(-1, 1, 0.1)
    sb_acceleration.set_value(settings["touchpad-pointer-accel"])
    sb_acceleration.connect("value-changed", set_from_spinbutton, settings, "touchpad-pointer-accel", 1)
    sb_acceleration.set_tooltip_text(voc["acceleration-tooltip"])
    grid.attach(sb_acceleration, 1, 3, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["natural-scroll"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 4, 1, 1)

    combo_nscroll = Gtk.ComboBoxText()
    combo_nscroll.set_property("halign", Gtk.Align.START)
    combo_nscroll.set_tooltip_text(voc["natural-scroll-tooltip"])
    for item in ["disabled", "enabled"]:
        combo_nscroll.append(item, voc[item])
    combo_nscroll.set_active_id(settings["touchpad-natural-scroll"])
    combo_nscroll.connect("changed", set_dict_key_from_combo, settings, "touchpad-natural-scroll")
    grid.attach(combo_nscroll, 1, 4, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["scroll-factor"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 5, 1, 1)

    sb_sfactor = Gtk.SpinButton.new_with_range(0.1, 10, 0.1)
    sb_sfactor.set_value(settings["touchpad-scroll-factor"])
    sb_sfactor.connect("value-changed", set_from_spinbutton, settings, "touchpad-scroll-factor", 1)
    sb_sfactor.set_tooltip_text(voc["scroll-factor-tooltip"])
    grid.attach(sb_sfactor, 1, 5, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["scroll-method"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 6, 1, 1)

    combo_scroll_method = Gtk.ComboBoxText()
    combo_scroll_method.set_property("halign", Gtk.Align.START)
    combo_scroll_method.set_tooltip_text(voc["scroll-method-tooltip"])
    for item in [("two_finger", voc["two_finger"]), ("edge", voc["edge"]), ("on_button_down", voc["on_button_down"]),
                 ("none", "None")]:
        combo_scroll_method.append(item[0], item[1])
    combo_scroll_method.set_active_id(settings["touchpad-scroll-method"])
    combo_scroll_method.connect("changed", set_dict_key_from_combo, settings, "touchpad-scroll-method")
    grid.attach(combo_scroll_method, 1, 6, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["left-handed"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 7, 1, 1)

    combo_left_handed = Gtk.ComboBoxText()
    combo_left_handed.set_property("halign", Gtk.Align.START)
    combo_left_handed.set_tooltip_text(voc["left-handed-tooltip"])
    for item in ["disabled", "enabled"]:
        combo_left_handed.append(item, voc[item])
    combo_left_handed.set_active_id(settings["touchpad-left-handed"])
    combo_left_handed.connect("changed", set_dict_key_from_combo, settings, "touchpad-left-handed")
    grid.attach(combo_left_handed, 1, 7, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["tap"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 2, 2, 1, 1)

    combo_tap = Gtk.ComboBoxText()
    combo_tap.set_property("halign", Gtk.Align.START)
    combo_tap.set_tooltip_text(voc["tap-tooltip"])
    for item in ["enabled", "disabled"]:
        combo_tap.append(item, voc[item])
    combo_tap.set_active_id(settings["touchpad-tap"])
    combo_tap.connect("changed", set_dict_key_from_combo, settings, "touchpad-tap")
    grid.attach(combo_tap, 3, 2, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["tap-button-map"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 2, 3, 1, 1)

    combo_tap_btn_map = Gtk.ComboBoxText()
    combo_tap_btn_map.set_property("halign", Gtk.Align.START)
    combo_tap_btn_map.set_tooltip_text(voc["tap-button-map-tooltip"])
    for item in ["lrm", "lmr"]:
        combo_tap_btn_map.append(item, item)
    combo_tap_btn_map.set_active_id(settings["touchpad-tap-button-map"])
    combo_tap_btn_map.connect("changed", set_dict_key_from_combo, settings, "touchpad-tap-button-map")
    grid.attach(combo_tap_btn_map, 3, 3, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["middle-emulation"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 2, 4, 1, 1)

    combo_memulation = Gtk.ComboBoxText()
    combo_memulation.set_property("halign", Gtk.Align.START)
    combo_memulation.set_tooltip_text(voc["middle-emulation-tooltip"])
    for item in ["enabled", "disabled"]:
        combo_memulation.append(item, voc[item])
    combo_memulation.set_active_id(settings["touchpad-middle-emulation"])
    combo_memulation.connect("changed", set_dict_key_from_combo, settings, "touchpad-middle-emulation")
    grid.attach(combo_memulation, 3, 4, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["drag"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 2, 5, 1, 1)

    combo_drag = Gtk.ComboBoxText()
    combo_drag.set_property("halign", Gtk.Align.START)
    combo_drag.set_tooltip_text(voc["drag-tooltip"])
    for item in ["enabled", "disabled"]:
        combo_drag.append(item, voc[item])
    combo_drag.set_active_id(settings["touchpad-drag"])
    combo_drag.connect("changed", set_dict_key_from_combo, settings, "touchpad-drag")
    grid.attach(combo_drag, 3, 5, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["drag-lock"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 2, 6, 1, 1)

    combo_drag_lock = Gtk.ComboBoxText()
    combo_drag_lock.set_property("halign", Gtk.Align.START)
    combo_drag_lock.set_tooltip_text(voc["drag-lock-tooltip"])
    for item in ["disabled", "enabled"]:
        combo_drag_lock.append(item, voc[item])
    combo_drag_lock.set_active_id(settings["touchpad-drag-lock"])
    combo_drag_lock.connect("changed", set_dict_key_from_combo, settings, "touchpad-drag-lock")
    grid.attach(combo_drag_lock, 3, 6, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["dwt"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 2, 7, 1, 1)

    combo_dwt = Gtk.ComboBoxText()
    combo_dwt.set_property("halign", Gtk.Align.START)
    combo_dwt.set_tooltip_text(voc["dwt-tooltip"])
    for item in ["enabled", "disabled"]:
        combo_dwt.append(item, voc[item])
    combo_dwt.set_active_id(settings["touchpad-dwt"])
    combo_dwt.connect("changed", set_dict_key_from_combo, settings, "touchpad-dwt")
    grid.attach(combo_dwt, 3, 7, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["custom-field"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 8, 1, 1)

    entry_cname = Gtk.Entry()
    entry_cname.set_tooltip_text(voc["custom-field-name-tooltip"])
    entry_cname.set_placeholder_text(voc["name"])
    entry_cname.set_text(settings["touchpad-custom-name"])
    entry_cname.connect("changed", set_from_entry, settings, "touchpad-custom-name")
    grid.attach(entry_cname, 1, 8, 1, 1)

    entry_cname = Gtk.Entry()
    entry_cname.set_tooltip_text(voc["custom-field-value-tooltip"])
    entry_cname.set_placeholder_text(voc["value"])
    entry_cname.set_text(settings["touchpad-custom-value"])
    entry_cname.connect("changed", set_from_entry, settings, "touchpad-custom-value")
    grid.attach(entry_cname, 2, 8, 2, 1)

    frame.show_all()

    return frame


def h_touchpad_tab(settings, voc):
    frame = Gtk.Frame()
    frame.set_label("  {}: {}  ".format(voc["common"], voc["touchpad"]))
    frame.set_label_align(0.5, 0.5)
    frame.set_property("hexpand", True)
    grid = Gtk.Grid()
    frame.add(grid)
    grid.set_property("margin", 12)
    grid.set_column_spacing(6)
    grid.set_row_spacing(6)

    cb_touchpad_use_settings = Gtk.CheckButton.new_with_label(voc["use-these-settings"])
    cb_touchpad_use_settings.set_property("halign", Gtk.Align.START)
    cb_touchpad_use_settings.set_property("margin-bottom", 6)
    cb_touchpad_use_settings.set_tooltip_text(voc["hyprland-include-tooltip"])
    cb_touchpad_use_settings.set_active(settings["touchpad-use-settings"])
    cb_touchpad_use_settings.connect("toggled", set_from_checkbutton, settings, "touchpad-use-settings")
    grid.attach(cb_touchpad_use_settings, 0, 0, 2, 1)

    cb_dwt = Gtk.CheckButton.new_with_label(voc["disable-while-typing"])
    cb_dwt.set_property("halign", Gtk.Align.START)
    cb_dwt.set_tooltip_text(voc["dwt-tooltip"])
    cb_dwt.set_active(settings["touchpad-disable_while_typing"])
    cb_dwt.connect("toggled", set_from_checkbutton, settings, "touchpad-disable_while_typing")
    grid.attach(cb_dwt, 1, 1, 1, 1)

    cb_nscroll = Gtk.CheckButton.new_with_label(voc["natural-scroll"])
    cb_nscroll.set_property("halign", Gtk.Align.START)
    cb_nscroll.set_tooltip_text(voc["natural-scroll-tooltip"])
    cb_nscroll.set_active(settings["touchpad-natural_scroll"])
    cb_nscroll.connect("toggled", set_from_checkbutton, settings, "touchpad-natural_scroll")
    grid.attach(cb_nscroll, 1, 2, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["scroll-factor"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 3, 1, 1)

    sb_sfactor = Gtk.SpinButton.new_with_range(0.1, 10, 0.1)
    sb_sfactor.set_value(settings["touchpad-scroll_factor"])
    sb_sfactor.connect("value-changed", set_from_spinbutton, settings, "touchpad-scroll_factor", 1)
    sb_sfactor.set_tooltip_text(voc["scroll-factor-tooltip"])
    grid.attach(sb_sfactor, 1, 3, 1, 1)

    cb_memulation = Gtk.CheckButton.new_with_label(voc["middle-emulation"])
    cb_memulation.set_property("halign", Gtk.Align.START)
    cb_memulation.set_tooltip_text(voc["middle-emulation-tooltip"])
    cb_memulation.set_active(settings["touchpad-middle_button_emulation"])
    cb_memulation.connect("toggled", set_from_checkbutton, settings, "touchpad-middle_button_emulation")
    grid.attach(cb_memulation, 1, 4, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["tap-button-map"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 5, 1, 1)

    combo_tap_btn_map = Gtk.ComboBoxText()
    combo_tap_btn_map.set_property("halign", Gtk.Align.START)
    combo_tap_btn_map.set_tooltip_text(voc["tap-button-map-tooltip"])
    for item in ["lrm", "lmr"]:
        combo_tap_btn_map.append(item, item)
    combo_tap_btn_map.set_active_id(settings["touchpad-tap_button_map"])
    combo_tap_btn_map.connect("changed", set_dict_key_from_combo, settings, "touchpad-tap_button_map")
    grid.attach(combo_tap_btn_map, 1, 5, 1, 1)

    cb_clickfinger = Gtk.CheckButton.new_with_label(voc["clickfinger-behavior"])
    cb_clickfinger.set_property("halign", Gtk.Align.START)
    cb_clickfinger.set_tooltip_text(voc["clickfinger-behavior-tooltip"])
    cb_clickfinger.set_active(settings["touchpad-clickfinger_behavior"])
    cb_clickfinger.connect("toggled", set_from_checkbutton, settings, "touchpad-clickfinger_behavior")
    grid.attach(cb_clickfinger, 1, 6, 1, 1)

    cb_tap2click = Gtk.CheckButton.new_with_label(voc["tap-to-click"])
    cb_tap2click.set_property("halign", Gtk.Align.START)
    cb_tap2click.set_tooltip_text(voc["tap-to-click-tooltip"])
    cb_tap2click.set_active(settings["touchpad-tap-to-click"])
    cb_tap2click.connect("toggled", set_from_checkbutton, settings, "touchpad-tap-to-click")
    grid.attach(cb_tap2click, 1, 7, 1, 1)

    cb_drag_lock = Gtk.CheckButton.new_with_label(voc["drag-lock"])
    cb_drag_lock.set_property("halign", Gtk.Align.START)
    cb_drag_lock.set_tooltip_text(voc["drag-lock-tooltip"])
    cb_drag_lock.set_active(settings["touchpad-drag_lock"])
    cb_drag_lock.connect("toggled", set_from_checkbutton, settings, "touchpad-drag_lock")
    grid.attach(cb_drag_lock, 1, 8, 1, 1)

    cb_tap_and_drag = Gtk.CheckButton.new_with_label(voc["tap-and-drag"])
    cb_tap_and_drag.set_property("halign", Gtk.Align.START)
    cb_tap_and_drag.set_tooltip_text(voc["tap-and-drag-tooltip"])
    cb_tap_and_drag.set_active(settings["touchpad-tap-and-drag"])
    cb_tap_and_drag.connect("toggled", set_from_checkbutton, settings, "touchpad-tap-and-drag")
    grid.attach(cb_tap_and_drag, 1, 9, 1, 1)

    frame.show_all()

    return frame


def lockscreen_tab(settings, voc):
    frame = Gtk.Frame()
    frame.set_label("  {}: {}  ".format(voc["common"], voc["idle-lock-screen"]))
    frame.set_label_align(0.5, 0.5)
    frame.set_property("hexpand", True)
    grid = Gtk.Grid()
    frame.add(grid)
    grid.set_property("margin", 6)
    grid.set_column_spacing(6)
    grid.set_row_spacing(6)

    cb_lockscreen_use_settings = Gtk.CheckButton.new_with_label(voc["use-these-settings"])
    cb_lockscreen_use_settings.set_property("halign", Gtk.Align.START)
    cb_lockscreen_use_settings.set_property("margin-bottom", 2)
    cb_lockscreen_use_settings.set_tooltip_text(voc["lock-screen-include-tooltip"])
    cb_lockscreen_use_settings.set_active(settings["lockscreen-use-settings"])
    cb_lockscreen_use_settings.connect("toggled", set_idle_use_from_checkbutton, settings)
    grid.attach(cb_lockscreen_use_settings, 0, 0, 2, 1)

    lbl = Gtk.Label()
    lbl.set_markup("<b>{}</b>".format(voc["lock-screen"]))
    lbl.set_property("halign", Gtk.Align.START)
    grid.attach(lbl, 0, 1, 2, 1)

    lbl = Gtk.Label.new("{}:".format(voc["locker"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 2, 1, 1)

    combo_locker = Gtk.ComboBoxText()
    combo_locker.set_tooltip_text(voc["locker-tooltip"])
    if not os.getenv("HYPRLAND_INSTANCE_SIGNATURE"):
        combo_locker.append("gtklock", "gtklock")
    if is_command("swaylock"):
        combo_locker.append("swaylock", "swaylock")
    else:
        combo_locker.set_tooltip_text(voc["locker-tooltip2"])
    combo_locker.set_active_id(settings["lockscreen-locker"])
    combo_locker.connect("changed", set_dict_key_from_combo, settings, "lockscreen-locker")
    grid.attach(combo_locker, 1, 2, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["backgrounds"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 3, 1, 1)

    combo_background = Gtk.ComboBoxText()
    combo_background.set_tooltip_text(voc["random-wallpaper-source"])
    combo_background.append("unsplash", voc["unsplash"])
    combo_background.append("local", voc["local"])
    combo_background.set_active_id(settings["lockscreen-background-source"])
    combo_background.connect("changed", set_dict_key_from_combo, settings, "lockscreen-background-source")
    grid.attach(combo_background, 1, 3, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["own-command"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 4, 1, 1)

    entry_lock_cmd = Gtk.Entry()
    entry_lock_cmd.set_placeholder_text(voc["leave-blank-to-use-above"])
    lbl.set_property("valign", Gtk.Align.CENTER)
    lbl.set_property("vexpand", False)
    entry_lock_cmd.set_width_chars(24)
    entry_lock_cmd.set_text(settings["lockscreen-custom-cmd"])
    entry_lock_cmd.set_tooltip_text(voc["own-command-tooltip"])
    grid.attach(entry_lock_cmd, 1, 4, 1, 1)
    entry_lock_cmd.connect("changed", set_custom_cmd_from_entry, settings, "lockscreen-custom-cmd",
                           [combo_locker, combo_background])

    lbl = Gtk.Label.new("{}:".format(voc["timeout"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 5, 1, 1)

    sb_lock_timeout = Gtk.SpinButton.new_with_range(5, 86400, 1)
    sb_lock_timeout.set_property("halign", Gtk.Align.START)
    sb_lock_timeout.set_value(settings["lockscreen-timeout"])
    # We need to validate this, and `sb_sleep_timeout` as well, so let's connect both when both already defined
    sb_lock_timeout.set_tooltip_text(voc["timeout-tooltip"])
    grid.attach(sb_lock_timeout, 1, 5, 1, 1)

    lbl = Gtk.Label()
    lbl.set_markup("<b>{}</b>".format(voc["idle-settings"]))
    lbl.set_property("halign", Gtk.Align.START)
    lbl.set_property("margin-top", 6)
    grid.attach(lbl, 0, 6, 2, 1)

    lbl = Gtk.Label.new("{}:".format(voc["sleep-command"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 7, 1, 1)

    entry_sleep_cmd = Gtk.Entry()
    entry_sleep_cmd.set_max_width_chars(22)
    entry_sleep_cmd.set_text(settings["sleep-cmd"])
    grid.attach(entry_sleep_cmd, 1, 7, 1, 1)
    entry_sleep_cmd.connect("changed", set_from_entry, settings, "sleep-cmd")

    lbl = Gtk.Label.new("{}:".format(voc["timeout"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 8, 1, 1)

    sb_sleep_timeout = Gtk.SpinButton.new_with_range(10, 86400, 1)
    sb_sleep_timeout.set_property("halign", Gtk.Align.START)
    sb_sleep_timeout.set_value(settings["sleep-timeout"])

    # Sleep timeout must be longer than lock timeout; we'll validate both values
    sb_sleep_timeout.connect("value-changed", set_sleep_timeout, sb_lock_timeout, settings, "sleep-timeout")
    sb_lock_timeout.connect("value-changed", set_timeouts, sb_sleep_timeout, settings, "lockscreen-timeout")

    sb_sleep_timeout.set_tooltip_text(voc["sleep-timeout-tooltip"])
    grid.attach(sb_sleep_timeout, 1, 8, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["resume-command"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 9, 1, 1)

    entry_resume_cmd = Gtk.Entry()
    entry_resume_cmd.set_text(settings["resume-cmd"])
    grid.attach(entry_resume_cmd, 1, 9, 1, 1)
    entry_resume_cmd.connect("changed", set_from_entry, settings, "resume-cmd")

    lbl = Gtk.Label.new("{}:".format(voc["after-resume"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 10, 1, 1)

    entry_after_resume = Gtk.Entry()
    entry_after_resume.set_text(settings["after-resume"])
    grid.attach(entry_after_resume, 1, 10, 1, 1)
    entry_after_resume.connect("changed", set_from_entry, settings, "after-resume")

    defaults_btn = Gtk.Button.new_with_label(voc["restore-defaults"])
    defaults_btn.set_property("margin-top", 6)
    defaults_btn.set_property("halign", Gtk.Align.START)
    defaults_btn.set_tooltip_text(voc["restore-defaults-tooltip"])
    if os.getenv("SWAYSOCK"):
        defaults_btn.connect("clicked", restore_defaults, {entry_sleep_cmd: 'swaymsg "output * dpms off"',
                                                           entry_resume_cmd: 'swaymsg "output * dpms on"',
                                                           entry_after_resume: 'swaymsg "output * enable"'})
    elif os.getenv("HYPRLAND_INSTANCE_SIGNATURE"):
        defaults_btn.connect("clicked", restore_defaults, {entry_sleep_cmd: 'systemctl suspend'})

    grid.attach(defaults_btn, 1, 6, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["before-sleep"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 11, 1, 1)

    entry_b4_sleep = Gtk.Entry()
    entry_b4_sleep.set_width_chars(24)
    entry_b4_sleep.set_text(settings["before-sleep"])
    entry_b4_sleep.set_tooltip_text(voc["before-sleep-tooltip"])
    grid.attach(entry_b4_sleep, 1, 11, 1, 1)
    entry_b4_sleep.connect("changed", set_from_entry, settings, "before-sleep")

    lbl = Gtk.Label()
    lbl.set_markup("<b>{}</b>".format(voc["local-background-paths"]))
    lbl.set_property("halign", Gtk.Align.START)
    grid.attach(lbl, 2, 1, 4, 1)

    bcg_window = Gtk.ScrolledWindow.new(None, None)
    bcg_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.ALWAYS)
    bcg_window.set_propagate_natural_width(True)

    grid.attach(bcg_window, 2, 2, 4, 4)
    bcg_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
    bcg_window.add(bcg_box)

    paths = list_background_dirs()
    # Preselect all in none preselected yet
    if not settings["background-dirs-once-set"] and not settings["background-dirs"]:
        settings["background-dirs"] = paths
        settings["background-dirs-once-set"] = True

    for p in paths:
        cb = Gtk.CheckButton.new_with_label(p)
        cb.set_active(p in settings["background-dirs"])
        cb.connect("toggled", on_folder_btn_toggled, settings)
        bcg_box.pack_start(cb, False, False, 0)

    box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 6)
    grid.attach(box, 2, 6, 3, 1)

    cb_custom_path = Gtk.CheckButton.new_with_label(voc["own-path"])
    cb_custom_path.set_active(settings["backgrounds-use-custom-path"])
    cb_custom_path.connect("toggled", set_key_from_checkbox, settings, "backgrounds-use-custom-path")
    box.pack_start(cb_custom_path, False, False, 0)

    fc_btn = Gtk.FileChooserButton.new(voc["select-folder"], Gtk.FileChooserAction.SELECT_FOLDER)
    fc_btn.set_tooltip_text(voc["select-folder-tooltip"])
    if settings["backgrounds-custom-path"]:
        fc_btn.set_current_folder(settings["backgrounds-custom-path"])
    fc_btn.connect("file-set", on_custom_folder_selected, cb_custom_path, settings)
    box.pack_start(fc_btn, False, False, 0)

    if not fc_btn.get_filename():
        cb_custom_path.set_sensitive(False)

    lbl = Gtk.Label()
    lbl.set_markup("<b>{}</b>".format(voc["unsplash-random-image"]))
    lbl.set_property("halign", Gtk.Align.START)
    lbl.set_property("margin-top", 6)
    grid.attach(lbl, 2, 8, 4, 1)

    sb_us_width = Gtk.SpinButton.new_with_range(640, 7680, 1)
    sb_us_width.set_value(settings["unsplash-width"])
    sb_us_width.connect("value-changed", set_int_from_spinbutton, settings, "unsplash-width")
    sb_us_width.set_tooltip_text(voc["desired-wallpaper-width"])
    grid.attach(sb_us_width, 2, 9, 1, 1)

    lbl = Gtk.Label.new("x")
    grid.attach(lbl, 3, 9, 1, 1)

    sb_us_width = Gtk.SpinButton.new_with_range(480, 4320, 1)
    sb_us_width.set_value(settings["unsplash-height"])
    sb_us_width.connect("value-changed", set_int_from_spinbutton, settings, "unsplash-height")
    sb_us_width.set_tooltip_text(voc["desired-wallpaper-height"])
    grid.attach(sb_us_width, 4, 9, 1, 1)

    box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 6)
    grid.attach(box, 2, 10, 3, 1)
    lbl = Gtk.Label.new("{}:".format(voc["keywords"]))
    lbl.set_property("halign", Gtk.Align.START)
    box.pack_start(lbl, False, False, 0)

    entry_us_keywords = Gtk.Entry()
    entry_us_keywords.set_tooltip_text(voc["keywords-tooltip"])
    entry_us_keywords.set_text(",".join(settings["unsplash-keywords"]))
    entry_us_keywords.connect("changed", set_keywords_from_entry, settings)
    box.pack_start(entry_us_keywords, True, True, 0)

    # WARNING about 'swayidle' in sway config
    config_home = os.getenv('XDG_CONFIG_HOME') if os.getenv('XDG_CONFIG_HOME') else os.path.join(
        os.getenv("HOME"), ".config/")
    sway_config = os.path.join(config_home, "sway", "config")
    if os.path.isfile(sway_config):
        lines = load_text_file(sway_config).splitlines()
        for line in lines:
            if not line.startswith("#") and "swayidle" in line:
                lbl = Gtk.Label()
                lbl.set_markup(
                    '<span foreground="red"><b>To use these settings,'
                    ' remove \'swayidle\' from your sway config file!</b></span>')
                lbl.set_property("margin-top", 10)
                grid.attach(lbl, 0, 11, 7, 1)
                cb_lockscreen_use_settings.set_active(False)
                # Prevent settings from exporting
                cb_lockscreen_use_settings.set_sensitive(False)
                break

    frame.show_all()

    return frame


def gtklock_tab(settings, voc):
    frame = Gtk.Frame()
    frame.set_label("  {}: Gtklock  ".format(voc["common"]))
    frame.set_label_align(0.5, 0.5)
    frame.set_property("hexpand", True)
    grid = Gtk.Grid()
    frame.add(grid)
    grid.set_property("margin", 6)
    grid.set_column_spacing(6)
    grid.set_row_spacing(6)

    lbl = Gtk.Label()
    lbl.set_markup("<b>{}</b>".format(voc["modules"]))
    lbl.set_property("halign", Gtk.Align.START)
    grid.attach(lbl, 0, 2, 1, 1)

    box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
    grid.attach(box, 1, 2, 1, 1)
    cb_gtklock_userinfo = Gtk.CheckButton.new_with_label("userinfo")
    cb_gtklock_userinfo.set_active(settings["gtklock-userinfo"])
    cb_gtklock_userinfo.connect("toggled", set_key_from_checkbox, settings, "gtklock-userinfo")
    cb_gtklock_userinfo.set_tooltip_text(voc["userinfo-tooltip"])
    box.pack_start(cb_gtklock_userinfo, False, False, 0)
    # Disable check button if module not installed
    if not gtklock_module_path("userinfo"):
        cb_gtklock_userinfo.set_active(False)
        cb_gtklock_userinfo.set_sensitive(False)

    cb_gtklock_powerbar = Gtk.CheckButton.new_with_label("powerbar")
    cb_gtklock_powerbar.set_active(settings["gtklock-powerbar"])
    cb_gtklock_powerbar.connect("toggled", set_key_from_checkbox, settings, "gtklock-powerbar")
    cb_gtklock_powerbar.set_tooltip_text(voc["powerbar-tooltip"])
    box.pack_start(cb_gtklock_powerbar, False, False, 0)

    if not gtklock_module_path("powerbar"):
        cb_gtklock_powerbar.set_active(False)
        cb_gtklock_powerbar.set_sensitive(False)

    cb_gtklock_layerctl = Gtk.CheckButton.new_with_label("playerctl")
    cb_gtklock_layerctl.set_active(settings["gtklock-playerctl"])
    cb_gtklock_layerctl.connect("toggled", set_key_from_checkbox, settings, "gtklock-playerctl")
    cb_gtklock_layerctl.set_tooltip_text(voc["playerctl-tooltip"])
    box.pack_start(cb_gtklock_layerctl, False, False, 0)

    if not gtklock_module_path("playerctl"):
        cb_gtklock_layerctl.set_active(False)
        cb_gtklock_layerctl.set_sensitive(False)

    lbl = Gtk.Label()
    lbl.set_markup("<b>{}</b>".format(voc["powerbar"]))
    lbl.set_property("halign", Gtk.Align.START)
    grid.attach(lbl, 0, 3, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["reboot"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 4, 1, 1)

    entry_layout = Gtk.Entry()
    entry_layout.set_tooltip_text(voc["reboot-tooltip"])
    entry_layout.set_text(settings["gtklock-reboot-command"])
    entry_layout.connect("changed", set_from_entry, settings, "gtklock-reboot-command")
    grid.attach(entry_layout, 1, 4, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["power-off"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 5, 1, 1)

    entry_gtklock_poweroff_command = Gtk.Entry()
    entry_gtklock_poweroff_command.set_tooltip_text(voc["power-off-tooltip"])
    entry_gtklock_poweroff_command.set_text(settings["gtklock-poweroff-command"])
    entry_gtklock_poweroff_command.connect("changed", set_from_entry, settings, "gtklock-poweroff-command")
    grid.attach(entry_gtklock_poweroff_command, 1, 5, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["suspend"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 6, 1, 1)

    entry_gtklock_suspend_command = Gtk.Entry()
    entry_gtklock_suspend_command.set_tooltip_text(voc["suspend-tooltip"])
    entry_gtklock_suspend_command.set_text(settings["gtklock-suspend-command"])
    entry_gtklock_suspend_command.connect("changed", set_from_entry, settings, "gtklock-suspend-command")
    grid.attach(entry_gtklock_suspend_command, 1, 6, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["logout"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 7, 1, 1)

    entry_gtklock_logout_command = Gtk.Entry()
    entry_gtklock_logout_command.set_tooltip_text(voc["logout-tooltip"])
    entry_gtklock_logout_command.set_text(settings["gtklock-logout-command"])
    entry_gtklock_logout_command.connect("changed", set_from_entry, settings, "gtklock-logout-command")
    grid.attach(entry_gtklock_logout_command, 1, 7, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["switch-user"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 8, 1, 1)

    entry_gtklock_switch_user_command = Gtk.Entry()
    entry_gtklock_switch_user_command.set_tooltip_text(voc["switch-user-tooltip"])
    entry_gtklock_switch_user_command.set_text(settings["gtklock-userswitch-command"])
    entry_gtklock_switch_user_command.connect("changed", set_from_entry, settings, "gtklock-userswitch-command")
    grid.attach(entry_gtklock_switch_user_command, 1, 8, 1, 1)

    lbl = Gtk.Label()
    lbl.set_markup("<b>{}</b>".format(voc["other"]))
    lbl.set_property("halign", Gtk.Align.START)
    grid.attach(lbl, 0, 9, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["time-format"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 10, 1, 1)

    entry_time_format = Gtk.Entry()
    entry_time_format.set_tooltip_text(voc["time-format-tooltip"])
    entry_time_format.set_text(settings["gtklock-time-format"])
    entry_time_format.connect("changed", set_from_entry, settings, "gtklock-time-format")
    grid.attach(entry_time_format, 1, 10, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["idle-timeout"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 11, 1, 1)

    sb_gtklock_idle_timeout = Gtk.SpinButton.new_with_range(5, 3600, 1)
    sb_gtklock_idle_timeout.set_value(settings["gtklock-idle-timeout"])
    sb_gtklock_idle_timeout.connect("value-changed", set_int_from_spinbutton, settings, "gtklock-idle-timeout")
    sb_gtklock_idle_timeout.set_tooltip_text(voc["idle-timeout-tooltip"])
    grid.attach(sb_gtklock_idle_timeout, 1, 11, 1, 1)

    cb_disable_input_inhibitor = Gtk.CheckButton.new_with_label(voc["disable-input-inhibitor"])
    cb_disable_input_inhibitor.set_active(settings["gtklock-disable-input-inhibitor"])
    cb_disable_input_inhibitor.connect("toggled", set_key_from_checkbox, settings, "gtklock-disable-input-inhibitor")
    cb_disable_input_inhibitor.set_tooltip_text(voc["disable-input-inhibitor-tooltip"])
    grid.attach(cb_disable_input_inhibitor, 1, 12, 1, 1)

    frame.show_all()

    return frame


def drawer_tab(preset, preset_name, outputs, voc):
    frame = Gtk.Frame()
    frame.set_label("  {}: {}  ".format(preset_name, voc["app-drawer"]))
    frame.set_label_align(0.5, 0.5)
    frame.set_property("hexpand", True)
    grid = Gtk.Grid()
    frame.add(grid)
    grid.set_property("margin", 12)
    grid.set_column_spacing(6)
    grid.set_row_spacing(6)

    cb_drawer_on = Gtk.CheckButton.new_with_label(voc["app-drawer-on"])
    cb_drawer_on.set_active(preset["launcher-on"])
    cb_drawer_on.connect("toggled", set_from_checkbutton, preset, "launcher-on")
    grid.attach(cb_drawer_on, 0, 0, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["columns"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 1, 1, 1)

    sb_columns = Gtk.SpinButton.new_with_range(1, 9, 1)
    sb_columns.set_value(preset["launcher-columns"])
    sb_columns.connect("value-changed", set_int_from_spinbutton, preset, "launcher-columns")
    sb_columns.set_tooltip_text(voc["app-drawer-columns-tooltip"])
    grid.attach(sb_columns, 1, 1, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["icon-size"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 2, 1, 1)

    sb_icon_size = Gtk.SpinButton.new_with_range(8, 256, 1)
    sb_icon_size.set_value(preset["launcher-icon-size"])
    sb_icon_size.connect("value-changed", set_int_from_spinbutton, preset, "launcher-icon-size")
    sb_icon_size.set_tooltip_text(voc["app-icon-size-tooltip"])
    grid.attach(sb_icon_size, 1, 2, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["file-search-columns"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 3, 1, 1)

    sb_fs_columns = Gtk.SpinButton.new_with_range(1, 9, 1)
    sb_fs_columns.set_value(preset["launcher-file-search-columns"])
    sb_fs_columns.connect("value-changed", set_int_from_spinbutton, preset, "launcher-file-search-columns")
    sb_fs_columns.set_tooltip_text(voc["file-search-columns-tooltip"])
    grid.attach(sb_fs_columns, 1, 3, 1, 1)

    cb_search_files = Gtk.CheckButton.new_with_label(voc["search-files"])
    cb_search_files.set_active(preset["launcher-search-files"])
    cb_search_files.connect("toggled", set_from_checkbutton, preset, "launcher-search-files")
    grid.attach(cb_search_files, 2, 3, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["gtk-theme"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 4, 1, 1)

    combo_gtk_theme = Gtk.ComboBoxText()
    combo_gtk_theme.append("", voc["default"])

    for name in get_theme_names():
        combo_gtk_theme.append(name, name)

    combo_gtk_theme.set_active_id(preset["launcher-gtk-theme"])
    combo_gtk_theme.connect("changed", set_dict_key_from_combo, preset, "launcher-gtk-theme")
    grid.attach(combo_gtk_theme, 1, 4, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["icon-theme"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 5, 1, 1)

    # dict: {"theme_name": "folder_name"}
    theme_names = get_icon_themes()
    names = []
    for key in theme_names:
        names.append(key)

    combo_gtk_icon_theme = Gtk.ComboBoxText()
    combo_gtk_icon_theme.append("", voc["default"])
    for name in sorted(names, key=str.casefold):
        combo_gtk_icon_theme.append(name, name)
    combo_gtk_icon_theme.set_active_id(preset["launcher-gtk-icon-theme"])
    combo_gtk_icon_theme.connect("changed", set_dict_key_from_combo, preset, "launcher-gtk-icon-theme")
    grid.attach(combo_gtk_icon_theme, 1, 5, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["output"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 6, 1, 1)

    combo_outputs = Gtk.ComboBoxText()
    combo_outputs.set_property("halign", Gtk.Align.START)
    grid.attach(combo_outputs, 1, 6, 1, 1)
    combo_outputs.append("Any", voc["any"])
    for item in outputs:
        combo_outputs.append(item, item)
    combo_outputs.set_active_id(preset["launcher-output"])
    combo_outputs.connect("changed", set_dict_key_from_combo, preset, "launcher-output")

    lbl = Gtk.Label.new("{}:".format(voc["pb-icon-size"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 7, 1, 1)

    sb_pb_icon_size = Gtk.SpinButton.new_with_range(8, 256, 1)
    sb_pb_icon_size.set_value(preset["pb-size"])
    sb_pb_icon_size.connect("value-changed", set_int_from_spinbutton, preset, "pb-size")
    sb_pb_icon_size.set_tooltip_text(voc["app-icon-size-tooltip"])
    grid.attach(sb_pb_icon_size, 1, 7, 1, 1)

    cb_categories = Gtk.CheckButton.new_with_label(voc["show-category-buttons"])
    cb_categories.set_tooltip_text(voc["show-category-buttons-tooltip"])
    cb_categories.set_active(preset["launcher-categories"])
    cb_categories.connect("toggled", set_from_checkbutton, preset, "launcher-categories")
    grid.attach(cb_categories, 0, 8, 2, 1)

    cb_resident = Gtk.CheckButton.new_with_label(voc["keep-resident"])
    cb_resident.set_tooltip_text(voc["keep-resident-tooltip"])
    cb_resident.set_active(preset["launcher-resident"])
    cb_resident.connect("toggled", set_from_checkbutton, preset, "launcher-resident")
    grid.attach(cb_resident, 0, 9, 2, 1)

    cb_super = Gtk.CheckButton.new_with_label(voc["open-on-super"])
    cb_super.set_tooltip_text(voc["open-on-super-tooltip"])
    cb_super.set_active(preset["launcher-super-key"])
    cb_super.connect("toggled", set_from_checkbutton, preset, "launcher-super-key")
    grid.attach(cb_super, 0, 10, 2, 1)

    cb_overlay = Gtk.CheckButton.new_with_label(voc["open-on-overlay"])
    cb_overlay.set_tooltip_text(voc["open-on-overlay-tooltip"])
    cb_overlay.set_active(preset["launcher-overlay"])
    cb_overlay.connect("toggled", set_from_checkbutton, preset, "launcher-overlay")
    grid.attach(cb_overlay, 0, 11, 2, 1)

    cb_force_theme = Gtk.CheckButton.new_with_label(voc["run-with-gtk-theme"])
    cb_force_theme.set_tooltip_text(voc["run-with-gtk-theme-tooltip"])
    cb_force_theme.set_active(preset["launcher-force-theme"])
    cb_force_theme.connect("toggled", set_from_checkbutton, preset, "launcher-force-theme")
    grid.attach(cb_force_theme, 2, 8, 2, 1)

    cb_run_through_compositor = Gtk.CheckButton.new_with_label(voc["run-through-compositor"])
    cb_run_through_compositor.set_tooltip_text(voc["run-through-compositor-tooltip"])
    cb_run_through_compositor.set_active(preset["launcher-run-through-compositor"])
    cb_run_through_compositor.connect("toggled", set_from_checkbutton, preset, "launcher-run-through-compositor")
    grid.attach(cb_run_through_compositor, 2, 9, 2, 1)

    cb_show_power_bar = Gtk.CheckButton.new_with_label(voc["show-power-bar"])
    cb_show_power_bar.set_tooltip_text(voc["show-power-bar-tooltip"])
    cb_show_power_bar.set_active(preset["powerbar-on"])
    cb_show_power_bar.connect("toggled", set_from_checkbutton, preset, "powerbar-on")
    grid.attach(cb_show_power_bar, 2, 10, 2, 1)

    cb_use_icon_theme = Gtk.CheckButton.new_with_label(voc["use-icon-theme"])
    cb_use_icon_theme.set_tooltip_text(voc["use-icon-theme-tooltip"])
    cb_use_icon_theme.set_active(preset["pb-icon-theme"])
    cb_use_icon_theme.connect("toggled", set_from_checkbutton, preset, "pb-icon-theme")
    grid.attach(cb_use_icon_theme, 2, 11, 2, 1)

    if os.getenv("HYPRLAND_INSTANCE_SIGNATURE"):
        cb_h_drawer_blur_bg = Gtk.CheckButton.new_with_label(voc["blur-background"])
        cb_h_drawer_blur_bg.set_active(preset["launcher-blur-background"])
        cb_h_drawer_blur_bg.connect("toggled", set_from_checkbutton, preset, "launcher-blur-background")
        grid.attach(cb_h_drawer_blur_bg, 0, 12, 2, 1)

    frame.show_all()

    return frame


def dock_tab(preset, preset_name, outputs, voc):
    frame = Gtk.Frame()
    frame.set_label("  {}: {}  ".format(preset_name, voc["dock"]))
    frame.set_label_align(0.5, 0.5)
    frame.set_property("hexpand", True)
    grid = Gtk.Grid()
    frame.add(grid)
    grid.set_property("margin", 12)
    grid.set_column_spacing(6)
    grid.set_row_spacing(6)

    cb_dock_on = Gtk.CheckButton.new_with_label(voc["dock-on"])
    cb_dock_on.set_active(preset["dock-on"])
    cb_dock_on.connect("toggled", set_from_checkbutton, preset, "dock-on")
    grid.attach(cb_dock_on, 0, 0, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["position"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 1, 1, 1)

    combo_position = Gtk.ComboBoxText()
    combo_position.set_property("halign", Gtk.Align.START)
    grid.attach(combo_position, 1, 1, 1, 1)
    for item in ["bottom", "top", "left"]:
        combo_position.append(item, voc[item])
    combo_position.set_active_id(preset["dock-position"])
    combo_position.connect("changed", set_dict_key_from_combo, preset, "dock-position")

    lbl = Gtk.Label.new("{}:".format(voc["alignment"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 2, 1, 1)

    combo_alignment = Gtk.ComboBoxText()
    combo_alignment.set_property("halign", Gtk.Align.START)
    grid.attach(combo_alignment, 1, 2, 1, 1)
    for item in ["center", "start", "end"]:
        combo_alignment.append(item, voc[item])
    combo_alignment.set_active_id(preset["dock-alignment"])
    combo_alignment.connect("changed", set_dict_key_from_combo, preset, "dock-alignment")

    lbl = Gtk.Label.new("{}:".format(voc["icon-size"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 3, 1, 1)

    sb_icon_size = Gtk.SpinButton.new_with_range(8, 256, 1)
    sb_icon_size.set_value(preset["dock-icon-size"])
    sb_icon_size.connect("value-changed", set_int_from_spinbutton, preset, "dock-icon-size")
    sb_icon_size.set_tooltip_text(voc["app-icon-size-tooltip"])
    grid.attach(sb_icon_size, 1, 3, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["margin"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 4, 1, 1)

    sb_margin = Gtk.SpinButton.new_with_range(0, 256, 1)
    sb_margin.set_value(preset["dock-margin"])
    sb_margin.connect("value-changed", set_int_from_spinbutton, preset, "dock-margin")
    sb_margin.set_tooltip_text(voc["margin-tooltip"])
    grid.attach(sb_margin, 1, 4, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["output"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 5, 1, 1)

    combo_outputs = Gtk.ComboBoxText()
    combo_outputs.set_property("halign", Gtk.Align.START)
    grid.attach(combo_outputs, 1, 5, 1, 1)
    combo_outputs.append("Any", voc["any"])
    for item in outputs:
        combo_outputs.append(item, item)
    combo_outputs.set_active_id(preset["dock-output"])
    combo_outputs.connect("changed", set_dict_key_from_combo, preset, "dock-output")

    lbl = Gtk.Label.new("{}:".format(voc["on-layer"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 6, 1, 1)

    combo_layer = Gtk.ComboBoxText()
    combo_layer.set_property("halign", Gtk.Align.START)
    grid.attach(combo_layer, 1, 6, 1, 1)
    combo_layer.set_tooltip_text(voc["on-layer-tooltip"])
    layers = ["overlay", "top"]
    for l in layers:
        combo_layer.append(l, l)
    combo_layer.set_active_id(preset["dock-layer"])
    combo_layer.connect("changed", set_dict_key_from_combo, preset, "dock-layer")

    lbl = Gtk.Label.new("{}:".format(voc["hotspot-delay"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 7, 1, 1)

    sb_hotspot_delay = Gtk.SpinButton.new_with_range(0, 10000, 1)
    sb_hotspot_delay.set_value(preset["dock-hotspot-delay"])
    sb_hotspot_delay.connect("value-changed", set_int_from_spinbutton, preset, "dock-hotspot-delay")
    sb_hotspot_delay.set_tooltip_text(voc["hotspot-delay-tooltip"])
    grid.attach(sb_hotspot_delay, 1, 7, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["startup-delay"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 8, 1, 1)

    sb_startup_delay = Gtk.SpinButton.new_with_range(0, 16, 0.1)
    sb_startup_delay.set_value(preset["dock-startup-delay"])
    sb_startup_delay.connect("value-changed", set_from_spinbutton, preset, "dock-startup-delay", 2)
    sb_startup_delay.set_tooltip_text(voc["startup-delay-tooltip"])
    grid.attach(sb_startup_delay, 1, 8, 1, 1)

    cb_permanent = Gtk.CheckButton.new_with_label(voc["permanent"])
    cb_permanent.set_active(preset["dock-permanent"])
    cb_permanent.connect("toggled", set_from_checkbutton, preset, "dock-permanent")
    cb_permanent.set_tooltip_text(voc["permanent-tooltip"])
    grid.attach(cb_permanent, 0, 9, 1, 1)

    cb_full = Gtk.CheckButton.new_with_label(voc["full-width-height"])
    cb_full.set_active(preset["dock-full"])
    cb_full.connect("toggled", set_from_checkbutton, preset, "dock-full")
    cb_full.set_tooltip_text(voc["full-width-height-tooltip"])
    grid.attach(cb_full, 0, 10, 1, 1)

    cb_autohide = Gtk.CheckButton.new_with_label(voc["auto-show-hide"])
    cb_autohide.set_active(preset["dock-autohide"])
    cb_autohide.connect("toggled", set_from_checkbutton, preset, "dock-autohide")
    cb_autohide.set_tooltip_text(voc["auto-show-hide-tooltip"])
    grid.attach(cb_autohide, 0, 11, 1, 1)

    cb_exclusive = Gtk.CheckButton.new_with_label(voc["exclusive-zone"])
    cb_exclusive.set_active(preset["dock-exclusive"])
    cb_exclusive.connect("toggled", set_from_checkbutton, preset, "dock-exclusive")
    cb_exclusive.set_tooltip_text(voc["exclusive-zone-tooltip"])
    grid.attach(cb_exclusive, 1, 9, 1, 1)

    cb_launcher_at_start = Gtk.CheckButton.new_with_label(voc["launcher-at-start"])
    cb_launcher_at_start.set_active(preset["launcher-at-start"])
    cb_launcher_at_start.connect("toggled", set_from_checkbutton, preset, "launcher-at-start")
    cb_launcher_at_start.set_tooltip_text(voc["launcher-at-start-tooltip"])
    grid.attach(cb_launcher_at_start, 1, 10, 1, 1)

    if os.getenv("HYPRLAND_INSTANCE_SIGNATURE"):
        cb_blur_bg = Gtk.CheckButton.new_with_label(voc["blur-background"])
        cb_blur_bg.set_active(preset["dock-blur-background"])
        cb_blur_bg.connect("toggled", set_from_checkbutton, preset, "dock-blur-background")
        grid.attach(cb_blur_bg, 1, 11, 1, 1)

    frame.show_all()

    return frame


# def bar_tab(preset, preset_name, voc):
#     frame = Gtk.Frame()
#     frame.set_label("  {}: {}  ".format(preset_name, voc["exit-menu"]))
#     frame.set_label_align(0.5, 0.5)
#     frame.set_property("hexpand", True)
#     grid = Gtk.Grid()
#     frame.add(grid)
#     grid.set_property("margin", 12)
#     grid.set_column_spacing(6)
#     grid.set_row_spacing(6)
#
#     cb_bar_on = Gtk.CheckButton.new_with_label(voc["exit-menu-on"])
#     cb_bar_on.set_active(preset["exit-on"])
#     cb_bar_on.connect("toggled", set_from_checkbutton, preset, "exit-on")
#     grid.attach(cb_bar_on, 0, 0, 2, 1)
#
#     lbl = Gtk.Label.new("{}:".format(voc["position"]))
#     lbl.set_property("halign", Gtk.Align.END)
#     grid.attach(lbl, 0, 1, 1, 1)
#
#     combo_position = Gtk.ComboBoxText()
#     combo_position.set_property("halign", Gtk.Align.START)
#     grid.attach(combo_position, 1, 1, 1, 1)
#     for item in ["center", "top", "bottom", "left", "right"]:
#         combo_position.append(item, voc[item])
#     combo_position.set_active_id(preset["exit-position"])
#     combo_position.connect("changed", set_dict_key_from_combo, preset, "exit-position")
#
#     lbl = Gtk.Label.new("{}:".format(voc["alignment"]))
#     lbl.set_property("halign", Gtk.Align.END)
#     grid.attach(lbl, 0, 2, 1, 1)
#
#     combo_alignment = Gtk.ComboBoxText()
#     combo_alignment.set_property("halign", Gtk.Align.START)
#     grid.attach(combo_alignment, 1, 2, 1, 1)
#     for item in ["middle", "start", "end"]:
#         combo_alignment.append(item, voc[item])
#     combo_alignment.set_active_id(preset["exit-alignment"])
#     combo_alignment.connect("changed", set_dict_key_from_combo, preset, "exit-alignment")
#     combo_alignment.set_tooltip_text("Alignment in full width/height.")
#
#     lbl = Gtk.Label.new("{}:".format(voc["icon-size"]))
#     lbl.set_property("halign", Gtk.Align.END)
#     grid.attach(lbl, 0, 3, 1, 1)
#
#     sb_icon_size = Gtk.SpinButton.new_with_range(8, 256, 1)
#     sb_icon_size.set_value(preset["exit-icon-size"])
#     sb_icon_size.connect("value-changed", set_int_from_spinbutton, preset, "exit-icon-size")
#     sb_icon_size.set_tooltip_text(voc["item-icon-size-tooltip"])
#     grid.attach(sb_icon_size, 1, 3, 1, 1)
#
#     lbl = Gtk.Label.new("{}:".format(voc["margin"]))
#     lbl.set_property("halign", Gtk.Align.END)
#     grid.attach(lbl, 0, 4, 1, 1)
#
#     sb_margin = Gtk.SpinButton.new_with_range(0, 256, 1)
#     sb_margin.set_value(preset["exit-margin"])
#     sb_margin.connect("value-changed", set_int_from_spinbutton, preset, "exit-margin")
#     sb_margin.set_tooltip_text(voc["margin-tooltip"])
#     grid.attach(sb_margin, 1, 4, 1, 1)
#
#     cb_full = Gtk.CheckButton.new_with_label(voc["full-width-height"])
#     cb_full.set_active(preset["exit-full"])
#     cb_full.connect("toggled", set_from_checkbutton, preset, "exit-full")
#     cb_full.set_tooltip_text(voc["full-width-height-tooltip"])
#     grid.attach(cb_full, 0, 5, 2, 1)
#
#     frame.show_all()
#
#     return frame


def notification_tab(preset, preset_name, voc):
    frame = Gtk.Frame()
    frame.set_label("  {}: Notification center  ".format(preset_name))
    frame.set_label_align(0.5, 0.5)
    frame.set_property("hexpand", True)
    grid = Gtk.Grid()
    frame.add(grid)
    grid.set_property("margin", 12)
    grid.set_column_spacing(6)
    grid.set_row_spacing(6)

    lbl = Gtk.Label.new("{}:".format(voc["horizontal-alignment"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 1, 1, 1)

    combo_position_x = Gtk.ComboBoxText()
    combo_position_x.set_property("halign", Gtk.Align.START)
    grid.attach(combo_position_x, 1, 1, 1, 1)
    for item in ["left", "right", "center"]:
        combo_position_x.append(item, voc[item])
    combo_position_x.set_active_id(preset["swaync-positionX"])
    combo_position_x.connect("changed", set_dict_key_from_combo, preset, "swaync-positionX")

    lbl = Gtk.Label.new("{}:".format(voc["vertical-alignment"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 2, 1, 1)

    combo_position_x = Gtk.ComboBoxText()
    combo_position_x.set_property("halign", Gtk.Align.START)
    grid.attach(combo_position_x, 1, 2, 1, 1)
    for item in ["top", "bottom"]:
        combo_position_x.append(item, voc[item])
    combo_position_x.set_active_id(preset["swaync-positionY"])
    combo_position_x.connect("changed", set_dict_key_from_combo, preset, "swaync-positionY")

    lbl = Gtk.Label.new("{}:".format(voc["notification-center-width"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 3, 1, 1)

    sb_cc_width = Gtk.SpinButton.new_with_range(0, 1000, 1)
    sb_cc_width.set_value(preset["swaync-control-center-width"])
    sb_cc_width.connect("value-changed", set_int_from_spinbutton, preset, "swaync-control-center-width")
    grid.attach(sb_cc_width, 1, 3, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["notification-window-width"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 4, 1, 1)

    sb_window_width = Gtk.SpinButton.new_with_range(0, 1000, 1)
    sb_window_width.set_value(preset["swaync-control-center-width"])
    sb_window_width.connect("value-changed", set_int_from_spinbutton, preset, "swaync-notification-window-width")
    grid.attach(sb_window_width, 1, 4, 1, 1)

    cb_swaync_mpris = Gtk.CheckButton.new_with_label("{}".format(voc["enable-mpris-widget"]))
    cb_swaync_mpris.set_active(preset["swaync-mpris"])
    cb_swaync_mpris.connect("toggled", set_from_checkbutton, preset, "swaync-mpris")
    cb_swaync_mpris.set_tooltip_text(voc["enable-mpris-widget-tooltip"])
    grid.attach(cb_swaync_mpris, 0, 5, 1, 1)

    frame.show_all()

    return frame


def gtklock_preset_tab(preset, preset_name, voc):
    frame = Gtk.Frame()
    frame.set_label("  {}: gtklock  ".format(preset_name))
    frame.set_label_align(0.5, 0.5)
    frame.set_property("hexpand", True)
    grid = Gtk.Grid()
    frame.add(grid)
    grid.set_property("margin", 12)
    grid.set_column_spacing(6)
    grid.set_row_spacing(6)

    if gtklock_module_path("userinfo"):
        lbl = Gtk.Label()
        lbl.set_markup("<b>{}</b>".format(voc["userinfo-module"]))
        lbl.set_property("halign", Gtk.Align.START)
        grid.attach(lbl, 0, 1, 1, 1)

        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        grid.attach(box, 1, 1, 3, 1)

        cb_userinfo_round_image = Gtk.CheckButton.new_with_label(voc["round-image"])
        cb_userinfo_round_image.set_active(preset["gtklock-userinfo-round-image"])
        cb_userinfo_round_image.connect("toggled", set_from_checkbutton, preset, "gtklock-userinfo-round-image")
        cb_userinfo_round_image.set_tooltip_text("user avatar shape")
        box.pack_start(cb_userinfo_round_image, False, False, 0)

        cb_userinfo_vertical_layout = Gtk.CheckButton.new_with_label(voc["vertical-layout"])
        cb_userinfo_vertical_layout.set_active(preset["gtklock-userinfo-vertical-layout"])
        cb_userinfo_vertical_layout.connect("toggled", set_from_checkbutton, preset, "gtklock-userinfo-vertical-layout")
        cb_userinfo_vertical_layout.set_tooltip_text("user name next to the avatar")
        box.pack_start(cb_userinfo_vertical_layout, False, False, 0)

        cb_userinfo_under_clock = Gtk.CheckButton.new_with_label(voc["under-clock"])
        cb_userinfo_under_clock.set_active(preset["gtklock-userinfo-under-clock"])
        cb_userinfo_under_clock.connect("toggled", set_from_checkbutton, preset, "gtklock-userinfo-under-clock")
        cb_userinfo_under_clock.set_tooltip_text("user avatar and name below the clock")
        box.pack_start(cb_userinfo_under_clock, False, False, 0)

    if gtklock_module_path("powerbar"):
        lbl = Gtk.Label()
        lbl.set_markup("<b>{}</b>".format(voc["powerbar-module"]))
        lbl.set_property("halign", Gtk.Align.START)
        grid.attach(lbl, 0, 2, 1, 1)

        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        grid.attach(box, 1, 2, 3, 1)

        cb_powerbar_show_labels = Gtk.CheckButton.new_with_label(voc["show-labels"])
        cb_powerbar_show_labels.set_active(preset["gtklock-powerbar-show-labels"])
        cb_powerbar_show_labels.connect("toggled", set_from_checkbutton, preset, "gtklock-powerbar-show-labels")
        box.pack_start(cb_powerbar_show_labels, False, False, 0)

        cb_powerbar_linked_buttons = Gtk.CheckButton.new_with_label(voc["linked-buttons"])
        cb_powerbar_linked_buttons.set_active(preset["gtklock-powerbar-linked-buttons"])
        cb_powerbar_linked_buttons.connect("toggled", set_from_checkbutton, preset, "gtklock-powerbar-linked-buttons")
        box.pack_start(cb_powerbar_linked_buttons, False, False, 0)

    if gtklock_module_path("playerctl"):
        lbl = Gtk.Label()
        lbl.set_markup("<b>{}</b>".format(voc["playerctl-module"]))
        lbl.set_property("halign", Gtk.Align.START)
        grid.attach(lbl, 0, 3, 1, 1)

        lbl = Gtk.Label.new("{}:".format(voc["album-cover-size"]))
        lbl.set_property("halign", Gtk.Align.END)
        grid.attach(lbl, 0, 4, 1, 1)

        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        grid.attach(box, 1, 4, 3, 1)

        sb_gtklock_playerctl_art_size = Gtk.SpinButton.new_with_range(0, 256, 1)
        sb_gtklock_playerctl_art_size.set_value(preset["gtklock-playerctl-art-size"])
        sb_gtklock_playerctl_art_size.connect("value-changed", set_int_from_spinbutton, preset,
                                              "gtklock-playerctl-art-size")
        sb_gtklock_playerctl_art_size.set_tooltip_text(voc["album-cover-size-tooltip"])
        box.pack_start(sb_gtklock_playerctl_art_size, False, False, 0)

        lbl = Gtk.Label.new("{}:".format(voc["position"]))
        lbl.set_property("halign", Gtk.Align.END)
        box.pack_start(lbl, False, False, 6)

        combo_gtklock_playerctl_position = Gtk.ComboBoxText()
        combo_gtklock_playerctl_position.set_property("halign", Gtk.Align.START)
        box.pack_start(combo_gtklock_playerctl_position, False, False, 0)
        for item in ["top-left", "top-center", "top-right", "bottom-left", "bottom-center", "bottom-right",
                     "above-clock", "under-clock"]:
            combo_gtklock_playerctl_position.append(item, voc[item])
        combo_gtklock_playerctl_position.set_active_id(preset["gtklock-playerctl-position"])
        combo_gtklock_playerctl_position.connect("changed", set_dict_key_from_combo, preset,
                                                 "gtklock-playerctl-position")
        combo_gtklock_playerctl_position.set_tooltip_text("playerctl widget placement")

        cb_gtklock_playerctl_show_hidden = Gtk.CheckButton.new_with_label(voc["always-show"])
        cb_gtklock_playerctl_show_hidden.set_active(preset["gtklock-playerctl-show-hidden"])
        cb_gtklock_playerctl_show_hidden.connect("toggled", set_from_checkbutton, preset,
                                                 "gtklock-playerctl-show-hidden")
        cb_gtklock_playerctl_show_hidden.set_tooltip_text(voc["always-show-gtklock-tooltip"])
        grid.attach(cb_gtklock_playerctl_show_hidden, 1, 5, 3, 1)

    frame.show_all()

    return frame


def panel_styling_tab(settings, preset, preset_name, voc):
    frame = Gtk.Frame()
    frame.set_label("  {}: {}  ".format(preset_name, voc["panel-css"]))
    frame.set_label_align(0.5, 0.5)
    frame.set_property("hexpand", True)
    grid = Gtk.Grid()
    frame.add(grid)
    grid.set_property("margin", 12)
    grid.set_column_spacing(6)
    grid.set_row_spacing(6)

    lbl = Gtk.Label.new("{}:".format(voc["panel-config-name"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 0, 1, 1)

    entry_panel = Gtk.Entry()
    entry_panel.set_placeholder_text("config")
    entry_panel.set_tooltip_text(voc["panel-config-name-tooltip"])
    entry_panel.set_property("halign", Gtk.Align.START)
    entry_panel.set_text(settings["panel-custom"])
    entry_panel.connect("changed", set_from_entry, settings, "panel-custom")
    grid.attach(entry_panel, 1, 0, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["panel-css-name"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 1, 1, 1)

    entry_panel_css = Gtk.Entry()
    entry_panel_css.set_placeholder_text("style.css")
    entry_panel_css.set_tooltip_text(voc["panel-css-name-tooltip"])
    entry_panel_css.set_property("halign", Gtk.Align.START)
    entry_panel_css.set_text(preset["panel-css"])
    entry_panel_css.connect("changed", set_from_entry, preset, "panel-css")
    grid.attach(entry_panel_css, 1, 1, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["drawer-css-name"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 2, 1, 1)

    entry_panel_css = Gtk.Entry()
    entry_panel_css.set_placeholder_text("drawer.css")
    entry_panel_css.set_property("halign", Gtk.Align.START)
    entry_panel_css.set_text(preset["launcher-css"])
    entry_panel_css.connect("changed", set_from_entry, preset, "launcher-css")
    entry_panel_css.set_tooltip_text(voc["drawer-css-name-tooltip"])
    grid.attach(entry_panel_css, 1, 2, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["dock-css-name"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 3, 1, 1)

    entry_panel_css = Gtk.Entry()
    entry_panel_css.set_placeholder_text("style.css")
    entry_panel_css.set_property("halign", Gtk.Align.START)
    entry_panel_css.set_text(preset["dock-css"])
    entry_panel_css.connect("changed", set_from_entry, preset, "dock-css")
    entry_panel_css.set_tooltip_text(voc["dock-css-name-tooltip"])
    grid.attach(entry_panel_css, 1, 3, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["exit-menu-css-name"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 4, 1, 1)

    entry_panel_css = Gtk.Entry()
    entry_panel_css.set_placeholder_text("style.css")
    entry_panel_css.set_property("halign", Gtk.Align.START)
    entry_panel_css.set_text(preset["exit-css"])
    entry_panel_css.connect("changed", set_from_entry, preset, "exit-css")
    entry_panel_css.set_tooltip_text(voc["exit-menu-css-name-tooltip"])
    grid.attach(entry_panel_css, 1, 4, 1, 1)

    frame.show_all()

    return frame


def sys_info_tab(voc):
    frame = Gtk.Frame()
    frame.set_label("  {}  ".format(voc["system-info"]))
    frame.set_label_align(0.5, 0.5)
    frame.set_property("hexpand", True)
    grid = Gtk.Grid()
    frame.add(grid)
    grid.set_property("margin", 12)
    grid.set_column_spacing(6)
    grid.set_row_spacing(3)

    name, home_url, logo = parse_os_release()
    if logo:
        img = Gtk.Image.new_from_icon_name(logo, Gtk.IconSize.DIALOG)
        img.set_property("halign", Gtk.Align.END)
        grid.attach(img, 0, 0, 1, 2)

    txt = get_command_output("uname -m")[0]
    if name:
        lbl = Gtk.Label()
        lbl.set_markup("<big><b>{} {}</b></big>".format(name, txt))
        lbl.set_property("halign", Gtk.Align.START)
        grid.attach(lbl, 1, 0, 1, 1)

    if home_url:
        lbl = Gtk.Label()
        lbl.set_markup('<a href="{}">{}</a>'.format(home_url, home_url))
        lbl.set_property("halign", Gtk.Align.START)
        grid.attach(lbl, 1, 1, 1, 1)

    txt = get_command_output("uname -r")[0]
    lbl = Gtk.Label.new("Kernel: {}".format(txt))
    lbl.set_line_wrap(True)
    lbl.set_property("xalign", 0)
    grid.attach(lbl, 1, 2, 1, 1)

    output = ""
    if os.getenv("SWAYSOCK"):
        output = get_command_output("sway -v")
        lbl = Gtk.Label.new(output[0])
        lbl.set_property("halign", Gtk.Align.START)
        grid.attach(lbl, 1, 3, 1, 1)
    elif os.getenv("HYPRLAND_INSTANCE_SIGNATURE"):
        reply = hyprctl("j/version")
        values = json.loads(reply)
        if values and "tag" in values:
            lbl = Gtk.Label.new("Hyprland Tag: {}".format(values["tag"]))
            lbl.set_property("halign", Gtk.Align.START)
            grid.attach(lbl, 1, 3, 1, 1)

    settings = Gtk.Settings.get_default()
    if settings:
        lbl = Gtk.Label.new("GTK theme:")
        lbl.set_property("halign", Gtk.Align.END)
        grid.attach(lbl, 0, 5, 1, 1)

        lbl = Gtk.Label.new(settings.get_property("gtk-theme-name"))
        lbl.set_property("halign", Gtk.Align.START)
        grid.attach(lbl, 1, 5, 1, 1)

        lbl = Gtk.Label.new("Icon theme:")
        lbl.set_property("halign", Gtk.Align.END)
        grid.attach(lbl, 0, 6, 1, 1)

        lbl = Gtk.Label.new(settings.get_property("gtk-icon-theme-name"))
        lbl.set_property("halign", Gtk.Align.START)
        grid.attach(lbl, 1, 6, 1, 1)

        lbl = Gtk.Label.new("Font:")
        lbl.set_property("halign", Gtk.Align.END)
        grid.attach(lbl, 0, 7, 1, 1)

        lbl = Gtk.Label.new(settings.get_property("gtk-font-name"))
        lbl.set_property("halign", Gtk.Align.START)
        grid.attach(lbl, 1, 7, 1, 1)

    if os.getenv("SWAYSOCK"):
        i3 = Connection()
        row = 9
        outputs = i3.get_outputs()
        for i in range(len(outputs)):
            output = outputs[i]

            lbl = Gtk.Label.new("{}:".format(output.name))
            lbl.set_property("halign", Gtk.Align.END)
            grid.attach(lbl, 0, row + i, 1, 1)

            r = output.rect
            lbl = Gtk.Label.new(
                "{}x{}, scale: {}, x: {}, y: {}".format(r.width, r.height, output.scale, r.x, r.y))
            lbl.set_property("halign", Gtk.Align.START)
            grid.attach(lbl, 1, row + i, 1, 1)

    elif os.getenv("HYPRLAND_INSTANCE_SIGNATURE"):
        row = 9
        reply = hyprctl("j/monitors")
        monitors = json.loads(reply)
        for i in range(len(monitors)):
            m = monitors[i]

            lbl = Gtk.Label.new("{}:".format(m["name"]))
            lbl.set_property("halign", Gtk.Align.END)
            grid.attach(lbl, 0, row + i, 1, 1)

            lbl = Gtk.Label.new(
                "{}x{}, scale: {}, x: {}, y: {}".format(m["width"], m["height"], m["scale"], m["x"], m["y"]))
            lbl.set_property("halign", Gtk.Align.START)
            grid.attach(lbl, 1, row + i, 1, 1)

    # Right column
    img = Gtk.Image.new_from_icon_name("nwg-shell", Gtk.IconSize.DIALOG)
    img.set_property("halign", Gtk.Align.END)
    grid.attach(img, 2, 0, 1, 2)

    output = get_command_output("nwg-shell -v")
    if output:
        lbl = Gtk.Label()
        lbl.set_markup("<big><b>{}</b></big>".format(output[0]))
        lbl.set_property("halign", Gtk.Align.START)
        grid.attach(lbl, 3, 0, 1, 1)

        lbl = Gtk.Label()
        lbl.set_markup('<a href="https://nwg-piotr.github.io/nwg-shell">https://nwg-piotr.github.io/nwg-shell</a>')
        lbl.set_property("halign", Gtk.Align.START)
        grid.attach(lbl, 3, 1, 1, 1)

    output = get_command_output("nwg-shell-config -v")
    if output:
        lbl = Gtk.Label.new(output[0])
        lbl.set_property("halign", Gtk.Align.START)
        grid.attach(lbl, 3, 2, 1, 1)

    output = get_command_output("nwg-panel -v")
    if output:
        lbl = Gtk.Label.new(output[0])
        lbl.set_property("halign", Gtk.Align.START)
        grid.attach(lbl, 3, 3, 1, 1)

    output = get_command_output("nwg-drawer -v")
    if output:
        lbl = Gtk.Label.new(output[0])
        lbl.set_property("halign", Gtk.Align.START)
        grid.attach(lbl, 3, 4, 1, 1)

    output = get_command_output("nwg-dock -v")
    if output:
        lbl = Gtk.Label.new(output[0])
        lbl.set_property("halign", Gtk.Align.START)
        grid.attach(lbl, 3, 5, 1, 1)

    output = get_command_output("nwg-menu -v")
    if output:
        lbl = Gtk.Label.new(output[0])
        lbl.set_property("halign", Gtk.Align.START)
        grid.attach(lbl, 3, 6, 1, 1)

    output = get_command_output("nwg-bar -v")
    if output:
        lbl = Gtk.Label.new(output[0])
        lbl.set_property("halign", Gtk.Align.START)
        grid.attach(lbl, 3, 7, 1, 1)

    output = get_command_output("nwg-look -v")
    if output:
        lbl = Gtk.Label.new(output[0])
        lbl.set_property("halign", Gtk.Align.START)
        grid.attach(lbl, 3, 8, 1, 1)

    output = get_command_output("nwg-displays -v")
    if output:
        lbl = Gtk.Label.new(output[0])
        lbl.set_property("halign", Gtk.Align.START)
        grid.attach(lbl, 3, 9, 1, 1)

    output = get_command_output("gtklock -v")
    if output:
        lbl = Gtk.Label.new(output[0])
        lbl.set_property("halign", Gtk.Align.START)
        grid.attach(lbl, 3, 10, 1, 1)

    output = get_command_output("swaync -v")
    if output:
        lbl = Gtk.Label.new(output[0])
        lbl.set_property("halign", Gtk.Align.START)
        grid.attach(lbl, 3, 11, 1, 1)

    output = get_command_output("azote -h")
    if output:
        lbl = Gtk.Label.new(output[1])
        lbl.set_property("halign", Gtk.Align.START)
        grid.attach(lbl, 3, 12, 1, 1)

    frame.show_all()

    return frame


def parse_os_release():
    name, home_url, logo = "", "", ""
    if os.path.isfile("/etc/os-release"):
        lines = load_text_file("/etc/os-release").splitlines()
        for line in lines:
            if line.startswith("NAME="):
                name = line.split("=")[1].replace('"', '')
                continue
            if line.startswith("HOME_URL="):
                home_url = line.split("=")[1].replace('"', '')
                continue
            if line.startswith("LOGO="):
                logo = line.split("=")[1]
                continue

        if not logo:
            logo = name

    return name, home_url, logo
