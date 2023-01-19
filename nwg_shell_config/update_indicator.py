#!/usr/bin/env python3

"""
nwg-shell system tray update indicator
Copyright: 2023 Piotr Miller & Contributors
e-mail: nwg.piotr@gmail.com
Repository: https://github.com/nwg-piotr/nwg-shell-config
Project: https://github.com/nwg-piotr/nwg-shell
License: MIT

NOTE: This script has been written to replace the 'updates' nwg-panel executor, which is Arch-specific.
It's quite well documented in comments, and expected to be adapted for use with other Linux distributions, too.

For use with Arch Linux and derivatives, the script depends on 'baph' (Basic AUR Package Helper) by Nate Maia
https://bitbucket.org/natemaia/baph, as well if it comes to checking updates, as to updating.
Updates are being performed by the `sway-update` script, distributed with the 'nwg-shell' AUR package.
For your own distro, you will need your own version of the latter, installed somewhere on $PATH.
"""

import gi
import os
import subprocess
import signal
import sys

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
from psutil import process_iter
from nwg_shell_config.tools import eprint, is_command, load_text_file, load_shell_data, load_json, check_key, get_data_dir

try:
    gi.require_version('AppIndicator3', '0.1')
    from gi.repository import AppIndicator3
except:
    eprint('libappindicator-gtk3 package not found - tray icon unavailable')
    sys.exit(1)

dir_name = os.path.dirname(__file__)
shell_data = load_shell_data()

settings_file = os.path.join(get_data_dir(), "settings")
settings = {}
if os.path.isfile(settings_file):
    settings = load_json(settings_file)
defaults = {
    "update-indicator-on": True,
    "update-indicator-interval": 30
}
for key in defaults:
    check_key(settings, key, defaults[key])

voc = {}  # Vocabulary

ind = None  # Indicator(object) containing


def signal_handler(sig, frame):
    if sig == 2 or sig == 15:
        desc = {2: "SIGINT", 15: "SIGTERM"}
        eprint("nwg-update-indicator: terminated with {}".format(desc[sig]))
        Gtk.main_quit()
    elif sig == 10:
        eprint("nwg-update-indicator: SIGUSR1 received, checking updates")
        if ind:
            ind.check_updates()
    elif sig != 17:
        print("nwg-update-indicator: signal {} received".format(sig))


def load_vocabulary():
    # We will only need several keys out of the global dictionary
    # Load basic vocabulary (en_US)
    global_voc = load_json(os.path.join(dir_name, "langs", "en_US.json"))
    if not global_voc:
        eprint("Failed loading vocabulary")
        sys.exit(1)

    lang = os.getenv("LANG").split(".")[0] if not shell_data["interface-locale"] else shell_data["interface-locale"]
    # Translate if necessary
    if lang != "en_US":
        loc_file = os.path.join(dir_name, "langs", "{}.json".format(lang))
        if os.path.isfile(loc_file):
            # Load localized vocabulary
            loc = load_json(loc_file)
            if not loc:
                eprint("Failed loading translation into '{}'".format(lang))
            else:
                # Replace keys w/ localized counterparts, if they exist
                for k in loc:
                    global_voc[k] = loc[k]

    # Select and return just the keys we need, in another dict
    global voc
    for k in ["you-are-up-to-date", "update", "check-updates", "exit"]:
        if k in global_voc:
            voc[k] = global_voc[k]

    return voc


def check_distro():
    # This is just a skeleton function, and for now it detects Arch Linux only. Feel free to contribute.
    # Use unambiguous, lowercase name for your distro. You will need it in the Indicator.check_updates method.
    if os.path.isfile("/etc/os-release"):
        lines = load_text_file("/etc/os-release").splitlines()
        for line in lines:
            if line.startswith("NAME"):
                if "Arch" in line:
                    return "arch"
                # add elif for other distros

            if line.startswith("ID"):
                if "arch" in line:
                    return "arch"
                # add elif for other distros

    elif os.path.isfile("/etc/lsb=release"):
        lines = load_text_file("/etc/lsb-release").splitlines()
        for line in lines:
            if line.startswith("DISTRIB_ID"):
                if "Arch" in line:
                    return "arch"
                # add elif for other distros

            if line.startswith("DISTRIB_DESCRIPTION"):
                if "Arch" in line:
                    return "arch"
                # add elif for other distros

    return ""


class Indicator(object):
    def __init__(self, distro):
        self.distro = distro
        self.item_update = None

        self.ind = AppIndicator3.Indicator.new('nwg_update_indicator', '',
                                               AppIndicator3.IndicatorCategory.APPLICATION_STATUS)

        self.ind.set_menu(self.menu())
        self.ind.set_title("Update notifier")

        self.check_updates()

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

        menu.show_all()
        return menu

    def check_updates(self, *args):
        update_details = ""
        # The code below should leave `update_details` string empty if no updates found

        GLib.timeout_add_seconds(0, self.switch_icon, "nwg-update-checking", "Checking")

        # Below we could add update check commands for other distros
        if self.distro == "arch":
            if is_command("baph"):
                output = subprocess.check_output("baph -c".split()).decode('utf-8').strip()
                if output and output != "0 0":
                    u = output.split()
                    update_details = "pacman: {}, AUR: {}".format(u[1], u[0])
            elif is_command("checkupdates"):
                output = subprocess.check_output("checkupdates".split()).decode('utf-8')
                if len(output.splitlines()) > 0:
                    update_details = "pacman: {} (checkupdates)".format(len(output.splitlines()))

        # elif self.distro == "something_else:
        #   place your code here

        if not update_details:
            GLib.timeout_add_seconds(1, self.switch_icon, "nwg-update-noupdate", voc["you-are-up-to-date"])
        else:
            GLib.timeout_add_seconds(1, self.switch_icon, "nwg-update-available", update_details)

        return True  # For this to be called periodically

    def update(self, *args):
        # Other distros: we already have the foot terminal installed.
        # You just need to provide your own `sway-update` script somewhere on $PATH.
        subprocess.call('exec foot sway-update', shell=True)

        self.check_updates()

    def switch_icon(self, icon, desc):
        self.ind.set_title(desc)
        if desc != voc["you-are-up-to-date"]:
            self.item_update.set_label("{} ({})".format(voc["update"], desc))
        else:
            self.item_update.set_label(voc["update"])
        self.ind.set_icon_full(icon, desc)


def main():
    own_pid = os.getpid()

    for proc in process_iter():
        if "nwg-update-ind" in proc.name():
            pid = proc.pid
            if not pid == own_pid:
                eprint("Killing '{}', pid {}".format(proc.name(), pid))
                os.kill(pid, signal.SIGINT)

    GLib.set_prgname('nwg-update-indicator')

    global voc
    voc = load_vocabulary()

    distro = check_distro()
    if not distro:
        eprint("Couldn't determine the Linux distribution, terminating")
        sys.exit(1)
    else:
        eprint("nwg-update-indicator running on '{}'".format(distro))

    if distro == "arch":
        if not is_command("baph") and not is_command("checkupdates"):
            eprint("No supported AUR helper found, terminating")
            sys.exit(1)

    global ind
    ind = Indicator(distro)  # Will check updates for the 1st time in the constructor
    GLib.timeout_add_seconds(settings["update-indicator-interval"] * 60, ind.check_updates)

    catchable_sigs = set(signal.Signals) - {signal.SIGKILL, signal.SIGSTOP}
    for sig in catchable_sigs:
        signal.signal(sig, signal_handler)

    Gtk.main()


if __name__ == "__main__":
    sys.exit(main())
