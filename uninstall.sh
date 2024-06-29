#!/usr/bin/env bash

PROGRAM_NAME="nwg-shell-config"
MODULE_NAME="nwg_shell_config"
SITE_PACKAGES="$(python3 -c "import sysconfig; print(sysconfig.get_paths()['purelib'])")"
PATTERN="$SITE_PACKAGES/$MODULE_NAME*"

# Remove from site_packages
for path in $PATTERN; do
    if [ -e "$path" ]; then
        echo "Removing $path"
        rm -r "$path"
    fi
done

# Remove launcher scripts
filenames=("/usr/bin/nwg-autotranslate"
           "/usr/bin/nwg-shell-config"
           "/usr/bin/nwg-shell-config-sway"
           "/usr/bin/nwg-shell-config-hyprland"
           "/usr/bin/nwg-lock"
           "/usr/bin/nwg-shell-help"
           "/usr/bin/nwg-autotiling"
           "/usr/bin/nwg-shell-updater"
           "/usr/bin/nwg-shell-translate"
           "/usr/bin/nwg-update-indicator"
           "/usr/bin/nwg-screenshot-applet"
           "/usr/bin/nwg-dialog")

for filename in "${filenames[@]}"; do
  rm -f "$filename"
  echo "Removing -f $filename"
done

rm -f "/usr/share/applications $PROGRAM_NAME.desktop"
rm -f "/usr/share/pixmaps $PROGRAM_NAME.svg"
rm -f /usr/share/pixmaps/nwg-shell-update.svg
rm -f /usr/share/pixmaps/nwg-shell-translate.svg
rm -f /usr/share/pixmaps/nwg-update-noupdate.svg
rm -f /usr/share/pixmaps/nwg-update-available.svg
rm -f /usr/share/pixmaps/nwg-update-checking.svg
rm -f /usr/share/pixmaps/nwg-screenshot.svg
rm -f /usr/share/pixmaps/nwg-3.svg
rm -f /usr/share/pixmaps/nwg-2.svg
rm -f /usr/share/pixmaps/nwg-1.svg
rm -f /usr/local/bin/nwg-system-update
rm -f /usr/share/licenses/nwg-shell-config/LICENSE
rm -f /usr/share/doc/nwg-shell-config/README.md
