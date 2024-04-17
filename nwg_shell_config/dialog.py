#!/usr/bin/env python3

"""
This script displays a simple confirmation window and executes a command, if given.
Repository: https://github.com/nwg-piotr/nwg-shell-config
Project site: https://nwg-piotr.github.io/nwg-shell
Author's email: nwg.piotr@gmail.com
Copyright (c) 2021-2024 Piotr Miller
License: MIT
"""

import argparse
import locale
import os
import subprocess
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

from gi.repository import Gtk, Gdk, GtkLayerShell

from nwg_shell_config.tools import get_config_home, load_shell_data, load_json, eprint

config_home = get_config_home()
dir_name = os.path.dirname(__file__)
voc = {}
args = None


def handle_keyboard(win, event):
    if event.type == Gdk.EventType.KEY_RELEASE:
        if event.keyval == Gdk.KEY_Escape:
            Gtk.main_quit()


def launch(*arguments):
    if args.cmd:
        eprint(f"Executing: {args.cmd}")
        subprocess.Popen('{}'.format(args.cmd), shell=True)
        Gtk.main_quit()
    else:
        eprint("No command provided")
        Gtk.main_quit()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c",
                        "--cmd",
                        type=str,
                        default="",
                        help='Command to execute if "Yes" clicked')

    parser.add_argument("-d",
                        "--dict",
                        action="store_true",
                        help="list Dictionary for current $LANG")

    parser.add_argument("-i",
                        "--icon",
                        type=str,
                        default="dialog-question",
                        help="Icon name")

    parser.add_argument("-l",
                        "--lang",
                        type=str,
                        default="",
                        help="force used Lang value (like en_US, pl_PL)")

    parser.add_argument("-p",
                        "--prompt",
                        type=str,
                        default="Did you forget\nto include a prompt?",
                        help="dialog window Prompt: string or a dictionary key")

    parser.parse_args()
    global args
    args = parser.parse_args()
    eprint(f"args: {args}")

    if args.lang:
        lang = args.lang
    else:
        shell_data = load_shell_data()
        lang = shell_data["interface-locale"] if "interface-locale" in shell_data and shell_data[
            "interface-locale"] else locale.getlocale()[0]
    eprint(f"User locale: {lang}")

    langs_dir = os.path.join(dir_name, "dialog")
    translations = os.listdir(langs_dir)

    global voc
    voc = load_json(os.path.join(langs_dir, "en_US"))

    if lang not in translations:
        eprint(f"Translation into '{lang}' not found. en_US will be used.")
    else:
        eprint(f"Translation into '{lang}' found.")
        user_lang = load_json(os.path.join(langs_dir, lang))
        for key in voc:
            if key in user_lang:
                voc[key] = user_lang[key]
        eprint(f"Vocabulary: {voc}")

    if args.dict:
        print(f"Key: value pairs for lang '{lang}':")
        for key in voc:
            print(f"'{key}': '{voc[key]}'")
        sys.exit(0)

    prompt = voc[args.prompt] if args.prompt in voc else args.prompt

    window = Gtk.Window.new(Gtk.WindowType.POPUP)
    window.set_size_request(200, 0)

    GtkLayerShell.init_for_window(window)
    GtkLayerShell.set_layer(window, GtkLayerShell.Layer.TOP)
    GtkLayerShell.set_exclusive_zone(window, 0)
    GtkLayerShell.set_keyboard_mode(window, GtkLayerShell.KeyboardMode.ON_DEMAND)

    window.connect('destroy', Gtk.main_quit)
    window.connect("key-release-event", handle_keyboard)

    vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 12)
    vbox.set_property("margin", 12)
    window.add(vbox)

    box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
    vbox.pack_start(box, False, False, 0)
    img = Gtk.Image.new_from_icon_name(args.icon, Gtk.IconSize.DIALOG)
    box.pack_start(img, True, True, 0)

    box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
    vbox.pack_start(box, False, False, 0)
    lbl = Gtk.Label.new(prompt)
    lbl.set_property("justify", Gtk.Justification.CENTER)
    box.pack_start(lbl, True, True, 0)

    box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 6)
    vbox.pack_start(box, False, False, 0)
    btn = Gtk.Button.new_with_label(voc["no"])
    btn.connect("clicked", Gtk.main_quit)

    box.pack_start(btn, True, True, 0)
    btn_y = Gtk.Button.new_with_label(voc["yes"])
    box.pack_start(btn_y, True, True, 0)

    window.show_all()

    if args.cmd:
        btn_y.connect("clicked", launch)
        btn_y.grab_focus()

    Gtk.main()


if __name__ == "__main__":
    main()
