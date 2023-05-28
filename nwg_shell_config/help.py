#!/usr/bin/env python3

"""
nwg-shell helper script to display system help window
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
try:
    gi.require_version('GtkLayerShell', '0.1')
except ValueError:
    raise RuntimeError('\n\n' +
                       'If you haven\'t installed GTK Layer Shell, you need to point Python to the\n' +
                       'library by setting GI_TYPELIB_PATH and LD_LIBRARY_PATH to <build-dir>/src/.\n' +
                       'For example you might need to run:\n\n' +
                       'GI_TYPELIB_PATH=build/src LD_LIBRARY_PATH=build/src python3 ' + ' '.join(sys.argv))

dir_name = os.path.dirname(__file__)

from gi.repository import Gtk, Gdk, GtkLayerShell

from nwg_shell_config.tools import temp_dir, init_files, get_data_dir, load_json, load_text_file, save_string, eprint, \
    check_key

data_dir = get_data_dir()
settings = load_json(os.path.join(data_dir, "settings"))
defaults = {
    "help-font-size": 14,
    "help-layer-shell": True,
    "help-keyboard": False
}
for key in defaults:
    check_key(settings, key, defaults[key])


def signal_handler(sig, frame):
    if sig == 2 or sig == 15:
        desc = {2: "SIGINT", 15: "SIGTERM"}
        print("Terminated with {}".format(desc[sig]))
        Gtk.main_quit()


def handle_keyboard(win, event):
    if event.type == Gdk.EventType.KEY_RELEASE and event.keyval == Gdk.KEY_Escape:
        win.destroy()


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

    if os.getenv("SWAYSOCK"):
        content_path = os.path.join(data_dir, "help.pango")
    elif os.getenv("HYPRLAND_INSTANCE_SIGNATURE"):
        content_path = os.path.join(data_dir, "help-hyprland.pango")
    else:
        eprint("This program only works on sway or Hyprland, terminating.")
        sys.exit(1)

    if not os.path.isfile(content_path):
        init_files(os.path.join(dir_name, "shell"), data_dir)
    content = load_text_file(content_path)

    window = Gtk.Window.new(Gtk.WindowType.POPUP)

    if settings["help-layer-shell"]:
        GtkLayerShell.init_for_window(window)
        GtkLayerShell.set_layer(window, GtkLayerShell.Layer.OVERLAY)
        GtkLayerShell.set_exclusive_zone(window, 0)
        if settings["help-keyboard"]:
            GtkLayerShell.set_keyboard_mode(window, GtkLayerShell.KeyboardMode.ON_DEMAND)

    window.connect('destroy', Gtk.main_quit)
    window.connect("key-release-event", handle_keyboard)

    scrolled_window = Gtk.ScrolledWindow.new(None, None)
    scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
    scrolled_window.set_propagate_natural_height(True)
    window.add(scrolled_window)

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    box.set_property("margin", 12)
    scrolled_window.add(box)

    label = Gtk.Label()
    label.set_markup(content)

    box.pack_start(label, False, False, 0)

    screen = Gdk.Screen.get_default()
    provider = Gtk.CssProvider()
    style_context = Gtk.StyleContext()
    style_context.add_provider_for_screen(screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
    css = b""" * { border-radius: 0px } """
    css += b""" window { border: solid 1px; border-color: #000 } """
    font_string = "label { font-size: %dpx }" % settings["help-font-size"]
    css += str.encode(font_string)
    provider.load_from_data(css)

    window.show_all()

    if settings["help-layer-shell"]:
        window.set_size_request(0, window.get_allocated_width() * 2)

    catchable_sigs = set(signal.Signals) - {signal.SIGKILL, signal.SIGSTOP}
    for sig in catchable_sigs:
        signal.signal(sig, signal_handler)

    Gtk.main()


if __name__ == "__main__":
    sys.exit(main())
