#!/usr/bin/env python3

# Wrapper for 'swaylock' & 'gtklock' commands to use them with a random image, local of downloaded from unsplash.com.
# All the setting come from the 'nwg-shell-config' 'settings' data file.

import os
import random
import subprocess
import sys

from nwg_shell_config.tools import get_data_dir, temp_dir, load_json, gtklock_module_path, \
    playerctl_metadata, eprint

try:
    import requests
except ModuleNotFoundError:
    eprint("python-requests module not found, terminating")
    sys.exit(1)

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
    "after-resume": 'swaymsg "output * enable"',
    "before-sleep": "",
    "backgrounds-custom-path": "",
    "backgrounds-use-custom-path": False,
    "background-dirs": ["/usr/share/backgrounds/nwg-shell"],
    "background-dirs-once-set": False,
    "unsplash-width": 1920,
    "unsplash-height": 1080,
    "unsplash-keywords": ["nature", "water", "landscape"],
    "wallhaven-api-key": "",
    "wallhaven-ratio": "16x9,16x10",
    "wallhaven-atleast": "1920x1080",
    "wallhaven-tags": ["nature", "landscape"],
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


def set_remote_wallpaper():
    wallpaper_path = os.path.join(data_dir, "wallpaper.jpg")
    try:
        load_wallhaven_image(wallpaper_path)
        if settings["lockscreen-locker"] == "swaylock":
            subprocess.Popen('swaylock -i {}'.format(wallpaper_path), shell=True)
        elif settings["lockscreen-locker"] == "gtklock":
            eprint('{} -S -H -T 10 -b {}'.format(gtklock_command(), wallpaper_path))
            subprocess.Popen('{} -S -H -T 10 -b {}'.format(gtklock_command(), wallpaper_path), shell=True)

    except Exception as e:
        eprint("Failed loading image from wallhaven.cc :/")
        set_local_wallpaper()


def load_wallhaven_image(path):
    api_key = settings['wallhaven-api-key'] if settings["wallhaven-api-key"] else None
    api_key_status = "set" if settings['wallhaven-api-key'] else "unset"
    tags = " ".join(settings['wallhaven-tags']) if settings['wallhaven-tags'] else "nature, landscape"
    ratios = settings['wallhaven-ratio'] if settings['wallhaven-ratio'] else "16x9,16x10"
    atleast = settings["wallhaven-atleast"] if settings["wallhaven-atleast"] else "1920x1080"
    print(
        f"Fetching random image from wallhaven.cc, tags: '{tags}', ratios: '{ratios}', atleast: '{atleast}', API key: {api_key_status}")
    # Wallhaven API endpoint
    url = "https://wallhaven.cc/api/v1/search"

    # Parameters for the API request
    params = {
        "q": tags,
        "ratios": ratios,
        "atleast": atleast,
        "sorting": "random"
    }
    if api_key:
        params["apikey"] = api_key

    # Make the API request
    response = requests.get(url, params=params)

    # Get the image URL from the response
    if response.status_code == 200:
        image_data = response.json()
        image_url = image_data["data"][0]["path"]

        for key in image_data["data"][0]:
            print(f"{key}: {image_data["data"][0][key]}")

        # Download the image
        image_response = requests.get(image_url)

        if image_response.status_code == 200:
            # Save the image locally
            with open(path, "wb") as file:
                file.write(image_response.content)
            eprint(f"Wallhaven image saved as {path}")
        else:
            eprint("Failed to download Wallhaven image")
    else:
        eprint("Failed to fetch Wallhaven image")


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

        elif settings["lockscreen-locker"] == "gtklock":
            eprint(
                '{} -S -H -T {} -b {}'.format(gtklock_command(), settings["gtklock-idle-timeout"], p))
            subprocess.Popen(
                '{} -S -H -T {} -b {}'.format(gtklock_command(), settings["gtklock-idle-timeout"], p), shell=True)
    else:
        print("No image paths found")

        if settings["lockscreen-locker"] == "swaylock":
            subprocess.Popen('exec swaylock -f', shell=True)

        elif settings["lockscreen-locker"] == "gtklock":
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

    if settings["lockscreen-custom-cmd"]:
        subprocess.Popen('exec {}'.format(settings["lockscreen-custom-cmd"]), shell=True)
        sys.exit(0)

    if settings["lockscreen-background-source"] == "wallhaven.cc":
        set_remote_wallpaper()

    elif settings["lockscreen-background-source"] == "local":
        set_local_wallpaper()


if __name__ == '__main__':
    main()
