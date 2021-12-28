#!/usr/bin/env bash

path=$(python -c 'import site; print(site.getsitepackages()[0])')
rm -r $path'/nwg_shell_config*'
rm /usr/bin/nwg-shell-config
