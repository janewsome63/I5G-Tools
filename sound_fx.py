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

def play(notif):
    folder = var.settings['path'] + "\\" + var.settings['sound']['path'] + "\\"
    if status[notif] == False:
        print("playing notif: ", notif)
        if notif == "low":
            if os.path.exists(folder + var.settings['sound']['hybrid_low']):
                status[notif] = True
                p.mixer.music.load(folder + var.settings['sound']['hybrid_low'])
                p.mixer.music.set_volume(var.settings['local']['volume'])
                p.mixer.music.play()
                status[notif] = False
        elif notif == "high":
            if os.path.exists(folder + var.settings['sound']['hybrid_high']):
                status[notif] = True
                p.mixer.music.load(folder + var.settings['sound']['hybrid_high'])
                p.mixer.music.set_volume(var.settings['local']['volume'])
                p.mixer.music.play()
                status[notif] = False
        elif notif == "limit":
            if os.path.exists(folder + var.settings['sound']['hybrid_limit']):
                status[notif] = True
                p.mixer.music.load(folder + var.settings['sound']['hybrid_limit'])
                p.mixer.music.set_volume(var.settings['local']['volume'])
                p.mixer.music.play()
                status[notif] = False
        elif notif == "upshift_beep":
            if os.path.exists(folder + var.settings['sound']['upshift_beep']):
                status[notif] = True
                p.mixer.music.load(folder + var.settings['sound']['upshift_beep'])
                p.mixer.music.set_volume(var.settings['local']['volume'])
                p.mixer.music.play()
        elif notif == "downshift_beep":
            if os.path.exists(folder + var.settings['sound']['downshift_beep']):
                status[notif] = True
                p.mixer.music.load(folder + var.settings['sound']['downshift_beep'])
                p.mixer.music.set_volume(var.settings['local']['volume'])
                p.mixer.music.play()