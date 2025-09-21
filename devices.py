import variables as var
import vjoy

import pygame as p
import os

devices = []
device_info = {}

def add_device(index):
    device = p.joystick.Joystick(index)
    if "vJoy" not in device.get_name():
        instance = device.get_instance_id()
        devices.append(device)
        device_info[instance] = {
            "name": device.get_name(),
            "guid": device.get_guid(),
            "index": index,
            "instance": instance,
            "initialized": device.get_init(),
        }
    # if device.get_numbuttons():
    #     device_info[instance]['buttons'] = {}
    #     for i in range(device.get_numbuttons()):
    #         device_info[instance]['buttons'][i] = device.get_button(i)
    # if device.get_numaxes():
    #     device_info[instance]['axes'] = {}
    #     for i in range(device.get_numaxes()):
    #         device_info[instance]['axes'][i] = device.get_axis(i)
    # if device.get_numhats():
    #     device_info[instance]['hats'] = {}
    #     for i in range(device.get_numhats()):
    #         device_info[instance]['hats'][i] = device.get_hat(i)
    # if device.get_numballs():
    #     device_info[instance]['balls'] = {}
    #     for i in range(device.get_numhats()):
    #         device_info[instance]['balls'][i] = device.get_ball(i)
    # print(device_info[instance])


def remove_device(instance):
    for i, device in enumerate(devices):
        if device.get_instance_id() == instance:
            # print(f"Joystick Removed: {device.get_name()} (ID: {instance})")
            devices.pop(i)
            break
    del device_info[instance]

def publish_event(id, type, input, value):
    var.current_event = {
        "name": device_info[id]['name'],
        "guid": device_info[id]['guid'],
        "index": device_info[id]['index'],
        "instance": device_info[id]['instance'],
        "initialized": device_info[id]['initialized'],
        "event": {
            "type": type,
            "input": input,
            "value": value,
        },
    }
    print(var.current_event)

def device_detection():
    os.environ["SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS"] = "1"
    p.init()

    p.joystick.init()

    #screen = p.display.set_mode((0, 0), flags=p.HIDDEN)

    for i in range(p.joystick.get_count()):
        add_device(i)

    vjoy.find_instance()

    running = True
    while running:
        for event in p.event.get():
            if event.type == p.QUIT:
                running = False
            if event.type == p.JOYBUTTONDOWN:
                #device_info[event.instance_id]['buttons'][event.button] = True
                publish_event(event.instance_id, "button", event.button, True)
            elif event.type == p.JOYBUTTONUP:
                #device_info[event.instance_id]['buttons'][event.button] = False
                publish_event(event.instance_id, "button", event.button, False)
            elif event.type == p.JOYAXISMOTION:
                #device_info[event.instance_id]['axes'][event.axis] = round((event.value + 1) / 2, 2)
                publish_event(event.instance_id, "axis", event.axis, round((event.value + 1) / 2, 2))
            elif event.type == p.JOYHATMOTION:
                #device_info[event.instance_id]['hats'][event.hat] = event.value
                if event.value[1] == 1:
                    v = "up"
                elif event.value[1] == -1:
                    v = "down"
                else:
                    v = ""
                if event.value[0] == 1:
                    h = "right"
                elif event.value[0] == -1:
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
                    value = None
                if value:
                    publish_event(event.instance_id, "hat", event.hat, value)
            # elif event.type == p.JOYBALLMOTION:
            #     #device_info[event.instance_id]['balls'][event.ball] = event.value
            #     publish_event(event.instance_id, "ball", event.ball, event.value)
            elif event.type == p.JOYDEVICEADDED:
                add_device(event.device_index)
            elif event.type == p.JOYDEVICEREMOVED:
                remove_device(event.instance_id)

    p.quit()
