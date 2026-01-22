import os
import variables as var
import pygame as p
import sys
import shutil

p.mixer.init()

sounds = {}

try:
    resources = sys._MEIPASS
except:
    resources = os.path.abspath(".")

if not os.path.exists(var.settings['path'] + "\\" + var.settings['sound']['path']):
    os.mkdir(var.settings['path'] + "\\" + var.settings['sound']['path'])

for sound in var.settings['sound']:
    if sound != "path":
        source = resources + "\\" + var.settings['sound']['path'] + "\\" + var.settings['sound'][sound]
        sounds[sound] = var.settings['path'] + "\\" + var.settings['sound']['path'] + "\\" + var.settings['sound'][sound]
        if not os.path.exists(sounds[sound]):
            shutil.copyfile(source, sounds[sound])

def play(notif):
    folder = var.settings['path'] + "\\" + var.settings['sound']['path'] + "\\"
    if notif == "low":
        if os.path.exists(folder + var.settings['sound']['hybrid_low']):
            p.mixer.music.load(folder + var.settings['sound']['hybrid_low'])
            p.mixer.music.set_volume(var.settings['local']['volume'])
            p.mixer.music.play()
    elif notif == "high":
        if os.path.exists(folder + var.settings['sound']['hybrid_high']):
            p.mixer.music.load(folder + var.settings['sound']['hybrid_high'])
            p.mixer.music.set_volume(var.settings['local']['volume'])
            p.mixer.music.play()
    elif notif == "limit":
        if os.path.exists(folder + var.settings['sound']['hybrid_limit']):
            p.mixer.music.load(folder + var.settings['sound']['hybrid_limit'])
            p.mixer.music.set_volume(var.settings['local']['volume'])
            p.mixer.music.play()