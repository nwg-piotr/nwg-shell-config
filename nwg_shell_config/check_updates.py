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


def check_autostart():
    lines = load_text_file(os.path.join(get_config_home(), "sway/autostart")).splitlines()
    success = False
    for line in lines:
        if line == "exec_always nwg-shell-check-updates":
            success = True
            break
    if not success:
        print("autostart: appending 'exec_always nwg-shell-check-updates'")
        lines.append("exec_always nwg-shell-check-updates")
        save_list_to_text_file(lines, os.path.join(get_config_home(), "sway/autostart"))


def main():
    print("nwg-shell-version: {} ({})".format(ver2int(__version__), __version__))
    check_autostart()
    load_settings()
    if __version__ != "unknown" and settings["last-upgrade-check"] < ver2int(__version__):
        print("Checking if upgrade required (v{})".format(__version__))
        upgrade(__version__, settings)
    else:
        print("No upgrade required")


if __name__ == '__main__':
    main()
