import devices as dev
import vjoy
import variables as var

from time import sleep

step = {
    "weight_jacker": 1 / (41 - 1),
    "front_roll_bar": 1 / (6 - 1),
    "rear_roll_bar": 1 / (6 - 1),
    "fuel_map": 1 / (8 - 1),
    "clutch": 1 / (201 - 1),
    "throttle": 1 / (201 - 1),
}

def increment(control):
    while True:
        try:
            if not var.status['calibration'] and not var.bindings['status']['active']:
                if var.status[control]['switched']:
                    current = var.status[control]['secondary']
                else:
                    current = var.status[control]['primary']

                for direction in ("up", "down"):
                    if direction == "up":
                        offset = step[control] * var.settings[control]['increment']
                    elif direction == "down":
                        offset = step[control] * var.settings[control]['increment'] * -1
                    else:
                        offset = 0.0

                    bind = var.bindings[control][direction]

                    if bind['type'] == "button":
                        if dev.device_info[bind['guid']]['buttons'][bind['num']]:
                            vjoy.set(control, current + offset)

                            if var.settings[control]['continuous']:
                                sleep(0.1)

                            while dev.device_info[bind['guid']]['buttons'][bind['num']] and not var.status['calibration'] and not var.bindings['status']['active']:
                                if var.settings[control]['continuous']:
                                    current = current + offset
                                    vjoy.set(control, current)

                                sleep(0.05)
                    elif bind['type'] == "axis":
                        if dev.device_info[bind['guid']]['axes'][bind['num']] >= var.settings['threshold']:
                            vjoy.set(control, current + offset)

                            if var.settings[control]['continuous']:
                                sleep(0.1)

                            while dev.device_info[bind['guid']]['axes'][bind['num']] >= var.settings['threshold'] and not var.status['calibration'] and not var.bindings['status']['active']:
                                if var.settings[control]['continuous']:
                                    current = current + offset
                                    vjoy.set(control, current)

                                sleep(0.05)
                    elif bind['type'] == "hat":
                        if dev.device_info[bind['guid']]['hats'][bind['num']] == bind['dir']:
                            vjoy.set(control, current + offset)

                            if var.settings[control]['continuous']:
                                sleep(0.1)

                            while dev.device_info[bind['guid']]['hats'][bind['num']] == bind['dir'] and not var.status['calibration'] and not var.bindings['status']['active']:
                                if var.settings[control]['continuous']:
                                    current = current + offset
                                    vjoy.set(control, current)

                                sleep(0.05)

        except Exception as e:
            print(e)

        sleep(var.settings['frequency'])

def switch(control):
    while True:
        try:
            if not var.status['calibration'] and not var.bindings['status']['active']:
                bind = var.bindings[control]['switch']

                if bind['type'] == "button":
                    if dev.device_info[bind['guid']]['buttons'][bind['num']]:
                        if var.status[control]['switched']:
                            var.status[control]['switched'] = False
                            vjoy.set(control, var.status[control]['primary'])
                        elif not var.status[control]['switched']:
                            var.status[control]['switched'] = True
                            vjoy.set(control, var.status[control]['secondary'])

                        while dev.device_info[bind['guid']]['buttons'][bind['num']] and not var.bindings['status']['active']:
                            sleep(0.05)

                        if not var.settings[control]['toggle']:
                            if var.status[control]['switched']:
                                var.status[control]['switched'] = False
                                vjoy.set(control, var.status[control]['primary'])
                            elif not var.status[control]['switched']:
                                var.status[control]['switched'] = True
                                vjoy.set(control, var.status[control]['secondary'])
                elif bind['type'] == "axis":
                    if dev.device_info[bind['guid']]['axes'][bind['num']] >= var.settings['threshold']:
                        if var.status[control]['switched']:
                            var.status[control]['switched'] = False
                            vjoy.set(control, var.status[control]['primary'])
                        elif not var.status[control]['switched']:
                            var.status[control]['switched'] = True
                            vjoy.set(control, var.status[control]['secondary'])

                        while dev.device_info[bind['guid']]['axes'][bind['num']] >= var.settings['threshold'] and not var.bindings['status']['active']:
                            sleep(0.05)

                        if not var.settings[control]['toggle']:
                            if var.status[control]['switched']:
                                var.status[control]['switched'] = False
                                vjoy.set(control, var.status[control]['primary'])
                            elif not var.status[control]['switched']:
                                var.status[control]['switched'] = True
                                vjoy.set(control, var.status[control]['secondary'])
                elif bind['type'] == "hat":
                    if dev.device_info[bind['guid']]['hats'][bind['num']] == bind['dir']:
                        if var.status[control]['switched']:
                            var.status[control]['switched'] = False
                            vjoy.set(control, var.status[control]['primary'])
                        elif not var.status[control]['switched']:
                            var.status[control]['switched'] = True
                            vjoy.set(control, var.status[control]['secondary'])

                        while dev.device_info[bind['guid']]['hats'][bind['num']] == bind['dir'] and not var.bindings['status']['active']:
                            sleep(0.05)

                        if not var.settings[control]['toggle']:
                            if var.status[control]['switched']:
                                var.status[control]['switched'] = False
                                vjoy.set(control, var.status[control]['primary'])
                            elif not var.status[control]['switched']:
                                var.status[control]['switched'] = True
                                vjoy.set(control, var.status[control]['secondary'])
        except Exception as e:
            print(e)