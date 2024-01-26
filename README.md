<img src="https://github.com/nwg-piotr/nwg-shell-config/assets/20579136/55289a50-5346-409f-bbe7-f8b8d58d5f6d" width="90" style="margin-right:10px" align=left alt="nwg-shell logo">
<H1>nwg-shell-config</H1><br>

This program is a part of the [nwg-shell](https://nwg-piotr.github.io/nwg-shell) project.

**Nwg-shell-config** utility provides a graphical user interface for configuring [sway](https://github.com/swaywm/sway) and [Hyprland](https://github.com/hyprwm/Hyprland) Wayland
compositors in nwg-shell.

<a href="https://github.com/nwg-piotr/nwg-shell-config/assets/20579136/8443e30a-7125-43ab-8994-b471b9343e74"><img src="https://github.com/nwg-piotr/nwg-shell-config/assets/20579136/8443e30a-7125-43ab-8994-b471b9343e74" width=640></a>

## Screen settings

- desktop style selection
- night light settings (user location, day/night color temperature, gamma)
- help window (key binding cheat sheet) settings
- update notification tray icon settings
- other system tray icons on/off switches

## General settings (Hyprland)

- window tiling layout selection (dwindle/Master)
- window border settings
- wingow gaps settings

## Dwindle layout (Hyprland)

- split settings
- smart resizing

## Master layout (Hyprland)

- split settings

## Input devices (Hyprland)

- keyboard layout & other settings
- mouse sensitivity, acceleration & other settings
- touchpad scroll factor & other settings

## Miscellaneous (Hyprland)

- disable Hyprland logo/background
- DMPS behavior
- focus settings

## Idle & Lock screen

- screen locker selection: swaylock / gtklock, the latter on sway only
- lock screen background source (local wallpapers / unsplash.com images)
- screen locker timeouts

## Applications

For key bindings to work properly, you need to select some default applications, and those are:

- terminal
- file manager
- text editor
- web browser

## Backup

- you'll find a backup / restore utility here. It allows to pack all nwg-shell-related configs into a `.tar.gz` file, and install them back from it.

## System info

- this tab gathers and displays some basic system info, including installed OS, Wayland compositor and nwg-shell-related packages versions.

## Desktop styles submenu

It allows to select per-preset app settings for:

- application drawer
- dock
- exit menu
- notifications
- gtklock (sway only)

## Translation tool

In the window footer you'll find the nwg-shell-translate button, in case you'd like to help at [translations](https://nwg-piotr.github.io/nwg-shell/contribution#translations).

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

