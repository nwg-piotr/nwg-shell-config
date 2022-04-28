import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


def side_menu():
    list_box = Gtk.ListBox()
    list_box.set_property("margin-top", 6)

    row = SideMenuRow("Screen settings")
    list_box.add(row)

    row = SideMenuRow("Keyboard")
    list_box.add(row)

    row = SideMenuRow("Pointer device")
    list_box.add(row)

    row = SideMenuRow("Touchpad")
    list_box.add(row)

    row = SideMenuRow("Default applications")
    list_box.add(row)

    row = SideMenuRow("Common settings")
    list_box.add(row)

    row = SideMenuRow("Preset 0")
    list_box.add(row)

    row = SideMenuRow("Preset 1")
    list_box.add(row)

    row = SideMenuRow("Preset 2")
    list_box.add(row)

    row = SideMenuRow("Custom preset")
    list_box.add(row)

    list_box.show_all()

    return list_box


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


def screen_tab():
    frame = Gtk.Frame()
    frame.set_label("  Screen settings  ")
    frame.set_label_align(0.5, 0.5)
    frame.set_property("hexpand", True)
    grid = Gtk.Grid()
    frame.add(grid)
    grid.set_property("margin", 6)
    grid.set_column_spacing(6)
    grid.set_row_spacing(6)

    btn = Gtk.Button()
    btn.set_property("name", "app-btn")
    btn.set_always_show_image(True)
    btn.set_image_position(Gtk.PositionType.TOP)
    img = Gtk.Image.new_from_icon_name("nwg-displays", Gtk.IconSize.DIALOG)
    btn.set_image(img)
    btn.set_label("Displays")
    grid.attach(btn, 0, 0, 1, 1)

    btn = Gtk.Button()
    btn.set_property("name", "app-btn")
    btn.set_always_show_image(True)
    btn.set_image_position(Gtk.PositionType.TOP)
    img = Gtk.Image.new_from_icon_name("azote", Gtk.IconSize.DIALOG)
    btn.set_image(img)
    btn.set_label("Wallpapers")
    grid.attach(btn, 1, 0, 1, 1)

    btn = Gtk.Button()
    btn.set_property("name", "app-btn")
    btn.set_always_show_image(True)
    btn.set_image_position(Gtk.PositionType.TOP)
    img = Gtk.Image.new_from_icon_name("nwg-look", Gtk.IconSize.DIALOG)
    btn.set_image(img)
    btn.set_label("Look & feel")
    grid.attach(btn, 2, 0, 1, 1)

    lbl = Gtk.Label()
    lbl.set_markup("<b>Autotiling</b>")
    lbl.set_property("margin-top", 6)
    lbl.set_property("margin-bottom", 6)
    lbl.set_property("halign", Gtk.Align.START)
    grid.attach(lbl, 0, 1, 1, 1)

    cb_autotiling_on = Gtk.CheckButton.new_with_label("on")
    grid.attach(cb_autotiling_on, 1, 1, 1, 1)

    lbl = Gtk.Label.new("Workspaces:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 2, 1, 1)

    entry = Gtk.Entry()
    entry.set_placeholder_text("1 2 3 4 5 6 7 8")
    grid.attach(entry, 1, 2, 1, 1)

    lbl = Gtk.Label()
    lbl.set_markup("<b>Night light</b>")
    lbl.set_property("margin-top", 6)
    lbl.set_property("margin-bottom", 6)
    lbl.set_property("halign", Gtk.Align.START)
    grid.attach(lbl, 0, 3, 1, 1)

    cb_night_light_on = Gtk.CheckButton.new_with_label("on")
    grid.attach(cb_night_light_on, 1, 3, 1, 1)

    lbl = Gtk.Label.new("Latitude:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 4, 1, 1)

    sb_lat = Gtk.SpinButton.new_with_range(-90.0, 90.0, 0.1)
    sb_lat.set_digits(4)
    grid.attach(sb_lat, 1, 4, 1, 1)

    lbl = Gtk.Label.new("Temp low:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 2, 4, 1, 1)

    sb_temp_low = Gtk.SpinButton.new_with_range(1000, 10000, 100)
    grid.attach(sb_temp_low, 3, 4, 1, 1)

    lbl = Gtk.Label.new("Longitude:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 5, 1, 1)

    sb_lon = Gtk.SpinButton.new_with_range(-180, 180, 0.1)
    sb_lon.set_digits(4)
    grid.attach(sb_lon, 1, 5, 1, 1)

    lbl = Gtk.Label.new("Temp high:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 2, 5, 1, 1)

    sb_temp_high = Gtk.SpinButton.new_with_range(1000, 10000, 100)
    grid.attach(sb_temp_high, 3, 5, 1, 1)

    lbl = Gtk.Label.new("Gamma:")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 6, 1, 1)

    sb_gamma = Gtk.SpinButton.new_with_range(0.1, 10.0, 0.1)
    grid.attach(sb_gamma, 1, 6, 1, 1)

    lbl = Gtk.Label()
    lbl.set_markup("<b>Help widget</b>")
    lbl.set_property("halign", Gtk.Align.END)
    grid.attach(lbl, 0, 7, 1, 1)

    cb_help_on = Gtk.CheckButton.new_with_label("on")
    grid.attach(cb_help_on, 1, 7, 1, 1)

    frame.show_all()

    return frame
