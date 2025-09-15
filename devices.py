import pygame as p
import os

devices = []
device_info = {}

def add_device(index):
    device = p.joystick.Joystick(index)
    instance = device.get_instance_id()
    devices.append(device)
    device_info[instance] = {
        "name": device.get_name(),
        "guid": device.get_guid(),
        "index": index,
        "instance": instance,
        "initialized": device.get_init(),
    }
    if device.get_numbuttons():
        device_info[instance]['buttons'] = {}
        for i in range(device.get_numbuttons()):
            device_info[instance]['buttons'][i] = False
    if device.get_numaxes():
        device_info[instance]['axes'] = {}
        for i in range(device.get_numaxes()):
            device_info[instance]['axes'][i] =  0.0
    if device.get_numhats():
        device_info[instance]['hats'] = {}
        for i in range(device.get_numhats()):
            device_info[instance]['hats'][i] = (0, 0)
    if device.get_numballs():
        device_info[instance]['balls'] = {}
        for i in range(device.get_numhats()):
            device_info[instance]['balls'][i] = (0, 0)
    print(f"Joystick Added: {device_info[instance]['name']} (ID: {device_info[instance]['instance']})")
    print(device_info[instance])

def remove_device(instance):
    for i, device in enumerate(devices):
        if device.get_instance_id() == instance:
            print(f"Joystick Removed: {device.get_name()} (ID: {instance})")
            devices.pop(i)
            break
    del device_info[instance]

def device_detection():
    os.environ["SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS"] = "1"
    p.init()

    p.joystick.init()

    #screen = p.display.set_mode((0, 0), flags=p.HIDDEN)

    for i in range(p.joystick.get_count()):
        add_device(i)

    running = True
    while running:
        for event in p.event.get():
            if event.type == p.QUIT:
                running = False
            if event.type == p.JOYBUTTONDOWN:
                device_info[event.instance_id]['buttons'][event.button] = True
                print(device_info[event.instance_id]['buttons'])
            elif event.type == p.JOYBUTTONUP:
                device_info[event.instance_id]['buttons'][event.button] = False
                print(device_info[event.instance_id]['buttons'])
            elif event.type == p.JOYAXISMOTION:
                device_info[event.instance_id]['axes'][event.axis] = round((event.value + 1) / 2, 2)
                print(device_info[event.instance_id]['axes'])
            elif event.type == p.JOYHATMOTION:
                device_info[event.instance_id]['hats'][event.hat] = event.value
                print(device_info[event.instance_id]['hats'])
            elif event.type == p.JOYBALLMOTION:
                device_info[event.instance_id]['balls'][event.ball] = event.value
                print(device_info[event.instance_id]['balls'])
            elif event.type == p.JOYDEVICEADDED:
                add_device(event.device_index)
            elif event.type == p.JOYDEVICEREMOVED:
                remove_device(event.instance_id)

    p.quit()