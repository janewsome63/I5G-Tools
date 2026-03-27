import os
import variables as var
import pygame as p
import sys
import shutil
from time import sleep

p.mixer.init()

sounds = {}

status = {
    "low": False,
    "high": False,
    "limit": False,
    "upshift_beep": False,
    "downshift_beep": False,
    "p2p_active": False,
    "p2p_active_single": False,
    "p2p_active_loop": False,
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
p2p_active = p.mixer.Sound(var.settings['path'] + "\\" + var.settings['sound']['path'] + "\\" + var.settings['sound']['p2p_active'])

def play(notif):
    if status[notif] == False:
        if not notif == "p2p_active":
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
        elif notif == "p2p_active" and status["p2p_active_single"] == False and status['p2p_active_loop'] == False:
            if p2p_active.get_num_channels() == 0: # not currently playing at all
                print("playing notif: ", notif)
                status[notif] = True
                status["p2p_active_single"] = True
                p2p_active.set_volume(var.settings['local']['volume'])
                p2p_active.play()
                status[notif] = False
                # status["p2p_active_single"] = False # latch this elsewhere, only release it to False once p2p single is eligible to be played again
            else:
                print ("p2p_active already playing ", p2p_active.get_num_channels(), " times")

def play_loop(notif):
    if notif == "p2p_active":
        if status["p2p_active_loop"] == False:
            print("playing notif on loop: ", notif)
            p2p_active.stop() # if currently playing single
            status['p2p_active_single'] = False
            status[notif] = True
            status["p2p_active_loop"] = True
            p2p_active.set_volume(var.settings['local']['volume'])
            p2p_active.play(loops=-1)

def stop_loop(notif):
    if status[notif] == True:
        print("stopping notif on loop: ", notif)
        if notif == "p2p_active":
            p2p_active.stop()
            status[notif] = False
            status["p2p_active_loop"] = False