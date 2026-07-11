import devices as dev
import functions as fn
import history
import variables as var
import vjoy
from time import sleep

def controls():
    try:
        check = fn.is_bind()
        # print(check)
        if check:
            for entry in check:
                function = entry['function']
                control = entry['control']
                if 'value' in entry:
                    value = entry['value']
                else:
                    value = None

                if var.status['calibration'] == "None" and not var.bindings['status']['active']:
                    bind = var.bindings[function][control]
                    if control == "pedal":
                        pedal(function, value)
                    elif control == "up" or control == "down":
                        if not var.status[function]['thread']['running'][control]:
                            var.status[function]['thread']['running'][control] = True
                            fn.start_thread(lambda: increment(bind, function, control))
                    elif control == "switch":
                        if not var.status[function]['thread']['waiting']:
                            var.status[function]['thread']['waiting'] = True
                            fn.start_thread(lambda: switch(bind, function))
                    elif control in ("regen", "deploy"):
                        if not var.status[function][control]['thread']['waiting']:
                            var.status[function][control]['thread']['waiting'] = True
                            fn.start_thread(lambda: button(bind, function, control))
    except Exception as e:
        fn.error_handling(e, "controls.controls()")

def check_pressed(bind):
    try:
        if bind['type'] == "button":
            if dev.device_info[bind['guid']]['buttons'][bind['num']]:
                pressed = True
            else:
                pressed = False
        elif bind['type'] == "axis":
            if dev.device_info[bind['guid']]['axes'][bind['num']] >= var.settings['device_axis_thresh'][str(bind['guid'])]['high_threshold'] and history.check_valid(bind['guid'], bind['num'], dev.device_info[bind['guid']]['axes'][bind['num']], True) and bind['value'] == var.settings['device_axis_thresh'][str(bind['guid'])]['high_threshold']:
                pressed = True
            elif dev.device_info[bind['guid']]['axes'][bind['num']] <= var.settings['device_axis_thresh'][str(bind['guid'])]['low_threshold'] and history.check_valid(bind['guid'], bind['num'], dev.device_info[bind['guid']]['axes'][bind['num']], False) and bind['value'] == var.settings['device_axis_thresh'][str(bind['guid'])]['low_threshold']:
                pressed = True
            else:
                pressed = False
        elif bind['type'] == "hat":
            if bind['dir'] in dev.device_info[bind['guid']]['hats'][bind['num']]:
                pressed = True
            else:
                pressed = False
        elif bind['type'] == "key":
            if bind['value'] == dev.device_info[bind['guid']]['keys'][bind['num']]:
                pressed = True
            else:
                pressed = False
        else:
            pressed = False

        return pressed
    except Exception as e:
        fn.error_handling(e, "controls.check_pressed()")

def increment(bind, function, control):
    try:
        #print("increment function print1: ", bind, function, control)
        if function == 'clutch' or function == 'throttle':
            if control == "up":
                offset = var.settings[function]['increment']/100
            elif control == "down":
                offset = -var.settings[function]['increment']/100
            else:
                offset = 0.0
        else:
            if control == "up":
                offset = var.step[function] * var.settings[function]['increment']
            elif control == "down":
                offset = var.step[function] * var.settings[function]['increment'] * -1
            else:
                offset = 0.0
        # print("offset: ", offset)
        if check_pressed(bind, function):

            if var.status[function]['switched']:
                vjoy.set_axis(function, var.status[function]['secondary'] + offset)
                #print("secondary")
            else:
                if function == 'clutch' or function == 'throttle':
                    var.status[function]['secondary'] = var.status[function]['secondary'] + offset
                else:
                    vjoy.set_axis(function, var.status[function]['primary'] + offset)
                #print("primary")

            interval = int(10)
            if var.settings[function]['continuous']:
                count = 1
                #print("count check1: ", count)
                timer = var.settings['timer_first']/1000
                while check_pressed(bind, function) and var.status['calibration'] == "None" and not var.bindings['status']['active']:
                    if count % interval == 0:
                        #print("count check2: ", count, var.status[function]['switched'])
                        #print("continuous loop")
                        if var.status[function]['switched']:
                            vjoy.set_axis(function, var.status[function]['secondary'] + offset)
                        else:
                            if function == 'clutch' or function == 'throttle':
                                var.status[function]['secondary'] = var.status[function]['secondary'] + offset
                            else:
                                vjoy.set_axis(function, var.status[function]['primary'] + offset)
                        if count == 10:
                            timer = var.settings['timer_loop']/1000
                    sleep(timer/interval)
                    count += 1
            else:
                while check_pressed(bind, function) and var.status['calibration']== "None" and not var.bindings['status']['active']:
                    sleep(var.settings['timer_first']/(1000*interval))
        #else:
            #print("bind check_pressed failed: ", bind)
        var.status[function]['thread']['running'][control] = False
    except Exception as e:
        fn.error_handling(e, "controls.increment()")


def switch(bind, function):
    try:
        if check_pressed(bind, function):
            if var.status[function]['switched']:
                var.status[function]['switched'] = False
                vjoy.set_axis(function, var.status[function]['primary'])
            elif not var.status[function]['switched']:
                var.status[function]['switched'] = True
                vjoy.set_axis(function, var.status[function]['secondary'])

            while check_pressed(bind, function) and not var.bindings['status']['active'] and var.status['calibration'] == "None":
                sleep(0.05)

            if not var.settings[function]['toggle']:
                if var.status[function]['switched']:
                    var.status[function]['switched'] = False
                    vjoy.set_axis(function, var.status[function]['primary'])
                elif not var.status[function]['switched']:
                    var.status[function]['switched'] = True
                    vjoy.set_axis(function, var.status[function]['secondary'])
        var.status[function]['thread']['waiting'] = False
    except Exception as e:
        fn.error_handling(e, "controls.switch()")

def pedal(function, value):
    try:
        if value is not None:
            var.status[function]['primary'] = value
            if not var.status[function]['switched']:
                vjoy.set_axis(function, value)
    except Exception as e:
        fn.error_handling(e, "controls.pedal()")

def button(bind, function, control):
    try:
        if check_pressed(bind):
            if var.status[function][control]['state']:
                var.status[function][control]['state'] = False
            elif not var.status[function][control]['state']:
                var.status[function][control]['state'] = True
            vjoy.set_button(control, var.status[function][control]['state'])

            while check_pressed(bind) and not var.bindings['status']['active']:
                sleep(0.05)

            if not var.settings[function][control + '_toggle']:
                if var.status[function][control]['state']:
                    var.status[function][control]['state'] = False
                elif not var.status[function][control]['state']:
                    var.status[function][control]['state'] = True
                vjoy.set_button(control, var.status[function][control]['state'])
        var.status[function][control]['thread']['waiting'] = False
    except Exception as e:
        fn.error_handling(e, "controls.button()")