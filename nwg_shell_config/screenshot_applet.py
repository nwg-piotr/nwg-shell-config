#!/usr/bin/env python3

"""
nwg-shell system tray screenshot applet
Copyright: 2023-2025 Piotr Miller & Contributors
e-mail: nwg.piotr@gmail.com
Repository: https://github.com/nwg-piotr/nwg-shell-config
Project: https://github.com/nwg-piotr/nwg-shell
License: MIT
"""

import gi
import os
import subprocess
import signal
import sys

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
from psutil import process_iter
from nwg_shell_config.tools import eprint, is_command, load_shell_data, load_json, check_key, get_data_dir
from enum import Enum

try:
    gi.require_version('AppIndicator3', '0.1')
    from gi.repository import AppIndicator3
except:
    eprint('libappindicator-gtk3 package not found - tray icon unavailable')

dir_name = os.path.dirname(__file__)
shell_data = load_shell_data()

settings_file = os.path.join(get_data_dir(), "settings")
settings = {}
if os.path.isfile(settings_file):
    settings = load_json(settings_file)
defaults = {
    "screenshot-applet-on": True
}
for key in defaults:
    check_key(settings, key, defaults[key])


voc = {}  # Vocabulary
nwg_system_update_arg = ""

_ind = None  # Indicator(object) containing

counter = 0
command = ""

if os.getenv("SWAYSOCK"):
    cmd_exec = "swaymsg exec"
elif os.getenv("HYPRLAND_INSTANCE_SIGNATURE"):
    cmd_exec = "hyprctl dispatch exec"
else:
    eprint("This program needs either sway or Hyprland environment")
    sys.exit(1)

if not is_command("screenshot"):
    eprint("'screenshot [fullscreen|region|focused|display|swappy]' command not found")
    sys.exit(1)


class ScreenshotType(Enum):
    FULLSCREEN = 1
    DISPLAY = 2
    FOCUSED = 3
    REGION = 4


def signal_handler(sig, frame):
    if sig == 2 or sig == 15:
        desc = {2: "SIGINT", 15: "SIGTERM"}
        eprint("screenshot-applet: terminated with {}".format(desc[sig]))
        Gtk.main_quit()
    elif sig != 17:
        print("screenshot-applet: signal {} received".format(sig))


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
    for k in ["screenshot", "screenshot-display", "screenshot-focused", "screenshot-fullscreen", "screenshot-region"]:
        if k in global_voc:
            voc[k] = global_voc[k]


def screenshot(item, s_type):
    global counter, command
    if s_type == ScreenshotType.FULLSCREEN:
        subprocess.Popen(f'{cmd_exec} screenshot fullscreen', shell=True)
    if s_type == ScreenshotType.DISPLAY:
        _ind.switch_icon(f'nwg-3', "")
        counter = 2
        command = f'{cmd_exec} screenshot display'
        GLib.timeout_add_seconds(1, count_down_and_execute)
    if s_type == ScreenshotType.FOCUSED:
        _ind.switch_icon(f'nwg-3', "")
        counter = 2
        command = f'{cmd_exec} screenshot focused'
        GLib.timeout_add_seconds(1, count_down_and_execute)
    elif s_type == ScreenshotType.REGION:
        subprocess.Popen(f'{cmd_exec} screenshot swappy', shell=True)


def menu():
    m = Gtk.Menu()

    item = Gtk.MenuItem.new_with_label(voc["screenshot-fullscreen"])
    item.connect('activate', screenshot, ScreenshotType.FULLSCREEN)
    m.append(item)

    item = Gtk.MenuItem.new_with_label(voc["screenshot-display"])
    item.connect('activate', screenshot, ScreenshotType.DISPLAY)
    m.append(item)

    item = Gtk.MenuItem.new_with_label(voc["screenshot-focused"])
    item.connect('activate', screenshot, ScreenshotType.FOCUSED)
    m.append(item)

    item = Gtk.MenuItem.new_with_label(voc["screenshot-region"])
    item.connect('activate', screenshot, ScreenshotType.REGION)
    m.append(item)

    item = Gtk.SeparatorMenuItem()
    m.append(item)

    m.show_all()
    return m


class Indicator(object):
    def __init__(self):
        self.item_update = None

        self.ind = AppIndicator3.Indicator.new('nwg_screenshot_applet', '',
                                               AppIndicator3.IndicatorCategory.APPLICATION_STATUS)

        self.ind.set_menu(menu())
        self.ind.set_title(voc["screenshot"])
        self.ind.set_icon_full("nwg-screenshot", voc["screenshot"])

    def switch_icon(self, icon, desc):
        self.ind.set_icon_full(icon, desc)


def count_down_and_execute():
    global counter, command, _ind
    if counter > 0:
        _ind.switch_icon(f'nwg-{counter}', "")
        counter -= 1
        # repeat
        return True
    else:
        cmd = command
        command = ""
        subprocess.Popen(cmd, shell=True)
        _ind.ind.set_icon_full("nwg-screenshot", voc["screenshot"])
        # do not repeat
        return False


def main():
    own_pid = os.getpid()
    # Interrupt running instances, if any
    for proc in process_iter():
        if "nwg-screenshot" in proc.name():
            pid = proc.pid
            if not pid == own_pid:
                eprint("Killing '{}', pid {}".format(proc.name(), pid))
                os.kill(pid, signal.SIGINT)

    # Set app_id
    GLib.set_prgname('nwg-screenshot')

    # Load localized dictionary
    load_vocabulary()

    global _ind
    _ind = Indicator()

    # Gentle termination; check updates on USR1 (for no reason / possible future use)
    catchable_sigs = set(signal.Signals) - {signal.SIGKILL, signal.SIGSTOP}
    for sig in catchable_sigs:
        signal.signal(sig, signal_handler)

    Gtk.main()


if __name__ == "__main__":
    sys.exit(main())
