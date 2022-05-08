#!/usr/bin/env bash

python3 setup.py install --optimize=1
cp nwg-shell-config.desktop /usr/share/applications/
cp nwg-shell-config.svg /usr/share/pixmaps/
