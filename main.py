import devices as dev
import functions as fn
import interface as ui
import variables as var
import vjoy
import threading
from PyQt5.QtCore import pyqtSignal
from time import sleep

from devices import device_info

def weight_jacker_increment():
    while True:
        try:
            if not var.status['calibration'] and not var.bindings['status']['active']:
                if var.bindings['weight_jacker']['up']:
                    up = var.bindings['weight_jacker']['up']
                else:
                    up = {
                        "guid": 0,
                        "type": "none",
                        "num": 0,
                    }

                if var.bindings['weight_jacker']['down']:
                    down = var.bindings['weight_jacker']['down']
                else:
                    down = {
                        "guid": 0,
                        "type": "none",
                        "num": 0,
                    }

                if not var.status['weight_jacker']['switched']:
                    current = var.status['weight_jacker']['primary']
                elif var.status['weight_jacker']['switched']:
                    current = var.status['weight_jacker']['secondary']

                if up['type'] == "button":
                    if dev.device_info[up['guid']]['buttons'][up['num']]:

                        vjoy.set("weight_jacker", current + 0.025)
                        if var.settings['wj_continuous']:
                            sleep(0.1)

                        while dev.device_info[up['guid']]['buttons'][up['num']] and not var.status['calibration'] and not var.bindings['status']['active']:
                            if var.settings['wj_continuous']:
                                vjoy.set("weight_jacker", current + 0.025)
                                current = current + 0.025
                            sleep(0.05)
                elif up['type'] == "axis":
                    if dev.device_info[up['guid']]['axes'][up['num']] >= var.settings['axis_threshold']:
                        vjoy.set("weight_jacker", current + 0.025)
                        if var.settings['wj_continuous']:
                            sleep(0.1)

                        while dev.device_info[up['guid']]['axes'][up['num']] >= var.settings['axis_threshold'] and not var.status['calibration'] and not var.bindings['status']['active']:
                            if var.settings['wj_continuous']:
                                vjoy.set("weight_jacker", current + 0.025)
                                current = current + 0.025
                            sleep(0.05)
                elif up['type'] == "hat":
                    if dev.device_info[up['guid']]['hats'][up['num']] == up['dir']:
                        vjoy.set("weight_jacker", current + 0.025)
                        if var.settings['wj_continuous']:
                            sleep(0.1)

                        while dev.device_info[up['guid']]['hats'][up['num']] == up['dir'] and not var.status['calibration'] and not var.bindings['status']['active']:
                            if var.settings['wj_continuous']:
                                vjoy.set("weight_jacker", current + 0.025)
                                current = current + 0.025
                            sleep(0.05)

                if down['type'] == "button":
                    if dev.device_info[down['guid']]['buttons'][down['num']]:

                        vjoy.set("weight_jacker", current - 0.025)
                        if var.settings['wj_continuous']:
                            sleep(0.1)

                        while dev.device_info[down['guid']]['buttons'][down['num']] and not var.status['calibration'] and not var.bindings['status']['active']:
                            if var.settings['wj_continuous']:
                                vjoy.set("weight_jacker", current - 0.025)
                                current = current - 0.025
                            sleep(0.05)
                elif down['type'] == "axis":
                    if dev.device_info[down['guid']]['axes'][down['num']] >= var.settings['axis_threshold']:
                        vjoy.set("weight_jacker", current - 0.025)
                        if var.settings['wj_continuous']:
                            sleep(0.1)

                        while dev.device_info[down['guid']]['axes'][down['num']] >= var.settings['axis_threshold'] and not var.status['calibration'] and not var.bindings['status']['active']:
                            if var.settings['wj_continuous']:
                                vjoy.set("weight_jacker", current - 0.025)
                                current = current - 0.025
                            sleep(0.05)
                elif down['type'] == "hat":
                    if dev.device_info[down['guid']]['hats'][down['num']] == down['dir']:
                        vjoy.set("weight_jacker", current - 0.025)
                        if var.settings['wj_continuous']:
                            sleep(0.1)

                        while dev.device_info[down['guid']]['hats'][down['num']] == down['dir'] and not var.status['calibration'] and not var.bindings['status']['active']:
                            if var.settings['wj_continuous']:
                                vjoy.set("weight_jacker", current - 0.025)
                                current = current - 0.025
                            sleep(0.05)
        except Exception as e:
            print(e)

        sleep(var.settings['polling_frequency'])

def weight_jacker_switch():
    while True:
        try:
            if not var.status['calibration'] and not var.bindings['status']['active']:
                if var.bindings['weight_jacker']['switch']:
                    switch = var.bindings['weight_jacker']['switch']
                else:
                    switch = {
                        "guid": 0,
                        "type": "none",
                        "num": 0,
                    }

                if switch['type'] == "button":
                    if dev.device_info[switch['guid']]['buttons'][switch['num']]:
                        if var.status['weight_jacker']['switched']:
                            var.status['weight_jacker']['switched'] = False
                            vjoy.set("weight_jacker", var.status['weight_jacker']['primary'])
                        elif not var.status['weight_jacker']['switched']:
                            var.status['weight_jacker']['switched'] = True
                            vjoy.set("weight_jacker", var.status['weight_jacker']['secondary'])

                        while dev.device_info[switch['guid']]['buttons'][switch['num']] and not var.status['calibration'] and not var.bindings['status']['active']:
                            sleep(0.05)

                        if not var.settings['wj_toggle']:
                            if var.status['weight_jacker']['switched']:
                                var.status['weight_jacker']['switched'] = False
                                vjoy.set("weight_jacker", var.status['weight_jacker']['primary'])
                            elif not var.status['weight_jacker']['switched']:
                                var.status['weight_jacker']['switched'] = True
                                vjoy.set("weight_jacker", var.status['weight_jacker']['secondary'])
                elif switch['type'] == "axis":
                    if dev.device_info[switch['guid']]['axes'][switch['num']] >= var.settings['axis_threshold']:
                        if var.status['weight_jacker']['switched']:
                            var.status['weight_jacker']['switched'] = False
                            vjoy.set("weight_jacker", var.status['weight_jacker']['primary'])
                        elif not var.status['weight_jacker']['switched']:
                            var.status['weight_jacker']['switched'] = True
                            vjoy.set("weight_jacker", var.status['weight_jacker']['secondary'])

                        while dev.device_info[switch['guid']]['axes'][switch['num']] >= var.settings['axis_threshold'] and not var.status['calibration'] and not var.bindings['status']['active']:
                            sleep(0.05)

                        if not var.settings['wj_toggle']:
                            if var.status['weight_jacker']['switched']:
                                var.status['weight_jacker']['switched'] = False
                                vjoy.set("weight_jacker", var.status['weight_jacker']['primary'])
                            elif not var.status['weight_jacker']['switched']:
                                var.status['weight_jacker']['switched'] = True
                                vjoy.set("weight_jacker", var.status['weight_jacker']['secondary'])
                elif switch['type'] == "hat":
                    if dev.device_info[switch['guid']]['hats'][switch['num']] == switch['dir']:
                        if var.status['weight_jacker']['switched']:
                            var.status['weight_jacker']['switched'] = False
                            vjoy.set("weight_jacker", var.status['weight_jacker']['primary'])
                        elif not var.status['weight_jacker']['switched']:
                            var.status['weight_jacker']['switched'] = True
                            vjoy.set("weight_jacker", var.status['weight_jacker']['secondary'])

                        while dev.device_info[switch['guid']]['hats'][switch['num']] == switch['dir'] and not var.status['calibration'] and not var.bindings['status'][
                            'active']:
                            sleep(0.05)

                        if not var.settings['wj_toggle']:
                            if var.status['weight_jacker']['switched']:
                                var.status['weight_jacker']['switched'] = False
                                vjoy.set("weight_jacker", var.status['weight_jacker']['primary'])
                            elif not var.status['weight_jacker']['switched']:
                                var.status['weight_jacker']['switched'] = True
                                vjoy.set("weight_jacker", var.status['weight_jacker']['secondary'])
        except Exception as e:
            print(e)
        sleep(var.settings['polling_frequency'])

if __name__ == '__main__':
    detect = threading.Thread(target=dev.device_detection, daemon=True)
    detect.start()
    wj_increment = threading.Thread(target=weight_jacker_increment, daemon=True)
    wj_increment.start()
    wj_switch = threading.Thread(target=weight_jacker_switch, daemon=True)
    wj_switch.start()

    vjoy.intialize()
    ui.main()