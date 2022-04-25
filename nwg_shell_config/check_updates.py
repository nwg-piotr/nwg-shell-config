#!/usr/bin/env python3

from nwg_shell_config.tools import *
from nwg_shell_config.__about__ import __version__

settings = {}


def load_settings():
    defaults = {
        "keyboard-layout": "us",
        "autotiling-workspaces": "1 2 3 4 5 6 7 8",
        "autotiling-on": True,
        "night-lat": -1,
        "night-long": -1,
        "night-temp-low": 4500,
        "night-temp-high": 6500,
        "night-gamma": 1.0,
        "night-on": True,
        "terminal": "",
        "file-manager": "",
        "editor": "",
        "browser": "",
        "panel-preset": "preset-0",
        "panel-custom": "",
        "show-on-startup": True,
        "show-help": False,
        "last-upgrade-check": 0
    }
    settings_file = os.path.join(get_data_dir(), "settings")
    global settings
    if os.path.isfile(settings_file):
        print("Loading settings")
        settings = load_json(settings_file)
        for key in defaults:
            missing = 0
            if key not in settings:
                settings[key] = defaults[key]
                print("'{}' key missing from settings, adding '{}'".format(key, defaults[key]))
                missing += 1
            if missing > 0:
                print("Saving {}".format(settings_file))
                save_json(defaults, settings_file)
    else:
        print("ERROR: failed loading settings, creating {}".format(settings_file), file=sys.stderr)
        save_json(defaults, settings_file)


def main():
    print("nwg-shell-installer: {} ({})".format(ver2int(__version__), __version__))
    load_settings()
    if __version__ != "unknown" and settings["last-upgrade-check"] < ver2int(__version__):
        upgrade(__version__, settings)

    if is_command("nwg-shell"):
        subprocess.Popen('exec {}'.format("nwg-shell -n"), shell=True)


if __name__ == '__main__':
    main()
