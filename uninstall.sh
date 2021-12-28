#!/usr/bin/env bash

path=$(python -c 'import site; print(site.getsitepackages()[0])')
sudo rm -r $path'/nwg_shell_config*'
sudo rm /usr/bin/nwg-shell-config
sudo rm /usr/share/applications/nwg-shell-config.desktop