import devices as dev
import functions as fn
import interface as ui
import variables as var
import vjoy
import threading
from PyQt5.QtCore import pyqtSignal
from time import sleep

from devices import device_info

frequency = 0.1

def weight_jacker_increment():
    while True:
        current = (var.current_event['name'], var.current_event['event']['type'], var.current_event['event']['input'])
        for function in var.bindings:
            if function == "weight_jacker":
                for control in var.bindings[function]:
                    if var.bindings[function][control] == current:
                        if var.current_event['event']['value'] == "pressed":
                            if control == "up":
                                vjoy.set(function, vjoy.axis_values[function] + 0.025)
                                if var.settings['wj_continuous'] == True:
                                    sleep(0.15)
                                    while var.current_event['event']['value'] == "pressed":
                                        vjoy.set(function, vjoy.axis_values[function] + 0.025)
                                        sleep(0.1)
                                else:
                                    while var.current_event['event']['value'] == "pressed":
                                        sleep(0.1)
                            elif control == "down":
                                vjoy.set(function, vjoy.axis_values[function] - 0.025)
                                if var.settings['wj_continuous'] == True:
                                    sleep(0.15)
                                    while var.current_event['event']['value'] == "pressed":
                                        vjoy.set(function, vjoy.axis_values[function] - 0.025)
                                        sleep(0.1)
                                else:
                                    while var.current_event['event']['value'] == "pressed":
                                        sleep(0.1)
        sleep(frequency)

def weight_jacker_switch():
    while True:
        current = (var.current_event['name'], var.current_event['event']['type'], var.current_event['event']['input'])
        for function in var.bindings:
            if function == "weight_jacker":
                for control in var.bindings[function]:
                    if var.bindings[function][control] == current:
                        if var.current_event['event']['value'] == "pressed":
                            if control == "switch":
                                if var.settings['wj_toggle']:
                                    if var.status['weight_jacker']['switched']:
                                        var.status['weight_jacker']['switched'] = False
                                        vjoy.set(function, var.status['weight_jacker']['primary'])
                                        while var.current_event['event']['value'] == "pressed":
                                            sleep(0.1)
                                    elif not var.status['weight_jacker']['switched']:
                                        var.status['weight_jacker']['switched'] = True
                                        vjoy.set(function, var.status['weight_jacker']['secondary'])
                                        while var.current_event['event']['value'] == "pressed":
                                            sleep(0.1)
                                elif not var.settings['wj_toggle']:
                                    if var.status['weight_jacker']['switched']:
                                        print(True)
                                        var.status['weight_jacker']['switched'] = False
                                        vjoy.set(function, var.status['weight_jacker']['primary'])
                                    elif not var.status['weight_jacker']['switched']:
                                        var.status['weight_jacker']['switched'] = True
                                        vjoy.set(function, var.status['weight_jacker']['secondary'])
                                        print(var.status['weight_jacker']['secondary'])
                                        while var.current_event['event']['value'] == "pressed":
                                            sleep(0.1)
                                        var.status['weight_jacker']['switched'] = False
                                        vjoy.set(function, var.status['weight_jacker']['primary'])

        sleep(frequency)

if __name__ == '__main__':
    detect = threading.Thread(target=dev.device_detection, daemon=True)
    detect.start()
    wj_increment = threading.Thread(target=weight_jacker_increment, daemon=True)
    wj_increment.start()
    wj_switch = threading.Thread(target=weight_jacker_switch, daemon=True)
    wj_switch.start()

    vjoy.intialize()
    ui.main()