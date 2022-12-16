#!/usr/bin/env python3

"""
nwg-shell graphical updater script

Copyright (c) 2022 Piotr Miller
e-mail: nwg.piotr@gmail.com
Project: https://github.com/nwg-piotr/nwg-shell
License: MIT
"""

import os
import signal
import subprocess
import sys

import gi

gi.require_version('Gtk', '3.0')

dir_name = os.path.dirname(__file__)

from datetime import datetime as dt

from nwg_shell_config.__about__ import __need_update__

from gi.repository import Gtk, Gdk

from nwg_shell_config.tools import temp_dir, get_data_dir, get_shell_data_dir, save_string, get_shell_version, \
    is_newer, load_shell_data, is_command, save_json, load_json, eprint

from nwg_shell_config.updates import *

data_dir = get_data_dir()
voc = {}

# pango-formatted descriptions
updates_dir = os.path.join(dir_name, "updates")

btn_update = Gtk.Button()

shell_data = load_shell_data()

lock_file = os.path.join(temp_dir(), "nwg-shell-updater.lock")

config_home = os.getenv('XDG_CONFIG_HOME') if os.getenv('XDG_CONFIG_HOME') else os.path.join(os.getenv("HOME"),
                                                                                             ".config")


def terminate(*args):
    if os.path.isfile(lock_file):
        os.remove(lock_file)
    # trigger 'Update' button refresh in the config utility
    subprocess.Popen("killall -s 10 nwg-shell-config", shell=True)
    Gtk.main_quit()


def signal_handler(sig, frame):
    if sig == 2 or sig == 15:
        desc = {2: "SIGINT", 15: "SIGTERM"}
        print("Terminated with {}".format(desc[sig]))
        terminate()


def handle_keyboard(win, event):
    if event.type == Gdk.EventType.KEY_RELEASE and event.keyval == Gdk.KEY_Escape:
        terminate()


def load_vocabulary():
    global voc
    # basic vocabulary (for en_US)
    voc = load_json(os.path.join(dir_name, "langs", "en_US.json"))
    if not voc:
        eprint("Failed loading vocabulary")
        sys.exit(1)

    lang = os.getenv("LANG").split(".")[0] if not shell_data["interface-locale"] else shell_data["interface-locale"]
    # translate if necessary
    if lang != "en_US":
        loc_file = os.path.join(dir_name, "langs", "{}.json".format(lang))
        if os.path.isfile(loc_file):
            # localized vocabulary
            loc = load_json(loc_file)
            if not loc:
                eprint("Failed loading translation into '{}'".format(lang))
            else:
                for key in loc:
                    voc[key] = loc[key]


def main():
    current_shell_version = get_shell_version()
    global lock_file
    if os.path.isfile(lock_file):
        try:
            pid = int(load_text_file(lock_file))
            # os.kill(pid, signal.SIGINT)
            print("Running instance found, PID {}".format(pid))
            sys.exit(0)
        except ProcessLookupError:
            pass
    save_string(str(os.getpid()), lock_file)

    load_vocabulary()

    print("{}: {}".format(voc["first-installed-version"], shell_data["installed-version"]))
    print("{}: {}".format(voc["current-version"], current_shell_version))
    pending_updates = []
    version_descriptions = []
    # If shell not just installed, let's check updates
    if current_shell_version > shell_data["installed-version"]:
        for version in __need_update__:
            if is_newer(version, shell_data["installed-version"]) and version not in shell_data["updates"]:
                version_descriptions.append(load_text_file(os.path.join(updates_dir, version)))
                pending_updates.append(version)

        content = '\n'.join(version_descriptions)

        if len(pending_updates) == 0:
            content = '<span font-size="large">{}</span>'.format(voc["you-are-up-to-date"])
            btn_update.set_sensitive(False)
            print(voc["you-are-up-to-date"])
    else:
        # Just installed, no check needed
        content = '<span font-size="large">{}</span>'.format(voc["you-are-up-to-date"])
        btn_update.set_sensitive(False)
        print("Just installed, nothing to do.")

    window = Gtk.Window.new(Gtk.WindowType.TOPLEVEL)

    window.connect('destroy', terminate)
    window.connect("key-release-event", handle_keyboard)

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    box.set_property("margin", 6)
    box.set_property("hexpand", True)
    window.add(box)

    frame = Gtk.Frame.new(" {} ".format(voc["pending-updates"]))
    frame.set_label_align(0.5, 0.5)
    box.pack_start(frame, True, True, 0)

    scrolled_window = Gtk.ScrolledWindow.new(None, None)
    scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
    scrolled_window.set_propagate_natural_height(True)
    frame.add(scrolled_window)

    label = Gtk.Label()
    label.set_line_wrap(True)
    label.set_markup(content)
    label.set_property("vexpand", True)
    label.set_property("hexpand", True)
    label.set_property("valign", Gtk.Align.START)
    label.set_property("halign", Gtk.Align.START)
    label.set_property("margin", 10)
    scrolled_window.add(label)

    h_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 6)
    box.pack_end(h_box, False, False, 0)

    img = Gtk.Image.new_from_icon_name("nwg-shell", Gtk.IconSize.BUTTON)
    h_box.pack_start(img, False, False, 0)
    lbl = Gtk.Label()
    lbl.set_markup(
        'nwg-shell-updater  <a href="https://github.com/nwg-piotr/nwg-shell/discussions/categories/changelog">{}</a>'.format(voc["updates-page"]))
    h_box.pack_start(lbl, False, False, 0)

    btn_update.set_label(voc["update"])
    h_box.pack_end(btn_update, False, False, 0)
    btn_update.connect("clicked", do_update, frame, label, pending_updates)

    btn_close = Gtk.Button.new()
    btn_close.set_label(voc["close"])
    btn_close.connect("clicked", terminate)
    h_box.pack_end(btn_close, False, False, 6)

    window.show_all()

    catchable_sigs = set(signal.Signals) - {signal.SIGKILL, signal.SIGSTOP}
    for sig in catchable_sigs:
        signal.signal(sig, signal_handler)

    Gtk.main()


def do_update(btn, frame, label, updates):
    frame.set_label(" Updating ")
    label.set_text("")
    log_path = os.path.join(get_shell_data_dir(), "update.log")
    log_file = open(log_path, 'a')
    label.set_justify(Gtk.Justification.LEFT)

    for version in updates:
        now = dt.now()
        log_line(log_file, label, "['{}' update {}]\n".format(version, now))
        update_version(version, log_file, label, config_home, shell_data)

    # Delete unused scripts
    home = os.getenv("HOME")
    paths = [os.path.join(home, "bin"), os.path.join(home, ".local", "bin")]
    scripts = ["import-gsettings", "sway-save-outputs", "screenshot", "sway-check-updates", "sway-update"]
    for path in paths:
        for script in scripts:
            script_path = os.path.join(home, path, script)
            if os.path.isfile(script_path):
                os.remove(script_path)
                log_line(log_file, label, "Deleted '{}' script.\n".format(os.path.join(path, script)))

    log_line(log_file, label, "\n")

    # Inform about no longer needed packages
    for item in ["lxappearance", "wdisplays", "nwg-wrapper", "autotiling"]:
        if is_command(item):
            log_line(log_file, label,
                     "The '{}' package is no longer necessary, you may uninstall it now.\n".format(item))

    # Save shell data file
    save_json(shell_data, os.path.join(get_shell_data_dir(), "data"))

    log_line(log_file, label, "\nUpdate log: '{}'\n\n".format(log_path))
    log_file.close()
    btn.set_sensitive(False)


if __name__ == "__main__":
    sys.exit(main())
