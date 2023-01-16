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
import os
import subprocess
import sys

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
from nwg_shell_config.tools import eprint, is_command, load_text_file

try:
    gi.require_version('AppIndicator3', '0.1')
    from gi.repository import AppIndicator3

except:
    eprint('libappindicator-gtk3 package not found - tray icon unavailable')
    sys.exit(1)


def check_distro():
    # This is just a skeleton function, and only works on Arch Linux for now.
    os_release = "/etc/os-release"
    if os.path.isfile(os_release):
        lines = load_text_file(os_release).splitlines()
        for line in lines:
            if line.startswith("NAME="):
                if "Arch" in line:
                    return "arch"
                # add elif for other distros
            if line.startswith("ID="):
                if "arch" in line:
                    return "arch"
                # add elif for other distros
    return ""


class Indicator(object):
    def __init__(self, distro):
        self.distro = distro
        self.item_update = None
        self.ind = AppIndicator3.Indicator.new('azote_status_icon', '',
                                               AppIndicator3.IndicatorCategory.APPLICATION_STATUS)
        # self.ind.set_icon_full('nwg-update-noupdate', 'Up to date')
        # self.ind.set_attention_icon_full('nwg-update-available', 'Update available')

        # self.ind.set_status(AppIndicator3.IndicatorStatus.ATTENTION)
        # self.ind.set_status(AppIndicator3.IndicatorStatus.ACTIVE)

        self.ind.set_menu(self.menu())
        self.ind.set_title("Update notifier")

    def menu(self):
        menu = Gtk.Menu()

        self.item_update = Gtk.MenuItem.new_with_label('Update')
        # item.connect('activate', self.clear_unused)
        menu.append(self.item_update)

        item = Gtk.MenuItem.new_with_label('Check updates')
        item.connect('activate', self.check_updates)
        menu.append(item)

        item = Gtk.SeparatorMenuItem()
        menu.append(item)

        item = Gtk.MenuItem.new_with_label('Exit')
        item.connect('activate', Gtk.main_quit)
        menu.append(item)

        menu.show_all()
        return menu

    def check_updates(self, *args):
        title = "Up to date"
        if self.distro == "arch":
            output = subprocess.check_output("baph -c".split()).decode('utf-8').strip()
            if output == "0 0":
                title = "Up to date"
            else:
                u = output.split()
                title = "pacman: {}, AUR: {}".format(u[1], u[0])

        self.ind.set_title(title)
        if title == "Up to date":
            self.ind.set_icon_full('nwg-update-noupdate', 'Up to date')
            self.ind.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        else:
            self.ind.set_icon_full('nwg-update-available', 'Update available')
            self.ind.set_status(AppIndicator3.IndicatorStatus.ATTENTION)


def main():
    distro = check_distro()
    if not distro:
        eprint("Couldn't determine the Linux distribution, terminating")
        sys.exit(1)
    else:
        print("Running on {}".format(distro))

    if distro == "arch":
        if not is_command("baph"):
            eprint("baph AUR helper not found, terminating")
            sys.exit(1)

    ind = Indicator(distro)
    ind.check_updates()

    Gtk.main()


if __name__ == "__main__":
    sys.exit(main())
