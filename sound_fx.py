import os
import variables as var
import functions as fn
import pygame as p
import sys
import shutil

p.mixer.init()

sounds = {}

status = {
    "hybrid_low": False,
    "hybrid_high": False,
    "hybrid_limit": False,
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
    'p2p_active_single': p.mixer.Sound(var.settings['path'] + "\\" + var.settings['sound']['path'] + "\\" + var.settings['sound']['p2p_active_single']),
    'p2p_active_loop': p.mixer.Sound(var.settings['path'] + "\\" + var.settings['sound']['path'] + "\\" + var.settings['sound']['p2p_active_loop']),
}

def play(notif):
    try:
        if not status[notif]:
            if not notif == "p2p_active_single" and not notif == "p2p_active_loop":
                print("playing notif: ", notif)
            if notif == "p2p_active_single" and status["p2p_active"] == False:
                if audio['p2p_active_single'].get_num_channels() == 0 and audio['p2p_active_loop'].get_num_channels() == 0: # not currently playing at all
                    print("playing notif: ", notif)
                    status[notif] = True
                    status["p2p_active"] = True
                    audio['p2p_active_single'].set_volume(var.settings['local']['volume'])
                    audio['p2p_active_single'].play()
                    status[notif] = False
                    # status["p2p_active_single"] = False # latch this elsewhere, only release it to False once p2p single is eligible to be played again
                else:
                    print ("p2p_active already playing ", audio['p2p_active_single'].get_num_channels(), " (single) and ", audio['p2p_active_loop'].get_num_channels(), " (cont) times")
            elif notif == "p2p_active_single" or notif == "p2p_active_loop":
                print ("in sfx.play for p2p_active, statuses are: ", status["p2p_active_single"], status['p2p_active_loop'])
            elif notif in audio:
                status[notif] = True
                audio[notif].set_volume(var.settings['local']['volume'])
                audio[notif].play()
                status[notif] = False
            else:
                print(notif, " is not valid in sfx.play")
        # else:
        #     print(notif, " sound status is already True in sfx.play")
    except Exception as e:
        fn.error_handling(e, "sound_fx.play()")

def play_loop(notif):
    try:
        if notif == "p2p_active_loop":
            if not status["p2p_active_loop"]:
                print("playing notif on loop: ", notif)
                audio['p2p_active_single'].stop() # if currently playing single
                status['p2p_active_single'] = False
                status[notif] = True
                status["p2p_active"] = True
                audio['p2p_active_loop'].set_volume(var.settings['local']['volume'])
                audio['p2p_active_loop'].play(loops=-1)
            else:
                print(notif, " sound status is already True in sfx.play_loop")
        else:
            print(notif, " is not valid in sfx.play_loop")
    except Exception as e:
        fn.error_handling(e, "sound_fx.play_loop()")

def play_num_loop(notif, num):
    try:
        if notif == "p2p_active_loop":
            if status["p2p_active_loop"] == False and audio['p2p_active_single'].get_num_channels() == 0 and audio['p2p_active_loop'].get_num_channels() == 0:
                print("playing notif on finite loop: ", notif, num)
                audio['p2p_active_single'].stop() # if currently playing single
                status['p2p_active_single'] = False
                status[notif] = True
                status["p2p_active"] = True
                audio['p2p_active_loop'].set_volume(var.settings['local']['volume'])
                audio['p2p_active_loop'].play(loops=num-1)
                status[notif] = False
                status["p2p_active"] = False
            else:
                print(notif, " sound status is already True in sfx.play_num_loop", audio['p2p_active'].get_num_channels(),"times")
        else:
            print(notif, " is not valid in sfx.play_num_loop")
    except Exception as e:
        fn.error_handling(e, "sound_fx.play_num_lop()")

def stop_loop(notif):
    try:
        if status[notif]:
            print("stopping notif: ", notif)
            if notif == "p2p_active_loop":
                audio['p2p_active_loop'].stop()
                status[notif] = False
                status["p2p_active_loop"] = False
        else:
            print(notif, " sound status is already True in sfx.stop_loop")
    except Exception as e:
        fn.error_handling(e, "sound_fx.stop_loop()")

def reset(notif):
    try:
        print("start sfx.reset() with", notif, var.settings['sound'][notif])
        audio[notif].stop()
        status[notif] = False
        if "p2p_active" in notif:
            status["p2p_active"] = False
            status["p2p_active_single"] = False
            status["p2p_active_loop"] = False
        audio[notif] = p.mixer.Sound(var.settings['path'] + "\\" + var.settings['sound']['path'] + "\\" + var.settings['sound'][notif])
        audio[notif].set_volume(var.settings['local']['volume'])
    except Exception as e:
        fn.error_handling(e, "sound_fx.reset()")