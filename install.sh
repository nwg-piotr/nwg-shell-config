#!/usr/bin/env bash

python3 setup.py install --optimize=1
cp nwg-shell-config.desktop /usr/share/applications/
cp nwg-shell-config.svg /usr/share/pixmaps/
cp nwg-shell-update.svg /usr/share/pixmaps/
cp nwg-shell-translate.svg /usr/share/pixmaps/
cp nwg-update-noupdate.svg /usr/share/pixmaps/
cp nwg-update-available.svg /usr/share/pixmaps/
cp nwg-update-checking.svg /usr/share/pixmaps/