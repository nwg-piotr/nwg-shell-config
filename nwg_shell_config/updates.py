#!/usr/bin/env python3

from nwg_shell_config.tools import log_line, get_command_output


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

    if version == "0.3.4":
        o = get_command_output("nwg-shell-installer -r")
        log_line(log_file, label, "\n".join(o))

    if version == "0.5.0":
        log_line(log_file, label, "\nnwg-shell 0.5.0 comes with Hyprland support.\n\n")
        log_line(log_file, label, "\nTo install them, you need to:.\n\n")

    shell_data["updates"].append(version)
