#!/usr/bin/env python3

"""
This script automagically translates some preinstalled UI labels into users $LANG.
Repository: https://github.com/nwg-piotr/nwg-shell-config
Project site: https://nwg-piotr.github.io/nwg-shell
Author's email: nwg.piotr@gmail.com
Copyright (c) 2021-2023 Piotr Miller & Contributors
License: MIT
"""

import os
import sys
import locale

from nwg_shell_config.tools import get_config_home, get_shell_data_dir, load_shell_data, load_json, save_json

config_home = get_config_home()
dir_name = os.path.dirname(__file__)
translation = {}


def main():
    shell_data_file = os.path.join(get_shell_data_dir(), "data")
    shell_data = load_shell_data()
    if not shell_data["autotranslated"]:
        print("Looks like auto-translation has not yet been done. Let's get this over with.")
        print("This will only be done once. Then you're free to modify labels manually.")

        user_locale = locale.getlocale()[0]

        langs_dir = os.path.join(dir_name, "autotranslate")
        translations = os.listdir(langs_dir)

        print(f"User locale: '{user_locale}'")
        if user_locale not in translations:
            print(f"Translation into '{user_locale}' not found. At least I tried.")
            shell_data["autotranslated"] = True
            save_json(shell_data, shell_data_file)
            sys.exit(0)
        else:
            print(f"Translation into '{user_locale}' found")
            global translation
            # en_US MUST contain all the keys, load them all just in case
            translation = load_json(os.path.join(dir_name, "autotranslate", "en_US"))
            user_lang = load_json(os.path.join(dir_name, "autotranslate", user_locale))
            # translate available words into users lang
            for key in translation:
                if key in user_lang:
                    translation[key] = user_lang[key]
            print(translation)

            # Translate panel configs
            config_dir = os.path.join(config_home, "nwg-panel")
            items = ["preset-0", "preset-1", "preset-2", "preset-2", "hyprland-0", "hyprland-1", "hyprland-2",
                     "hyprland-3"]
            for item in items:
                path = os.path.join(config_dir, item)
                panels = load_json(path)
                for panel in panels:
                    if "processes-label" in panel["controls-settings"]:
                        tr = translation["processes"]
                        panel["controls-settings"]["processes-label"] = tr

                    if "custom-items" in panel["controls-settings"]:
                        custom_items = panel["controls-settings"]["custom-items"]

                        for i in custom_items:
                            if i["name"] == "Wallpapers":
                                tr = translation["wallpapers"]
                                i["name"] = tr

                            if i["name"] == "GTK settings":
                                tr = translation["look-settings"]
                                i["name"] = tr

                            if i["name"] == "Wallpapers":
                                tr = translation["wallpapers"]
                                i["name"] = tr

                            if i["name"] == "Displays":
                                tr = translation["displays-settings"]
                                i["name"] = tr

                            if i["name"] == "Panel settings":
                                tr = translation["panel-settings"]
                                i["name"] = tr

                            if i["name"] == "Shell settings":
                                tr = translation["shell-settings"]
                                i["name"] = tr

                    if "menu" in panel["controls-settings"]:
                        menu = panel["controls-settings"]["menu"]
                        if menu["name"] == "Exit":
                            menu["name"] = translation["exit"]

                        entries = menu["items"]
                        for entry in entries:
                            if entry["name"] == "Lock":
                                entry["name"] = translation["lock-screen"]

                            if entry["name"] == "Exit sway session" or entry["name"] == "Exit Hyprland session" or \
                                    entry["name"] == "Logout":
                                entry["name"] = translation["exit-compositor"]

                            if entry["name"] == "Restart":
                                entry["name"] = translation["reboot"]

                            if entry["name"] == "Shutdown":
                                entry["name"] = translation["shutdown"]

                print(f"Saving {path}")
                save_json(panels, path)

            # Translate nwg-bar template
            config_dir = os.path.join(config_home, "nwg-bar")
            path = os.path.join(config_dir, "bar.json")

            bar = load_json(path)
            for item in bar:
                if item["label"] == "Lock":
                    item["label"] = translation["lock"]

                if item["label"] == "Logout":
                    item["label"] = translation["logout"]

                if item["label"] == "Reboot":
                    item["label"] = translation["reboot"]

                if item["label"] == "Shutdown":
                    item["label"] = translation["shutdown"]

            print(f"Saving {path}")
            save_json(bar, path)

            print("Marking autotranslation done.")
            shell_data["autotranslated"] = True
            save_json(shell_data, shell_data_file)

    else:
        print("Auto-translation already done, nothing to do.")
        sys.exit(0)


if __name__ == "__main__":
    main()
