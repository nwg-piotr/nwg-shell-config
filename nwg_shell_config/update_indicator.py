#!/usr/bin/env python3

"""
Tray system update indicator
Copyright: 2023 Piotr Miller & Contributors
e-mail: nwg.piotr@gmail.com
Repository: https://github.com/nwg-piotr/nwg-shell-config
Project: https://github.com/nwg-piotr/nwg-shell
License: MIT
"""
import gi
import sys
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
from nwg_shell_config.tools import eprint

try:
    gi.require_version('AppIndicator3', '0.1')
    from gi.repository import AppIndicator3

except:
    eprint('libappindicator-gtk3 package not found - tray icon unavailable')
    sys.exit(1)


class Indicator(object):
    def __init__(self):
        self.ind = AppIndicator3.Indicator.new('azote_status_icon', '',
                                               AppIndicator3.IndicatorCategory.APPLICATION_STATUS)
        self.ind.set_icon_full('/usr/share/azote/indicator_active.png', 'Tracking off')
        self.ind.set_attention_icon_full('/usr/share/azote/indicator_attention.png', 'Tracking on')

        # self.ind.set_status(AppIndicator3.IndicatorStatus.ATTENTION)
        self.ind.set_status(AppIndicator3.IndicatorStatus.ACTIVE)

        self.ind.set_menu(self.menu())

    def menu(self):
        menu = Gtk.Menu()

        item = Gtk.MenuItem.new_with_label('clear_unused_thumbnails')
        # item.connect('activate', self.clear_unused)
        menu.append(item)

        item = Gtk.MenuItem.new_with_label('about_azote')
        # item.connect('activate', on_about_button)
        menu.append(item)

        item = Gtk.SeparatorMenuItem()
        menu.append(item)

        item = Gtk.MenuItem.new_with_label('exit')
        item.connect('activate', Gtk.main_quit)
        menu.append(item)

        menu.show_all()
        return menu

    def switch_indication(self, item):
        if item.get_active():
            self.ind.set_status(AppIndicator3.IndicatorStatus.ATTENTION)
            self.ind.set_icon_full('/usr/share/azote/indicator_attention.png', 'Tracking on')
        else:
            self.ind.set_icon_full('/usr/share/azote/indicator_active.png', 'Tracking off')
            self.ind.set_status(AppIndicator3.IndicatorStatus.ACTIVE)


def main():
    GLib.set_prgname('Software updates')
    ind = Indicator()
    Gtk.main()


if __name__ == "__main__":
    sys.exit(main())
