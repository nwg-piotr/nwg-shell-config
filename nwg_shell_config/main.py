#!/usr/bin/env python3

# Dependencies: python-geopy

import locale
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib

from nwg_shell_config.tools import *

dir_name = os.path.dirname(__file__)

config_home = os.getenv('XDG_CONFIG_HOME') if os.getenv('XDG_CONFIG_HOME') else os.path.join(
    os.getenv("HOME"), ".config/")

lang = locale.getlocale()[0].split("_")[0]


class MainWindow(Gtk.Window):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.connect('destroy', Gtk.main_quit)
        builder = Gtk.Builder()
        builder.add_from_file(os.path.join(dir_name, "glade/main.glade"))

        self = builder.get_object("main-window")
        self.show_all()


def main():
    GLib.set_prgname('nwg-shell-config')

    win = MainWindow()

    print(lang)
    print(get_lat_lon())
    print(get_data_dir())
    print(config_home)
    print(check_deps())

    Gtk.main()


if __name__ == '__main__':
    sys.exit(main())
