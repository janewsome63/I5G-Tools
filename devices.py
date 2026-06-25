import os

import pygame as p
from string import capwords
import controls as con
import functions as fn
import variables as var
import history
from time import sleep
import keyboard

# devices = []
device_info = {
    "keyboard": {
        "guid": None,
        "name": "Keyboard",
        "index": -1,
        "instance": None,
        "initialized": True,
        "keys": {
            "0": ""
        },
    },
}

def add_device(startup):
    try:
        # device = p.joystick.Joystick(index)
        print("start add_device")
        for i in range(p.joystick.get_count()):
            print(i)
            device = p.joystick.Joystick(i)
            if "vJoy" not in device.get_name():
                guid = device.get_guid()
                index = i
                # devices.append(device)
                device_info[guid] = {
                    "guid": guid,
                    "name": device.get_name(),
                    "index": index,
                    "instance": device.get_instance_id(),
                    "initialized": device.get_init(),
                }
                while len(var.id_table) <= device.get_instance_id():
                    var.id_table.append([-2,-2])
                var.id_table[device.get_instance_id()] = [index, guid]
                if guid not in var.settings['device_axis_thresh']:
                    var.settings['device_axis_thresh'][guid] = {'name': device_info[guid]['name'], 'high_threshold': 0.90, 'low_threshold': 0.10}
                print("id_table is now ", var.id_table)
                if device.get_numbuttons():
                    device_info[guid]['buttons'] = {}
                    for b in range(device.get_numbuttons()):
                        device_info[guid]['buttons'][b] = device.get_button(b)
                if device.get_numaxes():
                    device_info[guid]['axes'] = {}
                    for a in range(device.get_numaxes()):
                        device_info[guid]['axes'][a] = device.get_axis(a)
                if device.get_numhats():
                    device_info[guid]['hats'] = {}
                    for h in range(device.get_numhats()):
                        device_info[guid]['hats'][h] = device.get_hat(h)
                print(device_info[guid])
        if not startup:
            fn.read_profile(var.settings['profile']['current'])
    except Exception as e:
        fn.error_handling(e, "devices.add_device()")

def remove_device(instance):
    try:
        # for i, device in enumerate(devices):
        #     if device.get_instance_id() == instance:
        #         devices.pop(i)
        #         break
        for i, guid in enumerate(device_info):
            if device_info[guid]['instance'] == instance:
                del device_info[guid]
                var.id_table[instance] = [-2, -2]
                print("id_table is now ", var.id_table)
                break
        fn.read_profile(var.settings['profile']['current'])
    except Exception as e:
        fn.error_handling(e, "devices.remove_device()")


def log_event(instance_id, type, num, value):
    try:
        # print(instance_id, type, num, value)
        # print(id_table)
        if instance_id != -1:
            [index, guid] = var.id_table[instance_id]
        else:
            [index, guid] = [-1, "keyboard"]
        # print(index, guid)
        # print(device_info)
        # if index != -1:
        #     guid = p.joystick.Joystick(index).get_guid()
        # else:
        #     guid = "-1"
        if guid in device_info:
            if type == "button":
                if "buttons" in device_info[guid] and num in device_info[guid]['buttons']:
                    device_info[guid]['buttons'][num] = value
            elif type == "axis":
                if guid in device_info and "axes" in device_info[guid] and num in device_info[guid]['axes']:
                    value = round((value + 1) / 2, 3)
                    device_info[guid]['axes'][num] = value
                    history.add(guid,num,value)
            elif type == "hat":
                if guid in device_info and "hats" in device_info[guid] and num in device_info[guid]['hats']:
                    if value[1] == 1:
                        v = "up"
                    elif value[1] == -1:
                        v = "down"
                    else:
                        v = ""

                    if value[0] == 1:
                        h = "right"
                    elif value[0] == -1:
                        h = "left"
                    else:
                        h = ""

                    if v and h:
                        value = v + " " + h
                    elif v:
                        value = v
                    elif h:
                        value = h
                    else:
                        value = "none"
                    device_info[guid]['hats'][num] = value
            elif type == "key":
                # print(guid)
                # print(device_info)
                device_info[guid]['keys'][num] = value
            var.event = {
                "guid": guid,
                "type": type,
                "num": num,
                "value": value,
            }
            print(var.event)
        # else:
            # print("guid in device_info failed: ", guid, device_info)
    except Exception as e:
        fn.error_handling(e, "devices.log_event()")


def device_detection():
    try:
        os.environ["SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS"] = "1"
        p.init()
        p.joystick.init()
        p.display.set_mode((0, 0), flags=p.HIDDEN)
        
        add_device(True)
        
        var.status['devices_loaded'] = True
        var.status['refresh_labels'] = True
        running = True
        p.event.wait(1000)
        p.event.clear()
        while running:
            for e in p.event.get():
                if e.type == p.QUIT:
                    running = False
                if e.type == p.JOYDEVICEADDED:
                    add_device(False)
                    var.status['refresh_labels'] = True
                    var.status['refresh_guid_list'] = True
                elif e.type == p.JOYDEVICEREMOVED:
                    remove_device(e.instance_id)
                    var.status['refresh_labels'] = True
                    var.status['refresh_guid_list'] = True
                if e.type == p.JOYBUTTONDOWN:
                    log_event(e.instance_id, "button", e.button, True)
                    fn.start_thread(con.controls)
                elif e.type == p.JOYBUTTONUP:
                    log_event(e.instance_id, "button", e.button, False)
                elif e.type == p.JOYAXISMOTION:
                    log_event(e.instance_id, "axis", e.axis, e.value)
                    fn.start_thread(con.controls)
                elif e.type == p.JOYHATMOTION:
                    log_event(e.instance_id, "hat", e.hat, e.value)
                    fn.start_thread(con.controls)

            try:
                key = keyboard.get_hotkey_name()
            except AttributeError:
                key = ""

            if not key:
                key = None

            if key != var.status['key_prev']:
                # print("key!: ", key)
                log_event(-1, "key", 0, key)
                fn.start_thread(con.controls)
            var.status['key_prev'] = key
            sleep(0.001)

        p.quit()
    except Exception as e:
        fn.error_handling(e, "devices.device_detection()")

def format_device(function, control):
    try:
        if var.bindings[function][control]:
            if var.bindings[function][control]['type'] == "none":
                dev_pretty = "None"
            elif var.bindings[function][control]['type'] == "hat":
                name = device_info[var.bindings[function][control]['guid']]['name']
                type = capwords(var.bindings[function][control]['type'])
                num = str(var.bindings[function][control]['num'])
                dir = capwords(var.bindings[function][control]['dir'])
                dev_pretty = name + " - " + type + " " + num + " " + dir
            elif var.bindings[function][control]['type'] == "axis":
                name = device_info[var.bindings[function][control]['guid']]['name']
                type = capwords(var.bindings[function][control]['type'])
                num = str(var.bindings[function][control]['num'])
                dev_pretty = name + " - " + type + " " + num
                if control != 'pedal':
                    axis_dir = var.bindings[function][control]['value'] >= var.settings['device_axis_thresh'][var.bindings[function][control]['guid']]['high_threshold']
                    if axis_dir:
                        dev_pretty += "+"
                    else:
                        dev_pretty += "-"
            elif var.bindings[function][control]['type'] == "key":
                name = device_info[var.bindings[function][control]['guid']]['name']
                value = var.bindings[function][control]['value']
                dev_pretty = name + " - " + value.upper()
            else:
                name = device_info[var.bindings[function][control]['guid']]['name']
                type = capwords(var.bindings[function][control]['type'])
                num = str(var.bindings[function][control]['num'])
                dev_pretty = name + " - " + type + " " + num

            var.bindings[function][control]['label'] = dev_pretty

            return var.bindings[function][control]['label']
        else:
            return 'None'
    except Exception as e:
        fn.error_handling(e, "devices.format_device()")