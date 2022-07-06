#!/usr/bin/env python3

# Wrapper for 'swaylock' & 'gtklock' commands to use them with a random image, local of downloaded from unsplash.com.
# All the setting come from the 'nwg-shell-config' 'settings' data file.

import os
import subprocess
import urllib.request
from nwg_shell_config.tools import get_data_dir, load_json

data_dir = get_data_dir()
settings = load_json(os.path.join(data_dir, "settings"))


def main():
    # for key in ["lockscreen-locker",
    #             "lockscreen-background-source",
    #             "backgrounds-custom-path",
    #             "background-dirs",
    #             "unsplash-width",
    #             "unsplash-height",
    #             "unsplash-keywords"]:
    #     print(key, settings[key])

    if settings["lockscreen-background-source"] == "unsplash":
        url = "https://source.unsplash.com/{}x{}/?{}".format(settings["unsplash-width"], settings["unsplash-height"],
                                                             ",".join(settings["unsplash-keywords"]))
        wallpaper = os.path.join(data_dir, "wallpaper.jpg")
        r = urllib.request.urlretrieve(url, wallpaper)
        if r[1]["Content-Type"] in ["image/jpeg", "image/png"]:
            if settings["lockscreen-locker"] == "swaylock":
                subprocess.Popen('exec swaylock -f -i {}'.format(wallpaper), shell=True)
            elif settings["lockscreen-locker"] == "gtklock":
                subprocess.Popen('exec gtklock -d -b {}'.format(wallpaper), shell=True)


if __name__ == '__main__':
    main()
