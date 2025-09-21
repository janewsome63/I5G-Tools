import variables as var
import devices as dev

import pygame as p

def bind(function, control):
    var.bindings['active'] = True
    start = dev.device_info
    bound = None
    while not bound and var.bindings['active']:
        for device in dev.device_info:
            for input in dev.device_info[device]:
                if input == "buttons":
                    for button in dev.device_info[device][input]:
                        if dev.device_info[device][input][button] != start[device][input][button]:
                            bound = dev.device_info[device][input][button]
    var.bindings[function][control] = bound
    var.bindings['active'] = False

def init_vars():
    var.bindings['wj_up_device'] = "Placeholder Device"
    var.bindings['wj_up_button'] = "1"
    var.bindings['wj_down_device'] = "Placeholder Device"
    var.bindings['wj_down_button'] = "2"
    var.bindings['wj_switch_device'] = "Placeholder Device"
    var.bindings['wj_switch_button'] = "3"

    var.wj_values['percent'] = 50
    var.wj_values['raw'] = 12345
    var.wj_values['value'] = -20
    var.wj_values['increment'] = 1
    var.wj_values['switch_value'] = -20
    var.wj_values['switch_mode'] = 1
    var.wj_values['increment_mode'] = 1

# Input Device Functions




# def format_vector(type, vector):
#     digits = 3
#     string = str(vector)
#     if type == "stick" or type == "dpad":
#         string = string.replace("(", " ")
#         string = string.replace(")", "")
#         string = string.replace("=", " ")
#         string = string.replace(",", "")
#         string = string.split()
#
#         if type == "dpad":
#             if "0.0" in string[2]:
#                 string[2] = string[2].replace("-", "")
#             pos_x = round(float(string[2]), digits)
#             if "0.0" in string[4]:
#                 string[4] = string[4].replace("-", "")
#             pos_y = round(float(string[4]), digits)
#         else:
#             pos_x = round((float(string[2]) + 1) / 2, digits)
#             pos_y = round((float(string[4]) + 1) / 2, digits)
#
#         position = {
#             "pos_x": pos_x,
#             "pos_y": pos_y,
#         }
#     elif type == "axis":
#         pos = round((float(string) + 1) / 2, digits)
#
#         position = {
#             "pos": pos,
#         }
#     elif type == "trigger":
#         pos = round(float(string), digits)
#
#         position = {
#             "pos": pos,
#         }
#
#     return position