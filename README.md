<img src="https://github.com/nwg-piotr/nwg-shell-config/assets/20579136/55289a50-5346-409f-bbe7-f8b8d58d5f6d" width="90" style="margin-right:10px" align=left alt="nwg-shell logo">
<H1>nwg-shell-config</H1><br>

This program is a part of the [nwg-shell](https://nwg-piotr.github.io/nwg-shell) project.

**Nwg-shell-config** utility provides a graphical user interface for configuring [sway](https://github.com/swaywm/sway) and [Hyprland](https://github.com/hyprwm/Hyprland) Wayland
compositors in nwg-shell.

## Installation

[![Packaging status](https://repology.org/badge/vertical-allrepos/nwg-shell-config.svg)](https://repology.org/project/nwg-shell-config/versions)

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
- `-s | --save` argument makes the program read current settings, export the `~/.config/hypr/includes.conf` file and 
terminate. This is for use with external scripts.

