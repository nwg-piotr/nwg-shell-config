#!/usr/bin/env bash

path=$(python -c 'import site; print(site.getsitepackages()[0])')
sh -c 'rm -r $path/nwg_shell_config*'
rm /usr/bin/nwg-shell-config
rm /usr/share/applications/nwg-shell-config.desktop