import os
import variables as var
import functions as fn
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
    "p2p_active": False,
    "p2p_active_single": False,
    "p2p_active_loop": False,
}

# noinspection PyBroadException
try:
    # noinspection PyProtectedMember
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

audio = {
    'hybrid_low': p.mixer.Sound(var.settings['path'] + "\\" + var.settings['sound']['path'] + "\\" + var.settings['sound']['hybrid_low']),
    'hybrid_high': p.mixer.Sound(var.settings['path'] + "\\" + var.settings['sound']['path'] + "\\" + var.settings['sound']['hybrid_high']),
    'hybrid_limit': p.mixer.Sound(var.settings['path'] + "\\" + var.settings['sound']['path'] + "\\" + var.settings['sound']['hybrid_limit']),
    'upshift_beep': p.mixer.Sound(var.settings['path'] + "\\" + var.settings['sound']['path'] + "\\" + var.settings['sound']['upshift_beep']),
    'downshift_beep': p.mixer.Sound(var.settings['path'] + "\\" + var.settings['sound']['path'] + "\\" + var.settings['sound']['downshift_beep']),
    'p2p_active': p.mixer.Sound(var.settings['path'] + "\\" + var.settings['sound']['path'] + "\\" + var.settings['sound']['p2p_active']),
}

def play(notif):
    try:
        if not status[notif]:
            if not notif == "p2p_active":
                print("playing notif: ", notif)
            if notif == "low":
                status[notif] = True
                audio['hybrid_low'].set_volume(var.settings['local']['volume'])
                audio['hybrid_low'].play()
                status[notif] = False
            elif notif == "high":
                status[notif] = True
                audio['hybrid_high'].set_volume(var.settings['local']['volume'])
                audio['hybrid_high'].play()
                status[notif] = False
            elif notif == "limit":
                status[notif] = True
                audio['hybrid_limit'].set_volume(var.settings['local']['volume'])
                audio['hybrid_limit'].play()
                status[notif] = False
            elif notif == "upshift_beep":
                status[notif] = True
                audio['upshift_beep'].set_volume(var.settings['local']['volume'])
                audio['upshift_beep'].play()
            elif notif == "downshift_beep":
                status[notif] = True
                audio['downshift_beep'].set_volume(var.settings['local']['volume'])
                audio['downshift_beep'].play()
            elif notif == "p2p_active" and status["p2p_active_single"] == False and status['p2p_active_loop'] == False:
                if audio['p2p_active'].get_num_channels() == 0: # not currently playing at all
                    print("playing notif: ", notif)
                    status[notif] = True
                    status["p2p_active_single"] = True
                    audio['p2p_active'].set_volume(var.settings['local']['volume'])
                    audio['p2p_active'].play()
                    status[notif] = False
                    # status["p2p_active_single"] = False # latch this elsewhere, only release it to False once p2p single is eligible to be played again
                else:
                    print ("p2p_active already playing ", audio['p2p_active'].get_num_channels(), " times")
            elif notif == "p2p_active":
                print ("in sfx.play for p2p_active, statuses are: ", status["p2p_active_single"], status['p2p_active_loop'])
            else:
                print(notif, " is not valid in sfx.play")
        else:
            print(notif, " sound status is already True in sfx.play")
    except Exception as e:
        fn.error_handling(e, "sound_fx.play()")

def play_loop(notif):
    try:
        if notif == "p2p_active":
            if not status["p2p_active_loop"]:
                print("playing notif on loop: ", notif)
                audio['p2p_active'].stop() # if currently playing single
                status['p2p_active_single'] = False
                status[notif] = True
                status["p2p_active_loop"] = True
                audio['p2p_active'].set_volume(var.settings['local']['volume'])
                audio['p2p_active'].play(loops=-1)
            else:
                print(notif, " sound status is already True in sfx.play_loop")
        else:
            print(notif, " is not valid in sfx.play_loop")
    except Exception as e:
        fn.error_handling(e, "sound_fx.play_loop()")

def play_num_loop(notif, num):
    try:
        if notif == "p2p_active":
            if status["p2p_active_loop"] == False and audio['p2p_active'].get_num_channels() == 0:
                print("playing notif on finite loop: ", notif, num)
                audio['p2p_active'].stop() # if currently playing single
                status['p2p_active_single'] = False
                status[notif] = True
                status["p2p_active_loop"] = True
                audio['p2p_active'].set_volume(var.settings['local']['volume'])
                audio['p2p_active'].play(loops=num-1)
                status[notif] = False
                status["p2p_active_loop"] = False
            else:
                print(notif, " sound status is already True in sfx.play_num_loop", audio['p2p_active'].get_num_channels(),"times")
        else:
            print(notif, " is not valid in sfx.play_num_loop")
    except Exception as e:
        fn.error_handling(e, "sound_fx.play_num_lop()")

def stop_loop(notif):
    try:
        if status[notif]:
            print("stopping notif on loop: ", notif)
            if notif == "p2p_active":
                audio['p2p_active'].stop()
                status[notif] = False
                status["p2p_active_loop"] = False
        else:
            print(notif, " sound status is already True in sfx.stop_loop")
    except Exception as e:
        fn.error_handling(e, "sound_fx.stop_loop()")