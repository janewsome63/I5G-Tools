import os

import pygame as p
from string import capwords
import controls as con
import functions as fn
import variables as var
import history
from time import sleep
import keyboard

devices = []
device_info = {
    "-1": {
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

def add_device(index, startup):
    device = p.joystick.Joystick(index)
    if "vJoy" not in device.get_name():
        guid = device.get_guid()
        devices.append(device)
        device_info[guid] = {
            "guid": guid,
            "name": device.get_name(),
            "index": index,
            "instance": device.get_instance_id(),
            "initialized": device.get_init(),
        }
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

def remove_device(instance):
    for i, device in enumerate(devices):
        if device.get_instance_id() == instance:
            devices.pop(i)
            break
    for i, guid in enumerate(device_info):
        if device_info[guid]['instance'] == instance:
            del device_info[guid]
            break
    fn.read_profile(var.settings['profile']['current'])


def log_event(index, type, num, value):
    if index != -1:
        guid = p.joystick.Joystick(index).get_guid()
    else:
        guid = "-1"
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
            device_info[guid]['keys'][num] = value
        var.event = {
            "guid": guid,
            "type": type,
            "num": num,
            "value": value,
        }
        # print(var.event)


def device_detection():
    os.environ["SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS"] = "1"
    p.init()
    p.joystick.init()
    p.display.set_mode((0, 0), flags=p.HIDDEN)

    for i in range(p.joystick.get_count()):
        add_device(i, True)
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
                add_device(e.device_index, False)
                var.status['refresh_labels'] = True
            elif e.type == p.JOYDEVICEREMOVED:
                remove_device(e.instance_id)
                var.status['refresh_labels'] = True
            if e.type == p.JOYBUTTONDOWN:
                log_event(e.joy, "button", e.button, True)
                fn.start_thread(con.controls)
            elif e.type == p.JOYBUTTONUP:
                log_event(e.joy, "button", e.button, False)
            elif e.type == p.JOYAXISMOTION:
                log_event(e.joy, "axis", e.axis, e.value)
                fn.start_thread(con.controls)
            elif e.type == p.JOYHATMOTION:
                log_event(e.joy, "hat", e.hat, e.value)
                fn.start_thread(con.controls)

        try:
            key = keyboard.get_hotkey_name()
        except AttributeError:
            key = ""

        if not key:
            key = None

        if key != var.status['key_prev']:
            log_event(-1, "key", 0, key)
            fn.start_thread(con.controls)
        var.status['key_prev'] = key
        sleep(0.001)

    p.quit()

def format_device(function, control):
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
                axis_dir = var.bindings[function][control]['value'] >= var.settings['local']['high_threshold']
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