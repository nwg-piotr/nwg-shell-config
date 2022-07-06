#!/usr/bin/env python3

# Wrapper for 'swaylock' & 'gtklock' commands to use them with a random image, local of downloaded from unsplash.com.
# All the setting come from the 'nwg-shell-config' 'settings' data file.

import os
from nwg_shell_config.tools import get_data_dir, load_json

data_dir = get_data_dir()
settings = load_json(os.path.join(data_dir, "settings"))


def main():
    for key in ["lockscreen-locker",
                "lockscreen-background-source",
                "lockscreen-custom-cmd",
                "lockscreen-timeout",
                "sleep-cmd",
                "sleep-timeout",
                "resume-cmd",
                "before-sleep",
                "backgrounds-custom-path",
                "background-dirs",
                "background-dirs-once-set",
                "unsplash-width",
                "unsplash-height",
                "unsplash-keywords"]:
        print(key, settings[key])


if __name__ == '__main__':
    main()
