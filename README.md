<img src="https://github.com/nwg-piotr/nwg-shell-config/assets/20579136/55289a50-5346-409f-bbe7-f8b8d58d5f6d" width="90" style="margin-right:10px" align=left alt="nwg-shell logo">
<H1>nwg-shell-config</H1><br>

This program is a part of the [nwg-shell](https://nwg-piotr.github.io/nwg-shell) project.

**Nwg-shell-config** utility provides a graphical user interface for configuring [sway](https://github.com/swaywm/sway) and [Hyprland](https://github.com/hyprwm/Hyprland) Wayland
compositors in nwg-shell.

<a href="https://github.com/nwg-piotr/nwg-shell-config/assets/20579136/8443e30a-7125-43ab-8994-b471b9343e74"><img src="https://github.com/nwg-piotr/nwg-shell-config/assets/20579136/8443e30a-7125-43ab-8994-b471b9343e74" width=640></a>

[![Packaging status](https://repology.org/badge/vertical-allrepos/nwg-shell-config.svg)](https://repology.org/project/nwg-shell-config/versions)

## Program window tabs

### Screen settings (common)

- desktop style (preset) selection
- night light settings (user location, day/night color temperature, gamma)
- help window (key binding cheat sheet) settings
- update notification tray icon settings
- other system tray icons on/off switches

### Autotiling (sway)

- workspaces for autotiling to work on
- split depth limit
- split width, height

### Keyboard (sway)

- system-wide or per device keyboard settings: layout, repeat settings, CapsLock & NumLock settings

### Pointer device (sway)

- system-wide or per device pointer device settings: acceleration, scroll & other

### Touchpad (sway)

- system-wide or per device touchpad settings: acceleration, scroll & tap behaviour

### General settings (Hyprland)

- window tiling layout selection (dwindle/Master)
- window border settings
- window gaps settings

### Dwindle layout (Hyprland)

- split settings
- smart resizing

### Master layout (Hyprland)

- split settings

### Input devices (Hyprland)

- keyboard layout & other settings
- mouse sensitivity, acceleration & other settings
- touchpad scroll factor & other settings

### Miscellaneous (Hyprland)

- disable Hyprland logo/background
- DMPS behavior
- focus settings

### Idle & Lock screen (common)

- screen locker selection: swaylock / gtklock, the latter on sway only
- lock screen background source (local wallpapers / unsplash.com images)
- screen locker timeouts

### Gtklock (sway)

- modules settings (userinfo, powerbar, playertl)
- commands settings (reboot, power off, suspend, logout)
- time format
- idle timeout

### Applications (common)

For key bindings to work properly, you need to select some default applications, and those are:

- terminal
- file manager
- text editor
- web browser

### Backup (common)

- You'll find a backup / restore utility here. It allows to pack all nwg-shell-related configs into a `.tar.gz` file, and install them back from it.

### System info (common)

- This tab gathers and displays some basic system info, including installed OS, Wayland compositor and nwg-shell-related packages versions.

### Desktop styles submenu (common)

It allows to select per-preset app settings for:

- application drawer
- dock
- exit menu
- notifications
- gtklock (sway only)

## Translation tool

In the window footer you'll find the nwg-shell-translate button, in case you'd like to help at [translations](https://nwg-piotr.github.io/nwg-shell/contribution#translations).

## Other tools

The nwg-shell-config module / package is also a home for several other utilities and scripts:

- `nwg-autotiling`: a version of the [autotiling](https://github.com/nwg-piotr/autotiling) script modified for better integration w/ nwg-shell
- `nwg-autotranslate`: during first run it translates panel and exit menu labels into user's locale - if we have this language 
- `nwg-lock`: provides communication between the shell and the screen the locker of your choice
- `nwg-update-indicator`: a script responsible for the system update tray indicator (Arch and Venom Linux only so far)
- `nwg-screenshot-applet`: provides the tray icon and menu, that executes the `/usr/local/bin/screenshot` script with appropriate arguments.  
- `nwg-shell-help`: provides the keyboard shortcuts help window, together with the system tray icon

### nwg-hud

This script displays a window containing a given icon and some text, and closes it on timeout.

Feature request: https://github.com/nwg-piotr/nwg-shell/discussions/450.

Example usage (Hyprland): display the workspace change notification. You need to launch the script after
switching to a workspace or moving an active window to it. Modify your hyprland.conf file:

```text
# SWITCH WORKSPACES with mainMod + [0-9]
bind = $mainMod, 1, workspace, 1
bind = $mainMod, 1, exec, nwg-hud -i xfce4-workspaces -m "WS 1"
(and so on)

# MOVE ACTIVE WINDOW TO A WORKSPACE with mainMod + SHIFT + [0-9]
bind = $mainMod SHIFT, 1, movetoworkspace, 1
bind = $mainMod SHIFT, 1, exec, nwg-hud -i xfce4-workspaces -m "WS 1"
(and so on)
```

Script arguments:

```text
❯ nwg-hud -h
usage: nwg-hud [-h] [-i ICON] [-z ICON_SIZE] [-m MESSAGE] [-t TIMEOUT] [-ha HORIZONTAL_ALIGNMENT] [-va VERTICAL_ALIGNMENT] [-r MARGIN] [-o OUTPUT]

options:
  -h, --help            show this help message and exit
  -i ICON, --icon ICON  Icon name or path
  -z ICON_SIZE, --icon_size ICON_SIZE
                        icon size
  -m MESSAGE, --message MESSAGE
                        Message text to display
  -t TIMEOUT, --timeout TIMEOUT
                        window Timeout in milliseconds
  -ha HORIZONTAL_ALIGNMENT, --horizontal_alignment HORIZONTAL_ALIGNMENT
                        window Horizontal Alignment: 'left' or 'right', 'center' by default
  -va VERTICAL_ALIGNMENT, --vertical_alignment VERTICAL_ALIGNMENT
                        window Vertical Alignment: 'top' or 'bottom', 'center' by default
  -r MARGIN, --margin MARGIN
                        window margin in pixels
  -o OUTPUT, --output OUTPUT
                        name of the Output to display HUD on
```

To avoid adding all the arguments every time the script is called, you can define some defaults in the 
`~/.config/nwg-hud/config.json` file. These settings will be overridden with arguments, if given.

```json
{
  "icon": "",
  "icon-size": 48,
  "message": "",
  "timeout": 1000,
  "horizontal-alignment": "",
  "vertical-alignment": "",
  "margin": 0,
  "output": ""
}
```
