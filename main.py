import controls as con
import devices as dev
import interface as ui
import vjoy

import threading

if __name__ == '__main__':
    detect = threading.Thread(target=dev.device_detection, daemon=True)
    detect.start()

    vjoy.intialize()
    ui.main()