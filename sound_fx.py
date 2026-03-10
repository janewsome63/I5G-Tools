import os
import variables as var
import pygame as p
import sys
import shutil

p.mixer.init()

sounds = {}

status = {
    "low": False,
    "high": False,
    "limit": False,
    "upshift_beep": False,
    "downshift_beep": False,
}

try:
    resources = sys._MEIPASS
except:
    resources = os.path.abspath(".")

if not os.path.exists(var.settings['path'] + "\\" + var.settings['sound']['path']):
    os.mkdir(var.settings['path'] + "\\" + var.settings['sound']['path'])

for sound in var.settings['sound']:
    if sound != "path" and "val" not in sound:
        source = resources + "\\" + var.settings['sound']['path'] + "\\" + var.settings['sound'][sound]
        sounds[sound] = var.settings['path'] + "\\" + var.settings['sound']['path'] + "\\" + var.settings['sound'][sound]
        if not os.path.exists(sounds[sound]):
            shutil.copyfile(source, sounds[sound])

hybrid_low = p.mixer.Sound(var.settings['path'] + "\\" + var.settings['sound']['path'] + "\\" + var.settings['sound']['hybrid_low'])
hybrid_high = p.mixer.Sound(var.settings['path'] + "\\" + var.settings['sound']['path'] + "\\" + var.settings['sound']['hybrid_high'])
hybrid_limit = p.mixer.Sound(var.settings['path'] + "\\" + var.settings['sound']['path'] + "\\" + var.settings['sound']['hybrid_limit'])
upshift_beep = p.mixer.Sound(var.settings['path'] + "\\" + var.settings['sound']['path'] + "\\" + var.settings['sound']['upshift_beep'])
downshift_beep = p.mixer.Sound(var.settings['path'] + "\\" + var.settings['sound']['path'] + "\\" + var.settings['sound']['downshift_beep'])

def play(notif):
    if status[notif] == False:
        print("playing notif: ", notif)
        if notif == "low":
            status[notif] = True
            hybrid_low.set_volume(var.settings['local']['volume'])
            hybrid_low.play()
            status[notif] = False
        elif notif == "high":
            status[notif] = True
            hybrid_high.set_volume(var.settings['local']['volume'])
            hybrid_high.play()
            status[notif] = False
        elif notif == "limit":
            status[notif] = True
            hybrid_limit.set_volume(var.settings['local']['volume'])
            hybrid_limit.play()
            status[notif] = False
        elif notif == "upshift_beep":
            status[notif] = True
            upshift_beep.set_volume(var.settings['local']['volume'])
            upshift_beep.play()
        elif notif == "downshift_beep":
            status[notif] = True
            downshift_beep.set_volume(var.settings['local']['volume'])
            downshift_beep.play()