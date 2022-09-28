#!/usr/bin/env python3

# Wrapper for 'swaylock' & 'gtklock' commands to use them with a random image, local of downloaded from unsplash.com.
# All the setting come from the 'nwg-shell-config' 'settings' data file.

import os
import random
import subprocess
import signal
import sys
import urllib.request

import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('GdkPixbuf', '2.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf, GtkLayerShell

from urllib.parse import unquote, urlparse

from nwg_shell_config.tools import get_data_dir, temp_dir, load_json, load_text_file, save_string

config_home = os.getenv('XDG_CONFIG_HOME') if os.getenv('XDG_CONFIG_HOME') else os.path.join(os.getenv("HOME"),
                                                                                             ".config/")
data_dir = get_data_dir()
tmp_dir = temp_dir()
settings = load_json(os.path.join(data_dir, "settings"))
preset = load_json(
    os.path.join(data_dir, settings["panel-preset"])) if "panel-preset" in settings and "panel-preset" else {}

pid = os.getpid()
pctl = None
cover = None

defaults = {
    "panel-preset": "preset-0",
    "lockscreen-use-settings": True,
    "lockscreen-locker": "swaylock",  # swaylock | gtklock
    "lockscreen-background-source": "local",  # unsplash | local
    "lockscreen-custom-cmd": "",
    "lockscreen-timeout": 1200,
    "lockscreen-playerctl": True,
    "lockscreen-playerctl-position": "bottom-right",
    "lockscreen-playerctl-hmargin": 60,
    "lockscreen-playerctl-vmargin": 40,
    "sleep-cmd": 'swaymsg "output * dpms off"',
    "sleep-timeout": 1800,
    "resume-cmd": 'swaymsg "output * dpms on"',
    "before-sleep": "",
    "backgrounds-custom-path": "",
    "backgrounds-use-custom-path": False,
    "background-dirs": ["/usr/share/backgrounds/nwg-shell"],
    "background-dirs-once-set": False,
    "unsplash-width": 1920,
    "unsplash-height": 1080,
    "unsplash-keywords": ["nature", "water", "landscape"],
    "gtklock-time-format": "%H:%M:%S",
    "gtklock-idle-timeout": 10,
    "gtklock-userinfo": False,
    "gtklock-powerbar": False
}

preset_defaults = {
    "gtklock-userinfo-round-image": True,
    "gtklock-userinfo-vertical-layout": False,
    "gtklock-userinfo-under-clock": False,
    "gtklock-powerbar-show-labels": False,
    "gtklock-powerbar-linked-buttons": False,
    "gtklock-playerctl-art-size": 64,
    "gtklock-playerctl-position": "top-right"
}


def signal_handler(sig, frame):
    desc = {2: "SIGINT", 15: "SIGTERM", 10: "SIGUSR1"}
    if sig == 2 or sig == 15:
        print("Terminated with {}".format(desc[sig]))
        global pctl
        if pctl:
            pctl.die()


def get_player_status():
    try:
        return subprocess.check_output("playerctl status 2>&1", shell=True).decode("utf-8").strip()
    except subprocess.CalledProcessError:
        return ""


def get_player_metadata():
    output = {"artist": "", "title": "", "artUrl": ""}
    try:
        lines = subprocess.check_output("playerctl metadata --format '{{artist}}:#:{{title}}:#:{{mpris:artUrl}}'", shell=True).decode(
            "utf-8").strip().split(":#:")
        if len(lines) > 0:
            output["artist"] = lines[0]
        if len(lines) > 1:
            output["title"] = lines[1]
        if len(lines) > 2:
            # output["artUrl"] = lines[2]
            output["artUrl"] = unquote(urlparse(lines[2]).path)
    except subprocess.CalledProcessError:
        pass

    return output


def launch(button, cmd):
    subprocess.Popen('exec {}'.format(cmd), shell=True)


class PlayerctlWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self)
        self.retries = 3
        self.btn_backward = None
        self.btn_play_pause = None
        self.btn_forward = None

        screen = Gdk.Screen.get_default()
        provider = Gtk.CssProvider()
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        css = b"""
                label { font-weight: bold }
                button { padding: 6px; background: none; border: none }
                button:hover { background: rgba (255, 255, 255, 0.1) }
                window { background-color: rgba (0, 0, 0, 0.5) }
                * { border-radius: 0px; outline: none }
                #dead { background-color: rgba (0, 0, 0, 0.0) }
                """
        provider.load_from_data(css)

        GtkLayerShell.init_for_window(self)

        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.OVERLAY)

        if settings["lockscreen-playerctl-position"] in ["top-left", "top", "top-right"]:
            GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.TOP, 1)
        elif settings["lockscreen-playerctl-position"] in ["bottom-left", "bottom", "bottom-right"]:
            GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.BOTTOM, 1)

        if settings["lockscreen-playerctl-position"] in ["top-left", "bottom-left"]:
            GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.LEFT, 1)
        elif settings["lockscreen-playerctl-position"] in ["top-right", "bottom-right"]:
            GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.RIGHT, 1)

        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.TOP, settings["lockscreen-playerctl-vmargin"])
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.BOTTOM, settings["lockscreen-playerctl-vmargin"])
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.RIGHT, settings["lockscreen-playerctl-hmargin"])
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.LEFT, settings["lockscreen-playerctl-hmargin"])

        ext_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.add(ext_box)
        global cover
        cover = Gtk.Image.new_from_icon_name("image-missing", Gtk.IconSize.BUTTON)
        ext_box.pack_start(cover, False, False, 6)

        vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 12)
        vbox.set_property("margin", 12)
        ext_box.pack_start(vbox, True, True, 0)
        hbox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        vbox.pack_start(hbox, True, True, 0)
        self.label = Gtk.Label()
        self.label.set_property("justify", Gtk.Justification.CENTER)
        hbox.pack_start(self.label, True, True, 0)

        if settings["lockscreen-locker"] == "gtklock":
            hbox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
            vbox.pack_start(hbox, True, True, 0)
            ibox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
            hbox.pack_start(ibox, True, False, 0)

            self.btn_backward = Gtk.Button.new_from_icon_name("media-skip-backward", Gtk.IconSize.BUTTON)
            self.btn_backward.connect("clicked", launch, "playerctl -a previous")
            ibox.pack_start(self.btn_backward, False, False, 0)

            self.img_pause = Gtk.Image.new_from_icon_name("media-pause", Gtk.IconSize.BUTTON)
            self.img_play = Gtk.Image.new_from_icon_name("media-play", Gtk.IconSize.BUTTON)

            self.btn_play_pause = Gtk.Button()
            self.btn_play_pause.set_image(self.img_pause)
            self.btn_play_pause.connect("clicked", launch, "playerctl -a play-pause")
            ibox.pack_start(self.btn_play_pause, False, False, 0)

            self.btn_forward = Gtk.Button.new_from_icon_name("media-skip-forward", Gtk.IconSize.BUTTON)
            self.btn_forward.connect("clicked", launch, "playerctl -a next")
            ibox.pack_start(self.btn_forward, False, False, 0)

        self.refresh()
        self.show_all()
        self.set_size_request(self.get_allocated_height() * 4, 0)

    def refresh(self):
        status = get_player_status()
        metadata = get_player_metadata()
        if settings["lockscreen-locker"] == "gtklock":  # otherwise we have no buttons!
            if status in ["Playing", "Paused"]:
                if status == "Playing":
                    self.btn_play_pause.set_image(self.img_pause)
                else:
                    self.btn_play_pause.set_image(self.img_play)

        if status in ["Playing", "Paused"]:
            self.set_property("name", "")
            self.show_all()

            output = ""
            if metadata["artist"]:
                if len(metadata["artist"]) < 40:
                    output += metadata["artist"]
                else:
                    output += metadata["artist"][:39]

            if metadata["title"]:
                if len(metadata["title"]) < 40:
                    output += "\n{}".format(metadata["title"])
                else:
                    output += "\n{}".format(metadata["title"][:39])
            self.label.set_text(output)

            if metadata["artUrl"]:
                try:
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(metadata["artUrl"], 64, 64)
                    cover.set_from_pixbuf(pixbuf)
                    cover.show()
                except Exception as e:
                    print(e)
                    cover.hide()
            else:
                cover.hide()

        else:
            # If the player has been stopped for some unknown reason (the screen is locked!), we can't restart it
            # with 'playerctl'. We'd like to hide the window, if so. BUT: playing from e.g. music.youtube.com will
            # give us the 'Stopped' status occasionally. We want the window to survive such accidents.
            # Once hidden, the window will never show up again OVER THE LOCKER. We'll just hide widgets and set
            # the window background transparent. Before doing so, let's make sure if the player really stopped .
            # If you play via a web browser, you may get the "Stopped" status while selecting previous/next tune.
            self.retries = 3
            Gdk.threads_add_timeout_seconds(GLib.PRIORITY_LOW, 3, self.hide_if_still_stopped)

        return True

    def hide_if_still_stopped(self):
        if self.retries > 0:
            self.retries -= 1
            # try again
            return True

        status = get_player_status()
        if status not in ["Playing", "Paused"]:
            # wide widgets
            self.label.hide()
            if self.btn_backward:
                self.btn_backward.hide()
            if self.btn_play_pause:
                self.btn_play_pause.hide()
            if self.btn_forward:
                self.btn_forward.hide()
            # set window background transparent
            self.set_property("name", "dead")

        return False

    def die(self):
        Gtk.main_quit()
        self.destroy()


def terminate_old_instance_if_any():
    try:
        old_pid = int(load_text_file(os.path.join(tmp_dir, "nwg-lock-pid")))
        if old_pid != pid:
            os.kill(old_pid, 15)
    except:
        pass
    save_string(str(pid), os.path.join(tmp_dir, "nwg-lock-pid"))


def set_remote_wallpaper():
    if settings["lockscreen-playerctl"] and get_player_status() in ["Playing", "Paused"]:
        global pctl
        pctl = PlayerctlWindow()
    else:
        pctl = None

    url = "https://source.unsplash.com/{}x{}/?{}".format(settings["unsplash-width"], settings["unsplash-height"],
                                                         ",".join(settings["unsplash-keywords"]))
    wallpaper = os.path.join(data_dir, "wallpaper.jpg")
    try:
        r = urllib.request.urlretrieve(url, wallpaper)
        if r[1]["Content-Type"] in ["image/jpeg", "image/png"]:
            if settings["lockscreen-locker"] == "swaylock":
                subprocess.call("pkill -f swaylock", shell=True)
                subprocess.Popen('swaylock -i {} && kill -n 15 {}'.format(wallpaper, pid), shell=True)
            elif settings["lockscreen-locker"] == "gtklock":
                subprocess.call("pkill -f gtklock", shell=True)

                subprocess.Popen('{} -S -H -T 10 -i -b {} && kill -n 15 {}'.format(gtklock_command(), wallpaper, pid),
                                 shell=True)

            if pctl:
                terminate_old_instance_if_any()
                Gdk.threads_add_timeout_seconds(GLib.PRIORITY_LOW, 1, pctl.refresh)
                Gtk.main()

    except Exception as e:
        print(e)
        set_local_wallpaper()


def set_local_wallpaper():
    global pctl
    pctl = PlayerctlWindow() if settings["lockscreen-playerctl"] and get_player_status() in ["Playing",
                                                                                             "Paused"] else None

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
            subprocess.call("pkill -f swaylock", shell=True)
            subprocess.Popen('swaylock -i {} && kill -n 15 {}'.format(p, pid), shell=True)
        elif settings["lockscreen-locker"] == "gtklock":
            subprocess.call("pkill -f gtklock", shell=True)

            subprocess.Popen(
                '{} -S -H -T {} -i -b {} && kill -n 15 {}'.format(gtklock_command(), settings["gtklock-idle-timeout"], p,
                                                                  pid), shell=True)
    else:
        print("No image paths found")

        if settings["lockscreen-locker"] == "swaylock":
            subprocess.call("pkill -f swaylock", shell=True)
            subprocess.Popen('exec swaylock -f', shell=True)
        elif settings["lockscreen-locker"] == "gtklock":
            subprocess.call("pkill -f gtklock", shell=True)
            subprocess.Popen('exec gtklock -d', shell=True)

    if pctl:
        terminate_old_instance_if_any()
        Gdk.threads_add_timeout_seconds(GLib.PRIORITY_LOW, 1, pctl.refresh)
        Gtk.main()

    sys.exit(0)


def gtklock_command():
    gtklock_cmd = "gtklock"

    # userinfo module
    if settings["gtklock-userinfo"]:
        gtklock_cmd += " -m userinfo-module"

        # optional userinfo module arguments
        if not preset["gtklock-userinfo-round-image"]:
            gtklock_cmd += " --no-round-image"
        if not preset["gtklock-userinfo-vertical-layout"]:
            gtklock_cmd += " --horizontal-layout"
        if preset["gtklock-userinfo-under-clock"]:
            gtklock_cmd += " --under-clock"

    # powerbar module
    if settings["gtklock-powerbar"]:
        gtklock_cmd += " -m powerbar-module"

        # optional powerbar module arguments
        if preset["gtklock-powerbar-show-labels"]:
            gtklock_cmd += " --show-labels"
        if preset["gtklock-powerbar-linked-buttons"]:
            gtklock_cmd += " --linked-buttons"
        if settings["gtklock-reboot-command"]:
            gtklock_cmd += " --reboot-command '{}'".format(settings["gtklock-reboot-command"])
        if settings["gtklock-poweroff-command"]:
            gtklock_cmd += " --poweroff-command '{}'".format(settings["gtklock-poweroff-command"])

    # playerctl module
    if settings["gtklock-playerctl"]:
        gtklock_cmd += " -m playerctl-module"

        # optional playerctl module arguments
        if "gtklock-playerctl-art-size" in preset:
            gtklock_cmd += " --art-size {}".format(preset["gtklock-playerctl-art-size"])
        if "gtklock-playerctl-position":
            gtklock_cmd += " --position '{}'".format(preset["gtklock-playerctl-position"])

    if settings["gtklock-time-format"]:
        gtklock_cmd += " --time-format '{}'".format(settings["gtklock-time-format"])

    # gtklock style sheets
    if settings["panel-preset"]:
        gtklock_config_dir = os.path.join(config_home, "gtklock")
        css_file = os.path.join(gtklock_config_dir, "{}.css".format(settings["panel-preset"]))

        if os.path.isfile(css_file):
            gtklock_cmd += " -s {}".format(css_file)

    return gtklock_cmd


def main():
    global defaults
    for key in defaults:
        if key not in settings:
            settings[key] = defaults[key]

    global preset_defaults
    for key in preset_defaults:
        if key not in preset:
            preset[key] = preset_defaults[key]

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
