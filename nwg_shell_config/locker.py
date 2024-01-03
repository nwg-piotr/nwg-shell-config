#!/usr/bin/env python3

# Wrapper for 'swaylock' & 'gtklock' commands to use them with a random image, local of downloaded from unsplash.com.
# All the setting come from the 'nwg-shell-config' 'settings' data file.

import os
import random
import subprocess
import signal
import sys
import urllib.request

from nwg_shell_config.tools import get_data_dir, temp_dir, load_json, load_text_file, save_string, gtklock_module_path, \
    playerctl_metadata, eprint

config_home = os.getenv('XDG_CONFIG_HOME') if os.getenv('XDG_CONFIG_HOME') else os.path.join(os.getenv("HOME"),
                                                                                             ".config/")
data_dir = get_data_dir()
tmp_dir = temp_dir()

if os.getenv("SWAYSOCK"):
    settings = load_json(os.path.join(data_dir, "settings"))
elif os.getenv("HYPRLAND_INSTANCE_SIGNATURE"):
    settings = load_json(os.path.join(data_dir, "settings-hyprland"))
else:
    eprint("This program only works on sway or Hyprland, terminating.")
    sys.exit(1)

preset = load_json(
    os.path.join(data_dir, settings["panel-preset"])) if "panel-preset" in settings and "panel-preset" else {}

pid = os.getpid()

defaults = {
    "panel-preset": "preset-0",
    "lockscreen-use-settings": True,
    "lockscreen-locker": "gtklock",  # swaylock | gtklock
    "lockscreen-background-source": "local",  # unsplash | local
    "lockscreen-custom-cmd": "",
    "lockscreen-timeout": 1200,
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
    "gtklock-disable-input-inhibitor": False,
    "gtklock-idle-timeout": 10,
    "gtklock-logout-command": "swaymsg exit",
    "gtklock-playerctl": False,
    "gtklock-powerbar": False,
    "gtklock-poweroff-command": "systemctl -i poweroff",
    "gtklock-reboot-command": "systemctl reboot",
    "gtklock-suspend-command": "systemctl suspend",
    "gtklock-time-format": "%H:%M:%S",
    "gtklock-userinfo": False,
    "gtklock-userswitch-command": ""
}

preset_defaults = {
    "gtklock-userinfo-round-image": True,
    "gtklock-userinfo-vertical-layout": False,
    "gtklock-userinfo-under-clock": False,
    "gtklock-powerbar-show-labels": False,
    "gtklock-powerbar-linked-buttons": False,
    "gtklock-playerctl-art-size": 64,
    "gtklock-playerctl-position": "top-right",
    "gtklock-playerctl-show-hidden": True
}


def signal_handler(sig, frame):
    desc = {2: "SIGINT", 15: "SIGTERM", 10: "SIGUSR1"}
    if sig == 2 or sig == 15:
        print("Terminated with {}".format(desc[sig]))


def launch(button, cmd):
    subprocess.Popen('exec {}'.format(cmd), shell=True)


def set_remote_wallpaper():
    url = "https://source.unsplash.com/{}x{}/?{}".format(settings["unsplash-width"], settings["unsplash-height"],
                                                         ",".join(settings["unsplash-keywords"]))
    wallpaper = os.path.join(data_dir, "wallpaper.jpg")
    try:
        r = urllib.request.urlretrieve(url, wallpaper)
        if r[1]["Content-Type"] in ["image/jpeg", "image/png"]:
            if settings["lockscreen-locker"] == "swaylock":
                subprocess.call("pkill -f swaylock", shell=True)
                subprocess.Popen('swaylock -i {} ; kill -n 15 {}'.format(wallpaper, pid), shell=True)
            elif settings["lockscreen-locker"] == "gtklock":
                subprocess.call("pkill -f gtklock", shell=True)

                eprint('{} -S -H -T 10 -b {} ; kill -n 15 {}'.format(gtklock_command(), wallpaper, pid))
                subprocess.Popen('{} -S -H -T 10 -b {} ; kill -n 15 {}'.format(gtklock_command(), wallpaper, pid),
                                 shell=True)

    except Exception as e:
        print(e)
        set_local_wallpaper()


def set_local_wallpaper():
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
            subprocess.Popen('swaylock -i {}'.format(p), shell=True)
            # just for clarity ;)
            sys.exit(0)

        elif settings["lockscreen-locker"] == "gtklock":
            subprocess.call("pkill -f gtklock", shell=True)

            eprint(
                '{} -S -H -T {} -b {} ; kill -n 15 {}'.format(gtklock_command(), settings["gtklock-idle-timeout"], p,
                                                               pid))
            subprocess.Popen(
                '{} -S -H -T {} -b {} ; kill -n 15 {}'.format(gtklock_command(), settings["gtklock-idle-timeout"],
                                                               p, pid), shell=True)
    else:
        print("No image paths found")

        if settings["lockscreen-locker"] == "swaylock":
            subprocess.call("pkill -f swaylock", shell=True)
            subprocess.Popen('exec swaylock -f', shell=True)
        elif settings["lockscreen-locker"] == "gtklock":
            subprocess.call("pkill -f gtklock", shell=True)
            subprocess.Popen('exec gtklock -d', shell=True)

    sys.exit(0)


def gtklock_command():
    gtklock_cmd = "gtklock"

    if settings["gtklock-disable-input-inhibitor"]:
        gtklock_cmd += " -i"

    # userinfo module
    if settings["gtklock-userinfo"]:
        gtklock_cmd += " -m {}".format(gtklock_module_path("userinfo"))

        # optional userinfo module arguments
        if not preset["gtklock-userinfo-round-image"]:
            gtklock_cmd += " --no-round-image"
        if not preset["gtklock-userinfo-vertical-layout"]:
            gtklock_cmd += " --horizontal-layout"
        if preset["gtklock-userinfo-under-clock"]:
            gtklock_cmd += " --under-clock"

    # powerbar module
    if settings["gtklock-powerbar"]:
        gtklock_cmd += " -m {}".format(gtklock_module_path("powerbar"))

        # optional powerbar module arguments
        if preset["gtklock-powerbar-show-labels"]:
            gtklock_cmd += " --show-labels"
        if preset["gtklock-powerbar-linked-buttons"]:
            gtklock_cmd += " --linked-buttons"
        # It seems a bit counter-intuitive, but to turn one of gtklock poweroff module commands off,
        # we need to pass the empty string, like `--suspend-command`.
        # See: https://github.com/jovanlanik/gtklock-powerbar-module/issues/1#issuecomment-1287509956
        if settings["gtklock-reboot-command"]:
            gtklock_cmd += " --reboot-command '{}'".format(settings["gtklock-reboot-command"])
        else:
            gtklock_cmd += " --reboot-command ''"
        if settings["gtklock-poweroff-command"]:
            gtklock_cmd += " --poweroff-command '{}'".format(settings["gtklock-poweroff-command"])
        else:
            gtklock_cmd += " --poweroff-command ''"
        if settings["gtklock-suspend-command"]:
            gtklock_cmd += " --suspend-command '{}'".format(settings["gtklock-suspend-command"])
        else:
            gtklock_cmd += " --suspend-command ''"

        if settings["gtklock-logout-command"]:
            gtklock_cmd += " --logout-command '{}'".format(settings["gtklock-logout-command"])
        else:
            gtklock_cmd += " --logout-command ''"

        if settings["gtklock-userswitch-command"]:
            gtklock_cmd += " --userswitch-command '{}'".format(settings["gtklock-userswitch-command"])
        else:
            gtklock_cmd += " --userswitch-command ''"

    # playerctl module
    # Don't show if playerctl_metadata() empty.
    # https://github.com/jovanlanik/gtklock-playerctl-module/issues/4
    if settings["gtklock-playerctl"] and playerctl_metadata():
        gtklock_cmd += " -m {}".format(gtklock_module_path("playerctl"))

        # optional playerctl module arguments
        if preset["gtklock-playerctl-show-hidden"]:
            gtklock_cmd += " --show-hidden"
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
