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
from nwg_shell_config.tools import eprint, is_command, load_text_file, load_json, load_shell_data

try:
    gi.require_version('AppIndicator3', '0.1')
    from gi.repository import AppIndicator3

except:
    eprint('libappindicator-gtk3 package not found - tray icon unavailable')
    sys.exit(1)

dir_name = os.path.dirname(__file__)
shell_data = load_shell_data()
voc = {}


def load_vocabulary():
    # We will only need several keys out of the global dictionary
    # Basic vocabulary (en_US)
    global_voc = load_json(os.path.join(dir_name, "langs", "en_US.json"))
    if not global_voc:
        eprint("Failed loading vocabulary")
        sys.exit(1)

    lang = os.getenv("LANG").split(".")[0] if not shell_data["interface-locale"] else shell_data["interface-locale"]
    # Translate if necessary
    if lang != "en_US":
        loc_file = os.path.join(dir_name, "langs", "{}.json".format(lang))
        if os.path.isfile(loc_file):
            # localized vocabulary
            loc = load_json(loc_file)
            if not loc:
                eprint("Failed loading translation into '{}'".format(lang))
            else:
                for key in loc:
                    global_voc[key] = loc[key]
    voc = {}
    for key in ["you-are-up-to-date", "update", "check-updates", "exit"]:
        if key in global_voc:
            voc[key] = global_voc[key]

    return voc


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

        self.ind.set_icon_full('nwg-update-noupdate', 'Up to date')
        self.ind.set_status(AppIndicator3.IndicatorStatus.ACTIVE)

        self.ind.set_menu(self.menu())
        self.ind.set_title("Update notifier")

    def menu(self):
        menu = Gtk.Menu()

        self.item_update = Gtk.MenuItem.new_with_label(voc["update"])
        self.item_update.connect('activate', self.update)
        menu.append(self.item_update)

        item = Gtk.MenuItem.new_with_label(voc["check-updates"])
        item.connect('activate', self.check_updates)
        menu.append(item)

        item = Gtk.SeparatorMenuItem()
        menu.append(item)

        item = Gtk.MenuItem.new_with_label(voc["exit"])
        item.connect('activate', Gtk.main_quit)
        menu.append(item)

        menu.show_all()
        return menu

    def check_updates(self, *args):
        update_desc = ""
        # The code below should leave `update_desc` string empty if no updates found

        # Below we could add update check commands for other distros
        if self.distro == "arch":
            if is_command("baph"):
                output = subprocess.check_output("baph -c".split()).decode('utf-8').strip()
                if output and output != "0 0":
                    u = output.split()
                    update_desc = "pacman: {}, AUR: {} (baph)".format(u[1], u[0])
            elif is_command("checkupdates"):
                output = subprocess.check_output("checkupdates".split()).decode('utf-8')
                if len(output.splitlines()) > 0:
                    update_desc = "pacman: {} (checkupdates)".format(len(output.splitlines()))

        # elif self.distro == "something_else:
        #   place your code here

        if not update_desc:
            self.ind.set_title(voc["you-are-up-to-date"])
        else:
            self.ind.set_title(update_desc)

        if update_desc == "Up to date":
            self.ind.set_icon_full('nwg-update-noupdate', 'Up to date')
            self.ind.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        else:
            self.ind.set_icon_full('nwg-update-available', 'Update available')
            self.ind.set_status(AppIndicator3.IndicatorStatus.ATTENTION)

    def update(self, *args):
        if self.distro == "arch":
            cmd = "foot sway-update"
            subprocess.Popen('exec {}'.format(cmd), shell=True)

        self.check_updates()


def main():
    global voc
    voc = load_vocabulary()
    print(voc)
    distro = check_distro()
    if not distro:
        eprint("Couldn't determine the Linux distribution, terminating")
        sys.exit(1)
    else:
        print("Running on {}".format(distro))

    if distro == "arch":
        if not is_command("baph") and not is_command("checkupdates"):
            eprint("No supported AUR helper found, terminating")
            sys.exit(1)

    ind = Indicator(distro)
    ind.check_updates()

    Gtk.main()


if __name__ == "__main__":
    sys.exit(main())
