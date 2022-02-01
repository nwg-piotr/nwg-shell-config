# nwg-shell config utility

The [nwg-shell](https://github.com/nwg-piotr/nwg-shell) project is a collection of components for building a GTK-based user interface for [sway](https://github.com/swaywm/sway) Wayland compositor. It consists of a panel, launcher, dock, traditional menu, wallpaper manager, as well as some helper scripts. Until now, it has functioned as a do-it-yourself kit, with items to choose from. This program is a GUI to configure all the components in one place. It also integrates several external programs, which we arbitrarily found the best to build a coherent user experience.

![nwg-shell-settings.png](https://raw.githubusercontent.com/nwg-piotr/nwg-shell/main/images/nwg-shell/nwg-shell-config.png)

At the top of the window you define common settings, including some custom solutions, like 
[autotiling](https://github.com/nwg-piotr/autotiling) (a part of the project) and gamma control, for which 
[wlsunset](https://sr.ht/~kennylevinsen/wlsunset) is responsible. Below you select / define the desktop style,
with 4 predefined styles to choose from, and the "Custom" preset, which you can define on your own. Each of the
presets 0 - 3 may also be adjusted to your taste.

Every preset is bound to its own [nwg-panel](https://github.com/nwg-piotr/nwg-panel) config file and css style sheet.
Along with it come settings for the launcher ([nwg-drawer](https://github.com/nwg-piotr/nwg-drawer)), exit menu
([nwg-bar](https://github.com/nwg-piotr/nwg-bar)), and the dock ([nwg-dock](https://github.com/nwg-piotr/nwg-dock)).
The latter is only turned on by default in `preset-1` and `preset-3`.


<div align="center">preset-0<br /><img src="https://raw.githubusercontent.com/nwg-piotr/nwg-shell/main/images/nwg-shell-config/preset-0.png" width="480"/></div>

<div align="center">preset-1<br /><img src="https://raw.githubusercontent.com/nwg-piotr/nwg-shell/main/images/nwg-shell-config/preset-1.png" width="480"/></div>

<div align="center">preset-2<br /><img src="https://raw.githubusercontent.com/nwg-piotr/nwg-shell/main/images/nwg-shell-config/preset-2.png" width="480"/></div>

<div align="center">preset-3<br /><img src="https://raw.githubusercontent.com/nwg-piotr/nwg-shell/main/images/nwg-shell-config/preset-3.png" width="480"/></div>

To familiarize yourself with key bindings, you may want to mark the "Show help" check box in the config utility. 
This will display a conky-like help widget, supported by [nwg-wrapper](https://github.com/nwg-piotr/nwg-wrapper).

The **Controls module** of the panel comes with some preconfigured goodies to fine tune what your system looks and 
behaves like. Some of the menu items rely on the other software you need to have installed. 

<div align="center">nwg-panel Controls module<br /><img src="https://raw.githubusercontent.com/nwg-piotr/nwg-shell/main/images/nwg-shell-config/controls.png"/></div>

- **Wallpapers**: you need [Azote](https://github.com/nwg-piotr/azote), which is a part of the nwg-shell project;
- **Look & Feel**: you need the [lxappearance](https://wiki.lxde.org/en/LXAppearance) package, and the 
[import-gsettings](https://github.com/swaywm/sway/wiki/GTK-3-settings-on-Wayland#setting-values-in-gsettings) script;
- **Outputs** management relies on [wdisplays](https://github.com/artizirk/wdisplays) and 
[this script](https://github.com/nwg-piotr/sway-save-outputs).

**Notification Center** is supported by Eric Reider's [SwayNotificationCenter](https://github.com/ErikReider/SwayNotificationCenter).

<div align="center">Notification Center<br /><img src="https://raw.githubusercontent.com/nwg-piotr/nwg-shell/main/images/nwg-shell-config/swaync.png" width="480"/></div>

All of above is installed by default together with the sway session of [ArchLabs Linux](https://archlabslinux.com), 
which the nwg-shell-config utility was developed for. Anyway, if you'd like to give it a try on another system,
take a look at the [skel/sway-home/.config](https://github.com/nwg-piotr/nwg-shell-config/tree/master/skel/sway-home/.config)
directory. It contains the sway config, together with the rest of necessary configs and style sheets.

## Notes

### Includes

All the settings managed by nwg-shell-config are included into the `~/.config/sway/config` file like this:

```text
# The file we include below is created and will be overwritten by nwg-shell-config GUI!
#
include ~/.config/sway/variables
include ~/.config/sway/outputs
include ~/.config/sway/autostart
#
```

Leave these lines as they are. You also should not edit these files manually: the program will overwrite your changes.

Basic key bindings use variables, which are also provided by the config utility:

```text
# launchers
bindsym Control+space   exec $launcher
bindsym Mod1+F1         exec $launcher

# core
bindsym $Mod+t          exec $term
bindsym $Mod+Return     exec $term
bindsym Control+Shift+t exec $term
bindsym $Mod+w          exec $browser
bindsym $Mod+f          exec $filemanager
bindsym $Mod+e          exec $editor
bindsym $Mod+d          exec $dock
```

Feel free to add whichever other binding you need, but do not change the variable values other way than with config GUI.

### Styling

To change the appearance of nwg-shell components, you need to edit their css style sheets. They are all located in appropriate `~./config/nwg-*` directories, named `preset-*.css`. You may either edit these files, or add own under another names, and set these names in the config GUI.

### nwg-panel & nwg-menu

have their own config GUI. Find the "Panel settings" entry in the Controls menu. More info there's in the [panel Wiki](https://github.com/nwg-piotr/nwg-panel/wiki).

### Restoring defaults

If you happen to break any of the `preset0-*` files, just delete it, and run the config utility. The file will be restored from the default one. You may also run `nwg-shell-config -r` to restore all default configs and style sheets.

## Credits

This collection of software relies on some great third-party programs and libraries:

- LXAppearance by [lxde](http://www.lxde.org) team
- [wdisplays](https://github.com/artizirk/wdisplays) by Michael Aquilina / Arti Zirk
- [wlsunset](https://sr.ht/~kennylevinsen/wlsunset) by Kenny Levinsen
- [SwayNotificationCenter](https://github.com/ErikReider/SwayNotificationCenter) by Eric Reider
- [gtk-layer-shell](https://github.com/wmww/gtk-layer-shell) Copyright (c) 2014 Dennis Blommesteijn, Copyright (c) 2020 William Wold
- [gotk3](https://github.com/gotk3/gotk3) Copyright (c) 2013-2014 Conformal Systems LLC,
Copyright (c) 2015-2018 gotk3 contributors
- [gotk3-layershell](https://github.com/dlasky/gotk3-layershell) by [@dlasky](https://github.com/dlasky/gotk3-layershell/commits?author=dlasky) - many thanks for writing this software, and for patience with my requests!
- [go-sway](https://github.com/joshuarubin/go-sway) Copyright (c) 2019 Joshua Rubin
- [go-singleinstance](github.com/allan-simon/go-singleinstance) Copyright (c) 2015 Allan Simon
- [python-i3ipc](https://github.com/altdesktop/i3ipc-python) Copyright (c) 2015, Tony Crisci
- [python-psutil](https://github.com/giampaolo/psutil) Copyright (c) 2009, Jay Loden, Dave Daeschler, Giampaolo Rodola
- [python-geopy](https://github.com/geopy/geopy) by Kostya Esmukov
- [brightnessctl](https://github.com/Hummer12007/brightnessctl) Copyright (c) 2016 Mykyta Holuakha
- [playerctl](https://github.com/altdesktop/playerctl) by Tony Crisci
- [PulseAudio](https://www.freedesktop.org/wiki/Software/PulseAudio), 
[bluez-utils](http://www.bluez.org), [python-netifaces](https://archlinux.org/packages/community/x86_64/python-netifaces),
 and probably more, which I forgot to mention here. Please forgive me, if so.

[sway](https://github.com/swaywm/sway) is an i3-compatible Wayland compositor Copyright (c) 2016-2017 Drew DeVault
