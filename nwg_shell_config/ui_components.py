import subprocess

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from nwg_shell_config.tools import is_command


def set_from_checkbutton(cb, settings, key):
    settings[key] = cb.get_active()


def set_from_spinbutton(cb, settings, key, ndigits):
    settings[key] = round(cb.get_value(), ndigits)


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


def launch(widget, cmd):
    print("Executing '{}'".format(cmd))
    subprocess.Popen('exec {}'.format(cmd), shell=True)


class SideMenuRow(Gtk.ListBoxRow):
    def __init__(self, label):
        super().__init__()
        self.eb = Gtk.EventBox()
        self.add(self.eb)
        lbl = Gtk.Label.new(label)
        lbl.set_property("halign", Gtk.Align.START)
        lbl.set_property("margin-start", 6)
        lbl.set_property("margin-end", 6)
        self.eb.add(lbl)


def screen_tab(settings):
    frame = Gtk.Frame()
    frame.set_label("  Screen settings  ")
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
    grid.attach(cb_autotiling_on, 1, 1, 1, 1)

    lbl = Gtk.Label.new("Workspaces:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 2, 1, 1)

    entry = Gtk.Entry()
    entry.set_placeholder_text("1 2 3 4 5 6 7 8")
    entry.set_text(settings["autotiling-workspaces"])
    entry.set_tooltip_text("Sets '-w' | '--workspaces' argument for the 'autotiling' command.\nSee 'autotiling -h`.")
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
    grid.attach(cb_night_light_on, 1, 3, 1, 1)

    lbl = Gtk.Label.new("Latitude:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 4, 1, 1)

    sb_lat = Gtk.SpinButton.new_with_range(-90.0, 90.0, 0.1)
    sb_lat.set_tooltip_text("Your location latitude\n'wlsunset -l'")
    sb_lat.set_digits(4)
    sb_lat.set_value(settings["night-lat"])
    sb_lat.connect("value-changed", set_from_spinbutton, settings, "night-lat", 4)
    grid.attach(sb_lat, 1, 4, 1, 1)

    lbl = Gtk.Label.new("Temp low:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 2, 4, 1, 1)

    sb_temp_low = Gtk.SpinButton.new_with_range(1000, 10000, 100)
    sb_temp_low.set_tooltip_text("Night light color temperature\n'wlsunset -t'")
    sb_temp_low.set_value(settings["night-temp-low"])
    grid.attach(sb_temp_low, 3, 4, 1, 1)

    lbl = Gtk.Label.new("Longitude:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 5, 1, 1)

    sb_lon = Gtk.SpinButton.new_with_range(-180, 180, 0.1)
    sb_lon.set_tooltip_text("Your location longitude\n'wlsunset -L'")
    sb_lon.set_value(settings["night-long"])
    sb_lon.connect("value-changed", set_from_spinbutton, settings, "night-long", 4)
    sb_lon.set_digits(4)
    grid.attach(sb_lon, 1, 5, 1, 1)

    lbl = Gtk.Label.new("Temp high:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 2, 5, 1, 1)

    sb_temp_high = Gtk.SpinButton.new_with_range(1000, 10000, 100)
    sb_temp_high.set_tooltip_text("Day light color temperature\n'wlsunset -T'")
    sb_temp_high.set_value(settings["night-temp-high"])
    grid.attach(sb_temp_high, 3, 5, 1, 1)

    lbl = Gtk.Label.new("Gamma:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 6, 1, 1)

    sb_gamma = Gtk.SpinButton.new_with_range(0.1, 10.0, 0.1)
    sb_gamma.set_value(settings["night-gamma"])
    sb_gamma.connect("value-changed", set_from_spinbutton, settings, "night-gamma", 1)
    sb_gamma.set_tooltip_text("'wlsunset -g'")
    grid.attach(sb_gamma, 1, 6, 1, 1)

    lbl = Gtk.Label()
    lbl.set_markup("<b>Help widget</b>")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 7, 1, 1)

    cb_help_on = Gtk.CheckButton.new_with_label("on")
    cb_help_on.set_active(settings["show-help"])
    cb_help_on.connect("toggled", set_from_checkbutton, settings, "show-help")
    grid.attach(cb_help_on, 1, 7, 1, 1)

    frame.show_all()

    return frame


def applications_tab(settings):
    frame = Gtk.Frame()
    frame.set_label("  Default applications  ")
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
    for cmd in ["foot", "alacritty", "kitty", "gnome-terminal", "sakura", "wterm"]:
        if is_command(cmd):
            entry_terminal.set_text(cmd)
            break
    entry_terminal.connect("changed", set_from_entry, settings, "terminal")
    grid.attach(entry_terminal, 1, 0, 1, 1)

    lbl = Gtk.Label.new("File manager:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 1, 1, 1)

    entry_fm = Gtk.Entry()
    entry_fm.set_tooltip_text("Command to run file manager")
    entry_fm.set_property("halign", Gtk.Align.START)
    for cmd in ["thunar", "pcmanfm", "nautilus", "caja"]:
        if is_command(cmd):
            entry_fm.set_text(cmd)
            break
    entry_fm.connect("changed", set_from_entry, settings, "file-manager")
    grid.attach(entry_fm, 1, 1, 1, 1)

    lbl = Gtk.Label.new("Text editor:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 2, 1, 1)

    entry_te = Gtk.Entry()
    entry_te.set_tooltip_text("Command to run text editor")
    entry_te.set_property("halign", Gtk.Align.START)
    for cmd in ["mousepad", "geany", "atom", "emacs", "gedit"]:
        if is_command(cmd):
            entry_te.set_text(cmd)
            break
    entry_te.connect("changed", set_from_entry, settings, "editor")
    grid.attach(entry_te, 1, 2, 1, 1)

    lbl = Gtk.Label.new("Web browser:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 3, 1, 1)

    entry_browser = Gtk.Entry()
    entry_browser.set_tooltip_text("Command to run web browser")
    entry_browser.set_property("hexpand", True)
    pairs = [("chromium", "chromium --enable-features=UseOzonePlatform --ozone-platform=wayland"),
                 ("firefox", "MOZ_ENABLE_WAYLAND=1 firefox"),
                 ("google-chrome-stable",
                  "google-chrome-stable --enable-features=UseOzonePlatform --ozone-platform=wayland")]
    detected = ""
    for pair in pairs:
        if is_command(pair[0]):
            entry_browser.set_text(pair[1])
            detected = pair[0]
            break
    entry_browser.connect("changed", set_from_entry, settings, "browser")
    grid.attach(entry_browser, 1, 3, 2, 1)

    combo = Gtk.ComboBoxText()
    combo.set_property("halign", Gtk.Align.START)
    combo.set_tooltip_text("Select from predefined commands.")
    grid.attach(combo, 1, 4, 1, 1)
    pairs_dict = {}
    for pair in pairs:
        pairs_dict[pair[0]] = pair[1]
        combo.append(pair[0], pair[0])
        if detected:
            combo.set_active_id(detected)
    combo.connect("changed", set_browser_from_combo, entry_browser, pairs_dict)

    frame.show_all()

    return frame
