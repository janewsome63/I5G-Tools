import devices as dev
import functions as fn
import variables as var
import vjoy

from time import sleep

step = {
    "weight_jacker": 1 / (41 - 1),
    "front_roll_bar": 1 / (6 - 1),
    "rear_roll_bar": 1 / (6 - 1),
    "fuel_map": 1 / (8 - 1),
    "clutch": 1 / (201 - 1),
    "throttle": 1 / (201 - 1),
}

def control():
    if fn.is_bind():
        function = fn.is_bind()
        if not var.status['calibration'] and not var.bindings['status']['active']:

            # Up/Down
            for direction in ("up", "down"):
                if direction == "up":
                    offset = step[function] * var.settings[function]['increment']
                elif direction == "down":
                    offset = step[function] * var.settings[function]['increment'] * -1
                else:
                    offset = 0.0
    
                bind = var.bindings[function][direction]
    
                if bind['type'] == "button":
                    if dev.device_info[bind['guid']]['buttons'][bind['num']]:
                        var.status[function]['thread']['current'] += 1
                        thread_id = var.status[function]['thread']['current']
                        var.status[function]['thread']['running'] = thread_id

                        if var.status[function]['switched']:
                            vjoy.set(function, var.status[function]['secondary'] + offset)
                        else:
                            vjoy.set(function, var.status[function]['primary'] + offset)

                        if var.settings[function]['continuous']:
                            sleep(0.2)
                        while dev.device_info[bind['guid']]['buttons'][bind['num']] and var.status[function]['thread']['running'] == thread_id:
                            if var.status['calibration'] or var.bindings['status']['active']:
                                break
                            if var.settings[function]['continuous']:
                                if var.status[function]['switched']:
                                    vjoy.set(function, var.status[function]['secondary'] + offset)
                                else:
                                    vjoy.set(function, var.status[function]['primary'] + offset)
                            sleep(0.075)

                        if var.status[function]['thread']['running'] == thread_id:
                            var.status[function]['thread']['running'] = 0

                elif bind['type'] == "axis":
                    if dev.device_info[bind['guid']]['axes'][bind['num']] >= var.settings['threshold']:
                        var.status[function]['thread']['current'] += 1
                        thread_id = var.status[function]['thread']['current']
                        var.status[function]['thread']['running'] = thread_id

                        if var.status[function]['switched']:
                            vjoy.set(function, var.status[function]['secondary'] + offset)
                        else:
                            vjoy.set(function, var.status[function]['primary'] + offset)

                        if var.settings[function]['continuous']:
                            sleep(0.2)
                        while dev.device_info[bind['guid']]['axes'][bind['num']] >= var.settings['threshold'] and var.status[function]['thread']['running'] == thread_id:
                            if var.status['calibration'] or var.bindings['status']['active']:
                                break
                            if var.settings[function]['continuous']:
                                if var.status[function]['switched']:
                                    vjoy.set(function, var.status[function]['secondary'] + offset)
                                else:
                                    vjoy.set(function, var.status[function]['primary'] + offset)
                            sleep(0.075)

                        if var.status[function]['thread']['running'] == thread_id:
                            var.status[function]['thread']['running'] = 0

                elif bind['type'] == "hat":
                    if bind['dir'] in dev.device_info[bind['guid']]['hats'][bind['num']]:
                        var.status[function]['thread']['current'] += 1
                        thread_id = var.status[function]['thread']['current']
                        var.status[function]['thread']['running'] = thread_id

                        if var.status[function]['switched']:
                            vjoy.set(function, var.status[function]['secondary'] + offset)
                        else:
                            vjoy.set(function, var.status[function]['primary'] + offset)

                        if var.settings[function]['continuous']:
                            sleep(0.2)
                        while bind['dir'] in dev.device_info[bind['guid']]['hats'][bind['num']] and var.status[function]['thread']['running'] == thread_id:
                            if var.status['calibration'] or var.bindings['status']['active']:
                                break
                            if var.settings[function]['continuous']:
                                if var.status[function]['switched']:
                                    vjoy.set(function, var.status[function]['secondary'] + offset)
                                else:
                                    vjoy.set(function, var.status[function]['primary'] + offset)
                            sleep(0.075)

                        if var.status[function]['thread']['running'] == thread_id:
                            var.status[function]['thread']['running'] = 0

            # Switch
            bind = var.bindings[function]['switch']

            if bind['type'] == "button":
                if dev.device_info[bind['guid']]['buttons'][bind['num']]:
                    if not var.status[function]['thread']['waiting']:
                        if var.status[function]['switched']:
                            var.status[function]['switched'] = False
                            vjoy.set(function, var.status[function]['primary'])
                        elif not var.status[function]['switched']:
                            var.status[function]['switched'] = True
                            vjoy.set(function, var.status[function]['secondary'])

                        var.status[function]['thread']['waiting'] = True
                        while dev.device_info[bind['guid']]['buttons'][bind['num']] and not var.bindings['status']['active']:
                            sleep(0.05)
                        var.status[function]['thread']['waiting'] = False

                        if not var.settings[function]['toggle']:
                            if var.status[function]['switched']:
                                var.status[function]['switched'] = False
                                vjoy.set(function, var.status[function]['primary'])
                            elif not var.status[function]['switched']:
                                var.status[function]['switched'] = True
                                vjoy.set(function, var.status[function]['secondary'])

            elif bind['type'] == "axis":
                if dev.device_info[bind['guid']]['axes'][bind['num']] >= var.settings['threshold']:
                    if not var.status[function]['thread']['waiting']:
                        if var.status[function]['switched']:
                            var.status[function]['switched'] = False
                            vjoy.set(function, var.status[function]['primary'])
                        elif not var.status[function]['switched']:
                            var.status[function]['switched'] = True
                            vjoy.set(function, var.status[function]['secondary'])

                        var.status[function]['thread']['waiting'] = True
                        while dev.device_info[bind['guid']]['axes'][bind['num']] >= var.settings['threshold'] and not var.bindings['status']['active']:
                            sleep(0.05)
                        var.status[function]['thread']['waiting'] = False

                        if not var.settings[function]['toggle']:
                            if var.status[function]['switched']:
                                var.status[function]['switched'] = False
                                vjoy.set(function, var.status[function]['primary'])
                            elif not var.status[function]['switched']:
                                var.status[function]['switched'] = True
                                vjoy.set(function, var.status[function]['secondary'])

            elif bind['type'] == "hat":
                if bind['dir'] in dev.device_info[bind['guid']]['hats'][bind['num']]:
                    if not var.status[function]['thread']['waiting']:
                        if var.status[function]['switched']:
                            var.status[function]['switched'] = False
                            vjoy.set(function, var.status[function]['primary'])
                        elif not var.status[function]['switched']:
                            var.status[function]['switched'] = True
                            vjoy.set(function, var.status[function]['secondary'])

                        var.status[function]['thread']['waiting'] = True
                        while bind['dir'] in dev.device_info[bind['guid']]['hats'][bind['num']] and not var.bindings['status']['active']:
                            sleep(0.05)
                        var.status[function]['thread']['waiting'] = False

                        if not var.settings[function]['toggle']:
                            if var.status[function]['switched']:
                                var.status[function]['switched'] = False
                                vjoy.set(function, var.status[function]['primary'])
                            elif not var.status[function]['switched']:
                                var.status[function]['switched'] = True
                                vjoy.set(function, var.status[function]['secondary'])