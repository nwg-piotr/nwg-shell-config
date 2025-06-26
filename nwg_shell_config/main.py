#!/usr/bin/env python3

"""
nwg-shell config utility
Repository: https://github.com/nwg-piotr/nwg-shell-config
Project site: https://nwg-piotr.github.io/nwg-shell
Author's email: nwg.piotr@gmail.com
Copyright (c) 2021-2025 Piotr Miller & Contributors
License: MIT
"""

import os
import sys
import subprocess

from nwg_shell_config.tools import eprint, load_shell_data

arguments = " ".join(sys.argv[1:])


def main():
    shell_data = load_shell_data()
    if not shell_data["autotranslated"]:
        subprocess.Popen("nwg-autotranslate")

        if os.getenv("HYPRLAND_INSTANCE_SIGNATURE"):
            eprint("Labels translated, reloading Hyprland.")
            subprocess.Popen("hyprctl reload".split())
        else:
            eprint("Labels translated, reloading sway.")
            subprocess.Popen("swaymsg reload".split())

    if os.getenv("SWAYSOCK"):
        cmd = "nwg-shell-config-sway {}".format(arguments)
        eprint("Starting sway version")
    elif os.getenv("HYPRLAND_INSTANCE_SIGNATURE"):
        cmd = "nwg-shell-config-hyprland {}".format(arguments)
        eprint("Starting Hyprland version")
    else:
        eprint("This program needs either sway or Hyprland environment")
        sys.exit(1)
    try:
        subprocess.Popen(cmd.split())
        sys.exit(0)
    except Exception as e:
        eprint(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
