#!/usr/bin/env python3

# Wrapper for 'swaylock' & 'gtklock' commands to use them with a random image, local of downloaded from unsplash.com.
# All the setting come from the 'nwg-shell-config' 'settings' data file.

import os
import random
import subprocess
import signal
import sys
import threading
import urllib.request
from datetime import datetime

import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, Gdk, GLib, GtkLayerShell

from nwg_shell_config.tools import get_data_dir, load_json

data_dir = get_data_dir()
settings = load_json(os.path.join(data_dir, "settings"))

pid = os.getpid()


def signal_handler(sig, frame):
    desc = {2: "SIGINT", 15: "SIGTERM", 10: "SIGUSR1"}
    if sig == 2 or sig == 15:
        print("Terminated with {}".format(desc[sig]))
        global pctl
        pctl.die()


def get_player_status():
    try:
        return subprocess.check_output("playerctl status 2>&1", shell=True).decode("utf-8").strip()
    except subprocess.CalledProcessError:
        return ""


def get_player_metadata():
    try:
        return subprocess.check_output("playerctl metadata --format '{{artist}}:#:{{title}}'", shell=True).decode(
            "utf-8").strip().split(":#:")
    except subprocess.CalledProcessError:
        return []


class PlayerctlWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self)
        screen = Gdk.Screen.get_default()
        provider = Gtk.CssProvider()
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        css = b"""
                button#app-btn { padding: 6px; border: none }
                * { border-radius: 5px; outline: none }
                window { background-color: rgba (0, 0, 0, 0.5) }
                """
        provider.load_from_data(css)

        GtkLayerShell.init_for_window(self)

        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.OVERLAY)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.BOTTOM, 1)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.RIGHT, 1)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.BOTTOM, 40)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.RIGHT, 60)
        lbl = Gtk.Label.new("label")
        self.add(lbl)
        lbl.set_property("margin", 20)
        self.show_all()

        GLib.timeout_add_seconds(2, self.get_output)

    def get_output(self):
        # status = get_player_status()
        # metadata = get_player_metadata()
        # print(status, metadata)
        now = datetime.now()

        current_time = now.strftime("%H:%M:%S")
        print("Current Time =", current_time)
        return True

    def refresh(self):
        thread = threading.Thread(target=self.get_output)
        thread.daemon = True
        thread.start()
        return True

    def die(self):
        Gtk.main_quit()
        self.destroy()


pctl = PlayerctlWindow()


def set_remote_wallpaper():
    global pctl
    pctl = PlayerctlWindow()
    url = "https://source.unsplash.com/{}x{}/?{}".format(settings["unsplash-width"], settings["unsplash-height"],
                                                         ",".join(settings["unsplash-keywords"]))
    wallpaper = os.path.join(data_dir, "wallpaper.jpg")
    try:
        r = urllib.request.urlretrieve(url, wallpaper)
        if r[1]["Content-Type"] in ["image/jpeg", "image/png"]:
            if settings["lockscreen-locker"] == "swaylock":
                subprocess.Popen('swaylock -i {} && kill -n 15 {}'.format(wallpaper, pid), shell=True)
            elif settings["lockscreen-locker"] == "gtklock":
                subprocess.Popen('gtklock -b {} && kill -n 15 {}'.format(wallpaper, pid), shell=True)

            Gtk.main()

    except Exception as e:
        print(e)
        set_local_wallpaper()


def set_local_wallpaper():
    global pctl
    pctl = PlayerctlWindow()

    paths = []
    dirs = settings["background-dirs"].copy()
    if settings["backgrounds-use-custom-path"] and settings["backgrounds-custom-path"]:
        dirs.append(settings["backgrounds-custom-path"])
    for d in dirs:
        for item in os.listdir(d):
            if os.path.isfile(os.path.join(d, item)):
                paths.append(os.path.join(d, item))
    if len(paths) > 0:
        p = paths[random.randrange(len(paths))]
        if settings["lockscreen-locker"] == "swaylock":
            subprocess.Popen('swaylock -i {} && kill -n 15 {}'.format(p, pid), shell=True)
        elif settings["lockscreen-locker"] == "gtklock":
            subprocess.Popen('gtklock -b {} && kill -n 15 {}'.format(p, pid), shell=True)

        Gtk.main()

    else:
        print("No image paths found")

        if settings["lockscreen-locker"] == "swaylock":
            subprocess.Popen('exec swaylock -f', shell=True)
        elif settings["lockscreen-locker"] == "gtklock":
            subprocess.Popen('exec gtklock -d', shell=True)

    sys.exit(0)


def main():
    catchable_sigs = set(signal.Signals) - {signal.SIGKILL, signal.SIGSTOP}
    for sig in catchable_sigs:
        signal.signal(sig, signal_handler)

    if settings["lockscreen-custom-cmd"]:
        subprocess.Popen('exec {}'.format(settings["lockscreen-custom-cmd"]), shell=True)

        sys.exit(0)

    if settings["lockscreen-background-source"] == "unsplash":
        set_remote_wallpaper()

    elif settings["lockscreen-background-source"] == "local":
        set_local_wallpaper()


if __name__ == '__main__':
    main()
