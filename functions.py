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
import datetime
import webbrowser

def read_config():
    print("read_config() start")
    if os.path.exists(var.settings['path'] + "\\" + var.settings['config']):
        config = parse.ConfigParser()
        config.read(var.settings['path'] + "\\" + var.settings['config'])

        ver = check_ver(config, 'config')
        if not ver in var.compatible_settings:
            if ver == "v0.4.Xb": # assume 0.4.10b, only need to inject version number into file, don't need to ask user since config has not changed
                var.settings['version'] = var.lang['settings_version']
                var.status['rewrite']['config'] = True
            # elif ver in var.lang['compatible_versions']: # for the future, if/when the config file has changed between versions
            #     var.status['rewrite']['config'] = True
            elif ver == "v0.5.0b":
                var.settings['version'] = var.lang['settings_version']
                var.status['rewrite']['config'] = True
            elif ver == "v0.5.2b":
                var.settings['version'] = var.lang['settings_version']
                var.status['rewrite']['config'] = True
            else: # if the version isn't valid, then something
                #TODO
                response = ctypes.windll.user32.MessageBoxW(0, "The config file " + var.settings['config'] + " has an unknown version number. The version number in this file must be valid.", "I5G Tools  -  Unknown config file!", 0)
                if response == 1:
                    sys.exit(0)

        errors = []
        for section in config.sections():
            for item in config[section]:
                if item not in var.obsolete:  # Check that variable isn't obsolete
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
        if var.status['first'] == False:
            response = ctypes.windll.user32.MessageBoxW(0, var.lang['not_found']['config']['body'], var.lang['not_found']['config']['title'], 1)
            if response == 1:
                pass
            elif response == 2:
                sys.exit(0)
        write_config()
    read_profile()

def read_profile(profile=None):
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
            if ver == "v0.4.Xb": # either 0.4.4b or 0.4.10b
                if "LOCAL" in config: # assume 0.4.10b, only need to inject version number into file, don't need to ask user since config has not changed
                    var.settings['version'] = var.lang['settings_version']
                    var.status['rewrite']['config'] = True
                elif "GENERAL" in config: # assume 0.4.4b
                    ver = "v0.4.4b"
                    response = ctypes.windll.user32.MessageBoxW(0, "The profile " + profile + ".ini being loaded does not have a self-identifying version. Click OK if you are upgrading from 0.4.4b and only want to use " + var.lang['settings_version'] + " (or newer) going forward.\n\nNote: If you are not upgrading from 0.4.4b, this will also edit your current global config file.", "I5G Tools  -  Profile Translation Needed!", 1)
                    if response == 1:
                        pass
                    elif response == 2:
                        sys.exit(0)
                    var.status['rewrite']['profile'] = True
            # elif ver in var.lang['compatible_versions']: # for the future, if/when the config file has changed between versions
            #     var.status['rewrite']['profile'] = True
            elif ver == "v0.5.0b":
                var.settings['version'] = var.lang['settings_version']
                # var.status['rewrite']['profile'] = True
            elif ver == "v0.5.2b":
                var.settings['version'] = var.lang['settings_version']
            else: # if the version isn't valid, then something
                #TODO
                response = ctypes.windll.user32.MessageBoxW(0, "The profile file " + profile + ".ini has an unknown version number. The version number in this file must be valid.", "I5G Tools  -  Unknown config file!", 0)
                if response == 1:
                    sys.exit(0)

        if var.status['rewrite']['profile'] == True:
            translate(config, 'profile', profile, ver)
            var.status['rewrite']['profile'] = False
            read_profile()
            return

        errors = []
        for section in config.sections():
            for item in config[section]:
                if item not in var.obsolete:  # Check that variable isn't obsolete
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
            text = var.lang['section_errors']['profile']['intro']
            for error in errors:
                text += error + "\n"
            text += var.lang['section_errors']['profile']['outro']
            response = ctypes.windll.user32.MessageBoxW(0, text, var.lang['section_errors']['profile']['title'], 1)
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
                    guid = var.bindings[function][control]['guid']
                    if guid != 0:
                        try:
                            dev.device_info[guid]
                        except KeyError:
                            var.bindings_cache[function][control] = var.bindings[function][control]
                            if var.bindings[function][control]['label']:
                                label = var.bindings[function][control]['label']
                            else:
                                label = "Unknown device"
                            var.bindings[function][control] = {"label": label, "guid": 0, "type": "none", "num": 0}
                            bind_errors.append([str(function), str(control)])

    else:
        if var.status['first'] == False:
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
        write_profile()
    var.status['refresh_labels'] = True
    # print(var.settings)
    print("read_profile() end")
def write_config():
    config = parse.ConfigParser()

    config['GLOBAL'] = {}
    config['GLOBAL']['version'] = var.lang['settings_version']
    for setting in var.settings:
        if setting not in var.obsolete:  # Check that variable isn't obsolete
            if not isinstance(var.settings[setting], dict):
                config['GLOBAL'][setting] = str(var.settings[setting])

    config['SOUND'] = {}
    for setting in var.settings['sound']:
        if setting not in var.obsolete:  # Check that variable isn't obsolete
            config['SOUND'][setting] = str(var.settings['sound'][setting])

    config['PROFILE'] = {}
    for setting in var.settings['profile']:
        if setting not in var.obsolete:  # Check that variable isn't obsolete
            config['PROFILE'][setting] = str(var.settings['profile'][setting])

    if not os.path.exists(var.settings['path']):
        os.mkdir(var.settings['path'])

    with open(var.settings['path'] + "\\"+ "global.ini", 'w') as file:
        # noinspection PyTypeChecker
        config.write(file)
        
def write_profile(profile=None):
    print("write_profile() start")
    if not profile:
        profile = var.settings['profile']['current']

    config = parse.ConfigParser()

    config['LOCAL'] = {}
    #config['LOCAL']['version'] = var.lang['version']
    config['LOCAL']['version'] = var.lang['settings_version']
    for setting in var.settings['local']:
        if setting not in var.obsolete:  # Check that variable isn't obsolete
            config['LOCAL'][setting] = str(var.settings['local'][setting])

    for bind in var.bindings:
        if bind != "status":
            config[bind.upper()] = {}
            if bind in var.settings:
                for subsetting in var.settings[bind]:
                    config[bind.upper()][subsetting] = str(var.settings[bind][subsetting])
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
    print("write_profile() end")
def delete_profile(profile):
    path = var.settings['path'] + "\\" + var.settings['profile']['path'] + "\\" + profile + ".ini"
    if profile in get_profiles():
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

        # Find a less janky way to do this other than repeating the loop from the end
        found = False
        for function in var.bindings:
            if function != "status":
                for control in var.bindings[function]:
                    bind = copy.deepcopy(var.bindings[function][control])
                    if event['guid'] == bind['guid'] and event['num'] == bind['num']:
                        found = True
                        if event['value'] > var.settings[function]['axis_threshold']:
                            event['value'] = var.settings[function]['axis_threshold']
                        elif event['value'] < round(1 - var.settings[function]['axis_threshold'], 2):
                            event['value'] = round(1 - var.settings[function]['axis_threshold'], 2)

        if not found:
            if event['value'] > var.settings['global_threshold']:
                event['value'] = var.settings['global_threshold']
            elif event['value'] < 1 - var.settings['global_threshold']:
                event['value'] = round(1 - var.settings['global_threshold'], 2)
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
                    bind.pop("inverted")
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

def reset_bind_thresh(function, value):
    for control in var.bindings[function]:
        if var.bindings[function][control] is not None and var.bindings[function][control]['type'] == 'axis' and not ((function == 'clutch' or function == 'throttle') and control == 'pedal'):
            if not var.bindings[function][control]['inverted']:
                var.bindings[function][control]['value'] = value
            else:
                var.bindings[function][control]['value'] = round(1 - value, 2)

def start_thread(target):
    thread = threading.Thread(target=target, daemon=True)
    thread.start()

def check_ver(file, type):
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

def translate(file, type, name, ver): # as of right now, this should only ever be called to translate a v0.4.4b config file into a current profile file
    # if type == 'config': # for when future versions change the config file
    if type == 'profile':
        if ver == "v0.4.4b":
            # backup the current profile file if something goes wrong
            now = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
            with open(var.settings['path'] + "\\" + var.settings['profile']['path'] + "\\" + name + ".ini." + ver + now + ".bak", 'w') as newfile:
                file.write(newfile)

            # check for any errors before starting the translation:
            errors = []
            for section in file.sections():
                if not section.lower() in var.bindings and section.lower() != "general" and section.lower() != "bite_point" and section.lower() != "engine_warming":
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

            var.settings['timer_loop'] = file['GENERAL']['timer_loop']
            var.settings['timer_first'] = file['GENERAL']['timer_first']
            # scale and axis samples could go here, but neither actually do anything
            var.status['rewrite']['config'] = True

            for section in file:
                if section == "GENERAL":
                    var.settings['local']['version'] = var.lang['settings_version']
                    # Not sure how this should be handled since the removal of these variables
                    # var.settings['local']['high_threshold'] = float(file[section]['high_threshold'])
                    # var.settings['local']['low_threshold'] = float(file[section]['low_threshold'])
                    var.status['rewrite']['config'] = True
                else:
                    if section == "BITE_POINT":
                        section_name = "clutch"
                    elif section == "ENGINE_WARMING":
                        section_name = "throttle"
                    else:
                        section_name = section.lower()
                    if not section in errors: # Skip all identified section errors that were OK'd
                        for item in file[section]:
                            if item == "up" or item == "down" or item == "switch" or item == "pedal":
                                bind = eval(file[section][item])
                                guid = bind['guid']
                                if guid == 0:
                                    var.bindings[section_name][item] = {"label": 'None', "guid": 0, "type": 'none', "num": 'none'}
                                else:
                                    label = 'Unknown device'
                                    type = bind['type']
                                    num = bind['num']
                                    if item != "pedal" and type == 'axis':
                                        var.bindings[section_name][item] = {"label": label, "guid": guid, "type": type, "num": num, "value": float(bind['value'])}
                                    elif item == "pedal":
                                        var.bindings[section_name][item] = {"label": label, "guid": guid, "type": type, "num": num, "input": True}
                                    elif type == 'hat':
                                        var.bindings[section_name][item] = {"label": label, "guid": guid, "type": type, "num": num, "dir": bind['dir']}
                                    else:
                                        var.bindings[section_name][item] = {"label": label, "guid": guid, "type": type, "num": num}
                            else:
                                var.settings[section_name][item] = file[section][item]
                            
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
        write_profile()
        var.status['rewrite']['profile'] = False

def open_browser(link):
    webbrowser.open(link)

def error_handling(e):
    now = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
    with open("I5G_Tools_err_" + now + ".log", "w") as f:
        f.write(now + "\n") 
        f.write(f"Error occurred: {str(e)}\n")