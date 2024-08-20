import json
import os
import shutil
import socket
import subprocess
import sys
import tarfile
from shutil import copy2

from geopy.geocoders import Nominatim


def get_config_home():
    config_home = os.getenv('XDG_CONFIG_HOME') if os.getenv('XDG_CONFIG_HOME') else os.path.join(
        os.getenv("HOME"), ".config/")
    return config_home


def get_data_home():
    d_home = os.getenv('XDG_DATA_HOME') if os.getenv('XDG_DATA_HOME') else os.path.join(
        os.getenv("HOME"), ".local/share")
    return d_home


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


def get_data_dirs():
    dirs = [get_data_home()]
    xdg_data_dirs = os.getenv("XDG_DATA_DIRS") if os.getenv("XDG_DATA_DIRS") else "/usr/local/share/:/usr/share/"
    for d in xdg_data_dirs.split(":"):
        dirs.append(d)
    confirmed = []
    for d in dirs:
        if os.path.isdir(d):
            confirmed.append(d)

    return confirmed


def get_shell_data_dir():
    data_dir = ""
    home = os.getenv("HOME")
    xdg_data_home = os.getenv("XDG_DATA_HOME")

    if xdg_data_home:
        data_dir = os.path.join(xdg_data_home, "nwg-shell/")
    else:
        if home:
            data_dir = os.path.join(home, ".local/share/nwg-shell/")

    return data_dir


def temp_dir():
    if os.getenv("TMPDIR"):
        return os.getenv("TMPDIR")
    elif os.getenv("TEMP"):
        return os.getenv("TEMP")
    elif os.getenv("TMP"):
        return os.getenv("TMP")

    return "/tmp"


def data_home():
    if os.getenv("XDG_DATA_HOME"):
        return os.getenv("XDG_DATA_HOME")

    return os.path.join(os.getenv("HOME"), ".local/share")


def get_theme_names():
    theme_dirs = []
    for d in get_data_dirs():
        p = os.path.join(d, "themes")
        if os.path.isdir(p):
            theme_dirs.append(p)

    home = os.getenv("HOME")
    if home:
        p = os.path.join(home, ".themes")
        if os.path.isdir(p):
            theme_dirs.append(p)

    names = []
    exclusions = ["Default", "Emacs"]
    for d in theme_dirs:
        for item in os.listdir(d):
            if os.path.isdir(os.path.join(d, item)) and item not in exclusions:
                content = os.listdir(os.path.join(d, item))
                for name in content:
                    if name.startswith("gtk-"):
                        if item not in names:
                            names.append(item)
                            break
    names.sort()
    return names


def has_dirs(path):
    for item in os.listdir(path):
        if os.path.isdir(os.path.join(path, item)):
            return True
    return False


def get_theme_name(path):
    for item in os.listdir(path):
        if item == "index.theme":
            lines = load_text_file(os.path.join(path, item)).splitlines()
            for line in lines:
                if line.startswith("Name="):
                    return line.split("=")[1].strip()
    return None


def get_icon_themes():
    # In contrary to the get_theme_names() function, this time we need as well the theme name, as its folder name,
    # as we select icon themes by their folder names, and display names may be different. Odd, isn't it?
    icon_dirs = []
    for d in get_data_dirs():
        p = os.path.join(d, "icons")
        if os.path.isdir(p):
            icon_dirs.append(p)

    home = os.getenv("HOME")
    if home:
        p = os.path.join(home, ".icons")
        if os.path.isdir(p):
            icon_dirs.append(p)

    names = {}
    exclusions = ["default", "hicolor", "locolor"]
    for d in icon_dirs:
        for item in os.listdir(d):
            p = os.path.join(d, item)
            if item not in exclusions and os.path.isdir(p) and has_dirs(p):
                name = get_theme_name(os.path.join(d, item))
                if name:
                    names[name] = item
    return names


def init_files(src_dir, dst_dir, overwrite=False):
    running_hyprland = os.getenv("HYPRLAND_INSTANCE_SIGNATURE")
    src_files = os.listdir(src_dir)
    for file in src_files:
        if os.path.isfile(os.path.join(src_dir, file)):
            if overwrite or not os.path.isfile(os.path.join(dst_dir, file)):
                if "hyprland" not in file or running_hyprland:
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


def h_list_monitors():
    reply = hyprctl("j/monitors")
    try:
        outputs = []
        for item in json.loads(reply):
            if "name" in item:
                outputs.append(item["name"])
        return outputs
    except Exception as e:
        eprint(e)
        return []


def list_inputs_by_type(input_type=""):
    inputs = []
    try:
        from i3ipc import Connection
    except ModuleNotFoundError:
        print("'python-i3ipc' package required on sway, terminating")
        sys.exit(1)

    i3 = Connection()
    all_inputs = i3.get_inputs()
    for i in all_inputs:
        if i.type == input_type or not input_type:
            inputs.append(i.identifier)

    return inputs


def h_list_devices_by_type(device_type):
    reply = hyprctl("j/devices")
    devices = json.loads(reply)
    if devices and device_type in devices:
        return devices[device_type]

    return {}


def get_lat_lon():
    eprint("Checking location for night light settings")
    # Placeholder in case something goes wrong
    tz, lat, lon = "Warsaw", 52.2322, 20.9841

    lines = get_command_output("timedatectl show")
    if lines:
        for line in lines:
            if line.startswith("Timezone="):
                tz = line.split("=")[1].split("/")[-1]
        try:
            geolocator = Nominatim(user_agent="my_request")
            location = geolocator.geocode(tz)
            lat = round(location.latitude, 5)
            lon = round(location.longitude, 5)
        except:
            eprint(f"Couldn't find coordinates for {tz}.")

    eprint(f"Setting coordinates: {tz}, {lat}, {lon}")
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


def gtklock_module_path(module_name):
    paths = ["/usr/lib/gtklock/{}-module.so".format(module_name), "/usr/local/lib/gtklock/{}-module.so".format(module_name)]
    for p in paths:
        if os.path.isfile(p):
            return p

    return ""


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
        eprint("Error loading json: {}".format(e))
        return None


def save_json(src_dict, path, en_ascii=True):
    with open(path, 'w') as f:
        json.dump(src_dict, f, indent=2, ensure_ascii=en_ascii)


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


def check_key(dictionary, key, default_value):
    """
    Adds a key w/ default value if missing from the dictionary
    """
    if key not in dictionary:
        dictionary[key] = default_value


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def load_shell_data():
    shell_data_file = os.path.join(get_shell_data_dir(), "data")
    shell_data = load_json(shell_data_file)
    defaults = {
        "installed-version": get_shell_version(),
        "updates": [],
        "interface-locale": "",
        "autotranslated": False
    }
    if not shell_data:
        shell_data = defaults
        save_json(shell_data, shell_data_file)
        eprint("ERROR: '{}' file not found or corrupted. Initializing from defaults.".format(shell_data_file))
        eprint("The update history has been lost!")

    # Upgrade v0.2.5 -> v0.3.0
    # 1. If the "last-upgrade" key found, let's use the value as the "installed-version".
    # 2. We no longer need the pre-v0.3.0 "last-upgrade" key: delete it if found.
    if "last-upgrade" in shell_data:
        shell_data["installed-version"] = shell_data["last-upgrade"]
        del shell_data["last-upgrade"]
        save_json(shell_data, shell_data_file)

    for key in defaults:
        if key not in shell_data:
            shell_data[key] = defaults[key]

    return shell_data


def get_shell_version():
    lines = subprocess.check_output("nwg-shell -v".split()).decode('utf-8').splitlines()
    return lines[0].split()[2]


def playerctl_metadata():
    try:
        return subprocess.check_output("playerctl metadata 2>&1", shell=True).decode("utf-8").strip()
    except subprocess.CalledProcessError:
        return ""


def is_newer(string_new, string_existing):
    """
    Compares versions in format 'major.minor.patch' (just numbers allowed).
    :param string_new: new version to compare with existing one
    :param string_existing: existing version
    :return: True if new is newer then existing
    """
    new = major_minor_path(string_new)
    existing = major_minor_path(string_existing)
    if new and existing:
        if new[0] > existing[0]:
            return True
        elif new[1] > existing[1] and new[0] >= existing[0]:
            return True
        elif new[2] > existing[2] and new[0] >= existing[0] and new[1] >= existing[1]:
            return True
        else:
            return False
    else:
        return False


def major_minor_path(string):
    parts = string.split(".")
    if len(parts) != 3:
        return None
    try:
        return int(parts[0]), int(parts[1]), int(parts[2])
    except:
        return None


def log_line(file, label, line):
    label.set_markup(label.get_text() + line)
    file.write(line)


def do_backup(btn, config_home_dir, data_home_dir, backup_configs, backup_data, entry_backup, voc):
    dest_file = entry_backup.get_text() + ".tar.gz"
    if dest_file:
        id_file = os.path.join(temp_dir(), "nwg-shell-backup-id")
        save_string(dest_file.split("/")[-1], id_file)
        try:
            tar = tarfile.open(dest_file, "w:gz")
            tar.add(id_file, "nwg-shell-backup-id")
            for item in backup_configs:
                for name in os.listdir(os.path.join(config_home_dir, item)):
                    tar.add(os.path.join(config_home_dir, item, name))

            for item in backup_data:
                for name in os.listdir(os.path.join(data_home_dir, item)):
                    tar.add(os.path.join(data_home_dir, item, name))
            tar.close()
            notify(voc["backup"], "{}".format(dest_file))
        except Exception as e:
            notify(voc["backup"], e)


def unpack_to_tmp(fcb, restore_btn, restore_warn, voc):
    unpack_to = os.path.join(temp_dir(), "nwg-shell-backup")
    if os.path.isdir(unpack_to):
        shutil.rmtree(unpack_to)
    os.mkdir(unpack_to)
    backup = fcb.get_file().get_path()
    try:
        file = tarfile.open(backup)
        file.extractall(unpack_to)
        id_file = os.path.join(unpack_to, "nwg-shell-backup-id")
        if os.path.isfile(id_file):
            print("Unpacked backup from '{}'".format(load_text_file(id_file)))
            restore_btn.show()
            restore_warn.show()
        else:
            eprint("'{}' file is not a valid nwg-shell backup".format(backup))
            restore_btn.hide()
            restore_warn.hide()
            notify(voc["backup"], "{} {}".format(backup.split("/")[-1], voc["backup-invalid-file"]), 3000)
    except Exception as e:
        eprint("'{}'".format(backup), e)


def unpack_from_path(b_path):
    unpack_to = os.path.join(temp_dir(), "nwg-shell-backup")
    if os.path.isdir(unpack_to):
        shutil.rmtree(unpack_to)
    os.mkdir(unpack_to)
    try:
        file = tarfile.open(b_path)
        file.extractall(unpack_to)
        id_file = os.path.join(unpack_to, "nwg-shell-backup-id")
        if os.path.isfile(id_file):
            print("Unpacked backup from '{}'".format(load_text_file(id_file)))
        else:
            eprint("'{}' file is not a valid nwg-shell backup".format(b_path))
    except Exception as e:
        eprint("'{}'".format(b_path), e)


def restore_from_tmp(btn, restore_warning_label, voc):
    # The source and destination $HOME paths may be different, if we're restoring on another machine or user
    # The function may be called from outside GUI (-b argument); `btn` and `restore_warning_label` will be None, if so.
    parent_dir = os.path.join(temp_dir(), "nwg-shell-backup", "home")
    src_dir = os.path.join(parent_dir, os.listdir(parent_dir)[0])
    try:
        shutil.copytree(src_dir, os.getenv("HOME"), dirs_exist_ok=True)
        if btn:
            btn.hide()
        if restore_warning_label:
            restore_warning_label.hide()
        notify("{}".format(voc["backup"]), voc["backup-restore-success"], 10000)
        print("Configs and data restored.")
    except Exception as e:
        notify(voc["backup"], "{}".format(e))
        eprint("Error restoring data {}".format(e))


def hyprctl(cmd, buf_size=20480):
    # /tmp/hypr moved to $XDG_RUNTIME_DIR/hypr in #5788
    xdg_runtime_dir = os.getenv("XDG_RUNTIME_DIR")
    hypr_dir = f"{xdg_runtime_dir}/hypr" if xdg_runtime_dir and os.path.isdir(
        f"{xdg_runtime_dir}/hypr") else "/tmp/hypr"

    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect(f"{hypr_dir}/{os.getenv('HYPRLAND_INSTANCE_SIGNATURE')}/.socket.sock")

    s.send(cmd.encode("utf-8"))
    output = s.recv(buf_size).decode('utf-8')
    s.close()

    return output


def bool2lower(bool_value):
    if bool_value:
        return "true"
    else:
        return "false"
