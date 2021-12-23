import os
import sys
import subprocess

from geopy.geocoders import Nominatim


def get_data_dir():
    data_dir = ""
    home = os.getenv("HOME")
    xdg_data_home = os.getenv("XDG_DATA_HOME")

    if xdg_data_home:
        data_dir = os.path.join(xdg_data_home, "nwg-shell-config/")
    else:
        if home:
            data_dir = os.path.join(home, ".local/share/nwg-shell-config/")

    if not os.path.isdir(data_dir):
        print("Creating '{}'".format(data_dir))
        os.mkdir(data_dir)

    return data_dir


def get_config_home():
    xdg_config_home = os.getenv('XDG_CONFIG_HOME')
    config_home = xdg_config_home if xdg_config_home else os.path.join(
        os.getenv("HOME"), ".config")
    config_dir = os.path.join(config_home, "scraper/")

    if not os.path.isdir(config_dir):
        print("Creating '{}'".format(config_dir))
        os.mkdir(config_dir)

    return config_dir


def get_lat_lon():
    # Placeholder in case something goes wrong
    tz, lat, lon = "Europe/Warsaw", 52.2322, 20.9841

    lines = get_command_output("timedatectl show")
    if lines:
        for line in lines:
            if line.startswith("Timezone="):
                tz = line.split("=")[1]
        geolocator = Nominatim(user_agent="my_request")
        location = geolocator.geocode(tz)
        lat = round(location.latitude, 5)
        lon = round(location.longitude, 5)

    return tz, lat, lon


def is_command(cmd):
    cmd = cmd.split()[0]
    cmd = "command -v {}".format(cmd)
    try:
        is_cmd = subprocess.check_output(
            cmd, shell=True).decode("utf-8").strip()
        if is_cmd:
            return True

    except subprocess.CalledProcessError:
        return False


def check_deps():
    d = {}
    for cmd in ["foot", "grim", "slurp", "swayidle", "swaylock", "xorg-xwayland", "wlsunset", "light",
                "wdisplays", "lxappearance", "autotiling", "azote", "imagemagick", "nwg-panel", "nwg-wrapper",
                "gopsuinfo", "nwg-drawer", "nwg-bar", "nwg-menu"]:
        d[cmd] = is_command(cmd)
    return d


def get_command_output(command):
    try:
        return subprocess.check_output(command.split()).decode('utf-8').splitlines()
    except Exception as e:
        print("get_command_output() {}".format(e), file=sys.stderr)
        return []
