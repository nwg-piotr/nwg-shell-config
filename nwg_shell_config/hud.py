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

from nwg_shell_config.tools import get_config_home, eprint

config_home = get_config_home()
config_dir = os.path.join(config_home, 'nwg-hud')
dir_name = os.path.dirname(__file__)
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
    # Initiate config files
    if not os.path.isdir(config_dir):
        os.mkdir(config_dir)
    style_path = os.path.join(config_dir, "style.css")
    if not os.path.isfile(os.path.join(config_dir, "style.css")):
        copy2(os.path.join(dir_name, "hud", "style.css"), style_path)

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
                        help="window Timeout in milliseconds")

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

    parser.add_argument("-o",
                        "--output",
                        type=str,
                        default="",
                        help="name of the Output to display HUD on")

    parser.add_argument("-ha",
                        "--horizontal_alignment",
                        type=str,
                        default="",
                        help="window Horizontal Alignment")

    parser.add_argument("-va",
                        "--vertical_alignment",
                        type=str,
                        default="",
                        help="window Vertical Alignment")

    parser.parse_args()
    global args
    args = parser.parse_args()
    eprint(f"args: {args}")

    window = Gtk.Window.new(Gtk.WindowType.POPUP)
    # window.set_size_request(200, 0)

    GtkLayerShell.init_for_window(window)
    GtkLayerShell.set_layer(window, GtkLayerShell.Layer.TOP)
    GtkLayerShell.set_exclusive_zone(window, 0)
    GtkLayerShell.set_keyboard_mode(window, GtkLayerShell.KeyboardMode.ON_DEMAND)

    window.connect('destroy', Gtk.main_quit)
    window.connect("key-release-event", handle_keyboard)

    vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 6)
    vbox.set_property("margin", 0)
    window.add(vbox)

    box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 6)
    vbox.pack_start(box, False, False, 6)

    if args.icon:
        img = Gtk.Image()
        update_image(img, args.icon, args.icon_size)
        box.pack_start(img, False, False, 6)

    lbl = Gtk.Label.new(args.message)
    box.pack_start(lbl, True, True, 6)

    # apply styling
    screen = Gdk.Screen.get_default()
    provider = Gtk.CssProvider()
    style_context = Gtk.StyleContext()
    style_context.add_provider_for_screen(screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
    try:
        provider.load_from_path(style_path)
    except Exception as e:
        eprint(e)
    css = provider.to_string().encode('utf-8')
    provider.load_from_data(css)

    window.show_all()

    GLib.timeout_add(args.timeout, Gtk.main_quit)

    Gtk.main()


if __name__ == "__main__":
    main()
