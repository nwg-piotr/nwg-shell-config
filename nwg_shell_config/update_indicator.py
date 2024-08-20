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

On Arch Linux and derivatives, the script depends on 'baph' (Basic AUR Package Helper) by Nate Maia
https://bitbucket.org/natemaia/baph, as well if it comes to checking updates, as to updating.

Updates are being performed by the `nwg-system-update` script. For your own distro, you will need your own
version of the latter, installed somewhere on $PATH.
"""
import time

import gi
import os
import subprocess
import signal
import sys
import threading

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
from psutil import process_iter
from nwg_shell_config.tools import eprint, is_command, load_text_file, load_shell_data, load_json, check_key, \
    get_data_dir

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
    "update-indicator-interval": 30,
    "update-command": "nwg-system-update"
}
for key in defaults:
    check_key(settings, key, defaults[key])

voc = {}  # Vocabulary
nwg_system_update_arg = ""

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

    # Detect lang (system or user-defined)
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
    for k in ["you-are-up-to-date", "update", "updates", "check-updates", "exit", "press-enter-to-exit"]:
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
                elif "Venom" in line:
                    return "venom"
                # add elif for other distros

            if line.startswith("ID"):
                if "arch" in line:
                    return "arch"
                elif "venom" in line:
                    return "venom"
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
        self.ind.set_title(voc["updates"])

        self.switch_icon("nwg-update-noupdate", "Checking")
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
        self.switch_icon("nwg-update-checking", "Checking")

        thr = threading.Thread(target=self.check_updates_actual_job, args=(), kwargs={})
        thr.start()

        return True  # For this to be called periodically

    def check_updates_actual_job(self):
        update_details = ""
        # The code below should leave `update_details` string empty if no updates found.
        # Otherwise, it should set it as a short info, that will be appended to the 'Update' menu item.

        # Below we could add update check commands for other distros
        global nwg_system_update_arg
        if self.distro == "arch":
            nwg_system_update_arg = "-pacman"

            if is_command("baph"):
                eprint("Using baph")
                output = subprocess.check_output("baph -c".split()).decode('utf-8').strip()
                if output and output != "0 0":
                    u = output.split()
                    update_details = f"pacman: {u[1]}, AUR: {u[0]}"

            elif is_command("yay"):
                nwg_system_update_arg = "-yay"
                eprint("Using yay")
                pacman, aur = 0, 0
                try:
                    output = subprocess.check_output("checkupdates".split()).decode('utf-8').splitlines()
                    pacman = len(output)
                except subprocess.CalledProcessError:
                    pass
                try:
                    output = subprocess.check_output("yay -Qu".split()).decode('utf-8').splitlines()
                    aur = len(output)
                except subprocess.CalledProcessError:
                    pass

                if pacman or aur:
                    update_details = f"pacman: {pacman}, AUR: {aur}"

            else:
                eprint("Using checkupdates")
                pacman = 0
                try:
                    output = subprocess.check_output("checkupdates".split()).decode('utf-8').splitlines()
                    pacman = len(output)
                except subprocess.CalledProcessError:
                    pass

                if pacman:
                    update_details = f"pacman: {pacman}"

            if update_details:
                eprint(update_details)
            else:
                eprint(voc["you-are-up-to-date"])

        elif self.distro == "venom":
            nwg_system_update_arg = "-scratch"
            eprint("Using scratch")
            scratch = 0
            try:
                output = subprocess.check_output("venomupdates".split()).decode('utf-8').splitlines()
                scratch = len(output)
            except subprocess.CalledProcessError:
                pass

            if scratch:
                update_details = f"scratch: {scratch}"

        # elif self.distro == "something_else":
        #   place your code here

        if not update_details:
            GLib.timeout_add_seconds(0, self.switch_icon, "nwg-update-noupdate", voc["you-are-up-to-date"])
        else:
            GLib.timeout_add_seconds(0, self.switch_icon, "nwg-update-available", update_details)

    def update(self, *args):
        # Other distros: we already have the foot terminal installed.
        # You just need to provide your own `nwg-system-update` script somewhere on $PATH.
        # IMPORTANT: the presence of this script will also determine if to display corresponding
        # options in the config utility.
        if settings["update-command"] == "nwg-system-update":
            cmd = "exec foot nwg-system-update '{}'".format(voc["press-enter-to-exit"])
            if nwg_system_update_arg:
                cmd += f" {nwg_system_update_arg}"
            subprocess.call(cmd, shell=True)
        else:
            subprocess.call("exec {}".format(settings["update-command"]), shell=True)

        self.check_updates()

    def switch_icon(self, icon, desc):
        # self.ind.set_title(desc)
        if desc != voc["you-are-up-to-date"]:
            self.item_update.set_label("{} ({})".format(voc["update"], desc))
            self.item_update.show()
        else:
            self.item_update.hide()
        self.ind.set_icon_full(icon, desc)


def main():
    # Die if 'nwg-system-update` script absent
    if not is_command(settings["update-command"]):
        eprint("'nwg-system-update' script not found, terminating")
        sys.exit(1)

    own_pid = os.getpid()
    # Interrupt running instances, if any
    for proc in process_iter():
        if "nwg-update-ind" in proc.name():
            pid = proc.pid
            if not pid == own_pid:
                eprint("Killing '{}', pid {}".format(proc.name(), pid))
                os.kill(pid, signal.SIGINT)

    # Set app_id
    GLib.set_prgname('nwg-update-indicator')

    # Load localized dictionary
    global voc
    voc = load_vocabulary()

    distro = check_distro()
    if not distro:
        eprint("Couldn't determine the Linux distribution, terminating")
        sys.exit(1)
    else:
        eprint("nwg-update-indicator running on '{}'".format(distro))

    if distro == "arch":
        if not is_command("baph") and not is_command("yay"):
            eprint("No supported AUR helper found, terminating")
            sys.exit(1)

    global ind
    ind = Indicator(distro)  # Will check updates for the 1st time in the constructor
    # Check periodically in given intervals
    GLib.timeout_add_seconds(settings["update-indicator-interval"] * 60, ind.check_updates)

    # Gentle termination; check updates on USR1 (for no reason / possible future use)
    catchable_sigs = set(signal.Signals) - {signal.SIGKILL, signal.SIGSTOP}
    for sig in catchable_sigs:
        signal.signal(sig, signal_handler)

    Gtk.main()


if __name__ == "__main__":
    sys.exit(main())
