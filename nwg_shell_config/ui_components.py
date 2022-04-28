import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


def side_menu():
    list_box = Gtk.ListBox()
    row = SideMenuRow("Item 1")
    list_box.append(row)

    row = SideMenuRow("Item 2")
    list_box.append(row)

    row = SideMenuRow("Item 3")
    list_box.append(row)

    list_box.show_all()


class SideMenuRow(Gtk.ListBoxRow):
    def __init__(self, label):
        super().__init__()
        self.eb = Gtk.EventBox()
        self.add(self.eb)
        lbl = Gtk.Label.new(label)
        self.eb.add(lbl)


def screen_tab():
    frame = Gtk.Frame()
    frame.set_size_request(500, 0)
    frame.set_label(" Screen configuration ")
    frame.set_label_align(0.5, 0.5)
    frame.set_property("margin", 12)
    frame.set_property("hexpand", True)
    grid = Gtk.Grid()
    frame.add(grid)
    grid.set_property("margin", 12)
    grid.set_column_spacing(12)
    grid.set_column_homogeneous(True)

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
    btn.set_label("Look and feel")
    grid.attach(btn, 2, 0, 1, 1)

    frame.show_all()

    return frame
