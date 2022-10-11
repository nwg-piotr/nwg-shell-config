import subprocess
import gi
import os

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from nwg_shell_config.tools import is_command, get_lat_lon, list_background_dirs, load_text_file, \
    gtklock_module_path


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


def screen_tab(settings, voc, pending_updates):
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
    box.set_property("margin-left", 12)
    box.set_property("margin-bottom", 12)
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

    update_btn = Gtk.Button()
    update_btn.set_property("name", "app-btn")
    update_btn.set_always_show_image(True)
    update_btn.set_image_position(Gtk.PositionType.TOP)
    if pending_updates == 0:
        update_btn.set_label(voc["updates"])
        img = Gtk.Image.new_from_icon_name("nwg-shell", Gtk.IconSize.DIALOG)
    else:
        update_btn.set_label("Updates ({})".format(pending_updates))
        img = Gtk.Image.new_from_icon_name("nwg-shell-update", Gtk.IconSize.DIALOG)
    update_btn.set_image(img)
    update_btn.connect("clicked", launch, "nwg-shell-updater")
    box.pack_start(update_btn, False, True, 0)

    lbl = Gtk.Label()
    lbl.set_markup("<b>{}</b>".format(voc["desktop-style"]))
    lbl.set_property("halign", Gtk.Align.START)
    grid.attach(lbl, 0, 1, 1, 1)

    combo = Gtk.ComboBoxText()
    combo.set_property("halign", Gtk.Align.START)
    grid.attach(combo, 1, 1, 1, 1)
    for p in ["preset-0", "preset-1", "preset-2", "preset-3", "custom"]:
        combo.append(p, p)
    combo.set_active_id(settings["panel-preset"])
    combo.connect("changed", set_dict_key_from_combo, settings, "panel-preset")
    combo.set_tooltip_text(voc["preset-tooltip"])

    lbl = Gtk.Label()
    lbl.set_markup("<b>{}</b>".format(voc["autotiling"]))
    lbl.set_property("margin-top", 6)
    lbl.set_property("margin-bottom", 6)
    lbl.set_property("halign", Gtk.Align.START)
    grid.attach(lbl, 0, 2, 1, 1)

    cb_autotiling_on = Gtk.CheckButton.new_with_label(voc["on"])
    cb_autotiling_on.set_active(settings["autotiling-on"])
    cb_autotiling_on.connect("toggled", set_from_checkbutton, settings, "autotiling-on")
    cb_autotiling_on.set_tooltip_text(voc["autotiling-tooltip"])
    grid.attach(cb_autotiling_on, 1, 2, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["workspaces"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 3, 1, 1)

    entry = Gtk.Entry()
    entry.set_placeholder_text("1 2 3 4 5 6 7 8")
    entry.set_text(settings["autotiling-workspaces"])
    entry.set_tooltip_text(voc["workspaces-tooltip"])
    entry.connect("changed", set_from_workspaces, settings)
    grid.attach(entry, 1, 3, 1, 1)

    lbl = Gtk.Label()
    lbl.set_markup("<b>{}</b>".format(voc["night-light"]))
    lbl.set_property("margin-top", 6)
    lbl.set_property("margin-bottom", 6)
    lbl.set_property("halign", Gtk.Align.START)
    grid.attach(lbl, 0, 4, 1, 1)

    cb_night_light_on = Gtk.CheckButton.new_with_label(voc["on"])
    cb_night_light_on.set_active(settings["night-on"])
    cb_night_light_on.connect("toggled", set_from_checkbutton, settings, "night-on")
    cb_night_light_on.set_tooltip_text(voc["night-light-tooltip"])
    grid.attach(cb_night_light_on, 1, 4, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["latitude"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 2, 5, 1, 1)

    sb_lat = Gtk.SpinButton.new_with_range(-90.0, 90.0, 0.1)
    sb_lat.set_tooltip_text(voc["latitude-tooltip"])
    sb_lat.set_digits(4)
    sb_lat.set_value(settings["night-lat"])
    sb_lat.connect("value-changed", set_from_spinbutton, settings, "night-lat", 4)
    grid.attach(sb_lat, 3, 5, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["temp-night"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 5, 1, 1)

    sb_temp_low = Gtk.SpinButton.new_with_range(1000, 10000, 100)
    sb_temp_low.set_tooltip_text(voc["night-light-night-tooltip"])
    sb_temp_low.set_value(settings["night-temp-low"])
    sb_temp_low.connect("value-changed", set_int_from_spinbutton, settings, "night-temp-low")
    grid.attach(sb_temp_low, 1, 5, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["longitude"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 2, 6, 1, 1)

    sb_lon = Gtk.SpinButton.new_with_range(-180, 180, 0.1)
    sb_lon.set_tooltip_text(voc["longitude-tooltip"])
    sb_lon.set_value(settings["night-long"])
    sb_lon.connect("value-changed", set_from_spinbutton, settings, "night-long", 4)
    sb_lon.set_digits(4)
    grid.attach(sb_lon, 3, 6, 1, 1)

    if (sb_lat.get_value() == -1.0 and sb_lon.get_value()) == -1.0 \
            or (sb_lat.get_value() == 0.0 and sb_lon.get_value() == 0.0):
        update_lat_lon(None, sb_lat, sb_lon)

    lbl = Gtk.Label.new("{}:".format(voc["temp-day"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 6, 1, 1)

    sb_temp_high = Gtk.SpinButton.new_with_range(1000, 10000, 100)
    sb_temp_high.set_tooltip_text(voc["night-light-day-tooltip"])
    sb_temp_high.set_value(settings["night-temp-high"])
    sb_temp_high.connect("value-changed", set_int_from_spinbutton, settings, "night-temp-high")
    grid.attach(sb_temp_high, 1, 6, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["gamma"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 7, 1, 1)

    btn = Gtk.Button.new_with_label(voc["calculate-lat-long"])
    btn.set_tooltip_text(voc["calculate-lat-long-tooltip"])
    btn.connect("clicked", update_lat_lon, sb_lat, sb_lon)
    grid.attach(btn, 3, 7, 1, 1)

    sb_gamma = Gtk.SpinButton.new_with_range(0.1, 10.0, 0.1)
    sb_gamma.set_value(settings["night-gamma"])
    sb_gamma.connect("value-changed", set_from_spinbutton, settings, "night-gamma", 1)
    sb_gamma.set_tooltip_text(voc["gamma-tooltip"])
    grid.attach(sb_gamma, 1, 7, 1, 1)

    lbl = Gtk.Label()
    lbl.set_markup("<b>{}</b>".format(voc["help-window"]))
    lbl.set_property("halign", Gtk.Align.START)
    grid.attach(lbl, 0, 8, 1, 1)

    box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
    grid.attach(box, 1, 8, 3, 1)

    cb_help_overlay = Gtk.CheckButton.new_with_label(voc["overlay"])
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
    box.pack_start(sb_help_font_size, False, False, 0)

    frame.show_all()

    return frame, update_btn


def applications_tab(settings, warn):
    frame = Gtk.Frame()
    frame.set_label("  Common: Applications  ")
    frame.set_label_align(0.5, 0.5)
    frame.set_property("hexpand", True)
    grid = Gtk.Grid()
    frame.add(grid)
    grid.set_property("margin", 12)
    grid.set_column_spacing(6)
    grid.set_row_spacing(6)

    lbl = Gtk.Label.new("Terminal:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 0, 1, 1)

    entry_terminal = Gtk.Entry.new()
    entry_terminal.set_tooltip_text("Command to run terminal emulator.")
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

    grid.attach(entry_terminal, 1, 0, 1, 1)

    lbl = Gtk.Label.new("File manager:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 1, 1, 1)

    entry_fm = Gtk.Entry()
    entry_fm.set_tooltip_text("Command to run file manager.")
    entry_fm.set_property("halign", Gtk.Align.START)

    entry_fm.connect("changed", set_from_entry, settings, "file-manager")
    if not settings["file-manager"]:
        for cmd in ["thunar", "pcmanfm", "nautilus", "caja"]:
            if is_command(cmd):
                entry_fm.set_text(cmd)
                break
    else:
        entry_fm.set_text(settings["file-manager"])

    grid.attach(entry_fm, 1, 1, 1, 1)

    lbl = Gtk.Label.new("Text editor:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 2, 1, 1)

    entry_te = Gtk.Entry()
    entry_te.set_tooltip_text("Command to run text editor.")
    entry_te.set_property("halign", Gtk.Align.START)

    entry_te.connect("changed", set_from_entry, settings, "editor")
    if not settings["editor"]:
        for cmd in ["mousepad", "geany", "atom", "emacs", "gedit"]:
            if is_command(cmd):
                entry_te.set_text(cmd)
                break
    else:
        entry_te.set_text(settings["editor"])

    grid.attach(entry_te, 1, 2, 1, 1)

    lbl = Gtk.Label.new("Web browser:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 3, 1, 1)

    entry_browser = Gtk.Entry.new()
    entry_browser.set_tooltip_text("Command to run web browser.")
    entry_browser.set_property("hexpand", True)

    entry_browser.set_text(settings["browser"])
    set_from_entry(entry_browser, settings, "browser")
    entry_browser.connect("changed", set_from_entry, settings, "browser")
    grid.attach(entry_browser, 1, 3, 2, 1)

    combo = Gtk.ComboBoxText()
    combo.set_property("halign", Gtk.Align.START)
    combo.set_tooltip_text("Select from known predefined commands\nfor installed browsers.")
    grid.attach(combo, 1, 4, 1, 1)
    browsers = get_browsers()
    for key in browsers:
        combo.append(key, key)
        if key in settings["browser"]:
            combo.set_active_id(key)

    if entry_browser.get_text():
        for key in ["chromium", "google-chrome-stable", "firefox", "qutebrowser", "epiphany", "surf"]:
            if entry_browser.get_text() == key:
                combo.set_active_id(key)

    combo.connect("changed", set_browser_from_combo, entry_browser, browsers)

    if warn:
        lbl = Gtk.Label.new("If you see this warning on startup, some of the fields above\n"
                            "have not yet been saved. Adjust these settings to your needs,\n"
                            "and press the 'Apply' button, for your key bindings to work.")
        lbl.set_property("halign", Gtk.Align.CENTER)
        lbl.set_justify(Gtk.Justification.CENTER)
        lbl.set_property("margin-top", 18)
        lbl.set_line_wrap(True)
        grid.attach(lbl, 0, 5, 3, 2)

    frame.show_all()

    return frame


def get_browsers():
    result = {}
    browsers = {
        "chromium": "chromium --enable-features=UseOzonePlatform --ozone-platform=wayland",
        "google-chrome-stable": "google-chrome-stable --enable-features=UseOzonePlatform --ozone-platform=wayland",
        "firefox": "MOZ_ENABLE_WAYLAND=1 firefox",
        "qutebrowser": "qutebrowser",
        "epiphany": "epiphany",
        "surf": "surf"
    }
    for key in browsers:
        if is_command(key):
            result[key] = browsers[key]

    return result


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

    lbl = Gtk.Label.new("{}:".format(voc["keyboard-layout"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 1, 1, 1)

    entry_layout = Gtk.Entry()
    entry_layout.set_tooltip_text(voc["keyboard-layout-tooltip"])
    entry_layout.set_text(settings["keyboard-xkb-layout"])
    entry_layout.connect("changed", set_from_entry, settings, "keyboard-xkb-layout")
    grid.attach(entry_layout, 1, 1, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["keyboard-variant"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 2, 1, 1)

    entry_variant = Gtk.Entry()
    entry_variant.set_tooltip_text(voc["keyboard-variant-tooltip"])
    entry_variant.set_text(settings["keyboard-xkb-variant"])
    entry_variant.connect("changed", set_from_entry, settings, "keyboard-xkb-variant")
    grid.attach(entry_variant, 1, 2, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["keyboard-repeat-delay"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 3, 1, 1)

    sb_repeat_delay = Gtk.SpinButton.new_with_range(1, 6000, 1)
    sb_repeat_delay.set_value(settings["keyboard-repeat-delay"])
    sb_repeat_delay.connect("value-changed", set_int_from_spinbutton, settings, "keyboard-repeat-delay")
    sb_repeat_delay.set_tooltip_text(voc["keyboard-repeat-delay-tooltip"])
    grid.attach(sb_repeat_delay, 1, 3, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["keyboard-repeat-rate"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 4, 1, 1)

    sb_repeat_rate = Gtk.SpinButton.new_with_range(1, 4000, 1)
    sb_repeat_rate.set_value(settings["keyboard-repeat-rate"])
    sb_repeat_rate.connect("value-changed", set_int_from_spinbutton, settings, "keyboard-repeat-rate")
    sb_repeat_rate.set_tooltip_text(voc["keyboard-repeat-rate-tooltip"])
    grid.attach(sb_repeat_rate, 1, 4, 1, 1)

    lbl = Gtk.Label.new("CapsLock:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 5, 1, 1)

    combo_caps = Gtk.ComboBoxText()
    combo_caps.set_property("halign", Gtk.Align.START)
    combo_caps.set_tooltip_text(voc["capslock-tooltip"])
    for item in ["disabled", "enabled"]:
        combo_caps.append(item, voc[item])
    combo_caps.set_active_id(settings["keyboard-xkb-capslock"])
    combo_caps.connect("changed", set_dict_key_from_combo, settings, "keyboard-xkb-capslock")
    grid.attach(combo_caps, 1, 5, 1, 1)

    lbl = Gtk.Label.new("NumLock:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 6, 1, 1)

    combo_num = Gtk.ComboBoxText()
    combo_num.set_property("halign", Gtk.Align.START)
    combo_num.set_tooltip_text(voc["numlock-tooltip"])
    for item in ["disabled", "enabled"]:
        combo_num.append(item, voc[item])
    combo_num.set_active_id(settings["keyboard-xkb-numlock"])
    combo_num.connect("changed", set_dict_key_from_combo, settings, "keyboard-xkb-numlock")
    grid.attach(combo_num, 1, 6, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["custom-field"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 7, 1, 1)

    entry_cname = Gtk.Entry()
    entry_cname.set_tooltip_text(voc["custom-field-name-tooltip"])
    entry_cname.set_placeholder_text(voc["name"])
    entry_cname.set_text(settings["keyboard-custom-name"])
    entry_cname.connect("changed", set_from_entry, settings, "keyboard-custom-name")
    grid.attach(entry_cname, 1, 7, 1, 1)

    entry_cname = Gtk.Entry()
    entry_cname.set_tooltip_text(voc["custom-field-value-tooltip"])
    entry_cname.set_placeholder_text(voc["value"])
    entry_cname.set_text(settings["keyboard-custom-value"])
    entry_cname.connect("changed", set_from_entry, settings, "keyboard-custom-value")
    grid.attach(entry_cname, 2, 7, 1, 1)

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

    lbl = Gtk.Label.new("{}:".format(voc["acceleration-profile"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 1, 1, 1)

    combo_aprofile = Gtk.ComboBoxText()
    combo_aprofile.set_property("halign", Gtk.Align.START)
    combo_aprofile.set_tooltip_text(voc["acceleration-profile-tooltip"])
    for item in ["flat", "adaptive"]:
        combo_aprofile.append(item, voc[item])
    combo_aprofile.set_active_id(settings["pointer-accel-profile"])
    combo_aprofile.connect("changed", set_dict_key_from_combo, settings, "pointer-accel-profile")
    grid.attach(combo_aprofile, 1, 1, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["acceleration"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 2, 1, 1)

    sb_acceleration = Gtk.SpinButton.new_with_range(-1, 1, 0.1)
    sb_acceleration.set_value(settings["pointer-pointer-accel"])
    sb_acceleration.connect("value-changed", set_from_spinbutton, settings, "pointer-pointer-accel", 1)
    sb_acceleration.set_tooltip_text(voc["acceleration-tooltip"])
    grid.attach(sb_acceleration, 1, 2, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["natural-scroll"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 3, 1, 1)

    combo_nscroll = Gtk.ComboBoxText()
    combo_nscroll.set_property("halign", Gtk.Align.START)
    combo_nscroll.set_tooltip_text(voc["natural-scroll-tooltip"])
    for item in ["disabled", "enabled"]:
        combo_nscroll.append(item, voc[item])
    combo_nscroll.set_active_id(settings["pointer-natural-scroll"])
    combo_nscroll.connect("changed", set_dict_key_from_combo, settings, "pointer-natural-scroll")
    grid.attach(combo_nscroll, 1, 3, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["scroll-factor"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 4, 1, 1)

    sb_sfactor = Gtk.SpinButton.new_with_range(0.1, 10, 0.1)
    sb_sfactor.set_value(settings["pointer-scroll-factor"])
    sb_sfactor.connect("value-changed", set_from_spinbutton, settings, "pointer-scroll-factor", 1)
    sb_sfactor.set_tooltip_text(voc["scroll-factor-tooltip"])
    grid.attach(sb_sfactor, 1, 4, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["left-handed"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 5, 1, 1)

    combo_left_handed = Gtk.ComboBoxText()
    combo_left_handed.set_property("halign", Gtk.Align.START)
    combo_left_handed.set_tooltip_text(voc["left-handed-tooltip"])
    for item in ["disabled", "enabled"]:
        combo_left_handed.append(item, voc[item])
    combo_left_handed.set_active_id(settings["pointer-left-handed"])
    combo_left_handed.connect("changed", set_dict_key_from_combo, settings, "pointer-left-handed")
    grid.attach(combo_left_handed, 1, 5, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["custom-field"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 6, 1, 1)

    entry_cname = Gtk.Entry()
    entry_cname.set_tooltip_text(voc["custom-field-name-tooltip"])
    entry_cname.set_placeholder_text(voc["name"])
    entry_cname.set_text(settings["pointer-custom-name"])
    entry_cname.connect("changed", set_from_entry, settings, "pointer-custom-name")
    grid.attach(entry_cname, 1, 6, 1, 1)

    entry_cname = Gtk.Entry()
    entry_cname.set_tooltip_text(voc["custom-field-value-tooltip"])
    entry_cname.set_placeholder_text(voc["value"])
    entry_cname.set_text(settings["pointer-custom-value"])
    entry_cname.connect("changed", set_from_entry, settings, "pointer-custom-value")
    grid.attach(entry_cname, 2, 6, 1, 1)

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

    lbl = Gtk.Label.new("{}:".format(voc["acceleration-profile"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 1, 1, 1)

    combo_aprofile = Gtk.ComboBoxText()
    combo_aprofile.set_property("halign", Gtk.Align.START)
    combo_aprofile.set_tooltip_text(voc["acceleration-profile-tooltip"])
    for item in ["flat", "adaptive"]:
        combo_aprofile.append(item, voc[item])
    combo_aprofile.set_active_id(settings["touchpad-accel-profile"])
    combo_aprofile.connect("changed", set_dict_key_from_combo, settings, "touchpad-accel-profile")
    grid.attach(combo_aprofile, 1, 1, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["acceleration"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 2, 1, 1)

    sb_acceleration = Gtk.SpinButton.new_with_range(-1, 1, 0.1)
    sb_acceleration.set_value(settings["touchpad-pointer-accel"])
    sb_acceleration.connect("value-changed", set_from_spinbutton, settings, "touchpad-pointer-accel", 1)
    sb_acceleration.set_tooltip_text(voc["acceleration-tooltip"])
    grid.attach(sb_acceleration, 1, 2, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["natural-scroll"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 3, 1, 1)

    combo_nscroll = Gtk.ComboBoxText()
    combo_nscroll.set_property("halign", Gtk.Align.START)
    combo_nscroll.set_tooltip_text(voc["natural-scroll-tooltip"])
    for item in ["disabled", "enabled"]:
        combo_nscroll.append(item, voc[item])
    combo_nscroll.set_active_id(settings["touchpad-natural-scroll"])
    combo_nscroll.connect("changed", set_dict_key_from_combo, settings, "touchpad-natural-scroll")
    grid.attach(combo_nscroll, 1, 3, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["scroll-factor"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 4, 1, 1)

    sb_sfactor = Gtk.SpinButton.new_with_range(0.1, 10, 0.1)
    sb_sfactor.set_value(settings["touchpad-scroll-factor"])
    sb_sfactor.connect("value-changed", set_from_spinbutton, settings, "touchpad-scroll-factor", 1)
    sb_sfactor.set_tooltip_text(voc["scroll-factor-tooltip"])
    grid.attach(sb_sfactor, 1, 4, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["scroll-method"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 5, 1, 1)

    combo_scroll_method = Gtk.ComboBoxText()
    combo_scroll_method.set_property("halign", Gtk.Align.START)
    combo_scroll_method.set_tooltip_text(voc["scroll-method-tooltip"])
    for item in [("two_finger", voc["two_finger"]), ("edge", voc["edge"]), ("on_button_down", voc["on_button_down"]),
                 ("none", "None")]:
        combo_scroll_method.append(item[0], item[1])
    combo_scroll_method.set_active_id(settings["touchpad-scroll-method"])
    combo_scroll_method.connect("changed", set_dict_key_from_combo, settings, "touchpad-scroll-method")
    grid.attach(combo_scroll_method, 1, 5, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["left-handed"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 6, 1, 1)

    combo_left_handed = Gtk.ComboBoxText()
    combo_left_handed.set_property("halign", Gtk.Align.START)
    combo_left_handed.set_tooltip_text(voc["left-handed-tooltip"])
    for item in ["disabled", "enabled"]:
        combo_left_handed.append(item, voc[item])
    combo_left_handed.set_active_id(settings["touchpad-left-handed"])
    combo_left_handed.connect("changed", set_dict_key_from_combo, settings, "touchpad-left-handed")
    grid.attach(combo_left_handed, 1, 6, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["tap"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 2, 1, 1, 1)

    combo_tap = Gtk.ComboBoxText()
    combo_tap.set_property("halign", Gtk.Align.START)
    combo_tap.set_tooltip_text(voc["tap-tooltip"])
    for item in ["enabled", "disabled"]:
        combo_tap.append(item, voc[item])
    combo_tap.set_active_id(settings["touchpad-tap"])
    combo_tap.connect("changed", set_dict_key_from_combo, settings, "touchpad-tap")
    grid.attach(combo_tap, 3, 1, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["tap-button-map"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 2, 2, 1, 1)

    combo_tap_btn_map = Gtk.ComboBoxText()
    combo_tap_btn_map.set_property("halign", Gtk.Align.START)
    combo_tap_btn_map.set_tooltip_text(voc["tap-button-map-tooltip"])
    for item in ["lrm", "lmr"]:
        combo_tap_btn_map.append(item, item)
    combo_tap_btn_map.set_active_id(settings["touchpad-tap-button-map"])
    combo_tap_btn_map.connect("changed", set_dict_key_from_combo, settings, "touchpad-tap-button-map")
    grid.attach(combo_tap_btn_map, 3, 2, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["middle-emulation"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 2, 3, 1, 1)

    combo_memulation = Gtk.ComboBoxText()
    combo_memulation.set_property("halign", Gtk.Align.START)
    combo_memulation.set_tooltip_text(voc["middle-emulation-tooltip"])
    for item in ["enabled", "disabled"]:
        combo_memulation.append(item, voc[item])
    combo_memulation.set_active_id(settings["touchpad-middle-emulation"])
    combo_memulation.connect("changed", set_dict_key_from_combo, settings, "touchpad-middle-emulation")
    grid.attach(combo_memulation, 3, 3, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["drag"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 2, 4, 1, 1)

    combo_drag = Gtk.ComboBoxText()
    combo_drag.set_property("halign", Gtk.Align.START)
    combo_drag.set_tooltip_text(voc["drag-tooltip"])
    for item in ["enabled", "disabled"]:
        combo_drag.append(item, voc[item])
    combo_drag.set_active_id(settings["touchpad-drag"])
    combo_drag.connect("changed", set_dict_key_from_combo, settings, "touchpad-drag")
    grid.attach(combo_drag, 3, 4, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["drag-lock"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 2, 5, 1, 1)

    combo_drag_lock = Gtk.ComboBoxText()
    combo_drag_lock.set_property("halign", Gtk.Align.START)
    combo_drag_lock.set_tooltip_text(voc["drag-lock-tooltip"])
    for item in ["disabled", "enabled"]:
        combo_drag_lock.append(item, voc[item])
    combo_drag_lock.set_active_id(settings["touchpad-drag-lock"])
    combo_drag_lock.connect("changed", set_dict_key_from_combo, settings, "touchpad-drag-lock")
    grid.attach(combo_drag_lock, 3, 5, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["dwt"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 2, 6, 1, 1)

    combo_dwt = Gtk.ComboBoxText()
    combo_dwt.set_property("halign", Gtk.Align.START)
    combo_dwt.set_tooltip_text(voc["dwt-tooltip"])
    for item in ["enabled", "disabled"]:
        combo_dwt.append(item, voc[item])
    combo_dwt.set_active_id(settings["touchpad-dwt"])
    combo_dwt.connect("changed", set_dict_key_from_combo, settings, "touchpad-dwt")
    grid.attach(combo_dwt, 3, 6, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["custom-field"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 7, 1, 1)

    entry_cname = Gtk.Entry()
    entry_cname.set_tooltip_text(voc["custom-field-name-tooltip"])
    entry_cname.set_placeholder_text(voc["name"])
    entry_cname.set_text(settings["touchpad-custom-name"])
    entry_cname.connect("changed", set_from_entry, settings, "touchpad-custom-name")
    grid.attach(entry_cname, 1, 7, 1, 1)

    entry_cname = Gtk.Entry()
    entry_cname.set_tooltip_text(voc["custom-field-value-tooltip"])
    entry_cname.set_placeholder_text(voc["value"])
    entry_cname.set_text(settings["touchpad-custom-value"])
    entry_cname.connect("changed", set_from_entry, settings, "touchpad-custom-value")
    grid.attach(entry_cname, 2, 7, 2, 1)

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

    defaults_btn = Gtk.Button.new_with_label(voc["restore-defaults"])
    defaults_btn.set_property("margin-top", 6)
    defaults_btn.set_property("halign", Gtk.Align.START)
    defaults_btn.set_tooltip_text(voc["restore-defaults-tooltip"])
    defaults_btn.connect("clicked", restore_defaults, {entry_sleep_cmd: 'swaymsg "output * dpms off"',
                                                       entry_resume_cmd: 'swaymsg "output * dpms on"'})
    grid.attach(defaults_btn, 1, 6, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["before-sleep"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 10, 1, 1)

    entry_b4_sleep = Gtk.Entry()
    entry_b4_sleep.set_width_chars(24)
    entry_b4_sleep.set_text(settings["before-sleep"])
    entry_b4_sleep.set_tooltip_text(voc["before-sleep-tooltip"])
    grid.attach(entry_b4_sleep, 1, 10, 1, 1)
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

    lbl = Gtk.Label()
    lbl.set_markup("<b>{}</b>".format(voc["other"]))
    lbl.set_property("halign", Gtk.Align.START)
    grid.attach(lbl, 0, 6, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["time-format"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 7, 1, 1)

    entry_time_format = Gtk.Entry()
    entry_time_format.set_tooltip_text(voc["time-format-tooltip"])
    entry_time_format.set_text(settings["gtklock-time-format"])
    entry_time_format.connect("changed", set_from_entry, settings, "gtklock-time-format")
    grid.attach(entry_time_format, 1, 7, 1, 1)

    lbl = Gtk.Label.new("{}:".format(voc["idle-timeout"]))
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 8, 1, 1)

    sb_gtklock_idle_timeout = Gtk.SpinButton.new_with_range(5, 3600, 1)
    sb_gtklock_idle_timeout.set_value(settings["gtklock-idle-timeout"])
    sb_gtklock_idle_timeout.connect("value-changed", set_int_from_spinbutton, settings, "gtklock-idle-timeout")
    sb_gtklock_idle_timeout.set_tooltip_text(voc["idle-timeout-tooltip"])
    grid.attach(sb_gtklock_idle_timeout, 1, 8, 1, 1)

    cb_disable_input_inhibitor = Gtk.CheckButton.new_with_label(voc["disable-input-inhibitor"])
    cb_disable_input_inhibitor.set_active(settings["gtklock-disable-input-inhibitor"])
    cb_disable_input_inhibitor.connect("toggled", set_key_from_checkbox, settings, "gtklock-disable-input-inhibitor")
    cb_disable_input_inhibitor.set_tooltip_text(voc["disable-input-inhibitor-tooltip"])
    grid.attach(cb_disable_input_inhibitor, 1, 9, 1, 1)

    frame.show_all()

    return frame


def drawer_tab(preset, preset_name):
    frame = Gtk.Frame()
    frame.set_label("  {}: Application drawer  ".format(preset_name))
    frame.set_label_align(0.5, 0.5)
    frame.set_property("hexpand", True)
    grid = Gtk.Grid()
    frame.add(grid)
    grid.set_property("margin", 12)
    grid.set_column_spacing(6)
    grid.set_row_spacing(6)

    cb_drawer_on = Gtk.CheckButton.new_with_label("Drawer on")
    cb_drawer_on.set_active(preset["launcher-on"])
    cb_drawer_on.connect("toggled", set_from_checkbutton, preset, "launcher-on")
    grid.attach(cb_drawer_on, 0, 0, 1, 1)

    lbl = Gtk.Label.new("Columns:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 1, 1, 1)

    sb_columns = Gtk.SpinButton.new_with_range(1, 9, 1)
    sb_columns.set_value(preset["launcher-columns"])
    sb_columns.connect("value-changed", set_int_from_spinbutton, preset, "launcher-columns")
    sb_columns.set_tooltip_text("Number of columns to show icons in.")
    grid.attach(sb_columns, 1, 1, 1, 1)

    lbl = Gtk.Label.new("Icon size:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 2, 1, 1)

    sb_icon_size = Gtk.SpinButton.new_with_range(8, 256, 1)
    sb_icon_size.set_value(preset["launcher-icon-size"])
    sb_icon_size.connect("value-changed", set_int_from_spinbutton, preset, "launcher-icon-size")
    sb_icon_size.set_tooltip_text("Application icon size.")
    grid.attach(sb_icon_size, 1, 2, 1, 1)

    lbl = Gtk.Label.new("File search columns:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 3, 1, 1)

    sb_fs_columns = Gtk.SpinButton.new_with_range(1, 9, 1)
    sb_fs_columns.set_value(preset["launcher-file-search-columns"])
    sb_fs_columns.connect("value-changed", set_int_from_spinbutton, preset, "launcher-file-search-columns")
    sb_fs_columns.set_tooltip_text("Number of columns to show file search result in.")
    grid.attach(sb_fs_columns, 1, 3, 1, 1)

    cb_search_files = Gtk.CheckButton.new_with_label("search files")
    cb_search_files.set_active(preset["launcher-search-files"])
    cb_search_files.connect("toggled", set_from_checkbutton, preset, "launcher-search-files")
    grid.attach(cb_search_files, 2, 3, 1, 1)

    cb_categories = Gtk.CheckButton.new_with_label("Show category menu")
    cb_categories.set_tooltip_text("Show categories menu (icons) on top.")
    cb_categories.set_active(preset["launcher-categories"])
    cb_categories.connect("toggled", set_from_checkbutton, preset, "launcher-categories")
    grid.attach(cb_categories, 0, 4, 1, 1)

    cb_resident = Gtk.CheckButton.new_with_label("Keep resident")
    cb_resident.set_tooltip_text("Keep drawer running in the background.")
    cb_resident.set_active(preset["launcher-resident"])
    cb_resident.connect("toggled", set_from_checkbutton, preset, "launcher-resident")
    grid.attach(cb_resident, 0, 5, 1, 1)

    cb_overlay = Gtk.CheckButton.new_with_label("Open on overlay")
    cb_overlay.set_tooltip_text("Open drawer on the overlay layer.")
    cb_overlay.set_active(preset["launcher-overlay"])
    cb_overlay.connect("toggled", set_from_checkbutton, preset, "launcher-overlay")
    grid.attach(cb_overlay, 0, 6, 1, 1)

    frame.show_all()

    return frame


def dock_tab(preset, preset_name, outputs):
    frame = Gtk.Frame()
    frame.set_label("  {}: Dock  ".format(preset_name))
    frame.set_label_align(0.5, 0.5)
    frame.set_property("hexpand", True)
    grid = Gtk.Grid()
    frame.add(grid)
    grid.set_property("margin", 12)
    grid.set_column_spacing(6)
    grid.set_row_spacing(6)

    cb_dock_on = Gtk.CheckButton.new_with_label("Dock on")
    cb_dock_on.set_active(preset["dock-on"])
    cb_dock_on.connect("toggled", set_from_checkbutton, preset, "dock-on")
    grid.attach(cb_dock_on, 0, 0, 1, 1)

    lbl = Gtk.Label.new("Position:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 1, 1, 1)

    combo_position = Gtk.ComboBoxText()
    combo_position.set_property("halign", Gtk.Align.START)
    grid.attach(combo_position, 1, 1, 1, 1)
    for item in ["bottom", "top", "left"]:
        combo_position.append(item, item)
    combo_position.set_active_id(preset["dock-position"])
    combo_position.connect("changed", set_dict_key_from_combo, preset, "dock-position")

    lbl = Gtk.Label.new("Alignment:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 2, 1, 1)

    combo_alignment = Gtk.ComboBoxText()
    combo_alignment.set_property("halign", Gtk.Align.START)
    grid.attach(combo_alignment, 1, 2, 1, 1)
    for item in ["center", "start", "end"]:
        combo_alignment.append(item, item)
    combo_alignment.set_active_id(preset["dock-alignment"])
    combo_alignment.connect("changed", set_dict_key_from_combo, preset, "dock-alignment")

    lbl = Gtk.Label.new("Icon size:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 3, 1, 1)

    sb_icon_size = Gtk.SpinButton.new_with_range(8, 256, 1)
    sb_icon_size.set_value(preset["dock-icon-size"])
    sb_icon_size.connect("value-changed", set_int_from_spinbutton, preset, "dock-icon-size")
    sb_icon_size.set_tooltip_text("Application icon size.")
    grid.attach(sb_icon_size, 1, 3, 1, 1)

    lbl = Gtk.Label.new("Margin:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 4, 1, 1)

    sb_margin = Gtk.SpinButton.new_with_range(0, 256, 1)
    sb_margin.set_value(preset["dock-margin"])
    sb_margin.connect("value-changed", set_int_from_spinbutton, preset, "dock-margin")
    grid.attach(sb_margin, 1, 4, 1, 1)

    lbl = Gtk.Label.new("Output:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 5, 1, 1)

    combo_outputs = Gtk.ComboBoxText()
    combo_outputs.set_property("halign", Gtk.Align.START)
    grid.attach(combo_outputs, 1, 5, 1, 1)
    combo_outputs.append("Any", "Any")
    for item in outputs:
        combo_outputs.append(item, item)
    combo_outputs.set_active_id(preset["dock-output"])
    combo_outputs.connect("changed", set_dict_key_from_combo, preset, "dock-output")

    cb_permanent = Gtk.CheckButton.new_with_label("Permanent")
    cb_permanent.set_active(preset["dock-permanent"])
    cb_permanent.connect("toggled", set_from_checkbutton, preset, "dock-permanent")
    cb_permanent.set_tooltip_text("Leave the dock resident, but w/o the hotspot.")
    grid.attach(cb_permanent, 0, 6, 1, 1)

    cb_full = Gtk.CheckButton.new_with_label("Full width/height")
    cb_full.set_active(preset["dock-full"])
    cb_full.connect("toggled", set_from_checkbutton, preset, "dock-full")
    cb_full.set_tooltip_text("Take full screen width/height.")
    grid.attach(cb_full, 0, 7, 1, 1)

    cb_autohide = Gtk.CheckButton.new_with_label("Auto-show/hide")
    cb_autohide.set_active(preset["dock-autohide"])
    cb_autohide.connect("toggled", set_from_checkbutton, preset, "dock-autohide")
    cb_autohide.set_tooltip_text("Auto-hide dock, show on hotspot pointed.")
    grid.attach(cb_autohide, 0, 8, 1, 1)

    cb_exclusive = Gtk.CheckButton.new_with_label("Exclusive zone")
    cb_exclusive.set_active(preset["dock-exclusive"])
    cb_exclusive.connect("toggled", set_from_checkbutton, preset, "dock-exclusive")
    cb_exclusive.set_tooltip_text("Move other windows away.")
    grid.attach(cb_exclusive, 0, 9, 1, 1)

    frame.show_all()

    return frame


def bar_tab(preset, preset_name):
    frame = Gtk.Frame()
    frame.set_label("  {}: Exit menu  ".format(preset_name))
    frame.set_label_align(0.5, 0.5)
    frame.set_property("hexpand", True)
    grid = Gtk.Grid()
    frame.add(grid)
    grid.set_property("margin", 12)
    grid.set_column_spacing(6)
    grid.set_row_spacing(6)

    cb_bar_on = Gtk.CheckButton.new_with_label("Exit menu on")
    cb_bar_on.set_active(preset["exit-on"])
    cb_bar_on.connect("toggled", set_from_checkbutton, preset, "exit-on")
    grid.attach(cb_bar_on, 0, 0, 1, 1)

    lbl = Gtk.Label.new("Position:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 1, 1, 1)

    combo_position = Gtk.ComboBoxText()
    combo_position.set_property("halign", Gtk.Align.START)
    grid.attach(combo_position, 1, 1, 1, 1)
    for item in ["center", "top", "bottom", "left", "right"]:
        combo_position.append(item, item)
    combo_position.set_active_id(preset["exit-position"])
    combo_position.connect("changed", set_dict_key_from_combo, preset, "exit-position")

    lbl = Gtk.Label.new("Alignment:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 2, 1, 1)

    combo_alignment = Gtk.ComboBoxText()
    combo_alignment.set_property("halign", Gtk.Align.START)
    grid.attach(combo_alignment, 1, 2, 1, 1)
    for item in ["middle", "start", "end"]:
        combo_alignment.append(item, item)
    combo_alignment.set_active_id(preset["exit-alignment"])
    combo_alignment.connect("changed", set_dict_key_from_combo, preset, "exit-alignment")
    combo_alignment.set_tooltip_text("Alignment in full width/height.")

    lbl = Gtk.Label.new("Icon size:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 3, 1, 1)

    sb_icon_size = Gtk.SpinButton.new_with_range(8, 256, 1)
    sb_icon_size.set_value(preset["exit-icon-size"])
    sb_icon_size.connect("value-changed", set_int_from_spinbutton, preset, "exit-icon-size")
    sb_icon_size.set_tooltip_text("Item icon size.")
    grid.attach(sb_icon_size, 1, 3, 1, 1)

    lbl = Gtk.Label.new("Margin:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 4, 1, 1)

    sb_margin = Gtk.SpinButton.new_with_range(0, 256, 1)
    sb_margin.set_value(preset["exit-margin"])
    sb_margin.connect("value-changed", set_int_from_spinbutton, preset, "exit-margin")
    grid.attach(sb_margin, 1, 4, 1, 1)

    cb_full = Gtk.CheckButton.new_with_label("Full width/height")
    cb_full.set_active(preset["exit-full"])
    cb_full.connect("toggled", set_from_checkbutton, preset, "exit-full")
    cb_full.set_tooltip_text("Take full screen width/height.")
    grid.attach(cb_full, 0, 5, 1, 1)

    frame.show_all()

    return frame


def notification_tab(preset, preset_name):
    frame = Gtk.Frame()
    frame.set_label("  {}: Notification center  ".format(preset_name))
    frame.set_label_align(0.5, 0.5)
    frame.set_property("hexpand", True)
    grid = Gtk.Grid()
    frame.add(grid)
    grid.set_property("margin", 12)
    grid.set_column_spacing(6)
    grid.set_row_spacing(6)

    lbl = Gtk.Label.new("Horizontal alignment:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 1, 1, 1)

    combo_position_x = Gtk.ComboBoxText()
    combo_position_x.set_property("halign", Gtk.Align.START)
    grid.attach(combo_position_x, 1, 1, 1, 1)
    for item in ["left", "right", "center"]:
        combo_position_x.append(item, item)
    combo_position_x.set_active_id(preset["swaync-positionX"])
    combo_position_x.connect("changed", set_dict_key_from_combo, preset, "swaync-positionX")

    lbl = Gtk.Label.new("Vertical alignment:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 2, 1, 1)

    combo_position_x = Gtk.ComboBoxText()
    combo_position_x.set_property("halign", Gtk.Align.START)
    grid.attach(combo_position_x, 1, 2, 1, 1)
    for item in ["top", "bottom"]:
        combo_position_x.append(item, item)
    combo_position_x.set_active_id(preset["swaync-positionY"])
    combo_position_x.connect("changed", set_dict_key_from_combo, preset, "swaync-positionY")

    lbl = Gtk.Label.new("Control center width:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 3, 1, 1)

    sb_cc_width = Gtk.SpinButton.new_with_range(0, 1000, 1)
    sb_cc_width.set_value(preset["swaync-control-center-width"])
    sb_cc_width.connect("value-changed", set_int_from_spinbutton, preset, "swaync-control-center-width")
    grid.attach(sb_cc_width, 1, 3, 1, 1)

    lbl = Gtk.Label.new("Notification window width:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 4, 1, 1)

    sb_window_width = Gtk.SpinButton.new_with_range(0, 1000, 1)
    sb_window_width.set_value(preset["swaync-control-center-width"])
    sb_window_width.connect("value-changed", set_int_from_spinbutton, preset, "swaync-notification-window-width")
    grid.attach(sb_window_width, 1, 4, 1, 1)

    cb_swaync_mpris = Gtk.CheckButton.new_with_label("MPRIS widget")
    cb_swaync_mpris.set_active(preset["swaync-mpris"])
    cb_swaync_mpris.connect("toggled", set_from_checkbutton, preset, "swaync-mpris")
    cb_swaync_mpris.set_tooltip_text("Show MPRIS media player control widget")
    grid.attach(cb_swaync_mpris, 1, 5, 1, 1)

    frame.show_all()

    return frame


def gtklock_preset_tab(preset, preset_name):
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
        lbl.set_markup("<b>Userinfo module</b>")
        lbl.set_property("halign", Gtk.Align.START)
        grid.attach(lbl, 0, 1, 1, 1)

        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        grid.attach(box, 1, 1, 3, 1)

        cb_userinfo_round_image = Gtk.CheckButton.new_with_label("round image")
        cb_userinfo_round_image.set_active(preset["gtklock-userinfo-round-image"])
        cb_userinfo_round_image.connect("toggled", set_from_checkbutton, preset, "gtklock-userinfo-round-image")
        cb_userinfo_round_image.set_tooltip_text("user avatar shape")
        box.pack_start(cb_userinfo_round_image, False, False, 0)

        cb_userinfo_vertical_layout = Gtk.CheckButton.new_with_label("vertical layout")
        cb_userinfo_vertical_layout.set_active(preset["gtklock-userinfo-vertical-layout"])
        cb_userinfo_vertical_layout.connect("toggled", set_from_checkbutton, preset, "gtklock-userinfo-vertical-layout")
        cb_userinfo_vertical_layout.set_tooltip_text("user name next to the avatar")
        box.pack_start(cb_userinfo_vertical_layout, False, False, 0)

        cb_userinfo_under_clock = Gtk.CheckButton.new_with_label("under clock")
        cb_userinfo_under_clock.set_active(preset["gtklock-userinfo-under-clock"])
        cb_userinfo_under_clock.connect("toggled", set_from_checkbutton, preset, "gtklock-userinfo-under-clock")
        cb_userinfo_under_clock.set_tooltip_text("user avatar and name below the clock")
        box.pack_start(cb_userinfo_under_clock, False, False, 0)

    if gtklock_module_path("powerbar"):
        lbl = Gtk.Label()
        lbl.set_markup("<b>Powerbar module</b>")
        lbl.set_property("halign", Gtk.Align.START)
        grid.attach(lbl, 0, 2, 1, 1)

        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        grid.attach(box, 1, 2, 3, 1)

        cb_powerbar_show_labels = Gtk.CheckButton.new_with_label("show labels")
        cb_powerbar_show_labels.set_active(preset["gtklock-powerbar-show-labels"])
        cb_powerbar_show_labels.connect("toggled", set_from_checkbutton, preset, "gtklock-powerbar-show-labels")
        box.pack_start(cb_powerbar_show_labels, False, False, 0)

        cb_powerbar_linked_buttons = Gtk.CheckButton.new_with_label("linked buttons")
        cb_powerbar_linked_buttons.set_active(preset["gtklock-powerbar-linked-buttons"])
        cb_powerbar_linked_buttons.connect("toggled", set_from_checkbutton, preset, "gtklock-powerbar-linked-buttons")
        box.pack_start(cb_powerbar_linked_buttons, False, False, 0)

    if gtklock_module_path("playerctl"):
        lbl = Gtk.Label()
        lbl.set_markup("<b>Playerctl module</b>")
        lbl.set_property("halign", Gtk.Align.START)
        grid.attach(lbl, 0, 3, 1, 1)

        lbl = Gtk.Label.new("Art size:")
        lbl.set_property("halign", Gtk.Align.END)
        grid.attach(lbl, 0, 4, 1, 1)

        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        grid.attach(box, 1, 4, 3, 1)

        sb_gtklock_playerctl_art_size = Gtk.SpinButton.new_with_range(0, 256, 1)
        sb_gtklock_playerctl_art_size.set_value(preset["gtklock-playerctl-art-size"])
        sb_gtklock_playerctl_art_size.connect("value-changed", set_int_from_spinbutton, preset,
                                              "gtklock-playerctl-art-size")
        sb_gtklock_playerctl_art_size.set_tooltip_text("album cover size in pixels; set 0 to hide")
        box.pack_start(sb_gtklock_playerctl_art_size, False, False, 0)

        lbl = Gtk.Label.new("Position:")
        lbl.set_property("halign", Gtk.Align.END)
        box.pack_start(lbl, False, False, 6)

        combo_gtklock_playerctl_position = Gtk.ComboBoxText()
        combo_gtklock_playerctl_position.set_property("halign", Gtk.Align.START)
        box.pack_start(combo_gtklock_playerctl_position, False, False, 0)
        for item in ["top-left", "top-center", "top-right", "bottom-left", "bottom-center", "bottom-right",
                     "above-clock", "under-clock"]:
            combo_gtklock_playerctl_position.append(item, item)
        combo_gtklock_playerctl_position.set_active_id(preset["gtklock-playerctl-position"])
        combo_gtklock_playerctl_position.connect("changed", set_dict_key_from_combo, preset,
                                                 "gtklock-playerctl-position")
        combo_gtklock_playerctl_position.set_tooltip_text("playerctl widget placement")

        cb_gtklock_playerctl_show_hidden = Gtk.CheckButton.new_with_label("always show")
        cb_gtklock_playerctl_show_hidden.set_active(preset["gtklock-playerctl-show-hidden"])
        cb_gtklock_playerctl_show_hidden.connect("toggled", set_from_checkbutton, preset,
                                                 "gtklock-playerctl-show-hidden")
        grid.attach(cb_gtklock_playerctl_show_hidden, 1, 5, 3, 1)

    frame.show_all()

    return frame


def panel_styling_tab(settings, preset, preset_name):
    frame = Gtk.Frame()
    frame.set_label("  {}: Panel & css styles  ".format(preset_name))
    frame.set_label_align(0.5, 0.5)
    frame.set_property("hexpand", True)
    grid = Gtk.Grid()
    frame.add(grid)
    grid.set_property("margin", 12)
    grid.set_column_spacing(6)
    grid.set_row_spacing(6)

    lbl = Gtk.Label.new("Panel config name:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 0, 1, 1)

    entry_panel = Gtk.Entry()
    entry_panel.set_placeholder_text("config")
    entry_panel.set_tooltip_text("Panel config file name.")
    entry_panel.set_property("halign", Gtk.Align.START)
    entry_panel.set_text(settings["panel-custom"])
    entry_panel.connect("changed", set_from_entry, settings, "panel-custom")
    grid.attach(entry_panel, 1, 0, 1, 1)

    lbl = Gtk.Label.new("Panel css name:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 1, 1, 1)

    entry_panel_css = Gtk.Entry()
    entry_panel_css.set_placeholder_text("style.css")
    entry_panel_css.set_tooltip_text("Panel css file name.")
    entry_panel_css.set_property("halign", Gtk.Align.START)
    entry_panel_css.set_text(preset["panel-css"])
    entry_panel_css.connect("changed", set_from_entry, preset, "panel-css")
    grid.attach(entry_panel_css, 1, 1, 1, 1)

    lbl = Gtk.Label.new("Drawer css name:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 2, 1, 1)

    entry_panel_css = Gtk.Entry()
    entry_panel_css.set_placeholder_text("drawer.css")
    entry_panel_css.set_property("halign", Gtk.Align.START)
    entry_panel_css.set_text(preset["launcher-css"])
    entry_panel_css.connect("changed", set_from_entry, preset, "launcher-css")
    grid.attach(entry_panel_css, 1, 2, 1, 1)

    lbl = Gtk.Label.new("Dock css name:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 3, 1, 1)

    entry_panel_css = Gtk.Entry()
    entry_panel_css.set_placeholder_text("style.css")
    entry_panel_css.set_property("halign", Gtk.Align.START)
    entry_panel_css.set_text(preset["dock-css"])
    entry_panel_css.connect("changed", set_from_entry, preset, "dock-css")
    grid.attach(entry_panel_css, 1, 3, 1, 1)

    lbl = Gtk.Label.new("Exit menu css name:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 4, 1, 1)

    entry_panel_css = Gtk.Entry()
    entry_panel_css.set_placeholder_text("style.css")
    entry_panel_css.set_property("halign", Gtk.Align.START)
    entry_panel_css.set_text(preset["exit-css"])
    entry_panel_css.connect("changed", set_from_entry, preset, "exit-css")
    grid.attach(entry_panel_css, 1, 4, 1, 1)

    frame.show_all()

    return frame
