# nwg-shell config utility

**Contributing:** please read the [general contributing rules for the nwg-shell project](https://nwg-piotr.github.io/nwg-shell/contribution).

The [nwg-shell](https://github.com/nwg-piotr/nwg-shell) project is a collection of components to build a GTK-based user interface for [sway](https://github.com/swaywm/sway) and [Hyprland](https://github.com/hyprwm/Hyprland) Wayland compositor. It consists of a panel, launcher, dock, traditional menu, wallpaper manager, as well as some helper scripts. This program is a GUI to configure all the components in one place. It also integrates several third party components, which we arbitrarily found the best to build a coherent user experience.

[Learn more about nwg-shell on the project website](https://nwg-piotr.github.io/nwg-shell)

[![Packaging status](https://repology.org/badge/vertical-allrepos/nwg-shell-config.svg)](https://repology.org/project/nwg-shell-config/versions)

![2022-06-20-233635_screenshot](https://user-images.githubusercontent.com/20579136/174680829-84065416-b270-4ffe-bd36-23dd266d3cf8.png)

![2022-06-20-233644_screenshot](https://user-images.githubusercontent.com/20579136/174680835-c6208da4-9875-4e62-b3e3-02cb1bc4cb5d.png)

![2022-06-20-233702_screenshot](https://user-images.githubusercontent.com/20579136/174680842-64c640e2-0eb8-4817-bdf1-209e98670358.png)

![2022-06-20-233707_screenshot](https://user-images.githubusercontent.com/20579136/174680856-fbf7f58e-acb0-45e4-a0a8-0d8d57e6b12c.png)

![2022-06-20-233713_screenshot](https://user-images.githubusercontent.com/20579136/174680866-eb4a6222-c240-4518-b3a2-22e2bef7a315.png)

## Idle & Lock screen (since v0.3.7)

![image](https://user-images.githubusercontent.com/20579136/179640976-22be9fb7-970f-4d4a-bae5-ab48fb495984.png)

You may use either `gtklock` or `swaylock` as the locker, and either local or Unsplash random images as the background. Of course you may also opt-out, by unchecking the "Use these settings" box.

Hint: use the nwg-lock command system-wide (well, wlroots only) to lock screen with the locker and background defined in this tab.

**Safety**: for the media player buttons to work with gtklock, we use the `--no-input-inhibit` argument. If safety is more important to you than appearance, consider using swaylock. The playerctl window will display no buttons, however

## Desktop styles

Every preset is bound to its own [nwg-panel](https://github.com/nwg-piotr/nwg-panel) config file and css style sheet.
Along with it come settings for the launcher ([nwg-drawer](https://github.com/nwg-piotr/nwg-drawer)), exit menu
([nwg-bar](https://github.com/nwg-piotr/nwg-bar)), and the dock ([nwg-dock](https://github.com/nwg-piotr/nwg-dock)).
The latter is only turned on by default in `preset-1` and `preset-3`.

<div align="center">preset-0<br /><img src="https://raw.githubusercontent.com/nwg-piotr/nwg-shell-resources/master/images/nwg-shell-config/preset-0.png" width="480"/></div>

<div align="center">preset-1<br /><img src="https://raw.githubusercontent.com/nwg-piotr/nwg-shell-resources/master/images/nwg-shell-config/preset-1.png" width="480"/></div>

<div align="center">preset-2<br /><img src="https://raw.githubusercontent.com/nwg-piotr/nwg-shell-resources/master/images/nwg-shell-config/preset-2.png" width="480"/></div>

<div align="center">preset-3<br /><img src="https://raw.githubusercontent.com/nwg-piotr/nwg-shell-resources/master/images/nwg-shell-config/preset-3.png" width="480"/></div>

For key bindings help, press `[Super]+F1`.

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

