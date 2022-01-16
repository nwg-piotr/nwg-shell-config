# nwg-shell-config

This program is a GUI to configure the components of [nwg-shell](https://github.com/nwg-piotr/nwg-shell) for
[sway](https://github.com/swaywm/sway) Wayland compositor. It also preconfigures commands for several external
programs, which I arbitrarily found the best to build a coherent, GTK3-based user experience on sway.

![nwg-shell-settings.png](https://scrot.cloud/images/2022/01/16/nwg-shell-settings.png)

At the top of the window you define common settings, including some custom solutions, like 
[autotiling](https://github.com/nwg-piotr/autotiling) (a part of the project) and gamma control, for which 
[wlsusnet](https://sr.ht/~kennylevinsen/wlsunset) is responsible. Below you select / define the desktop style,
with 4 predefined styles to choose from, and the "Custom" preset, which you can define on your own. Each of the
presets 0 - 3 may also be redefined according to your taste.

Each preset is bound to its own [nwg-panel](https://github.com/nwg-piotr/nwg-panel) config file and css style sheet.
Along with it come settings for the launcher ([nwg-drawer](https://github.com/nwg-piotr/nwg-drawer)), exit menu
([nwg-bar](https://github.com/nwg-piotr/nwg-bar)), and the dock ([nwg-dock](https://github.com/nwg-piotr/nwg-dock)).
The latter is only turned on by default in `preset-1` and `preset-3`.


<div align="center">preset-0<br /><img src="https://scrot.cloud/images/2022/01/16/preset-0.png" width="480"/></div>

<div align="center">preset-1<br /><img src="https://scrot.cloud/images/2022/01/16/preset-1.png" width="480"/></div>

<div align="center">preset-2<br /><img src="https://scrot.cloud/images/2022/01/16/preset-2.png" width="480"/></div>

<div align="center">preset-3<br /><img src="https://scrot.cloud/images/2022/01/16/preset-3.png" width="480"/></div>

