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

def read_config():
    try:
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
                    try:
                        setting = eval(config[section][item])
                    except (SyntaxError, ValueError):
                        setting = config[section][item]

                    if section == "GLOBAL":
                        if not (item == "high_threshold" or item == "low_threshold"): # to make up for a mistake in all 0.6.Xb versions
                            if item == "vjoy_rid":
                                print('item is vjoy_rid in read_config(): ' + str(setting))
                                if int(setting) < 1 or int(setting) > 16:
                                    var.settings[item] = int(1) # temp fix, improve this later, pop up a warning or something
                                else:
                                    var.settings[item] = int(setting)
                            else:
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

            if var.status['rewrite']['profile']:
                translate(config, 'profile', profile, ver)
                var.status['rewrite']['profile'] = False
                read_profile()
                return

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
                    if var.bindings[bind][subbind]['label'] != "None" and var.bindings[bind][subbind]['guid'] == 0:
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
    except Exception as e:
        error_handling(e, "functions.is_bind()")

def reset_bind_thresh(thresh, value):
    try:
        if not (thresh == 'low_threshold' or thresh == 'high_threshold'):
            print("Warning: reset_bind_thresh with arguments: ", thresh, value)
            return
        for function in var.bindings:
            if function != 'status':
                for control in var.bindings[function]:
                    if var.bindings[function][control] is not None and var.bindings[function][control]['type'] == 'axis' and not ((function == 'clutch' or function == 'throttle') and control == 'pedal'):
                        guid = var.bindings[function][control]['guid']
                        if (var.bindings[function][control]['value'] == var.settings['device_axis_thresh'][str(guid)]['high_threshold'] and thresh == 'high_threshold') or (var.bindings[function][control]['value'] == var.settings['device_axis_thresh'][str(guid)]['low_threshold'] and thresh == 'low_threshold'):
                            var.bindings[function][control]['value'] = value
                        elif (var.bindings[function][control]['label'][-1] == "+" and thresh == 'high_threshold') or (var.bindings[function][control]['label'][-1] == "-" and thresh == 'low_threshold'):
                            var.bindings[function][control]['value'] = value
                            print("using backup method in fn.reset_bind_thresh()")
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

def translate(file, type, name, ver): # as of right now, this should only ever be called to translate a v0.4.4b config file into a current profile file
    try:
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
                        var.settings['local']['high_threshold'] = float(file[section]['high_threshold'])
                        var.settings['local']['low_threshold'] = float(file[section]['low_threshold'])
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
            var.status['rewrite_profile'] = True
            var.status['rewrite']['profile'] = False
    except Exception as e:
        error_handling(e, "functions.translate()")

def open_browser(link):
    try:
        webbrowser.open(link)
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