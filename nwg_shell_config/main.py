#!/usr/bin/env python3

# Dependencies: python-geopy

import locale

from nwg_shell_config.tools import *

dir_name = os.path.dirname(__file__)

config_home = os.getenv('XDG_CONFIG_HOME') if os.getenv('XDG_CONFIG_HOME') else os.path.join(
    os.getenv("HOME"), ".config/")

lang = locale.getlocale()[0].split("_")[0]


def main():
    print(lang)
    print(get_lat_lon())
    print(get_data_dir())
    print(config_home)
    print(check_deps())


if __name__ == '__main__':
    main()
