#!/usr/bin/env python3

import gi
import locale
import os
import sys

from nwg_shell_config.tools import load_json, eprint

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib

dir_name = os.path.dirname(__file__)

translation_window = None


def handle_keyboard(win, event):
    if event.type == Gdk.EventType.KEY_RELEASE and event.keyval == Gdk.KEY_Escape:
        win.destroy()


def build_translation_window(keys, voc_en_us, voc_user):
    scrolled_window = Gtk.ScrolledWindow.new(None, None)
    scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
    scrolled_window.set_propagate_natural_height(True)
    box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 6)
    scrolled_window.add(box)
    for i in range(len(keys)):
        row = Gtk.Box.new(Gtk.Orientation.VERTICAL, 3)
        row.set_property("name", "row")
        box.pack_start(row, False, False, 0)
        key = keys[i]

        lbl = Gtk.Label()
        lbl.set_markup('<b>"{}"</b>'.format(key))
        lbl.set_property("halign", Gtk.Align.START)
        row.pack_start(lbl, False, False, 0)

        lbl = Gtk.Label.new(voc_en_us[key])
        lbl.set_line_wrap(True)
        lbl.set_property("halign", Gtk.Align.START)
        row.pack_start(lbl, False, False, 0)

        text_view = Gtk.TextView()
        text_view.set_property("name", "translation")
        text_buffer = text_view.get_buffer()
        translation = voc_user[key] if key in voc_user else ""
        text_buffer.set_text(translation)
        text_view.set_editable(True)
        text_view.set_wrap_mode(Gtk.WrapMode.WORD)
        row.pack_start(text_view, False, False, 0)

    scrolled_window.show_all()
    return scrolled_window


def main():
    GLib.set_prgname('nwg-shell-translate')

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

    screen = Gdk.Screen.get_default()
    provider = Gtk.CssProvider()
    style_context = Gtk.StyleContext()
    style_context.add_provider_for_screen(screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
    css = b"""
                textview#translation { padding: 4px 2px 4px 2px }
                box#row { margin: 0 12px 0 0; padding: 6px; border: solid 1px }
                """
    provider.load_from_data(css)

    window = Gtk.Window.new(Gtk.WindowType.TOPLEVEL)
    window.connect('destroy', Gtk.main_quit)
    window.connect("key-release-event", handle_keyboard)

    box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 6)
    box.set_property("margin", 6)
    window.add(box)

    translation_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 6)
    translation_box.set_property("expand", True)
    box.pack_start(translation_box, True, True, 0)

    button_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 6)
    button_box.set_property("margin", 6)
    box.pack_start(button_box, False, False, 0)

    img = Gtk.Image.new_from_icon_name("translator", Gtk.IconSize.LARGE_TOOLBAR)
    button_box.pack_start(img, False, False, 0)
    lbl = Gtk.Label()
    lbl.set_markup("nwg-shell-translate | <b>en_US</b> into <b>{}</b>".format(user_locale))
    button_box.pack_start(lbl, False, False, 0)

    btn = Gtk.Button.new_with_label("Export")
    button_box.pack_end(btn, False, False, 6)

    btn = Gtk.Button.new_with_label("Close")
    button_box.pack_end(btn, False, False, 6)

    global translation_window
    translation_window = build_translation_window(keys, voc_en_us, voc_user)
    translation_box.pack_start(translation_window, True, True, 0)

    window.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
