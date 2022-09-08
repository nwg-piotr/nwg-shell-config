#!/usr/bin/env python3

import os

from nwg_shell_config.tools import load_text_file, log_line, save_list_to_text_file


def update_version(version, log_file, label, config_home, shell_data):
    # if version == "0.2.5":
    #     autostart = os.path.join(config_home, "sway", "autostart")
    #     old = load_text_file(autostart).splitlines()
    #     new = []
    #     changed = False
    #     for line in old:
    #         if "autotiling" not in line:
    #             new.append(line)
    #         elif "nwg-autotiling" not in line:
    #             new.append("exec_always nwg-autotiling")
    #             log_line(log_file, label, "\n`autotiling` replaced  with nwg-autotiling\n\n")
    #             changed = True
    #
    #     if changed:
    #         save_list_to_text_file(new, autostart)
    #     else:
    #         log_line(log_file, label, "\nNo change needed.\n\n")

    if version == "0.3.0":
        log_line(log_file, label, "\nNo change needed.\n\n")

    shell_data["updates"].append(version)
