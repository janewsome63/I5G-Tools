import threading

import devices as dev
import interface as ui
import vjoy

if __name__ == '__main__':
    detect = threading.Thread(target=dev.device_detection, daemon=True)
    detect.start()

    vjoy.intialize()
    ui.main()