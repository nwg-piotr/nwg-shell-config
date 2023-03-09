#!/usr/bin/env python3

"""
nwg-shell translation utility
Copyright: 2023 Piotr Miller
e-mail: nwg.piotr@gmail.com
Repository: https://github.com/nwg-piotr/nwg-shell-config
Project: https://github.com/nwg-piotr/nwg-shell
License: MIT
"""

import gi
import importlib
import locale
import os
import sys

from nwg_shell_config.tools import load_json, save_json, load_shell_data, eprint

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib

from importlib import util

dir_name = os.path.dirname(__file__)

# "entry_point": "command-name"
modules = {
    "nwg_shell_config": "nwg-shell-config",
    "nwg_panel": "nwg-panel",
    "nwg_displays": "nwg-displays",
    "azote": "Azote"
}
# supported apps, that aren't python modules
apps = ["nwg-look"]

existing_langs = []
keys = []
voc_en_us = {}
voc_user = {}
app_in_edition = ""
user_locale = None
scrolled_window = None
translation_box = None
lang_hint_menu = None
existing_translations_label = None
keys_label = None
window = None


class Row(Gtk.Box):
    def __init__(self, key, voc_user):
        super().__init__()
        global voc_en_us
        self.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.set_spacing(6)
        vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.pack_start(vbox, True, True, 0)
        self.key = key
        self.voc_en_us = voc_en_us
        self.voc_user = voc_user

        lbl = Gtk.Label()
        lbl.set_markup('<b>"{}"</b>'.format(self.key))
        lbl.set_property("halign", Gtk.Align.START)
        vbox.pack_start(lbl, False, False, 0)

        lbl = Gtk.Label.new(self.voc_en_us[self.key])
        lbl.set_property("name", "original-text")
        lbl.set_selectable(True)
        lbl.set_line_wrap(True)
        lbl.set_property("halign", Gtk.Align.START)
        vbox.pack_start(lbl, False, False, 0)

        text_view = Gtk.TextView()
        text_view.set_property("name", "translation")
        self.text_buffer = text_view.get_buffer()
        translation = self.voc_user[self.key] if self.key in voc_user else ""
        self.text_buffer.set_text(translation)
        text_view.set_wrap_mode(Gtk.WrapMode.WORD)
        vbox.pack_start(text_view, False, False, 0)

        self.set_highlight()

        btn_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 6)
        self.pack_start(btn_box, False, False, 0)

        self.btn_apply = Gtk.Button.new_from_icon_name("object-select", Gtk.IconSize.BUTTON)
        self.btn_apply.set_tooltip_text("Apply")
        self.btn_apply.connect("clicked", self.on_btn_apply)
        self.btn_apply.set_sensitive(False)
        btn_box.pack_end(self.btn_apply, False, True, 0)

        self.btn_restore = Gtk.Button.new_from_icon_name("edit-undo", Gtk.IconSize.BUTTON)
        self.btn_restore.set_tooltip_text("Restore")
        self.btn_restore.connect("clicked", self.on_btn_restore)
        self.btn_restore.set_sensitive(False)
        btn_box.pack_end(self.btn_restore, False, True, 0)

    def connect_textview(self):
        self.text_buffer.connect("changed", self.on_text_buffer_changed)

    def on_text_buffer_changed(self, text_buffer):
        start, end = text_buffer.get_bounds()
        text = text_buffer.get_text(start, end, True)
        if text:
            if self.key not in self.voc_user or text != self.voc_user[self.key]:
                self.btn_apply.set_sensitive(True)
            else:
                self.btn_apply.set_sensitive(False)
        else:
            self.btn_apply.set_sensitive(False)
        if self.key in self.voc_user and text != self.voc_user[self.key]:
            self.btn_restore.set_sensitive(True)
        else:
            self.btn_restore.set_sensitive(False)

    def on_btn_restore(self, btn):
        if self.key in self.voc_user and self.voc_user[self.key]:
            self.text_buffer.set_text(self.voc_user[self.key])
        else:
            self.text_buffer.set_text("")

    def on_btn_apply(self, btn):
        start, end = self.text_buffer.get_bounds()
        text = self.text_buffer.get_text(start, end, True)
        if text:
            self.voc_user[self.key] = text
            btn.set_sensitive(False)
            self.btn_restore.set_sensitive(False)
            self.set_highlight()

    def set_highlight(self):
        if self.key in self.voc_user and self.voc_user[self.key]:
            self.set_property("name", "row")
        else:
            self.set_property("name", "row-empty")


def build_translation_window():
    global scrolled_window
    if scrolled_window:
        scrolled_window.destroy()

    scrolled_window = Gtk.ScrolledWindow.new(None, None)
    scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
    scrolled_window.set_propagate_natural_height(True)
    box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 6)
    scrolled_window.add(box)
    for key in keys:
        row = Row(key, voc_user)
        row.connect_textview()
        box.pack_start(row, False, False, 0)

    scrolled_window.show_all()
    translation_box.pack_start(scrolled_window, True, True, 0)

    window.show_all()


class LangHintMenu(Gtk.Menu):
    def __init__(self, text, valid_locales, entry):
        super().__init__()
        self.set_reserve_toggle_size(False)
        for loc in valid_locales:
            if text in loc:
                item = Gtk.MenuItem.new_with_label(loc)
                if loc in existing_langs:
                    item.set_property("name", "existing")
                item.connect("activate", set_entry_from_item, entry)
                self.append(item)
                self.show_all()


def set_entry_from_item(item, entry):
    entry.set_text(item.get_label())
    entry.grab_focus()


def validate_lang(entry, valid_locales, btn):
    global lang_hint_menu
    text = entry.get_text()
    if text in valid_locales:
        btn.set_sensitive(True)
    else:
        btn.set_sensitive(False)
        if len(text) >= 2:
            lang_hint_menu = LangHintMenu(text, valid_locales, entry)
            if len(lang_hint_menu.get_children()) > 0:
                lang_hint_menu.popup_at_widget(entry, Gdk.Gravity.NORTH, Gdk.Gravity.SOUTH, None)


def on_btn_select(btn, entry, fc_btn, combo):
    _locale = entry.get_text()
    global user_locale
    user_locale = _locale
    if _locale:
        load_dict_and_build_window(combo)
    fc_btn.unselect_all()


def on_btn_export(btn, ckb_ascii):
    global voc_user
    voc_user["_lang"] = user_locale
    voc_user["_module"] = app_in_edition
    save_json(voc_user, os.path.join(os.getenv("HOME"), "{}-{}.json".format(app_in_edition, user_locale)),
              en_ascii=ckb_ascii.get_active())


def on_file_chooser_button(fc_btn, entry_lang, combo):
    global voc_user
    voc_user = load_json(fc_btn.get_file().get_path())
    global user_locale
    user_locale = voc_user["_lang"]
    entry_lang.set_text(user_locale)
    # The "changed" signal must be emitted, even if we're setting the same id again.
    combo.set_active_id(None)
    combo.set_active_id(voc_user["_module"])  # Triggers the load_dict_and_build_window() function.


def load_dict_and_build_window(combo, load_voc_user=True):
    if combo.get_active_id():
        global app_in_edition
        app_in_edition = combo.get_active_id()
        print("\n[Application: '{}']".format(app_in_edition))
        # some apps won't be python modules, so the path will be different
        exclusions = ["nwg-look"]  # store langs in `/usr/share/app_name/langs/` (t.b.c.)
        if app_in_edition not in exclusions:
            name = importlib.util.find_spec(combo.get_active_id()).origin
            parts = name.split("/")
            langs_dir = os.path.join("/".join(parts[:-1]), "langs")
        else:
            langs_dir = os.path.join("/usr/share", app_in_edition, "langs")
        print("langs_dir: {}".format(langs_dir))

        global existing_langs
        existing_langs = []
        for item in os.listdir(langs_dir):
            if item.endswith(".json"):
                existing_langs.append(item.split(".")[0])
        print("Existing langs:", existing_langs)
        existing_translations_label.set_markup(
            "<small><b>Existing langs</b>: {}</small>".format(", ".join(existing_langs)))

        # basic dictionary
        global voc_en_us
        voc_en_us = load_json(os.path.join(langs_dir, "en_US.json"))
        if voc_en_us:
            print("Default dict: en_US.json, {} keys".format(len(voc_en_us)))
        else:
            eprint("Couldn't load basic dictionary, exiting.")
            sys.exit(1)

        # basic dictionary keys
        global keys
        keys = []
        for key in voc_en_us:
            keys.append(key)
        keys.sort()

        if load_voc_user:
            global voc_user
            voc_user = load_json(os.path.join(langs_dir, "{}.json".format(user_locale)))
            if voc_user:
                print("User dict: {}.json, {} keys".format(user_locale, len(voc_user)))
            else:
                voc_user = {}
                print("User lang '{}' does not yet exist, creating empty dictionary.".format(user_locale))

        build_translation_window()


def main():
    GLib.set_prgname('nwg-shell-translate')

    valid_locales = []
    for loc in os.listdir("/usr/share/i18n/locales/"):
        if not loc.startswith("translit") and "_" in loc:
            valid_locales.append(loc)
    print("{} valid locales found".format(len(valid_locales)))

    shell_data = load_shell_data()

    global user_locale
    user_locale = locale.getlocale()[0] if not shell_data["interface-locale"] else shell_data["interface-locale"]

    screen = Gdk.Screen.get_default()
    provider = Gtk.CssProvider()
    style_context = Gtk.StyleContext()
    style_context.add_provider_for_screen(screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
    css = b"""
            label#original-text { font-style: italic; padding: 2px }
            textview#translation { padding: 2px 2px 4px 2px }
            box#row { margin: 0 12px 0 0; padding: 6px; border: solid 1px }
            box#row-empty { margin: 0 12px 0 0; padding: 6px; border: solid 2px; border-color: #F00 }
            menuitem#existing { font-weight: bold; color: #0c6 }
            """
    provider.load_from_data(css)

    global window
    window = Gtk.Window.new(Gtk.WindowType.TOPLEVEL)
    window.connect('destroy', Gtk.main_quit)

    box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 6)
    box.set_property("margin", 6)
    window.add(box)

    app_select_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 6)
    box.pack_start(app_select_box, False, False, 6)
    lbl = Gtk.Label.new("Application:")
    app_select_box.pack_start(lbl, False, False, 0)

    combo = Gtk.ComboBoxText()
    app_select_box.pack_start(combo, False, False, 0)
    for key in modules:
        try:
            # Older nwg-shell components' versions may have no valid langs. We don't want them in the combo.
            name = importlib.util.find_spec(key).origin
            parts = name.split("/")
            base_dict = os.path.join("/".join(parts[:-1]), "langs", "en_US.json")
            if os.path.isfile(base_dict):
                combo.append(key, modules[key])
            else:
                eprint("Skipping '{}', 'en_US.json' file not found.".format(key))
        except:
            eprint("Couldn't find path for module '{}'".format(key))

    for app in apps:
        if os.path.isfile(os.path.join("/usr/share", app, "langs", "en_US.json")):
            combo.append(app, app)

    global existing_translations_label
    existing_translations_label = Gtk.Label()
    existing_translations_label.set_line_wrap_mode(Gtk.WrapMode.WORD)
    app_select_box.pack_start(existing_translations_label, False, False, 0)

    global translation_box
    translation_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 6)
    translation_box.set_property("expand", True)
    box.pack_start(translation_box, True, True, 0)

    button_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 6)
    button_box.set_property("margin", 6)
    box.pack_start(button_box, False, False, 0)

    img = Gtk.Image.new_from_icon_name("nwg-shell-translate", Gtk.IconSize.LARGE_TOOLBAR)
    button_box.pack_start(img, False, False, 0)
    lbl = Gtk.Label()
    lbl.set_markup("<b>nwg-shell-translate</b> | lang:".format(user_locale))
    button_box.pack_start(lbl, False, False, 0)

    btn_select = Gtk.Button.new_with_label("Select")
    btn_select.set_tooltip_text("Opens current dictionary for entered locale,\nif it exists. Otherwise - "
                                "creates an empty dictionary")

    fc_btn = Gtk.FileChooserButton.new("Open", Gtk.FileChooserAction.OPEN)

    entry_lang = Gtk.Entry()
    entry_lang.set_width_chars(10)
    entry_lang.set_text(user_locale)
    entry_lang.connect("changed", validate_lang, valid_locales, btn_select)
    button_box.pack_start(entry_lang, False, False, 0)

    button_box.pack_start(btn_select, False, False, 0)
    btn_select.connect("clicked", on_btn_select, entry_lang, fc_btn, combo)

    fc_btn.set_current_folder(os.getenv("HOME"))
    fc_btn.set_width_chars(10)
    fc_btn.set_tooltip_text("Opens your previously saved translation")
    f_filter = Gtk.FileFilter()
    f_filter.set_name("Translation files (*_??.json)")
    f_filter.add_pattern("*_??.json")
    fc_btn.connect("file-set", on_file_chooser_button, entry_lang, combo)
    fc_btn.add_filter(f_filter)
    button_box.pack_start(fc_btn, False, False, 0)

    ckb_ascii = Gtk.CheckButton.new()
    ckb_ascii.set_label("ASCII")
    ckb_ascii.set_tooltip_text("Replace accented characters with ASCII codes.")
    button_box.pack_end(ckb_ascii, False, False, 0)

    btn = Gtk.Button.new_with_label("Export")
    btn.set_tooltip_text("Exports current translation to a .json file in you $HOME directory.\n"
                         "You can then email it to nwg.piotr@gmail.com or share in another way.\n"
                         "E.g. gist.github.com is always a good idea.")
    btn.connect("clicked", on_btn_export, ckb_ascii)

    button_box.pack_end(btn, False, False, 0)

    btn = Gtk.Button.new_with_label("Close")
    btn.set_tooltip_text("Exits the program")
    btn.connect('clicked', Gtk.main_quit)
    button_box.pack_end(btn, False, False, 0)

    combo.connect("changed", load_dict_and_build_window)
    combo.set_active_id("nwg_shell_config")

    window.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
