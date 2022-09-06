#!/usr/bin/env python3

"""
nwg-shell update window script
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
    is_newer, load_shell_data, is_command, save_json

from nwg_shell_config.updates import *

data_dir = get_data_dir()
updates_dir = os.path.join(dir_name, "updates")
btn_update = Gtk.Button()

shell_data = load_shell_data()

current_shell_version = get_shell_version()

lock_file = os.path.join(temp_dir(), "nwg-shell-updater.lock")

config_home = os.getenv('XDG_CONFIG_HOME') if os.getenv('XDG_CONFIG_HOME') else os.path.join(os.getenv("HOME"),
                                                                                             ".config")

data_home = os.getenv('XDG_DATA_HOME') if os.getenv('XDG_DATA_HOME') else os.path.join(os.getenv("HOME"),
                                                                                       ".local/share")


def terminate(*args):
    if os.path.isfile(lock_file):
        os.remove(lock_file)
    # Trigger 'Update' button refresh
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


def main():
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

    print("First installed version: {}".format(shell_data["installed-version"]))
    print("Current version: {}".format(current_shell_version))
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
            content = '<span font-size="large">You are up to date :)</span>'
            btn_update.set_sensitive(False)
            print("You are up to date :)")
    else:
        # Just installed, no check needed
        content = '<span font-size="large">You are up to date :)</span>'
        btn_update.set_sensitive(False)
        print("Just installed, nothing to do.")

    window = Gtk.Window.new(Gtk.WindowType.TOPLEVEL)

    window.connect('destroy', terminate)
    window.connect("key-release-event", handle_keyboard)

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    box.set_property("margin", 6)
    box.set_property("hexpand", True)
    window.add(box)

    frame = Gtk.Frame.new(" Pending updates ")
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
    lbl.set_markup('nwg-shell updates  <a href="https://nwg-piotr.github.io/nwg-shell/updates">Updates page</a>')
    h_box.pack_start(lbl, False, False, 0)

    btn_update.set_label("Update")
    h_box.pack_end(btn_update, False, False, 0)
    btn_update.connect("clicked", do_update, frame, label, pending_updates)

    btn_close = Gtk.Button.new()
    btn_close.set_label("Close")
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

    # Inform about no longer needed stuff
    # Packages
    for item in ["lxappearance", "wdisplays", "nwg-wrapper", "autotiling"]:
        if is_command(item):
            log_line(log_file, label,
                     "The '{}' package is no longer necessary, you may uninstall it now.\n".format(item))

    # Scripts
    for item in ["import-gsettings", "sway-save-outputs"]:
        if is_command(item):
            c = is_command(item)
            if c:
                log_line(log_file, label,
                         "The '{}' script is no longer necessary, you may delete it now.\n".format(item))

    # Save shell data file
    save_json(shell_data, os.path.join(get_shell_data_dir(), "data"))

    log_line(log_file, label, "\nUpdate log: '{}'\n\n".format(log_path))
    log_file.close()
    btn.set_sensitive(False)


if __name__ == "__main__":
    sys.exit(main())
