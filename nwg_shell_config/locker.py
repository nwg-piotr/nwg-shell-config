#!/usr/bin/env python3

# Wrapper for 'swaylock' & 'gtklock' commands to use them with a random image, local of downloaded from unsplash.com.
# All the setting come from the 'nwg-shell-config' 'settings' data file.

import os
import random
import subprocess
import sys
import urllib.request
from nwg_shell_config.tools import get_data_dir, load_json

data_dir = get_data_dir()
settings = load_json(os.path.join(data_dir, "settings"))


def set_remote_wallpaper():
    url = "https://source.unsplash.com/{}x{}/?{}".format(settings["unsplash-width"], settings["unsplash-height"],
                                                         ",".join(settings["unsplash-keywords"]))
    wallpaper = os.path.join(data_dir, "wallpaper.jpg")
    try:
        r = urllib.request.urlretrieve(url, wallpaper)
        if r[1]["Content-Type"] in ["image/jpeg", "image/png"]:
            if settings["lockscreen-locker"] == "swaylock":
                subprocess.Popen('exec swaylock -f -i {}'.format(wallpaper), shell=True)
            elif settings["lockscreen-locker"] == "gtklock":
                subprocess.Popen('exec gtklock -d -b {}'.format(wallpaper), shell=True)

            sys.exit(0)

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
            subprocess.Popen('exec swaylock -f -i {}'.format(p), shell=True)
        elif settings["lockscreen-locker"] == "gtklock":
            subprocess.Popen('exec gtklock -d -b {}'.format(p), shell=True)
    else:
        print("No image paths found")

        if settings["lockscreen-locker"] == "swaylock":
            subprocess.Popen('exec swaylock -f', shell=True)
        elif settings["lockscreen-locker"] == "gtklock":
            subprocess.Popen('exec gtklock -d', shell=True)

    sys.exit(0)


def main():
    if settings["lockscreen-custom-cmd"]:
        subprocess.Popen('exec {}'.format(settings["lockscreen-custom-cmd"]), shell=True)

        sys.exit(0)

    if settings["lockscreen-background-source"] == "unsplash":
        set_remote_wallpaper()

    elif settings["lockscreen-background-source"] == "local":
        set_local_wallpaper()


if __name__ == '__main__':
    main()
