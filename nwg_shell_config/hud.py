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
import os
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

from gi.repository import Gtk, Gdk, GLib, GdkPixbuf, GtkLayerShell

from shutil import copy2
from psutil import process_iter

from nwg_shell_config.tools import get_config_home, load_json, eprint

config_home = get_config_home()
config_dir = os.path.join(config_home, 'nwg-hud')
dir_name = os.path.dirname(__file__)
settings = None
args = None


def handle_keyboard(win, event):
    if event.type == Gdk.EventType.KEY_RELEASE:
        if event.keyval == Gdk.KEY_Escape:
            Gtk.main_quit()


def create_pixbuf(icon_name, icon_size):
    # In case a full path was given
    if icon_name.startswith("/"):
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
            icon_name, icon_size, icon_size)
    else:
        icon_theme = Gtk.IconTheme.get_default()
        try:
            pixbuf = icon_theme.load_icon(icon_name, icon_size, Gtk.IconLookupFlags.FORCE_SIZE)
        except:
            pixbuf = icon_theme.load_icon("image-missing", icon_size, Gtk.IconLookupFlags.FORCE_SIZE)

    return pixbuf


def update_image(image, icon_name, icon_size):
    scale = image.get_scale_factor()
    icon_size *= scale
    pixbuf = create_pixbuf(icon_name, icon_size)
    surface = Gdk.cairo_surface_create_from_pixbuf(pixbuf, scale, image.get_window())
    image.set_from_surface(surface)


def main():
    for proc in process_iter():
        if "nwg-hud" in proc.name() and proc.pid != os.getpid():
            eprint("nwg-hud: running instance found, terminating")
            sys.exit(1)

    # initiate config files if not found
    if not os.path.isdir(config_dir):
        os.mkdir(config_dir)
    for filename in ["config.json", "style.css"]:
        file_path = os.path.join(config_dir, filename)
        if not os.path.isfile(os.path.join(config_dir, filename)):
            copy2(os.path.join(dir_name, "hud", filename), file_path)

    # load settings
    global settings
    settings = load_json(os.path.join(config_dir, "config.json"))

    parser = argparse.ArgumentParser()
    parser.add_argument("-i",
                        "--icon",
                        type=str,
                        default="",
                        help='Icon name or path')

    parser.add_argument("-z",
                        "--icon_size",
                        type=int,
                        default=48,
                        help="icon size")

    parser.add_argument("-m",
                        "--message",
                        type=str,
                        default="HUD message",
                        help='Message text to display')

    parser.add_argument("-t",
                        "--timeout",
                        type=int,
                        default=1000,
                        help="window Timeout in milliseconds")

    parser.add_argument("-ha",
                        "--horizontal_alignment",
                        type=str,
                        default="center",
                        help="window Horizontal Alignment: 'left' or 'right', 'center' by default")

    parser.add_argument("-va",
                        "--vertical_alignment",
                        type=str,
                        default="center",
                        help="window Vertical Alignment: 'top' or 'bottom', 'center' by default")

    parser.add_argument("-r",
                        "--margin",
                        type=int,
                        default=0,
                        help="window margin in pixels")

    parser.add_argument("-o",
                        "--output",
                        type=str,
                        default="",
                        help="name of the Output to display HUD on")

    parser.parse_args()
    global args
    args = parser.parse_args()
    print("[nwg-hud]")
    print(f"settings: {settings}")
    print(f"args: {args}")

    # arguments override settings, if given
    if args.icon:
        settings["icon"] = args.icon
    if args.icon_size not in [0, 48]:
        settings["icon_size"] = args.icon_size
    if args.message:
        settings["message"] = args.message
    if args.timeout not in [0, 1000]:
        try:
            settings["timeout"] = int(args.timeout)
        except Exception as e:
            eprint(e)
    if args.horizontal_alignment:
        settings["horizontal_alignment"] = args.horizontal_alignment
    if args.vertical_alignment:
        settings["vertical_alignment"] = args.vertical_alignment
    if args.margin:
        try:
            settings["margin"] = int(args.margin)
        except Exception as e:
            eprint(e)

    # make sure we have all values
    defaults = {
        "icon": "",
        "icon-size": 48,
        "message": "",
        "timeout": 1000,
        "horizontal-alignment": "",
        "vertical-alignment": "",
        "margin": 0,
        "output": ""
    }
    for key in defaults:
        if key not in settings:
            settings[key] = defaults[key]

    window = Gtk.Window.new(Gtk.WindowType.POPUP)

    GtkLayerShell.init_for_window(window)
    GtkLayerShell.set_layer(window, GtkLayerShell.Layer.TOP)
    GtkLayerShell.set_exclusive_zone(window, 0)
    GtkLayerShell.set_keyboard_mode(window, GtkLayerShell.KeyboardMode.ON_DEMAND)

    window.connect('destroy', Gtk.main_quit)
    window.connect("key-release-event", handle_keyboard)

    vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
    vbox.set_property("margin", 0)
    window.add(vbox)

    hbox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 12)
    hbox.set_property("margin", 12)
    vbox.pack_start(hbox, False, False, 0)

    if args.icon:
        img = Gtk.Image()
        update_image(img, settings["icon"], settings["icon-size"])
        hbox.pack_start(img, False, False, 0)

    lbl = Gtk.Label.new(settings["message"])
    hbox.pack_start(lbl, True, True, 0)

    # apply styling
    screen = Gdk.Screen.get_default()
    provider = Gtk.CssProvider()
    style_context = Gtk.StyleContext()
    style_context.add_provider_for_screen(screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
    try:
        provider.load_from_path(os.path.join(dir_name, "hud", "style.css"))
    except Exception as e:
        eprint(e)
    css = provider.to_string().encode('utf-8')
    provider.load_from_data(css)

    window.show_all()

    GLib.timeout_add(args.timeout, Gtk.main_quit)

    Gtk.main()


if __name__ == "__main__":
    main()
