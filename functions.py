import variables as var
import devices as dev

import pygame as p

def bind(function, control):
    start = dev.device_info
    bound = ("", "", "")
    prev = var.current_event
    while bound == ("", "", ""):
        if var.current_event != prev and var.current_event['event']['value'] != "released":
            if var.current_event['event']['type'] != "hat":
                bound = (var.current_event['name'], var.current_event['event']['type'], var.current_event['event']['input'])
            else:
                bound = (var.current_event['name'], var.current_event['event']['type'], var.current_event['event']['input'], var.current_event['event']['value'])
    var.bindings[function][control] = bound