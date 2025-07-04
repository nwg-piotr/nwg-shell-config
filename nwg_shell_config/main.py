#!/usr/bin/env python3

"""
nwg-shell config utility
Repository: https://github.com/nwg-piotr/nwg-shell-config
Project site: https://nwg-piotr.github.io/nwg-shell
Author's email: nwg.piotr@gmail.com
Copyright (c) 2021-2025 Piotr Miller & Contributors
License: MIT
"""

import argparse
import os
import sys
import subprocess

from nwg_shell_config.tools import eprint, load_shell_data
from nwg_shell_config.__about__ import __version__

arguments = " ".join(sys.argv[1:])


def main():
    # We actually support just -v and -h her. The rest is to display proper help content, as they're being passed farther anyway.
    parser = argparse.ArgumentParser()
    parser.add_argument("-v",
                        "--version",
                        action="version",
                        version="%(prog)s version {}".format(__version__),
                        help="display version information")
    parser.add_argument("-r",
                        "--restore",
                        action="store_true",
                        help="restore default presets")

    parser.add_argument("-b",
                        "--restore_backup",
                        type=str,
                        default="",
                        help="restore all configs from a backup file (given path)")

    parser.add_argument("-s",
                        "--save",
                        action="store_true",
                        help="load settings & Save includes (for use w/ external scripts)")

    parser.parse_args()

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
