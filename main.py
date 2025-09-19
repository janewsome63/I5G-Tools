import devices as dev
import functions as fn
import interface as ui
import variables as var
import vjoy
import threading
from PyQt5.QtCore import pyqtSignal
from time import sleep

from devices import device_info


def main():
    vjoy.intialize()
    while True:
        sleep(0.25)

if __name__ == '__main__':
    detect = threading.Thread(target=dev.device_detection, daemon=True)
    detect.start()
    main = threading.Thread(target=main, daemon=True)
    main.start()

    fn.init_vars()

    sleep(0.0)
    ui.main()