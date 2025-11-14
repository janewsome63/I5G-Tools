import configparser as parse
import os.path
import threading
from os import write
from string import capwords
from turtle import config_dict
from ast import literal_eval as eval

import devices as dev
import variables as var
from time import sleep

def read_config():
    if os.path.exists(var.backend['config']):
        config = parse.ConfigParser()
        config.read(var.backend['config'])
        for section in config.sections():
            for item in config[section]:
                setting = eval(config[section][item])

                if section == "GENERAL":
                    var.settings[item] = setting
                elif item == "up" or item == "down" or item == "switch" or item == "pedal":
                    var.bindings[section.lower()][item] = setting
                else:
                    var.settings[section.lower()][item] = setting
        while not var.status['devices_loaded']:
            sleep(0.1)
        for function in var.bindings:
            if function != "status":
                for control in var.bindings[function]:
                    if var.bindings[function][control]['guid'] != 0:
                        try:
                            dev.device_info[var.bindings[function][control]['guid']]
                        except:
                            var.bindings[function][control]['guid'] = 0
                            var.bindings[function][control]['type'] = "none"
                            var.bindings[function][control]['num'] = 0
    else:
        write_config()

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
    result = None

    for function in var.bindings:
        if function != "status":
            for control in var.bindings[function]:
                if event['type'] == "axis" and var.bindings[function][control] != None:
                    #if event['guid'] == var.bindings[function][control]['guid'] and event['num'] == var.bindings[function][control]['num'] and event['value'] == var.bindings[function][control]['value']:
                    if function == 'bite_point' and event['guid'] == var.bindings[function][control]['guid'] and event['num'] == var.bindings[function][control]['num']:
                        if result == None:
                            result = [{
                                "function": function,
                                "control": control,
                                "value": var.event['value']
                            }]
                        else:
                            result.append({
                                "function": function,
                                "control": control,
                                "value": var.event['value']
                            })
                    elif event == var.bindings[function][control]:
                        if result == None:
                            result = [{
                                "function": function,
                                "control": control,
                            }]
                        else:
                            result.append({
                                "function": function,
                                "control": control,
                            })
                elif event['type'] == "hat" and var.bindings[function][control] != None:
                    if var.bindings[function][control]['type'] == "hat" and var.bindings[function][control]['dir'] in event['dir']:
                        if result == None:
                            result = [{
                                "function": function,
                                "control": control,
                            }]
                        else:
                            result.append({
                                "function": function,
                                "control": control,
                            })
                elif event == var.bindings[function][control]:
                    if result == None:
                        result = [{
                            "function": function,
                            "control": control,
                            }]
                    else:
                        result.append({
                            "function": function,
                            "control": control,
                        })
    print(result)
    return result

def reset_bind_thresh(thresh, value):
    if not (thresh == 'low_threshold' or thresh == 'high_threshold'):
        print("Warning: reset_bind_thresh with arguments: ", thresh, value)
        return
    for function in var.bindings:
        if function != 'status':
            for control in var.bindings[function]:
                if var.bindings[function][control] != None and var.bindings[function][control]['type'] == 'axis' and not (function == 'bite_point' and control == 'pedal'):
                    if (var.bindings[function][control]['value'] == var.settings['high_threshold'] and thresh == 'high_threshold') or (var.bindings[function][control]['value'] == var.settings['low_threshold'] and thresh == 'low_threshold'):
                        var.bindings[function][control]['value'] = value

def start_thread(target):
    thread = threading.Thread(target=target, daemon=True)
    thread.start()