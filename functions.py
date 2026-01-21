import configparser as parse
import copy
import os.path
import threading
from ast import literal_eval as eval
import ctypes
import sys

import devices as dev
import variables as var
from time import sleep

def read_config():
    if os.path.exists(var.settings['path'] + "\\" + var.settings['config']):
        config = parse.ConfigParser()
        config.read(var.settings['path'] + "\\" + var.settings['config'])

        errors = []
        for section in config.sections():
            for item in config[section]:
                try:
                    setting = eval(config[section][item])
                except (SyntaxError, ValueError):
                    setting = config[section][item]

                if section == "GLOBAL":
                    var.settings[item] = setting
                elif section == "SOUND":
                    var.settings['sound'][item] = setting
                elif section == "PROFILE":
                    var.settings['profile'][item] = setting
                else:
                    if not section in errors:
                        errors.append(section)

        if errors:
            text = var.lang['section_errors']['intro']
            for error in errors:
                text += error + "\n"
            text += var.lang['section_errors']['outro']
            response = ctypes.windll.user32.MessageBoxW(0, text, var.lang['section_errors']['title'], 1)
            if response == 1:
                pass
            elif response == 2:
                sys.exit(0)
    else:
        write_config()
    read_profile()

def read_profile(profile=None):
    if not get_profiles():
        var.settings['profile']['current'] = "Default"

    if not profile:
        profile = var.settings['profile']['current']
    elif profile != var.settings['profile']['current']:
        var.status['profile_prev'] = var.settings['profile']['current']
        var.settings['profile']['current'] = profile

    if os.path.exists(var.settings['path'] + "\\" + var.settings['profile']['path'] + "\\" + profile + ".ini"):
        config = parse.ConfigParser()
        config.read(var.settings['path'] + "\\" + var.settings['profile']['path'] + "\\" + profile + ".ini")

        errors = []
        for section in config.sections():
            for item in config[section]:
                setting = eval(config[section][item])
                if section == "LOCAL":
                    var.settings['local'][item] = setting
                elif section.lower() in var.bindings:
                    if item == "up" or item == "down" or item == "switch" or item == "pedal" or item == "label":
                        var.bindings[section.lower()][item] = setting
                    else:
                        var.settings[section.lower()][item] = setting
                else:
                    if not section in errors:
                        errors.append(section)

        if errors:
            text = var.lang['section_errors']['intro']
            for error in errors:
                text += error + "\n"
            text += var.lang['section_errors']['outro']
            response = ctypes.windll.user32.MessageBoxW(0, text, var.lang['section_errors']['title'], 1)
            if response == 1:
                pass
            elif response == 2:
                sys.exit(0)

        while not var.status['devices_loaded']:
            sleep(0.1)
        bind_errors = []
        for function in var.bindings:
            if function != "status":
                for control in var.bindings[function]:
                    if var.bindings[function][control]['guid'] != 0:
                        try:
                            dev.device_info[var.bindings[function][control]['guid']]
                        except KeyError:
                            var.bindings_cache[function][control] = var.bindings[function][control]
                            var.bindings[function][control] = {"label": var.bindings[function][control]['label'], "guid": 0, "type": "none", "num": 0}
                            bind_errors.append([str(function), str(control)])

    else:
        write_profile(profile)

def write_config():
    config = parse.ConfigParser()

    config['GLOBAL'] = {}
    for setting in var.settings:
        if not isinstance(var.settings[setting], dict):
            config['GLOBAL'][setting] = str(var.settings[setting])

    config['SOUND'] = {}
    for setting in var.settings['sound']:
        config['SOUND'][setting] = str(var.settings['sound'][setting])

    config['PROFILE'] = {}
    for setting in var.settings['profile']:
        if setting != "previous":
            config['PROFILE'][setting] = str(var.settings['profile'][setting])

    if not os.path.exists(var.settings['path']):
        os.mkdir(var.settings['path'])

    with open(var.settings['path'] + "\\"+ "global.ini", 'w') as file:
        # noinspection PyTypeChecker
        config.write(file)
        
def write_profile(profile=None):
    if not profile:
        profile = var.settings['profile']['current']

    config = parse.ConfigParser()

    config['LOCAL'] = {}
    for setting in var.settings['local']:
        config['LOCAL'][setting] = str(var.settings['local'][setting])

    for bind in var.bindings:
        if bind != "status":
            config[bind.upper()] = {}
            for subbind in var.bindings[bind]:
                if var.bindings[bind][subbind]['label'] != "None" and var.bindings[bind][subbind]['guid'] == 0:
                    config[bind.upper()][subbind] = str(var.bindings_cache[bind][subbind])
                else:
                    config[bind.upper()][subbind] = str(var.bindings[bind][subbind])

    if not os.path.exists(var.settings['path'] + "\\" + var.settings['profile']['path']):
        os.mkdir(var.settings['path'] + "\\" + var.settings['profile']['path'])

    with open(var.settings['path'] + "\\" + var.settings['profile']['path'] + "\\" + profile + ".ini", 'w') as file:
        # noinspection PyTypeChecker
        config.write(file)

def delete_profile(profile):
    path = var.settings['path'] + "\\" + var.settings['profile']['path'] + "\\" + profile + ".ini"
    if profile in get_profiles() and len(get_profiles()) > 1:
        if os.path.exists(path):
            os.remove(path)

def get_profiles():
    directory = var.settings['path'] + "\\" + var.settings['profile']['path']
    var.status['profile_list'] = []
    for name in os.listdir(path = directory):
        if name.endswith(".ini"):
            var.status['profile_list'].append(name.split('.', 1)[0])
    return var.status['profile_list']

def is_bind():
    if var.event['type'] == "axis":
        event = {
            "guid": var.event['guid'],
            "type": var.event['type'],
            "num": var.event['num'],
            "value": var.event['value']
        }
        if event['value'] > var.settings['local']['high_threshold']:
            event['value'] = var.settings['local']['high_threshold']
        elif event['value'] < var.settings['local']['low_threshold']:
            event['value'] = var.settings['local']['low_threshold']
    elif var.event['type'] == "hat":
        event = {
            "guid": var.event['guid'],
            "type": var.event['type'],
            "num": var.event['num'],
            "dir": var.event['value']
        }
    elif var.event['type'] == "key":
        event = {
            "guid": var.event['guid'],
            "type": var.event['type'],
            "num": var.event['num'],
            "value": var.event['value']
        }
    else:
        event = {
            "guid": var.event['guid'],
            "type": var.event['type'],
            "num": var.event['num'],
        }
    result = []

    for function in var.bindings:
        if function != "status":
            for control in var.bindings[function]:
                bind = copy.deepcopy(var.bindings[function][control])
                try:
                    bind.pop("label")
                except KeyError:
                    pass
                if "input" in bind:
                    if event['guid'] == bind['guid'] and event['num'] == bind['num'] and bind['type'] == "axis":
                        result.append({"function": function, "control": control, "value": var.event['value']})
                elif event == bind:
                    result.append({"function": function, "control": control})

    if not result:
        result = False
    return result

def check_uid(irsdk):
    if irsdk.is_connected:
        if irsdk['DriverInfo']['DriverUserID'] not in var.backend['whitelist']:
            response = ctypes.windll.user32.MessageBoxW(0, "You've not been authorized to use this program.", "I5G Tools  -  Unauthorized user!", 0)
            if response == 1:
                sys.exit(0)

def reset_bind_thresh(thresh, value):
    if not (thresh == 'low_threshold' or thresh == 'high_threshold'):
        print("Warning: reset_bind_thresh with arguments: ", thresh, value)
        return
    for function in var.bindings:
        if function != 'status':
            for control in var.bindings[function]:
                if var.bindings[function][control] is not None and var.bindings[function][control]['type'] == 'axis' and not ((function == 'clutch' or function == 'throttle') and control == 'pedal'):
                    if (var.bindings[function][control]['value'] == var.settings['local']['high_threshold'] and thresh == 'high_threshold') or (var.bindings[function][control]['value'] == var.settings['local']['low_threshold'] and thresh == 'low_threshold'):
                        var.bindings[function][control]['value'] = value

def start_thread(target):
    thread = threading.Thread(target=target, daemon=True)
    thread.start()