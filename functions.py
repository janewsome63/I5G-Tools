import configparser as parse
import copy
import os.path
import threading
import traceback
from ast import literal_eval as eval
import ctypes
import sys

import devices as dev
import variables as var
from time import sleep
import datetime
import webbrowser
import car_settings_list
import csv

def read_config():
    try:
        print("read_config() start")
        if os.path.exists(var.settings['path'] + "\\" + var.settings['config']):
            config = parse.ConfigParser()
            config.read(var.settings['path'] + "\\" + var.settings['config'])

            ver = check_ver(config, 'config')
            if not ver in var.compatible_settings:
                if ver in var.single_input_settings: # need to update how input settings are stored, no changes to config actually needed
                    var.settings['version'] = var.lang['settings_version']
                else: # if the version isn't valid, then something
                    #TODO
                    response = ctypes.windll.user32.MessageBoxW(0, "The config file " + var.settings['config'] + " has an unknown version number. The version number in this file must be valid.", "I5G Tools  -  Unknown config file!", 0)
                    if response == 1:
                        sys.exit(0)

            errors = []
            for section in config.sections():
                for item in config[section]:
                    try:
                        setting = eval(config[section][item])
                    except (SyntaxError, ValueError):
                        setting = config[section][item]

                    if section == "GLOBAL":
                        if not (item == "high_threshold" or item == "low_threshold"): # to make up for a mistake in all 0.6.Xb versions
                            if item == "vjoy_rid":
                                print('item is vjoy_rid in read_config(): ' + str(setting))
                                if (int(setting) < 1 or int(setting) > 16) and not int(setting) == -1:
                                    var.settings[item] = int(1) # temp fix, improve this later, pop up a warning or something
                                else:
                                    var.settings[item] = int(setting)
                            else:
                                var.settings[item] = setting
                    elif section == "SOUND":
                        var.settings['sound'][item] = setting
                    elif section == "PROFILE":
                        if item == "current":
                            var.settings['profile'][item] = str(setting)
                        else:
                            var.settings['profile'][item] = setting
                    else:
                        if not section in errors:
                            errors.append(section)

            if errors: # and not var.status['rewrite']['config']:
                text = var.lang['section_errors']['config']['intro']
                for error in errors:
                    text += error + "\n"
                text += var.lang['section_errors']['config']['outro']
                response = ctypes.windll.user32.MessageBoxW(0, text, var.lang['section_errors']['config']['title'], 1)
                if response == 1:
                    pass
                elif response == 2:
                    sys.exit(0)
            if var.status['rewrite']['config']:
                write_config()
                var.status['rewrite']['config'] = False
        else:
            if not var.status['first']:
                response = ctypes.windll.user32.MessageBoxW(0, var.lang['not_found']['config']['body'], var.lang['not_found']['config']['title'], 1)
                if response == 1:
                    pass
                elif response == 2:
                    sys.exit(0)
            write_config()
        read_profile()
    except Exception as e:
        error_handling(e, "functions.read_config()")

def read_profile(profile=None):
    try:
        print("read_profile() start")
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

            ver = check_ver(config, 'profile')
            if not ver in var.compatible_settings:
                if ver in var.single_input_settings: # just need to update the structure of how binds are stored
                    var.status['rewrite']['profile'] = True
                    translate(config, 'profile', profile, ver)
                    read_profile()
                    return
                else: # if the version isn't valid, then something
                    #TODO
                    response = ctypes.windll.user32.MessageBoxW(0, "The profile file " + profile + ".ini has an unknown version number. The version number in this file must be valid.", "I5G Tools  -  Unknown config file!", 0)
                    if response == 1:
                        sys.exit(0)
                        
            copy_from_profile(config)
            interpret_profile()

        else:
            if not var.status['first']:
                text = var.lang['not_found']['profile']['intro'] + profile + var.lang['not_found']['profile']['outro']
                response = ctypes.windll.user32.MessageBoxW(0, text, var.lang['not_found']['profile']['title'], 1)
                if response == 1:
                    var.settings['profile']['current'] = 'Default'
                    var.status['first'] = True
                    read_profile()
                    var.status['first'] = False
                    return
                elif response == 2:
                    sys.exit(0)
            var.settings['profile']['current'] = 'Default'
            var.status['rewrite_profile'] = True
        var.status['refresh_labels'] = True
        # print(var.settings)
        print("read_profile() end")
    except Exception as e:
        error_handling(e, "functions.read_profile()")

def copy_from_profile(config): # copy data out of profile and store it in var.settings and var.settings
    try:
        errors = []
        for section in config.sections():
            for item in config[section]:
                if section == 'LOCAL':
                    if item == 'version':
                        print (item, var.lang['settings_version'])
                    else:
                        print(item, eval(config[section][item]))
                if item == 'version':
                    # setting = config[section][item]
                    setting = var.lang['settings_version']
                else:
                    setting = eval(config[section][item])
                if section == "LOCAL":
                    if item not in var.obsolete:
                        var.settings['local'][item] = setting
                elif section.lower() in var.bindings:
                    if item in var.bindings_info['types']:
                        var.bindings[section.lower()][item] = setting
                    else:
                        var.settings[section.lower()][item] = setting
                elif section == "DEVICE_AXIS_THRESH":
                    var.settings['device_axis_thresh'][item] = setting
                else:
                    if not section in errors:
                        errors.append(section)

        if errors:
            text = var.lang['section_errors']['profile']['intro']
            for error in errors:
                text += error + "\n"
            text += var.lang['section_errors']['profile']['outro']
            response = ctypes.windll.user32.MessageBoxW(0, text, var.lang['section_errors']['profile']['title'], 1)
            if response == 1:
                pass
            elif response == 2:
                sys.exit(0)

    except Exception as e:
        error_handling(e, "functions.copy_from_profile()")

def interpret_profile():
    try:
        while not var.status['devices_loaded']:
            sleep(0.1)
            bind_errors = []
            for function in var.bindings:
                if function != "status":
                    for control in var.bindings[function]:
                        guid = var.bindings[function][control][0]['guid']
                        if guid != 0:
                            try:
                                dev.device_info[guid]
                            except KeyError:
                                var.bindings_cache[function][control] = var.bindings[function][control]
                                if var.bindings[function][control][0]['label']:
                                    label = var.bindings[function][control][0]['label']
                                else:
                                    label = "Unknown device"
                                var.bindings[function][control] = [{"label": label, "guid": 0, "type": "none", "num": 0}]
                                bind_errors.append([str(function), str(control)])
            
            for guid in var.settings['device_axis_thresh']:
                for function in var.bindings:
                    if function != 'status' and function != 'hybrid':
                        for control in var.bindings[function]:
                            bind = var.bindings[function][control]
                            for i in range(0,len(bind)):
                                if bind[i]['guid'] == guid and bind[i]['type'] == 'axis' and not 'input' in bind[i]:
                                    if bind[i]['label'][-1] == '+':
                                        if bind[i]['value'] != var.settings['device_axis_thresh'][guid]['high_threshold']:
                                            print("Warning, overriding high bind value for " + str(function) + " " + str(control) + " in fn.interpret_profile()")
                                            var.bindings[function][control][i]['value'] = var.settings['device_axis_thresh'][guid]['high_threshold']
                                    elif bind[i]['label'][-1] == '-':
                                        if bind[i]['value'] != var.settings['device_axis_thresh'][guid]['low_threshold']:
                                            print("Warning, overriding low bind value for " + str(function) + " " + str(control) + " in fn.interpret_profile()")
                                            var.bindings[function][control][i]['value'] = var.settings['device_axis_thresh'][guid]['low_threshold']
                                    else:
                                        print("Warning, unknown axis label for " + str(bind[i]['label']) + " in fn.interpret_profile()")
        update_subbind_list()
    except Exception as e:
        error_handling(e, "functions.interpret_profile()")

def write_config():
    try:
        print("write_config() start")
        config = parse.ConfigParser()

        config['GLOBAL'] = {}
        config['GLOBAL']['version'] = var.lang['settings_version']
        for setting in var.settings:
            if not isinstance(var.settings[setting], dict) and setting != 'version':
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
        print("write_config() end")
    except Exception as e:
        error_handling(e, "functions.write_config()")
        
def write_profile(profile=None):
    try:
        print("write_profile() start")
        if not profile:
            profile = var.settings['profile']['current']

        config = parse.ConfigParser()

        config['LOCAL'] = {}
        #config['LOCAL']['version'] = var.lang['version']
        config['LOCAL']['version'] = var.lang['settings_version']
        for setting in var.settings['local']:
            config['LOCAL'][setting] = str(var.settings['local'][setting])

        for bind in var.bindings:
            if bind != "status":
                config[bind.upper()] = {}
                if bind in var.settings:
                    for subsetting in var.settings[bind]:
                        config[bind.upper()][subsetting] = str(var.settings[bind][subsetting])
                for subbind in var.bindings[bind]:
                    if var.bindings[bind][subbind][0]['label'] != "None" and var.bindings[bind][subbind][0]['guid'] == 0:
                        config[bind.upper()][subbind] = str(var.bindings_cache[bind][subbind])
                    else:
                        config[bind.upper()][subbind] = str(var.bindings[bind][subbind])
        config['DEVICE_AXIS_THRESH'] = {}
        for guid in var.settings['device_axis_thresh']:
            if guid != "-2":
                config['DEVICE_AXIS_THRESH'][guid] = str(var.settings['device_axis_thresh'][guid])

        if not os.path.exists(var.settings['path'] + "\\" + var.settings['profile']['path']):
            os.mkdir(var.settings['path'] + "\\" + var.settings['profile']['path'])

        with open(var.settings['path'] + "\\" + var.settings['profile']['path'] + "\\" + profile + ".ini", 'w') as file:
            # noinspection PyTypeChecker
            config.write(file)
        print("write_profile() end")
    except Exception as e:
        error_handling(e, "functions.write_profile()")

def delete_profile(profile):
    try:
        path = var.settings['path'] + "\\" + var.settings['profile']['path'] + "\\" + profile + ".ini"
        if profile in get_profiles():
            if os.path.exists(path):
                os.remove(path)
    except Exception as e:
        error_handling(e, "functions.delete_profile()")

def get_profiles():
    try:
        directory = var.settings['path'] + "\\" + var.settings['profile']['path']
        var.status['profile_list'] = []
        for name in os.listdir(path = directory):
            if name.endswith(".ini"):
                var.status['profile_list'].append(name.split('.', 1)[0])
        return var.status['profile_list']
    except Exception as e:
        error_handling(e, "functions.get_profiles()")

def get_sound_files():
    try:
        directory = var.settings['path'] + "\\" + 'sfx'
        var.status['sound_files_list'] = []
        for name in os.listdir(path = directory):
            if name.endswith(".mp3") or name.endswith(".wav") or name.endswith(".ogg"):
                var.status['sound_files_list'].append(name)#.split('.', 1)[0])
        return var.status['sound_files_list']
    except Exception as e:
        error_handling(e, "functions.get_profiles()")

def is_bind():
    try:
        if var.event['type'] == "axis":
            event = {
                "guid": var.event['guid'],
                "type": var.event['type'],
                "num": var.event['num'],
                "value": var.event['value']
            }
            if event['value'] > var.settings['device_axis_thresh'][str(event['guid'])]['high_threshold']:
                event['value'] = var.settings['device_axis_thresh'][str(event['guid'])]['high_threshold']
            elif event['value'] < var.settings['device_axis_thresh'][str(event['guid'])]['low_threshold']:
                event['value'] = var.settings['device_axis_thresh'][str(event['guid'])]['low_threshold']
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
                    for i in range(0,len(var.bindings[function][control])):
                        bind = copy.deepcopy(var.bindings[function][control][i])
                        try:
                            bind.pop("label")
                        except KeyError:
                            pass
                        if "input" in bind:
                            if event['guid'] == bind['guid'] and event['num'] == bind['num'] and bind['type'] == "axis":
                                result.append({"function": function, "control": control, "value": var.event['value']})
                        elif event['type'] == 'key' and bind['type'] == 'key':
                            if not {"function": function, "control": control} in result and event['guid'] == bind['guid'] and event['num'] == bind['num'] and event['value']:
                                single_keys = event['value'].split('+')
                                valid = False
                                for single_key in single_keys:
                                    if single_key == bind['value']:
                                        valid = True
                                if valid:
                                    result.append({"function": function, "control": control})
                        elif event == bind:
                            result.append({"function": function, "control": control})
        if not result:
            result = False
        return result
    except Exception as e:
        error_handling(e, "functions.is_bind()")

def sort_input_array(data):
    try:
        # print("starting sort_input_array()")
        output = sorted(data, key=lambda d: [d.get('guid', '-1'), d.get('type', chr(0)), d.get('num', chr(0)), d.get('value', chr(0)), d.get('dir', [chr(0),chr(0)])])
        print("sorted: " + str(output))
        return output
    except Exception as e:
        error_handling(e, "functions.sort_input_array()")

def update_subbind_list():
    try:
        print("starting fn.update_subbind_list()")
        for function in var.bindings:
            if function != 'status':
                for control in var.bindings[function]:
                    var.bindings_subbind[function][control] = [{
                        'function': None,
                        'control': None,
                    }]
                    if var.bindings[function][control][0]['label'] != "None":
                        for function2 in var.bindings:
                            if function2 != 'status':
                                for control2 in var.bindings[function2]:
                                    if not (function == function2 and control == control2):
                                        subbind = True # stores if control function is a subbind of control2 function2
                                        if var.bindings[function][control] == var.bindings[function2][control2]: # if a bind is used multiple times, don't let them block each other
                                            subbind = False
                                        else:
                                            for bind in var.bindings[function][control]:
                                                if not bind in var.bindings[function2][control2]:
                                                    subbind = False
                                            if subbind:
                                                if var.bindings_subbind[function][control][0] == {'function': None, 'control': None}:
                                                    var.bindings_subbind[function][control][0] = {'function': function2, 'control': control2}
                                                else:
                                                    var.bindings_subbind[function][control].append({'function': function2, 'control': control2})

        print("new subbind list:")
        for function in var.bindings_subbind:
            if function != 'status':
                for control in var.bindings_subbind[function]:
                    print(function, control, ":", var.bindings_subbind[function][control])
    except Exception as e:
        error_handling(e, "functions.update_subbind_list()")

def reset_bind_thresh(guid, thresh, value):
    try:
        if not (thresh == 'low_threshold' or thresh == 'high_threshold'):
            print("Warning: reset_bind_thresh with arguments: ", thresh, value)
            return
        for function in var.bindings:
            if function != 'status':
                for control in var.bindings[function]:
                    if var.bindings[function][control] is not None and not ((function == 'clutch' or function == 'throttle') and control == 'pedal'):
                        for i in range(0,len(var.bindings[function][control])):
                            if var.bindings[function][control][i]['type'] == 'axis':
                                if guid == var.bindings[function][control][i]['guid']:
                                    if (var.bindings[function][control][i]['value'] == var.settings['device_axis_thresh'][str(guid)]['high_threshold'] and thresh == 'high_threshold') or (var.bindings[function][control][i]['value'] == var.settings['device_axis_thresh'][str(guid)]['low_threshold'] and thresh == 'low_threshold'):
                                        var.bindings[function][control][i]['value'] = value

    except Exception as e:
        error_handling(e, "functions.reset_bind_thresh()")

def start_thread(target):
    try:
        thread = threading.Thread(target=target, daemon=True)
        thread.start()
    except Exception as e:
        error_handling(e, "functions.start_thread()")

def check_ver(file, type):
    try:
        if type == 'config':
            if 'GLOBAL' not in file or 'version' not in file['GLOBAL']:
                return "v0.4.Xb"
            return file['GLOBAL']['version']
        elif type == 'profile':
            if 'LOCAL' not in file or 'version' not in file['LOCAL']:
                return "v0.4.Xb"
            if file['LOCAL']['version'] in var.compatible_settings:
                return var.lang['version']
            return file['LOCAL']['version']
        # else:
        #     sys.exit(0)
    except Exception as e:
        error_handling(e, "functions.check_ver()")

def translate(file, type, name, ver):
    try:
        print('fn_translate() start')
        # if type == 'config': # for when future versions change the config file
        if type == 'profile':
            # backup the current profile file if something goes wrong
            now = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
            with open(var.settings['path'] + "\\" + var.settings['profile']['path'] + "\\" + name + ".ini." + ver + now + ".bak", 'w') as newfile:
                file.write(newfile)
            if ver in var.single_input_settings: # convert binds to a single dict to an array of a single dict, except for pedal inputs
                print('Converting from single input to chorded input')
                copy_from_profile(file)
                for function in var.bindings:
                    if function != "status":
                        for control in var.bindings[function]:
                            copy = var.bindings[function][control]
                            var.bindings[function][control] = [None]
                            var.bindings[function][control][0] = copy
                            # print('copying single input: ' + str(copy) + " to: " + str(var.bindings[function][control]))
                interpret_profile()
                
                var.status['rewrite']['profile'] = True
            # elif ver in var.lang['compatible_versions']:
            #     var.settings['local']['version'] = var.lang['settings_version']
            #     var.status['rewrite']['config'] = True
            else:
                response = ctypes.windll.user32.MessageBoxW(0, "Oops! Something went wrong in fn.translate(). Error Code 1. Program closing", "I5G Tools  -  Translate Error 1!", 0)
                if response == 1:
                    sys.exit(0)
                sys.exit(0)

            # else: # for when future versions change things
        else:
            response = ctypes.windll.user32.MessageBoxW(0, "Oops! Something went wrong in fn.translate(). Error Code 2. Program closing", "I5G Tools  -  Translate Error 2!", 0)
            if response == 1:
                sys.exit(0)
            sys.exit(0)

        if var.status['rewrite']['config']:
            write_config()
            var.status['rewrite']['config'] = False

        if var.status['rewrite']['profile']:
            var.status['rewrite_profile'] = True
            var.status['rewrite']['profile'] = False
            write_profile()
    except Exception as e:
        error_handling(e, "functions.translate()")

def read_car_settings():
    try:
        print("starting read_car_settings()")
        if os.path.exists(var.settings['path'] + "\\" + var.settings['car_settings']):
            print("car settings file found")
            with open(var.settings['path'] + "\\" + var.settings['car_settings'], mode='r', newline='', encoding='utf-8') as file:
                settings = csv.reader(file)
                header = True
                for row in settings:
                    if not header and row[0] != "":
                        carid = int(row[0])
                        name = str(row[1])
                        hybrid = row[2]
                        weight_jacker_low = row[3]
                        weight_jacker_high = row[4]
                        front_roll_bar_low = row[5]
                        front_roll_bar_high = row[6]
                        rear_roll_bar_low = row[7]
                        rear_roll_bar_high = row[8]
                        fuel_map_low = row[9]
                        fuel_map_high = row[10]
                        if name != "":
                            car_settings_list.car_settings[carid]['name'] = str(name)
                        if hybrid != "":
                            car_settings_list.car_settings[carid]['hybrid'] = bool(hybrid)
                        if weight_jacker_low != "" and weight_jacker_high != "":
                            car_settings_list.car_settings[carid]['weight_jacker'] = [int(weight_jacker_low), int(weight_jacker_high)]
                        if front_roll_bar_low != "" and front_roll_bar_high != "":
                            car_settings_list.car_settings[carid]['front_roll_bar'] = [int(front_roll_bar_low), int(front_roll_bar_high)]
                        if rear_roll_bar_low != "" and rear_roll_bar_high != "":
                            car_settings_list.car_settings[carid]['rear_roll_bar'] = [int(rear_roll_bar_low), int(rear_roll_bar_high)]
                        if fuel_map_low != "" and fuel_map_high != "":
                            car_settings_list.car_settings[carid]['fuel_map'] = [int(fuel_map_low), int(fuel_map_high)]
                    else:
                        header = False
            print("done in read_car_settings()")
        else:
            print("car settings file not found")
            write_car_settings(var.settings['car_settings'])
    except Exception as e:
        error_handling(e, "functions.read_car_settings()")

def write_car_settings(filename):
    try:
        print("start write_car_settings()")
        header = ['CarID', 'name', 'hybrid', 'WJ low', 'WJ high', 'FARB low', 'FARB high', 'RARB low', 'RARB high', 'Map low', 'Map high']
        list = car_settings_list.car_settings
        data = [[0 for _ in range(11)] for _ in range(len(list))]
        i = 0
        for carid in list:
            data[i][0] = carid
            if 'name' in list[carid]:
                data[i][1] = list[carid]['name']
            else:
                data[i][1] = ""
            if 'hybrid' in list[carid]:
                data[i][2] = list[carid]['hybrid']
            else:
                data[i][2] = ""
            if 'weight_jacker' in list[carid]:
                data[i][3] = list[carid]['weight_jacker'][0]
                data[i][4] = list[carid]['weight_jacker'][1]
            else:
                data[i][3] = ""
                data[i][4] = ""
            if 'front_roll_bar' in list[carid]:
                data[i][5] = list[carid]['front_roll_bar'][0]
                data[i][6] = list[carid]['front_roll_bar'][1]
            else:
                data[i][5] = ""
                data[i][6] = ""
            if 'rear_roll_bar' in list[carid]:
                data[i][7] = list[carid]['rear_roll_bar'][0]
                data[i][8] = list[carid]['rear_roll_bar'][1]
            else:
                data[i][7] = ""
                data[i][8] = ""
            if 'fuel_map' in list[carid]:
                data[i][9] = list[carid]['fuel_map'][0]
                data[i][10] = list[carid]['fuel_map'][1]
            else:
                data[i][9] = ""
                data[i][10] = ""
            i += 1
        with open(var.settings['path'] + "\\" + filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(data)
        print("Finished write_car_settings()")
    except Exception as e:
        error_handling(e, "functions.write_car_settings()")

def open_browser(link):
    try:
        webbrowser.open(link)
    except Exception as e:
        error_handling(e, "functions.open_browser()")

def open_path(path):
    try:
        os.startfile(path)
    except Exception as e:
        error_handling(e, "functions.open_browser()")

def check_audio_setting(sound): # returns true if the settings for this sound are on, returns false if settings for this sound are off
    if not var.settings['local']['audio']:
        return False
    elif sound == 'hybrid_low':
        return var.settings['local']['hybrid_low_audio']
    elif sound == 'hybrid_high':
        return var.settings['local']['hybrid_high_audio']
    elif sound == 'hybrid_limit':
        return var.settings['local']['hybrid_limit_audio']
    elif sound == 'upshift_beep':
        return var.settings['local']['upshift_beep']
    elif sound == 'downshift_beep':
        return var.settings['local']['downshift_beep']
    elif sound == 'p2p_active':
        return var.settings['local']['p2p_behind_audio'] or var.settings['local']['p2p_behind_audio_cont']
    else:
        print("something went wrong in fn.check_aduio_setting", sound)

def error_handling(e, loc):
    error = traceback.format_exc()
    print("!!! An error has occured !!! :(")
    print(str(type(e)) + " " + loc)
    print(error)
    now_pretty = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    if var.backend['startup_time'] == None:
        startup_time()
    sleep(0.001) # stupid hack to prevent the app from having time to write a log file when the user closes the app
    with open("I5G_Tools_err_" + var.backend['startup_time'] + ".log", "a") as f:
        f.write(now_pretty + "\n")
        f.write(error)
        #f.write(f"{type(e)}: {str(e.args)}, {str(e)}\n" + loc + "\n\n")
    # sys.exit(0) # exit program to make it obvious an error occured. Otherwise, the app could continue partially functioning with only part of it in a broken state

def startup_time():
    var.backend['startup_time'] = str(datetime.datetime.today().strftime('%Y-%m-%d_%H-%M-%S'))