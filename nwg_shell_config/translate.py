#!/usr/bin/env python3

import locale


def main():
    print(locale.getlocale())
    locales = locale.locale_alias
    for item in locales:
        print(item)


if __name__ == "__main__":
    main()
