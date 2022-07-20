# nwg-shell config utility

The [nwg-shell](https://github.com/nwg-piotr/nwg-shell) project is a collection of components to build a GTK-based user interface for [sway](https://github.com/swaywm/sway) Wayland compositor. It consists of a panel, launcher, dock, traditional menu, wallpaper manager, as well as some helper scripts. Until now, it has functioned as a do-it-yourself kit, with items to choose from. This program is a GUI to configure all the components in one place. It also integrates several third party components, which we arbitrarily found the best to build a coherent user experience.

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

To familiarize yourself with key bindings, you may want to mark the "Show help" check box in the config utility. 
This will display a conky-like help widget, supported by [nwg-wrapper](https://github.com/nwg-piotr/nwg-wrapper).

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

In case you need to configure some settings on your own, uncheck the appropriate "Use these settings" box and/or delete `include <whatever>` from the sway config file.

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

Feel free to add whichever other binding you need, but do not change the variable values other way than with the config GUI.

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
