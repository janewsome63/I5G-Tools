import configparser as parse
import os.path
import threading
from os import write
from string import capwords
from turtle import config_dict
from ast import literal_eval as eval
import ctypes
import sys

import devices as dev
import variables as var
from time import sleep

startup = True
rewrite = False

def read_config():
    global startup
    global rewrite
    if os.path.exists(var.backend['config']):
        config = parse.ConfigParser()
        config.read(var.backend['config'])
        section_errors = []
        for section in config.sections():
            for item in config[section]:
                setting = eval(config[section][item])

                if section == "GENERAL":
                    var.settings[item] = setting
                elif section.lower() in var.bindings: # ignore unknown sections, for example if loading a settings file with axes an old version doesn't have yet
                    if item == "up" or item == "down" or item == "switch" or item == "pedal":
                        var.bindings[section.lower()][item] = setting
                    else:
                        var.settings[section.lower()][item] = setting
                else:
                    if not section in section_errors:
                        section_errors.append(section)
        if not section_errors == [] and not rewrite:
            text = "There are sections in the settings file that are not recognized by this version of the program. The unknown sections have the following names:\n\n"
            for section_error in section_errors:
                text += section_error + "\n"
            text += "\nIf this settings file is used, any settings related to the unrecognized sections listed above will be deleted.\n\nPressing OK will open the app and delete all settings related to the unrecognized sections.\n"
            if startup:
                text += "Pressing Cancel will close the app now if you want to manually backup the settings file before opening this app again.\nProceed?"
            else:
                text += "Pressing Cancel will revert to the last applied settings file.\nProceed?"
            response = ctypes.windll.user32.MessageBoxW(0, text, "I5G Tools  -  Unknown sections in settings file!", 1)
            # if response == 1: # OK pressed, do not intervene with reading and writing settings at this time
            if response == 2:
                if startup == True:
                    sys.exit(0)
                else:
                    rewrite = True # set this for later when config is reread
                    re_read_config(var.settings_old)
                    return # do not go further and overwrite bindings from the old settings file with the new bad settings file
        while not var.status['devices_loaded']:
            sleep(0.1)
        bind_errors = []
        for function in var.bindings:
            if function != "status":
                for control in var.bindings[function]:
                    if var.bindings[function][control]['guid'] != 0:
                        try:
                            dev.device_info[var.bindings[function][control]['guid']]
                        except:
                            var.bindings[function][control] = {"guid": 0, "type": "none", "num": 0}
                            bind_errors.append([str(function), str(control)])
        if not bind_errors == []:
            text = "The following inputs could not be bound because its bound controller could not be found. If the app is used, these will all be unbound.\n\n"
            for binding in bind_errors:
                text += binding[0] + "  " + binding[1] + "\n"
            text += "\n\nPressing OK will open the app and immediately unbind these inputs.\n"
            if startup:
                text += "Pressing Cancel will close the app now if you want to plug in the controller before using the app.\nProceed?"
            else:
                text += "Pressing Cancel will revert to the last applied settings file.\nProceed?"
            response = ctypes.windll.user32.MessageBoxW(0, text, "I5G Tools  -  Bound input device not detected!", 1)
            if response == 1:
                return
            if response == 2:
                if startup == True:
                    sys.exit(0)
                else:
                    re_read_config(var.settings_old)
        if rewrite:
            write_config()
            rewrite = False
    else:
        write_config()
    startup = False

def re_read_config(filename):
    if var.settings_old != var.settings_active and filename != var.settings_active:
        var.settings_old = var.settings_active
    var.settings_active = filename
    print([filename, var.settings_active, var.settings_old])
    var.backend = {
        "config": os.path.expanduser("~") + "\\AppData\\Local\\I5G Tools" + "\\" + filename,
    }
    read_config()

def write_config():
    config = parse.ConfigParser()

    config['GENERAL'] = {}
    for setting in var.settings:
        if isinstance(var.settings[setting], dict):
            config[setting.upper()] = {}
            for subsetting in var.settings[setting]:
                config[setting.upper()][subsetting] = str(var.settings[setting][subsetting])
        else:
            config['GENERAL'][setting] = str(var.settings[setting])

    for bind in var.bindings:
        if bind != "status":
            for subbind in var.bindings[bind]:
                config[bind.upper()][subbind] = str(var.bindings[bind][subbind])

    directory = os.path.split(var.backend['config'])[0]
    if not os.path.exists(directory):
        os.mkdir(directory)

    with open(var.backend['config'], 'w') as file:
        config.write(file)

def get_settings_files():
    directory = os.path.split(var.backend['config'])[0]
    var.settings_list = []
    for name in os.listdir(path = directory):
        if name.endswith(".ini"):
            var.settings_list.append(name)
    return var.settings_list

def is_bind():
    if var.event['type'] == "hat":
        event = {
            "guid": var.event['guid'],
            "type": var.event['type'],
            "num": var.event['num'],
            "dir": var.event['value']
        }
    elif var.event['type'] == "axis":
        event = {
            "guid": var.event['guid'],
            "type": var.event['type'],
            "num": var.event['num'],
            "value": var.event['value']
        }
        if event['value'] > var.settings['high_threshold']:
            event['value'] = var.settings['high_threshold']
        elif event['value'] < var.settings['low_threshold']:
            event['value'] = var.settings['low_threshold']
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
                if event['type'] == "axis" and var.bindings[function][control] != None:
                    #if event['guid'] == var.bindings[function][control]['guid'] and event['num'] == var.bindings[function][control]['num'] and event['value'] == var.bindings[function][control]['value']:
                    if (function == 'bite_point' or function == 'engine_warming') and event['guid'] == var.bindings[function][control]['guid'] and event['num'] == var.bindings[function][control]['num'] and var.bindings[function][control]['type'] == "axis":
                        result.append({ "function": function, 
                                        "control": control,
                                        "value": var.event['value']})
                    elif event == var.bindings[function][control]:
                        result.append({ "function": function,
                                        "control": control})
                elif event['type'] == "hat" and var.bindings[function][control] != None:
                    if var.bindings[function][control]['type'] == "hat" and var.bindings[function][control]['dir'] in event['dir']:
                        result.append({ "function": function,
                                        "control": control})
                elif event == var.bindings[function][control]:
                    result.append({ "function": function,
                                    "control": control})
    print(result)
    return result

def reset_bind_thresh(thresh, value):
    if not (thresh == 'low_threshold' or thresh == 'high_threshold'):
        print("Warning: reset_bind_thresh with arguments: ", thresh, value)
        return
    for function in var.bindings:
        if function != 'status':
            for control in var.bindings[function]:
                if var.bindings[function][control] != None and var.bindings[function][control]['type'] == 'axis' and not ((function == 'bite_point' or function == 'engine_warming') and control == 'pedal'):
                    if (var.bindings[function][control]['value'] == var.settings['high_threshold'] and thresh == 'high_threshold') or (var.bindings[function][control]['value'] == var.settings['low_threshold'] and thresh == 'low_threshold'):
                        var.bindings[function][control]['value'] = value

def start_thread(target):
    thread = threading.Thread(target=target, daemon=True)
    thread.start()