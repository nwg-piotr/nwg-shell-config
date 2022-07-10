import json
import os
import subprocess
import sys
from shutil import copy2

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
        os.makedirs(data_dir, exist_ok=True)

    return data_dir


def init_files(src_dir, dst_dir, overwrite=False):
    src_files = os.listdir(src_dir)
    for file in src_files:
        if os.path.isfile(os.path.join(src_dir, file)):
            if overwrite or not os.path.isfile(os.path.join(dst_dir, file)):
                copy2(os.path.join(src_dir, file), os.path.join(dst_dir, file))
                print("Copying default file to '{}'".format(
                    os.path.join(dst_dir, file)))


def list_outputs():
    outputs = []
    try:
        from i3ipc import Connection
    except ModuleNotFoundError:
        print("'python-i3ipc' package required on sway, terminating")
        sys.exit(1)

    i3 = Connection()
    tree = i3.get_tree()
    for item in tree:
        if item.type == "output" and not item.name.startswith("__"):
            outputs.append(item.name)

    return outputs


def get_lat_lon():
    # Placeholder in case something goes wrong
    tz, lat, lon = "Europe/Warsaw", 52.2322, 20.9841

    lines = get_command_output("timedatectl show")
    if lines:
        for line in lines:
            if line.startswith("Timezone="):
                tz = line.split("=")[1]
        try:
            geolocator = Nominatim(user_agent="my_request")
            location = geolocator.geocode(tz)
            lat = round(location.latitude, 5)
            lon = round(location.longitude, 5)
        except:
            print("Geocoder unavailable. Do you have internet connection?", file=sys.stderr)

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


def get_command_output(command):
    try:
        return subprocess.check_output(command.split()).decode('utf-8').splitlines()
    except Exception as e:
        print("get_command_output() {}".format(e), file=sys.stderr)
        return []


def load_json(path):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print("Error loading json: {}".format(e))
        return None


def save_json(src_dict, path):
    with open(path, 'w') as f:
        json.dump(src_dict, f, indent=2)


def load_text_file(path):
    try:
        with open(path, 'r') as file:
            data = file.read()
            return data
    except Exception as e:
        print(e)
        return None


def save_string(string, file):
    try:
        file = open(file, "wt")
        file.write(string)
        file.close()
    except:
        print("Error writing file '{}'".format(file))


def save_list_to_text_file(data, file_path):
    text_file = open(file_path, "w")
    for line in data:
        text_file.write(line + "\n")
    text_file.close()


def distro_id():
    r = load_text_file("/etc/os-release")
    if r:
        for line in r.splitlines():
            if "ID=" in line:
                return line.lstrip("ID=")

    return ""


def list_background_dirs():
    files_in_main = False
    paths = []
    main = "/usr/share/backgrounds"
    items = os.listdir(main)
    for item in items:
        try:
            p = os.path.join(main, item)
            if os.path.isdir(p) and os.listdir(p):
                paths.append(p)
            else:
                files_in_main = True
        except Exception as e:
            print(e)
    if files_in_main:
        paths.insert(0, main)

    return paths


def notify(summary, body, timeout=3000):
    cmd = "notify-send '{}' '{}' -i /usr/share/pixmaps/nwg-shell-config.svg -t {}".format(summary, body, timeout)
    subprocess.call(cmd, shell=True)
