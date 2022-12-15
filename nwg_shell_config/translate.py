#!/usr/bin/env python3

import gi
import locale
import os
import sys

from nwg_shell_config.tools import load_json, eprint

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

dir_name = os.path.dirname(__file__)


def handle_keyboard(win, event):
    if event.type == Gdk.EventType.KEY_RELEASE and event.keyval == Gdk.KEY_Escape:
        win.destroy()


def main():
    user_locale = locale.getlocale()[0]
    voc_en_us = load_json(os.path.join(dir_name, "langs", "en_US.json"))
    if voc_en_us:
        print("Default dict:\ten_US.json, {} keys".format(len(voc_en_us)))
    else:
        eprint("Couldn't load basic dictionary, exiting.")
        sys.exit(1)

    voc_user = load_json(os.path.join(dir_name, "langs", "{}.json".format(user_locale)))
    if voc_user:
        print("User dict:\t\t{}.json, {} keys".format(user_locale, len(voc_user)))
    else:
        print("User lang {} does not yet exist, creating empty dictionary.".format(user_locale))

    keys = []
    for key in voc_en_us:
        keys.append(key)
    keys.sort()

    window = Gtk.Window.new(Gtk.WindowType.TOPLEVEL)
    window.connect('destroy', Gtk.main_quit)
    window.connect("key-release-event", handle_keyboard)

    box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 6)
    box.set_property("margin", 12)
    window.add(box)

    translation_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 6)
    translation_box.set_property("expand", True)
    box.pack_start(translation_box, True, True, 0)

    lbl = Gtk.Label.new("Translation box")
    translation_box.pack_start(lbl, True, True, 0)

    button_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 6)
    box.pack_start(button_box, False, False, 0)

    lbl = Gtk.Label.new("Button box")
    button_box.pack_start(lbl, False, False, 0)

    window.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
