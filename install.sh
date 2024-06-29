#!/usr/bin/env bash

# Before running this script, make sure you have python-build, python-installer,
# python-wheel and python-setuptools installed.

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

# Remove launcher script
if [ -f "/usr/bin/$PROGRAM_NAME" ]; then
  echo "Removing /usr/bin/$PROGRAM_NAME"
  rm "/usr/bin/$PROGRAM_NAME"
fi

python -m build --wheel --no-isolation
python -m installer dist/*.whl

install -Dm 644 -t "/usr/share/applications" "$PROGRAM_NAME.desktop"
install -Dm 644 -t "/usr/share/pixmaps" "$PROGRAM_NAME.svg"
install -Dm 644 -t "/usr/share/pixmaps" nwg-shell-update.svg
install -Dm 644 -t "/usr/share/pixmaps" nwg-shell-translate.svg
install -Dm 644 -t "/usr/share/pixmaps" nwg-update-noupdate.svg
install -Dm 644 -t "/usr/share/pixmaps" nwg-update-available.svg
install -Dm 644 -t "/usr/share/pixmaps" nwg-update-checking.svg
install -Dm 644 -t "/usr/share/pixmaps" nwg-screenshot.svg
install -Dm 644 -t "/usr/share/pixmaps" nwg-3.svg
install -Dm 644 -t "/usr/share/pixmaps" nwg-2.svg
install -Dm 644 -t "/usr/share/pixmaps" nwg-1.svg
install -Dm 755 -t "/usr/local/bin" nwg-system-update

install -Dm 644 -t "/usr/share/licenses/nwg-shell-config" LICENSE
install -Dm 644 -t "/usr/share/doc/nwg-shell-config" README.md
