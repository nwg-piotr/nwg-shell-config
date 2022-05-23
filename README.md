# nwg-shell config utility

The [nwg-shell](https://github.com/nwg-piotr/nwg-shell) project is a collection of components for building a GTK-based user interface for [sway](https://github.com/swaywm/sway) Wayland compositor. It consists of a panel, launcher, dock, traditional menu, wallpaper manager, as well as some helper scripts. Until now, it has functioned as a do-it-yourself kit, with items to choose from. This program is a GUI to configure all the components in one place. It also integrates several external programs, which we arbitrarily found the best to build a coherent user experience.

[![Packaging status](https://repology.org/badge/vertical-allrepos/nwg-shell-config.svg)](https://repology.org/project/nwg-shell-config/versions)

![nwg-shell-settings.png](https://raw.githubusercontent.com/nwg-piotr/nwg-shell-resources/master/images/nwg-shell/nwg-shell-config-02.png)

At the top of the window you define common settings, including some custom solutions, like 
[autotiling](https://github.com/nwg-piotr/autotiling) (a part of the project) and gamma control, for which 
[wlsunset](https://sr.ht/~kennylevinsen/wlsunset) is responsible. Below you select / define the desktop style,
with 4 predefined styles to choose from, and the "Custom" preset, which you can define on your own. Each of the
presets 0 - 3 may also be adjusted to your taste.

## Desktop styles

Every preset is bound to its own [nwg-panel](https://github.com/nwg-piotr/nwg-panel) config file and css style sheet.
Along with it come settings for the launcher ([nwg-drawer](https://github.com/nwg-piotr/nwg-drawer)), exit menu
([nwg-bar](https://github.com/nwg-piotr/nwg-bar)), and the dock ([nwg-dock](https://github.com/nwg-piotr/nwg-dock)).
The latter is only turned on by default in `preset-1` and `preset-3`.


<div align="center">preset-0<br /><img src="https://raw.githubusercontent.com/nwg-piotr/nwg-shell-resources/master/images/nwg-shell-config/preset-0.png" width="480"/></div>

<div align="center">preset-1<br /><img src="https://raw.githubusercontent.com/nwg-piotr/nwg-shell-resources/master/images/nwg-shell-config/preset-1.png" width="480"/></div>

<div align="center">preset-2<br /><img src="https://raw.githubusercontent.com/nwg-piotr/nwg-shell-resources/master/images/nwg-shell-config/preset-2.png" width="480"/></div>

<div align="center">preset-3<br /><img src="https://raw.githubusercontent.com/nwg-piotr/nwg-shell-resources/master/images/nwg-shell-config/preset-3.png" width="480"/></div>

To familiarize yourself with key bindings, you may want to mark the "Show help" check box in the config utility. 
This will display a conky-like help widget, supported by [nwg-wrapper](https://github.com/nwg-piotr/nwg-wrapper).

The **Controls module** of the panel comes with some preconfigured goodies to fine tune what your system looks and 
behaves like. Some menu items rely on the other software you need to have installed. 

<div align="center">nwg-panel Controls module<br /><img src="https://raw.githubusercontent.com/nwg-piotr/nwg-shell-resources/master/images/nwg-shell-config/controls.png"/></div>

- **Wallpapers**: you need [Azote](https://github.com/nwg-piotr/azote), which is a part of the nwg-shell project;
- **GTK settings**: you need the [nwg-look](https://github.com/nwg-piotr/nwg-look) package;
- **Outputs** management relies on [nwg-displays](https://github.com/nwg-piotr/nwg-displays).

**Notification Center** is supported by Eric Reider's [SwayNotificationCenter](https://github.com/ErikReider/SwayNotificationCenter).

<div align="center">Notification Center<br /><img src="https://raw.githubusercontent.com/nwg-piotr/nwg-shell-resources/master/images/nwg-shell-config/swaync.png" width="480"/></div>

All of above is installed by default together with the sway session of [ArchLabs Linux](https://archlabslinux.com), 
which the nwg-shell-config utility was developed for. Anyway, if you'd like to give it a try on another system,
take a look at the [skel/sway-home/.config](https://github.com/nwg-piotr/nwg-shell-config/tree/master/skel/sway-home/.config)
directory. It contains the sway config, together with the rest of necessary configs and style sheets.

## Notes

### Includes

All the settings managed by nwg-shell-config are included into the `~/.config/sway/config` file like this:

```text
# The files we include below will be created / overwritten by nwg-shell tools
#
include variables
include outputs
include autostart
include workspaces
include keyboard
include pointer
include touchpad
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

To change the appearance of nwg-shell components, you need to edit their css style sheets. They are all located in 
appropriate `~./config/nwg-*` directories, named `preset-*.css`. You may edit them to your liking.
For the Custom preset add own styles under another names, and set these names in the config GUI (Custom preset -> 
Panel & css).

### nwg-panel & nwg-menu

have their own config GUI. Find the "Panel settings" entry in the Controls menu. More info there's in the [panel Wiki](https://github.com/nwg-piotr/nwg-panel/wiki).

### Restoring defaults

If you happen to break any of the `preset0-*` files, just delete it, and run the config utility. 
The file will be restored from the default one. You may also run `nwg-shell-config -r` to restore all default presets.
