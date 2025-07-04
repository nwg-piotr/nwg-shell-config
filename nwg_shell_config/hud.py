#!/usr/bin/env python3

"""
This script displays a window containing given icon and text, a closes it on timeout.
Repository: https://github.com/nwg-piotr/nwg-shell-config
Project site: https://nwg-piotr.github.io/nwg-shell
Author's email: nwg.piotr@gmail.com
Copyright (c) 2024-2025 Piotr Miller
License: MIT
"""

import argparse
import json
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


def list_outputs():
    outputs_dict = {}
    if os.getenv("SWAYSOCK"):
        try:
            from i3ipc import Connection
        except ModuleNotFoundError:
            print("'python-i3ipc' package required on sway, terminating")
            sys.exit(1)

        i3 = Connection()
        outputs = i3.get_outputs()
        for item in outputs:
            outputs_dict[item.name] = {"description": f"{item.make} {item.model} {item.serial}",
                                       "monitor": None}

    elif os.getenv('HYPRLAND_INSTANCE_SIGNATURE') is not None:
        cmd = "hyprctl -j monitors"
        result = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()
        outputs = json.loads(result)
        for item in outputs:
            outputs_dict[item["name"]] = {"description": item["description"],
                                          "monitor": None}

    else:
        eprint("nwg-hud script only works on sway or Hyprland, terminating")
        sys.exit(1)

    monitors = []
    display = Gdk.Display.get_default()
    for i in range(display.get_n_monitors()):
        monitor = display.get_monitor(i)
        monitors.append(monitor)

    for key, monitor in zip(outputs_dict.keys(), monitors):
        outputs_dict[key]["monitor"] = monitor

    # map monitor descriptions to output names
    mon_desc2output_name = {}
    for key in outputs_dict:
        if "description" in outputs_dict[key]:
            mon_desc2output_name[outputs_dict[key]["description"]] = key

    return outputs_dict, mon_desc2output_name


def main():
    # disallow multiple instances
    for proc in process_iter():
        if "nwg-hud" in proc.name() and proc.pid != os.getpid():
            eprint(f"nwg-hud: running instance found, PID {proc.pid}, terminating")
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

    parser.add_argument("-k",
                        "--keyboard",
                        action="store_true",
                        default=False,
                        help='turn on Keyboard support (Esc to close)')

    parser.add_argument("-z",
                        "--icon_size",
                        type=int,
                        default=48,
                        help="icon siZe")

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
                        help="window maRgin in pixels")

    parser.add_argument("-o",
                        "--output",
                        type=str,
                        default="",
                        help="name of the Output to display HUD on")

    parser.parse_args()
    global args
    args = parser.parse_args()

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
    if args.horizontal_alignment != "center":
        settings["horizontal-alignment"] = args.horizontal_alignment
    if args.vertical_alignment != "center":
        settings["vertical-alignment"] = args.vertical_alignment
    if args.margin:
        try:
            settings["margin"] = int(args.margin)
        except Exception as e:
            eprint(e)
    if args.output:
        settings["output"] = args.output

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
    if args.keyboard:
        GtkLayerShell.set_keyboard_mode(window, GtkLayerShell.KeyboardMode.ON_DEMAND)
    GtkLayerShell.set_namespace(window, "nwg-hud")

    if settings["vertical-alignment"] == "top":
        GtkLayerShell.set_anchor(window, GtkLayerShell.Edge.TOP, 1)
    elif settings["vertical-alignment"] == "bottom":
        GtkLayerShell.set_anchor(window, GtkLayerShell.Edge.BOTTOM, 1)
    if settings["horizontal-alignment"] == "left":
        GtkLayerShell.set_anchor(window, GtkLayerShell.Edge.LEFT, 1)
    elif settings["horizontal-alignment"] == "right":
        GtkLayerShell.set_anchor(window, GtkLayerShell.Edge.RIGHT, 1)

    if settings["margin"] > 0:
        GtkLayerShell.set_margin(window, GtkLayerShell.Edge.TOP, settings["margin"])
        GtkLayerShell.set_margin(window, GtkLayerShell.Edge.BOTTOM, settings["margin"])
        GtkLayerShell.set_margin(window, GtkLayerShell.Edge.LEFT, settings["margin"])
        GtkLayerShell.set_margin(window, GtkLayerShell.Edge.RIGHT, settings["margin"])

    # assign to a monitor if output name or monitor description given
    if settings["output"]:
        outputs, mon_desc2output_name = list_outputs()
        monitor = None
        if settings["output"] in outputs and "monitor" in outputs[settings["output"]]:
            monitor = outputs[settings["output"]]["monitor"]
        elif settings["output"] in mon_desc2output_name:
            name = mon_desc2output_name[settings["output"]]
            monitor = outputs[name]["monitor"]
        else:
            eprint(f"Couldn't assign monitor to {settings['output']}")

        if monitor:
            GtkLayerShell.set_monitor(window, monitor)

    window.connect('destroy', Gtk.main_quit)
    window.connect("key-release-event", handle_keyboard)

    vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
    vbox.set_property("margin", 0)
    window.add(vbox)

    hbox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 12)
    hbox.set_property("margin", 12)
    vbox.pack_start(hbox, False, False, 0)

    if settings["icon"]:
        img = Gtk.Image()
        update_image(img, settings["icon"], settings["icon-size"])
        hbox.pack_start(img, False, False, 0)

    lbl = Gtk.Label()
    lbl.set_markup(settings["message"])
    hbox.pack_start(lbl, True, True, 0)

    # apply styling
    screen = Gdk.Screen.get_default()
    provider = Gtk.CssProvider()
    style_context = Gtk.StyleContext()
    style_context.add_provider_for_screen(screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
    try:
        provider.load_from_path(os.path.join(config_dir, "style.css"))
    except Exception as e:
        eprint(e)
    css = provider.to_string().encode('utf-8')
    provider.load_from_data(css)

    window.show_all()

    GLib.timeout_add(settings["timeout"], Gtk.main_quit)

    Gtk.main()


if __name__ == "__main__":
    main()
