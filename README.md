<img src="https://github.com/nwg-piotr/nwg-shell-config/assets/20579136/55289a50-5346-409f-bbe7-f8b8d58d5f6d" width="90" style="margin-right:10px" align=left alt="nwg-shell logo">
<H1>nwg-shell-config</H1><br>

This program is a part of the [nwg-shell](https://nwg-piotr.github.io/nwg-shell) project.

**Nwg-shell-config** utility provides a graphical user interface for configuring [sway](https://github.com/swaywm/sway) and [Hyprland](https://github.com/hyprwm/Hyprland) Wayland
compositors in nwg-shell.

## Installation

[![Packaging status](https://repology.org/badge/vertical-allrepos/nwg-shell-config.svg)](https://repology.org/project/nwg-shell-config/versions)

## Desktop styles

Every preset is bound to its own [nwg-panel](https://github.com/nwg-piotr/nwg-panel) config file and css style sheet.
Along with it come settings for the launcher ([nwg-drawer](https://github.com/nwg-piotr/nwg-drawer)), exit menu
([nwg-bar](https://github.com/nwg-piotr/nwg-bar)), and the dock ([nwg-dock](https://github.com/nwg-piotr/nwg-dock)).
The latter is only turned on by default in `preset-1` and `preset-3`.

<div align="center">preset-0<br /><img src="https://raw.githubusercontent.com/nwg-piotr/nwg-shell-resources/master/images/nwg-shell-config/preset-0.png" width="480"/></div>

<div align="center">preset-1<br /><img src="https://raw.githubusercontent.com/nwg-piotr/nwg-shell-resources/master/images/nwg-shell-config/preset-1.png" width="480"/></div>

<div align="center">preset-2<br /><img src="https://raw.githubusercontent.com/nwg-piotr/nwg-shell-resources/master/images/nwg-shell-config/preset-2.png" width="480"/></div>

<div align="center">preset-3<br /><img src="https://raw.githubusercontent.com/nwg-piotr/nwg-shell-resources/master/images/nwg-shell-config/preset-3.png" width="480"/></div>

## Command line arguments

```text
$ nwg-shell-config -h
usage: nwg-shell-config-hyprland [-h] [-v] [-r] [-b RESTORE_BACKUP] [-s]

options:
  -h, --help            show this help message and exit
  -v, --version         display version information
  -r, --restore         restore default presets
  -b RESTORE_BACKUP, --restore_backup RESTORE_BACKUP
                        restore all configs from a backup file (given path)
  -s, --save            load settings & Save includes (for use w/ external scripts)
```

### `-s | --save` argument:

If set, the program will read current settings, export the `~/.config/hypr/includes.conf` file and die. This is for use with external scripts. See: https://www.reddit.com/r/nwg_shell/comments/14by0by/request_keyboard_layout_switching.

Sample nwg-panel executor:

```python
#!/usr/bin/env python3

# nwg-panel executor to display keyboard layout and switch it with `nwg-shell-config -s` command
# 1. Save anywhere on $PATH as e.g. `kb-layout-hyprland` file.
# 2. Enter `kb-layout-hyprland` in the executor "Script" field.
# 3. Enter `kb-layout-hyprland -s` in the executor "On left clock" field.

import os
import sys
import json
import subprocess

# We need to change the "input-kb_layout" value in the "settings-hyprland" json file.
settings_file = os.path.join(os.getenv("HOME"), ".local/share/nwg-shell-config/settings-hyprland")


def main():
    # load settings-hyprland to a dictionary
    try:
        with open(settings_file, 'r') as f:
            settings = json.load(f)
    except Exception as e:
        print("Error loading json: {}".format(e))
        sys.exit(1)

    if len(sys.argv) > 1 and sys.argv[1] == "-s":  # argument `-s` given
        # switch keyboard layout in the dictionary
        settings["input-kb_layout"] = "pl" if settings["input-kb_layout"] == "us" else "us"
        # save to the json file
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=2, ensure_ascii=True)

        # run `nwg-shell-config -s` to export settings to ~/.config/hypr/includes
        subprocess.Popen("nwg-shell-config -s", shell=True)

    # executor output in 2 lines (icon + text)
    print("input-keyboard")             # icon name
    print(settings["input-kb_layout"])  # current layout


if __name__ == "__main__":
    main()

```

![image](https://github.com/nwg-piotr/nwg-shell-config/assets/20579136/c0b03acf-4634-4eb3-90e4-996b421dfe82)

