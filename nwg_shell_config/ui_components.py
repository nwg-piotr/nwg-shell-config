import subprocess

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from nwg_shell_config.tools import is_command, get_lat_lon


def set_from_checkbutton(cb, settings, key):
    settings[key] = cb.get_active()


def set_from_spinbutton(cb, settings, key, ndigits):
    settings[key] = round(cb.get_value(), ndigits)


def set_int_from_spinbutton(cb, settings, key):
    settings[key] = int(cb.get_value())


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


def set_browser_from_combo(combo, entry, browsers_dict):
    entry.set_text(browsers_dict[combo.get_active_id()])


def set_dict_key_from_combo(combo, settings, key):
    settings[key] = combo.get_active_id()


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


def screen_tab(settings):
    frame = Gtk.Frame()
    frame.set_label("  Common: Screen settings  ")
    frame.set_label_align(0.5, 0.5)
    frame.set_property("hexpand", True)
    grid = Gtk.Grid()
    frame.add(grid)
    grid.set_property("margin", 6)
    grid.set_column_spacing(6)
    grid.set_row_spacing(6)

    box = Gtk.Box(Gtk.Orientation.HORIZONTAL, 6)
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
    btn.set_label("Displays")
    btn.connect("clicked", launch, "nwg-displays")
    box.pack_start(btn, False, True, 0)

    btn = Gtk.Button()
    btn.set_property("name", "app-btn")
    btn.set_always_show_image(True)
    btn.set_image_position(Gtk.PositionType.TOP)
    img = Gtk.Image.new_from_icon_name("azote", Gtk.IconSize.DIALOG)
    btn.set_image(img)
    btn.set_label("Wallpapers")
    btn.connect("clicked", launch, "azote")
    box.pack_start(btn, False, True, 0)

    btn = Gtk.Button()
    btn.set_property("name", "app-btn")
    btn.set_always_show_image(True)
    btn.set_image_position(Gtk.PositionType.TOP)
    img = Gtk.Image.new_from_icon_name("nwg-look", Gtk.IconSize.DIALOG)
    btn.set_image(img)
    btn.set_label("Look & feel")
    btn.connect("clicked", launch, "nwg-look")
    box.pack_start(btn, False, True, 0)

    btn = Gtk.Button()
    btn.set_property("name", "app-btn")
    btn.set_always_show_image(True)
    btn.set_image_position(Gtk.PositionType.TOP)
    img = Gtk.Image.new_from_icon_name("nwg-panel", Gtk.IconSize.DIALOG)
    btn.set_image(img)
    btn.set_label("Panel settings")
    btn.connect("clicked", launch, "nwg-panel-config")
    box.pack_start(btn, False, True, 0)

    lbl = Gtk.Label()
    lbl.set_markup("<b>Autotiling</b>")
    lbl.set_property("margin-top", 6)
    lbl.set_property("margin-bottom", 6)
    lbl.set_property("halign", Gtk.Align.START)
    grid.attach(lbl, 0, 1, 1, 1)

    cb_autotiling_on = Gtk.CheckButton.new_with_label("on")
    cb_autotiling_on.set_active(settings["autotiling-on"])
    cb_autotiling_on.connect("toggled", set_from_checkbutton, settings, "autotiling-on")
    cb_autotiling_on.set_tooltip_text("Automates changing the horizontal/vertical\nwindow split orientation.")
    grid.attach(cb_autotiling_on, 1, 1, 1, 1)

    lbl = Gtk.Label.new("Workspaces:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 2, 1, 1)

    entry = Gtk.Entry()
    entry.set_placeholder_text("1 2 3 4 5 6 7 8")
    entry.set_text(settings["autotiling-workspaces"])
    entry.set_tooltip_text("Defines which workspaces to use autotiling on.\nSee 'autotiling -h`.")
    entry.connect("changed", set_from_workspaces, settings)
    grid.attach(entry, 1, 2, 1, 1)

    lbl = Gtk.Label()
    lbl.set_markup("<b>Night light</b>")
    lbl.set_property("margin-top", 6)
    lbl.set_property("margin-bottom", 6)
    lbl.set_property("halign", Gtk.Align.START)
    grid.attach(lbl, 0, 3, 1, 1)

    cb_night_light_on = Gtk.CheckButton.new_with_label("on")
    cb_night_light_on.set_active(settings["night-on"])
    cb_night_light_on.connect("toggled", set_from_checkbutton, settings, "night-on")
    cb_night_light_on.set_tooltip_text("Determines if to use `wlsunset'.")
    grid.attach(cb_night_light_on, 1, 3, 1, 1)

    lbl = Gtk.Label.new("Latitude:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 2, 4, 1, 1)

    sb_lat = Gtk.SpinButton.new_with_range(-90.0, 90.0, 0.1)
    sb_lat.set_tooltip_text("Your location latitude\n'wlsunset -l'")
    sb_lat.set_digits(4)
    sb_lat.set_value(settings["night-lat"])
    sb_lat.connect("value-changed", set_from_spinbutton, settings, "night-lat", 4)
    grid.attach(sb_lat, 3, 4, 1, 1)

    lbl = Gtk.Label.new("Temp low:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 4, 1, 1)

    sb_temp_low = Gtk.SpinButton.new_with_range(1000, 10000, 100)
    sb_temp_low.set_tooltip_text("Night light color temperature\n'wlsunset -t'")
    sb_temp_low.set_value(settings["night-temp-low"])
    sb_temp_low.connect("value-changed", set_int_from_spinbutton, settings, "night-temp-low")
    grid.attach(sb_temp_low, 1, 4, 1, 1)

    lbl = Gtk.Label.new("Longitude:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 2, 5, 1, 1)

    sb_lon = Gtk.SpinButton.new_with_range(-180, 180, 0.1)
    sb_lon.set_tooltip_text("Your location longitude\n'wlsunset -L'")
    sb_lon.set_value(settings["night-long"])
    sb_lon.connect("value-changed", set_from_spinbutton, settings, "night-long", 4)
    sb_lon.set_digits(4)
    grid.attach(sb_lon, 3, 5, 1, 1)

    if (sb_lat.get_value() == -1.0 and sb_lon.get_value()) == -1.0 \
            or (sb_lat.get_value() == 0.0 and sb_lon.get_value() == 0.0):
        update_lat_lon(None, sb_lat, sb_lon)

    lbl = Gtk.Label.new("Temp high:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 5, 1, 1)

    sb_temp_high = Gtk.SpinButton.new_with_range(1000, 10000, 100)
    sb_temp_high.set_tooltip_text("Day light color temperature\n'wlsunset -T'")
    sb_temp_high.set_value(settings["night-temp-high"])
    sb_temp_high.connect("value-changed", set_int_from_spinbutton, settings, "night-temp-high")
    grid.attach(sb_temp_high, 1, 5, 1, 1)

    lbl = Gtk.Label.new("Gamma:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 6, 1, 1)

    btn = Gtk.Button.new_with_label("Calculate Lat/Long")
    btn.set_tooltip_text("If you were online during the first run, the Lat/Long"
                         "\nvalues should already reflect your timezone settings.\n"
                         "Push the button if something went wrong\nAND if you're online now.")
    btn.connect("clicked", update_lat_lon, sb_lat, sb_lon)
    grid.attach(btn, 3, 6, 1, 1)

    sb_gamma = Gtk.SpinButton.new_with_range(0.1, 10.0, 0.1)
    sb_gamma.set_value(settings["night-gamma"])
    sb_gamma.connect("value-changed", set_from_spinbutton, settings, "night-gamma", 1)
    sb_gamma.set_tooltip_text("Monitor gamma\n'wlsunset -g'")
    grid.attach(sb_gamma, 1, 6, 1, 1)

    lbl = Gtk.Label()
    lbl.set_markup("<b>Help widget</b>")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 7, 1, 1)

    cb_help_on = Gtk.CheckButton.new_with_label("on")
    cb_help_on.set_active(settings["show-help"])
    cb_help_on.connect("toggled", set_from_checkbutton, settings, "show-help")
    cb_help_on.set_tooltip_text("Determines if to display the 'conky-like' help widget.")
    grid.attach(cb_help_on, 1, 7, 1, 1)

    lbl = Gtk.Label()
    lbl.set_markup("<b>Desktop style</b>")
    lbl.set_property("halign", Gtk.Align.END)
    lbl.set_property("margin-top", 12)
    grid.attach(lbl, 0, 8, 1, 1)

    combo = Gtk.ComboBoxText()
    combo.set_property("halign", Gtk.Align.START)
    grid.attach(combo, 1, 8, 1, 2)
    for p in ["preset-0", "preset-1", "preset-2", "preset-3", "custom"]:
        combo.append(p, p)
    combo.set_active_id(settings["panel-preset"])
    combo.connect("changed", set_dict_key_from_combo, settings, "panel-preset")
    combo.set_tooltip_text("Switches current desktop preset.")
    frame.show_all()

    return frame


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

    entry_terminal = Gtk.Entry()
    entry_terminal.set_tooltip_text("Command to run terminal emulator")
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
    entry_fm.set_tooltip_text("Command to run file manager")
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
    entry_te.set_tooltip_text("Command to run text editor")
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

    entry_browser = Gtk.Entry()
    entry_browser.set_tooltip_text("Command to run web browser")
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
    combo.connect("changed", set_browser_from_combo, entry_browser, browsers)
    for key in ["chromium", "google-chrome-stable", "firefox", "qutebrowser", "epiphany", "surf"]:
        if key in browsers:
            combo.set_active_id(key)
            break

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


def keyboard_tab(settings):
    frame = Gtk.Frame()
    frame.set_label("  Common: Keyboard  ")
    frame.set_label_align(0.5, 0.5)
    frame.set_property("hexpand", True)
    grid = Gtk.Grid()
    frame.add(grid)
    grid.set_property("margin", 12)
    grid.set_column_spacing(6)
    grid.set_row_spacing(6)

    cb_keyboard_use_settings = Gtk.CheckButton.new_with_label("Use these settings")
    cb_keyboard_use_settings.set_property("halign", Gtk.Align.START)
    cb_keyboard_use_settings.set_property("margin-bottom", 6)
    cb_keyboard_use_settings.set_tooltip_text("Determines if to export the 'keyboard' config include.")
    grid.attach(cb_keyboard_use_settings, 0, 0, 2, 1)

    lbl = Gtk.Label.new("Layout:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 1, 1, 1)

    entry_layout = Gtk.Entry()
    entry_layout.set_tooltip_text("Layout of the keyboard like 'us' or 'de'.\nMultiple layouts can be specified\n"
                                  "by separating them with commas.")
    entry_layout.set_text(settings["keyboard-xkb-layout"])
    entry_layout.connect("changed", set_from_entry, settings, "keyboard-xkb-layout")
    grid.attach(entry_layout, 1, 1, 1, 1)

    lbl = Gtk.Label.new("Variant:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 2, 1, 1)

    entry_variant = Gtk.Entry()
    entry_variant.set_tooltip_text("Variant of the keyboard like 'dvorak' or 'colemak'.")
    entry_variant.set_text(settings["keyboard-xkb-variant"])
    entry_variant.connect("changed", set_from_entry, settings, "keyboard-xkb-variant")
    grid.attach(entry_variant, 1, 2, 1, 1)

    lbl = Gtk.Label.new("Repeat delay:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 3, 1, 1)

    sb_repeat_delay = Gtk.SpinButton.new_with_range(1, 6000, 1)
    sb_repeat_delay.set_value(settings["keyboard-repeat-delay"])
    sb_repeat_delay.connect("value-changed", set_int_from_spinbutton, settings, "keyboard-repeat-delay")
    sb_repeat_delay.set_tooltip_text("Amount of time a key must be held before it starts repeating.")
    grid.attach(sb_repeat_delay, 1, 3, 1, 1)

    lbl = Gtk.Label.new("Repeat rate:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 4, 1, 1)

    sb_repeat_rate = Gtk.SpinButton.new_with_range(1, 4000, 1)
    sb_repeat_rate.set_value(settings["keyboard-repeat-rate"])
    sb_repeat_rate.connect("value-changed", set_int_from_spinbutton, settings, "keyboard-repeat-rate")
    sb_repeat_rate.set_tooltip_text("Frequency of key repeats once the repeat_delay has passed.")
    grid.attach(sb_repeat_rate, 1, 4, 1, 1)

    lbl = Gtk.Label.new("CapsLock:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 5, 1, 1)

    combo_caps = Gtk.ComboBoxText()
    combo_caps.set_property("halign", Gtk.Align.START)
    combo_caps.set_tooltip_text("Initially enables or disables CapsLock on startup.")
    for item in ["disabled", "enabled"]:
        combo_caps.append(item, item)
    combo_caps.set_active_id(settings["keyboard-xkb-capslock"])
    combo_caps.connect("changed", set_dict_key_from_combo, settings, "keyboard-xkb-capslock")
    grid.attach(combo_caps, 1, 5, 1, 1)

    lbl = Gtk.Label.new("NumLock:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 6, 1, 1)

    combo_num = Gtk.ComboBoxText()
    combo_num.set_property("halign", Gtk.Align.START)
    combo_num.set_tooltip_text("Initially enables or disables NumLock on startup.")
    for item in ["disabled", "enabled"]:
        combo_num.append(item, item)
    combo_num.set_active_id(settings["keyboard-xkb-numlock"])
    combo_num.connect("changed", set_dict_key_from_combo, settings, "keyboard-xkb-numlock")
    grid.attach(combo_num, 1, 6, 1, 1)

    frame.show_all()

    return frame


def pointer_tab(settings):
    frame = Gtk.Frame()
    frame.set_label("  Common: Pointer device  ")
    frame.set_label_align(0.5, 0.5)
    frame.set_property("hexpand", True)
    grid = Gtk.Grid()
    frame.add(grid)
    grid.set_property("margin", 12)
    grid.set_column_spacing(6)
    grid.set_row_spacing(6)

    cb_pointer_use_settings = Gtk.CheckButton.new_with_label("Use these settings")
    cb_pointer_use_settings.set_property("halign", Gtk.Align.START)
    cb_pointer_use_settings.set_property("margin-bottom", 6)
    cb_pointer_use_settings.set_tooltip_text("Determines if to export the 'pointer' config include.")
    grid.attach(cb_pointer_use_settings, 0, 0, 2, 1)

    lbl = Gtk.Label.new("Acceleration profile:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 1, 1, 1)

    combo_aprofile = Gtk.ComboBoxText()
    combo_aprofile.set_property("halign", Gtk.Align.START)
    combo_aprofile.set_tooltip_text("Sets the pointer acceleration profile.")
    for item in ["flat", "adaptive"]:
        combo_aprofile.append(item, item)
    combo_aprofile.set_active_id(settings["pointer-accel-profile"])
    combo_aprofile.connect("changed", set_dict_key_from_combo, settings, "pointer-accel-profile")
    grid.attach(combo_aprofile, 1, 1, 1, 1)

    lbl = Gtk.Label.new("Acceleration:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 2, 1, 1)

    sb_acceleration = Gtk.SpinButton.new_with_range(-1, 1, 0.1)
    sb_acceleration.set_value(settings["pointer-pointer-accel"])
    sb_acceleration.connect("value-changed", set_from_spinbutton, settings, "pointer-pointer-accel", 1)
    sb_acceleration.set_tooltip_text("Changes the pointer acceleration.")
    grid.attach(sb_acceleration, 1, 2, 1, 1)

    lbl = Gtk.Label.new("Natural scroll:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 3, 1, 1)

    combo_nscroll = Gtk.ComboBoxText()
    combo_nscroll.set_property("halign", Gtk.Align.START)
    combo_nscroll.set_tooltip_text("Enables or disables natural (inverted) scrolling.")
    for item in ["disabled", "enabled"]:
        combo_nscroll.append(item, item)
    combo_nscroll.set_active_id(settings["pointer-natural-scroll"])
    combo_nscroll.connect("changed", set_dict_key_from_combo, settings, "pointer-natural-scroll")
    grid.attach(combo_nscroll, 1, 3, 1, 1)

    lbl = Gtk.Label.new("Scroll factor:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 4, 1, 1)

    sb_sfactor = Gtk.SpinButton.new_with_range(0.1, 10, 0.1)
    sb_sfactor.set_value(settings["pointer-scroll-factor"])
    sb_sfactor.connect("value-changed", set_from_spinbutton, settings, "pointer-scroll-factor", 1)
    sb_sfactor.set_tooltip_text("Scroll speed will be scaled by the given value.")
    grid.attach(sb_sfactor, 1, 4, 1, 1)

    lbl = Gtk.Label.new("Left handed:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 5, 1, 1)

    combo_left_handed = Gtk.ComboBoxText()
    combo_left_handed.set_property("halign", Gtk.Align.START)
    combo_left_handed.set_tooltip_text("Enables or disables left handed mode.")
    for item in ["disabled", "enabled"]:
        combo_left_handed.append(item, item)
    combo_left_handed.set_active_id(settings["pointer-left-handed"])
    combo_left_handed.connect("changed", set_dict_key_from_combo, settings, "pointer-left-handed")
    grid.attach(combo_left_handed, 1, 5, 1, 1)

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
    sb_columns.set_tooltip_text("number of columns to show icons in")
    grid.attach(sb_columns, 1, 1, 1, 1)

    lbl = Gtk.Label.new("Icon size:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 2, 1, 1)

    sb_icon_size = Gtk.SpinButton.new_with_range(8, 256, 1)
    sb_icon_size.set_value(preset["launcher-icon-size"])
    sb_icon_size.connect("value-changed", set_int_from_spinbutton, preset, "launcher-icon-size")
    sb_icon_size.set_tooltip_text("application icon size")
    grid.attach(sb_icon_size, 1, 2, 1, 1)

    lbl = Gtk.Label.new("File search columns:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 3, 1, 1)

    sb_fs_columns = Gtk.SpinButton.new_with_range(1, 9, 1)
    sb_fs_columns.set_value(preset["launcher-file-search-columns"])
    sb_fs_columns.connect("value-changed", set_int_from_spinbutton, preset, "launcher-file-search-columns")
    sb_fs_columns.set_tooltip_text("number of columns to show file search result in")
    grid.attach(sb_fs_columns, 1, 3, 1, 1)

    cb_search_files = Gtk.CheckButton.new_with_label("search files")
    cb_search_files.set_active(preset["launcher-search-files"])
    cb_search_files.connect("toggled", set_from_checkbutton, preset, "launcher-search-files")
    grid.attach(cb_search_files, 2, 3, 1, 1)

    cb_categories = Gtk.CheckButton.new_with_label("Show category menu")
    cb_categories.set_tooltip_text("show categories menu (icons) on top")
    cb_categories.set_active(preset["launcher-categories"])
    cb_categories.connect("toggled", set_from_checkbutton, preset, "launcher-categories")
    grid.attach(cb_categories, 0, 4, 1, 1)

    cb_resident = Gtk.CheckButton.new_with_label("Keep resident")
    cb_resident.set_tooltip_text("keep drawer running in the background")
    cb_resident.set_active(preset["launcher-resident"])
    cb_resident.connect("toggled", set_from_checkbutton, preset, "launcher-resident")
    grid.attach(cb_resident, 0, 5, 1, 1)

    cb_overlay = Gtk.CheckButton.new_with_label("Open on overlay")
    cb_overlay.set_tooltip_text("open drawer on the overlay layer")
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
    sb_icon_size.connect("value-changed", set_from_spinbutton, preset, "dock-icon-size", 1)
    sb_icon_size.set_tooltip_text("Application icon size.")
    grid.attach(sb_icon_size, 1, 3, 1, 1)

    lbl = Gtk.Label.new("Margin:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 4, 1, 1)

    sb_margin = Gtk.SpinButton.new_with_range(0, 256, 1)
    sb_margin.set_value(preset["dock-margin"])
    sb_margin.connect("value-changed", set_from_spinbutton, preset, "dock-margin", 1)
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
    cb_full.set_tooltip_text("take full screen width/height")
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
    combo_alignment.set_tooltip_text("Alignment in full width/height")

    lbl = Gtk.Label.new("Icon size:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 3, 1, 1)

    sb_icon_size = Gtk.SpinButton.new_with_range(8, 256, 1)
    sb_icon_size.set_value(preset["exit-icon-size"])
    sb_icon_size.connect("value-changed", set_from_spinbutton, preset, "exit-icon-size", 1)
    sb_icon_size.set_tooltip_text("item icon size")
    grid.attach(sb_icon_size, 1, 3, 1, 1)

    lbl = Gtk.Label.new("Margin:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 4, 1, 1)

    sb_margin = Gtk.SpinButton.new_with_range(0, 256, 1)
    sb_margin.set_value(preset["exit-margin"])
    sb_margin.connect("value-changed", set_from_spinbutton, preset, "exit-margin", 1)
    grid.attach(sb_margin, 1, 4, 1, 1)

    cb_full = Gtk.CheckButton.new_with_label("Full width/height")
    cb_full.set_active(preset["exit-full"])
    cb_full.connect("toggled", set_from_checkbutton, preset, "exit-full")
    cb_full.set_tooltip_text("take full screen width/height")
    grid.attach(cb_full, 0, 5, 1, 1)

    frame.show_all()

    return frame


def notification_tab(preset, preset_name):
    frame = Gtk.Frame()
    frame.set_label("  {}: Notification placement  ".format(preset_name))
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
    entry_panel.set_tooltip_text("Panel config file name")
    entry_panel.set_property("halign", Gtk.Align.START)
    entry_panel.set_text(settings["panel-custom"])
    entry_panel.connect("changed", set_from_entry, settings, "panel-custom")
    grid.attach(entry_panel, 1, 0, 1, 1)

    lbl = Gtk.Label.new("Panel css name:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 1, 1, 1)

    entry_panel_css = Gtk.Entry()
    entry_panel_css.set_placeholder_text("style.css")
    entry_panel_css.set_tooltip_text("Panel css file name")
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
