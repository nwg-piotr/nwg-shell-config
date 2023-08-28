#!/usr/bin/env python3

"""
nwg-shell config utility
Repository: https://github.com/nwg-piotr/nwg-shell-config
Project site: https://nwg-piotr.github.io/nwg-shell
Author's email: nwg.piotr@gmail.com
Copyright (c) 2021-2023 Piotr Miller & Contributors
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

    if os.getenv("SWAYSOCK"):
        cmd = "nwg-shell-config-sway {}".format(arguments)
        eprint("Starting sway version")
    elif os.getenv("HYPRLAND_INSTANCE_SIGNATURE"):
        subprocess.Popen("hyprctl reload")
        cmd = "nwg-shell-config-hyprland {}".format(arguments)
        eprint("Starting Hyprland version")
    else:
        eprint("This program needs either sway or Hyprland environment")
        sys.exit(1)
    try:
        subprocess.Popen(cmd.split())
    except Exception as e:
        eprint(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
