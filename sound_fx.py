import os
import variables as var
import pygame as p
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

p.mixer.init()
sound_file_low = resource_path("soclow.mp3")
sound_file_high = resource_path("sochigh.mp3")

print("sound file low ", sound_file_low)
print("sound file high ", sound_file_high)

def play(notif):
    if notif == "low":
        print("low sound")
        p.mixer.music.load(sound_file_low)
        p.mixer.music.play()
    elif notif == "high":
        print("high sound")
        p.mixer.music.load(sound_file_high)
        p.mixer.music.play()