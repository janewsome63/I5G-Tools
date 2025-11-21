from time import sleep

import devices as dev
import functions as fn
import variables as var
import vjoy
import history

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
        if dev.device_info[bind['guid']]['axes'][bind['num']] >= var.settings['high_threshold'] and history.check_valid(bind['guid'], bind['num'], dev.device_info[bind['guid']]['axes'][bind['num']], True) and bind['value'] == var.settings['high_threshold']:
            pressed = True
        elif dev.device_info[bind['guid']]['axes'][bind['num']] <= var.settings['low_threshold'] and history.check_valid(bind['guid'], bind['num'], dev.device_info[bind['guid']]['axes'][bind['num']], False) and bind['value'] == var.settings['low_threshold']:
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
    #print("increment function print1: ", bind, function, control)
    if function == 'bite_point' or function == 'engine_warming':
        if control == "up":
            offset = var.settings[function]['increment']/100
        elif control == "down":
            offset = -var.settings[function]['increment']/100
        else:
            offset = 0.0
    else:
        if control == "up":
            offset = step[function] * var.settings[function]['increment']
        elif control == "down":
            offset = step[function] * var.settings[function]['increment'] * -1
        else:
            offset = 0.0
    #print("offset: ", offset)
    if check_pressed(bind):

        if var.status[function]['switched']:
            vjoy.set(function, var.status[function]['secondary'] + offset)
            #print("secondary")
        else:
            if function == 'bite_point' or function == 'engine_warming':
                var.status[function]['secondary'] = var.status[function]['secondary'] + offset
            else:
                vjoy.set(function, var.status[function]['primary'] + offset)
            #print("primary")

        interval = int(10)
        if var.settings[function]['continuous']:
            count = 1
            #print("count check1: ", count)
            timer = var.settings['timer_first']/1000
            while check_pressed(bind) and not var.status['calibration'] and not var.bindings['status']['active']:
                if count % interval == 0:
                    #print("count check2: ", count, var.status[function]['switched'])
                    #print("continuous loop")
                    if var.status[function]['switched']:
                        vjoy.set(function, var.status[function]['secondary'] + offset)
                    else:
                        if function == 'bite_point' or function == 'engine_warming':
                            var.status[function]['secondary'] = var.status[function]['secondary'] + offset
                        else:
                            vjoy.set(function, var.status[function]['primary'] + offset)
                    if count == 10:
                        timer = var.settings['timer_loop']/1000
                sleep(timer/interval)
                count += 1
        else:
            while check_pressed(bind) and not var.status['calibration'] and not var.bindings['status']['active']:
                sleep(var.settings['timer_first']/(1000*interval))
    #else:
        #print("bind check_pressed failed: ", bind)
    var.status[function]['thread']['running'][control] = False


def switch(bind, function):
    if check_pressed(bind):
        if var.status[function]['switched']:
            var.status[function]['switched'] = False
            vjoy.set(function, var.status[function]['primary'])
        elif not var.status[function]['switched']:
            var.status[function]['switched'] = True
            vjoy.set(function, var.status[function]['secondary'])

        while check_pressed(bind) and not var.bindings['status']['active'] and not var.status['calibration']:
            sleep(0.05)

        if not var.settings[function]['toggle']:
            if var.status[function]['switched']:
                var.status[function]['switched'] = False
                vjoy.set(function, var.status[function]['primary'])
            elif not var.status[function]['switched']:
                var.status[function]['switched'] = True
                vjoy.set(function, var.status[function]['secondary'])
    var.status[function]['thread']['waiting'] = False

def controls():
    check = fn.is_bind()
    #print(check)
    if check:
        #print("check pass")
        for entry in check:
            function = entry['function']
            control = entry['control']
            #print("entry, function, control: ", entry, function, control)
            if not var.status['calibration'] and not var.bindings['status']['active']:

                bind = var.bindings[function][control]
                #print("bind: ", bind)
                if function == 'bite_point' or function == 'engine_warming':
                    if control == "pedal":
                        if 'value' in entry:
                            value = entry['value']
                            if var.status[function]['thread']['running'][control] == False:
                                var.status[function]['thread']['running'][control] = True
                                print("start thread: ", function, control, value)
                                var.status[function]['primary'] = value
                                if not var.status[function]['switched']:
                                    print("pedal set: ", function, value)
                                    vjoy.set(function, value)
                                var.status[function]['thread']['running'][control] = False
                    elif control == "up" or control == "down":
                        if var.status[function]['thread']['running'][control] == False:
                            var.status[function]['thread']['running'][control] = True
                            print("start thread: ", function, control)
                            fn.start_thread(lambda: increment(bind, function, control))
                            #increment(bind, function, control)
                            #var.status[function]['thread']['running'] = None
                        # else:
                        #     print("thread running check failed: ", var.status[function['thread']['running']])
                    elif control == "switch":
                        if not var.status[function]['thread']['waiting']:
                            var.status[function]['thread']['waiting'] = True
                            fn.start_thread(lambda: switch(bind, function))
                else:
                    if control == "up" or control == "down":
                        if var.status[function]['thread']['running'][control] == False:
                            var.status[function]['thread']['running'][control] = True
                            print("start thread: ", function, control)
                            fn.start_thread(lambda: increment(bind, function, control))
                            #increment(bind, function, control)
                            #var.status[function]['thread']['running'] = None
                        # else:
                        #     print("thread running check failed: ", var.status[function['thread']['running']])

                    elif control == "switch":
                        if not var.status[function]['thread']['waiting']:
                            var.status[function]['thread']['waiting'] = True
                            fn.start_thread(lambda: switch(bind, function))