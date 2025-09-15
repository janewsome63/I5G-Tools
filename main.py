import devices as dev
import functions as fn
import interface as ui
import variables as var
import threading
from PyQt5.QtCore import pyqtSignal
from time import sleep

import vjoy


def main():
    pct = 0.0
    sleep(5)
    vjoy.calibrate_axis("x")
    while True:
        #vjoy.set_wj(pct)
        #pct = pct + 0.01
        sleep(0.25)

if __name__ == '__main__':
    detect = threading.Thread(target=dev.device_detection, daemon=True)
    detect.start()
    main = threading.Thread(target=main, daemon=True)
    main.start()

    fn.init_vars()

    sleep(0.0)
    ui.ui()