import sys
import subprocess

from geopy.geocoders import Nominatim


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


def check_dependencies():
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
