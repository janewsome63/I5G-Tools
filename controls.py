from time import sleep

import devices as dev
import functions as fn
import variables as var
import vjoy

step = {
    "weight_jacker": 1 / (41 - 1),
    "front_roll_bar": 1 / (6 - 1),
    "rear_roll_bar": 1 / (6 - 1),
    "fuel_map": 1 / (8 - 1),
    "clutch": 1 / (201 - 1),
    "throttle": 1 / (201 - 1),
}

def check_pressed(bind):
    if bind['type'] == "button":
        if dev.device_info[bind['guid']]['buttons'][bind['num']]:
            pressed = True
        else:
            pressed = False
    elif bind['type'] == "axis":
        if dev.device_info[bind['guid']]['axes'][bind['num']] >= var.settings['threshold']:
            pressed = True
        else:
            pressed = False
    elif bind['type'] == "hat":
        if bind['dir'] in dev.device_info[bind['guid']]['hats'][bind['num']]:
            pressed = True
        else:
            pressed = False
    else:
        pressed = False

    return pressed

def increment(bind, function, control):
    if control == "up":
        offset = step[function] * var.settings[function]['increment']
    elif control == "down":
        offset = step[function] * var.settings[function]['increment'] * -1
    else:
        offset = 0.0

    if check_pressed(bind) and var.status[function]['thread']['running'] != control:
        var.status[function]['thread']['running'] = control

        if var.status[function]['switched']:
            vjoy.set(function, var.status[function]['secondary'] + offset)
        else:
            vjoy.set(function, var.status[function]['primary'] + offset)

        if var.settings[function]['continuous']:
            sleep(0.2)
        while check_pressed(bind) and var.status[function]['thread']['running'] == control and not var.status['calibration'] and not var.bindings['status']['active']:
            if var.settings[function]['continuous']:
                if var.status[function]['switched']:
                    vjoy.set(function, var.status[function]['secondary'] + offset)
                else:
                    vjoy.set(function, var.status[function]['primary'] + offset)
            sleep(0.075)

        if var.status[function]['thread']['running'] == control:
            var.status[function]['thread']['running'] = None

def switch(bind, function):
   if check_pressed(bind):
        if not var.status[function]['thread']['waiting']:
            if var.status[function]['switched']:
                var.status[function]['switched'] = False
                vjoy.set(function, var.status[function]['primary'])
            elif not var.status[function]['switched']:
                var.status[function]['switched'] = True
                vjoy.set(function, var.status[function]['secondary'])

            var.status[function]['thread']['waiting'] = True
            while check_pressed(bind) and not var.bindings['status']['active']:
                sleep(0.05)
            var.status[function]['thread']['waiting'] = False

            if not var.settings[function]['toggle']:
                if var.status[function]['switched']:
                    var.status[function]['switched'] = False
                    vjoy.set(function, var.status[function]['primary'])
                elif not var.status[function]['switched']:
                    var.status[function]['switched'] = True
                    vjoy.set(function, var.status[function]['secondary'])

def controls():
    if fn.is_bind():
        function = fn.is_bind()['function']
        control = fn.is_bind()['control']
        if not var.status['calibration'] and not var.bindings['status']['active']:

            bind = var.bindings[function][control]

            if control == "up" or control == "down":
                increment(bind, function, control)

            elif control == "switch":
                switch(bind, function)