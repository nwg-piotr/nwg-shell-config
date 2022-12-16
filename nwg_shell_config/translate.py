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


class Row(Gtk.Box):
    def __init__(self, key, voc_en_us, voc_user):
        super().__init__()
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(3)
        self.key = key
        self.voc_en_us = voc_en_us
        self.voc_user = voc_user

        lbl = Gtk.Label()
        lbl.set_markup('<b>"{}"</b>'.format(self.key))
        lbl.set_property("halign", Gtk.Align.START)
        self.pack_start(lbl, False, False, 0)

        lbl = Gtk.Label.new(self.voc_en_us[self.key])
        lbl.set_property("name", "original-text")
        lbl.set_line_wrap(True)
        lbl.set_property("halign", Gtk.Align.START)
        self.pack_start(lbl, False, False, 0)

        text_view = Gtk.TextView()
        text_view.set_property("name", "translation")
        self.text_buffer = text_view.get_buffer()
        translation = self.voc_user[self.key] if self.key in voc_user else ""
        self.text_buffer.set_text(translation)
        text_view.set_editable(True)
        text_view.set_wrap_mode(Gtk.WrapMode.WORD)
        self.pack_start(text_view, False, False, 0)

        self.set_highlight()

    def set_highlight(self):
        if self.key in self.voc_user and self.voc_user[self.key]:
            self.set_property("name", "row")
        else:
            self.set_property("name", "row-empty")


def build_translation_window(keys, voc_en_us, voc_user):
    scrolled_window = Gtk.ScrolledWindow.new(None, None)
    scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
    scrolled_window.set_propagate_natural_height(True)
    box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 6)
    scrolled_window.add(box)
    for key in keys:
        row = Row(key, voc_en_us, voc_user)
        box.pack_start(row, False, False, 0)

    scrolled_window.show_all()
    return scrolled_window


def main():
    GLib.set_prgname('nwg-shell-translate')
    # List valid locales
    valid_locales = []
    for loc in os.listdir("/usr/share/i18n/locales/"):
        if not loc.startswith("translit") and "_" in loc:
            valid_locales.append(loc)
    print("{} valid locales found".format(len(valid_locales)))

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
            label#original-text { font-style: italic; padding: 2px }
            textview#translation { padding: 2px 2px 4px 2px }
            box#row { margin: 0 12px 0 0; padding: 6px; border: solid 1px }
            box#row-empty { margin: 0 12px 0 0; padding: 6px; border: solid 1px; border-color: #F00 }
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
    button_box.pack_end(btn, False, False, 3)

    btn = Gtk.Button.new_with_label("Close")
    btn.connect('clicked', Gtk.main_quit)
    button_box.pack_end(btn, False, False, 3)

    global translation_window
    translation_window = build_translation_window(keys, voc_en_us, voc_user)
    translation_box.pack_start(translation_window, True, True, 0)

    window.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
