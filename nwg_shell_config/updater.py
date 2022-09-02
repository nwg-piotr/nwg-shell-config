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
import sys

import gi

gi.require_version('Gtk', '3.0')

dir_name = os.path.dirname(__file__)

from gi.repository import Gtk, Gdk

from nwg_shell_config.tools import temp_dir, init_files, get_data_dir, get_shell_data_dir, load_json, load_text_file, \
    save_string, current_shell_version, is_newer

# Shell versions that need to trigger upgrade
need_upgrade = ["0.2.0", "0.2.4", "0.2.5"]

data_dir = get_data_dir()
updates_dir = os.path.join(dir_name, "updates")
shell_data = load_json(os.path.join(get_shell_data_dir(), "data"))
print(shell_data)
# current_version = current_shell_version()
current_version = "0.2.0"


def signal_handler(sig, frame):
    if sig == 2 or sig == 15:
        desc = {2: "SIGINT", 15: "SIGTERM"}
        print("Terminated with {}".format(desc[sig]))
        Gtk.main_quit()


def handle_keyboard(win, event):
    if event.type == Gdk.EventType.KEY_RELEASE and event.keyval == Gdk.KEY_Escape:
        Gtk.main_quit()


def main():
    # Try and kill already running instance, if any
    pid_file = os.path.join(temp_dir(), "nwg-help.pid")
    if os.path.isfile(pid_file):
        try:
            pid = int(load_text_file(pid_file))
            os.kill(pid, signal.SIGINT)
            print("Running instance killed, PID {}".format(pid))
            sys.exit(0)
        except ProcessLookupError:
            pass
    save_string(str(os.getpid()), pid_file)

    version_descriptions = []
    for version in need_upgrade:
        if is_newer(current_version, version):
            print("current_version {} is newer than {}".format(current_version, version))
        else:
            content_path = os.path.join(updates_dir, version)
            version_descriptions.append(load_text_file(content_path))
            print("current_version {} is older than {}".format(current_version, version))

    content = "\n".join(version_descriptions)

    window = Gtk.Window.new(Gtk.WindowType.TOPLEVEL)

    window.connect('destroy', Gtk.main_quit)
    window.connect("key-release-event", handle_keyboard)

    scrolled_window = Gtk.ScrolledWindow.new(None, None)
    scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
    scrolled_window.set_propagate_natural_height(True)
    window.add(scrolled_window)

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    box.set_property("margin", 12)
    box.set_property("hexpand", True)
    scrolled_window.add(box)

    frame = Gtk.Frame.new(" Description ")
    frame.set_label_align(0.5, 0.5)
    frame.set_property("hexpand", True)
    label = Gtk.Label()
    label.set_line_wrap(True)
    label.set_markup(content)
    frame.add(label)

    box.pack_start(frame, False, False, 0)

    screen = Gdk.Screen.get_default()
    provider = Gtk.CssProvider()
    style_context = Gtk.StyleContext()
    style_context.add_provider_for_screen(screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
    css = b""" * { border-radius: 0px } """
    css += b""" window { border: solid 1px; border-color: #000 } """
    css += b""" label { padding: 10px } """
    provider.load_from_data(css)

    window.show_all()

    window.set_size_request(0, window.get_allocated_width() * 2)

    catchable_sigs = set(signal.Signals) - {signal.SIGKILL, signal.SIGSTOP}
    for sig in catchable_sigs:
        signal.signal(sig, signal_handler)

    Gtk.main()


if __name__ == "__main__":
    sys.exit(main())
