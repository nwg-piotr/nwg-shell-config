#!/usr/bin/env python3

# dependencies: python-geopy

from nwg_shell_config.tools import *


def main():
    print(get_lat_lon())
    print(check_dependencies())


if __name__ == '__main__':
    main()
