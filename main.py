import controls as con
import devices as dev
import functions as fn
import interface as ui
import variables as var
import vjoy
import threading
from PyQt5.QtCore import pyqtSignal
from time import sleep

from devices import device_info

def weight_jacker_increment():
    con.increment("weight_jacker")

def weight_jacker_switch():
    con.switch("weight_jacker")

if __name__ == '__main__':
    detect = threading.Thread(target=dev.device_detection, daemon=True)
    detect.start()
    wj_increment = threading.Thread(target=weight_jacker_increment, daemon=True)
    wj_increment.start()
    wj_switch = threading.Thread(target=weight_jacker_switch, daemon=True)
    wj_switch.start()

    vjoy.intialize()
    ui.main()